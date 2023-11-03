import sys
import requests
import json
from peewee import *
import os
from dotenv import load_dotenv
import time
import uuid


load_dotenv()


# Conexão com o banco de dados
class Database:
    def __init__(self):
        self.database = PostgresqlDatabase(
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
        )

        try:
            self.database.connect()
            print('Conexão com o banco de dados estabelecida!')
        except:
            print('Não foi possível conectar ao banco de dados!')

    def close(self):
        self.database.close()
        print('Conexão com o banco de dados encerrada!')

    def table_exists(self, table_name):
        return self.database.table_exists(table_name, schema='public')

    def getDatabase(self):
        return self.database


# Consumidor de dados
class Consumer:
    def __init__(self):
        self.url_art = 'https://www.rijksmuseum.nl/api/en/collection'
        self.url_artists = 'https://www.rijksmuseum.nl/en/collection/'
        self.api_key = os.getenv('API_KEY')

    def request(self, endpoint):
        response = requests.get(self.url_art + endpoint)
        return json.loads(response.text)

    def request_page(self, page):
        endpoint = '?key=' + self.api_key + \
            '&format=json&ps=100&p=' + str(page)
        return self.request(endpoint)

    def request_art(self, object_number):
        endpoint = '/' + \
            object_number + '?key=' + self.api_key + '&format=json&ps=100'
        return self.request(endpoint)


# Publicador de dados
class Publisher:
    def __init__(self):
        self.database = Database()
        self.db = self.database.getDatabase()

    def verify_art_exists(self, object_number):
        art_exists = self.db.execute_sql(
            'SELECT * FROM obra WHERE num_objeto = %s', (object_number,)).fetchone()

        return art_exists != None

    def verify_artist_exists(self, artist_name):
        artist_exists = self.db.execute_sql(
            'SELECT * FROM autor WHERE nome = %s', (artist_name,)).fetchone()

        return artist_exists != None

    def verify_occupation_exists(self, occupation_name):
        occupation_exists = self.db.execute_sql(
            'SELECT * FROM ocupacao WHERE nome_ocupacao = %s', (occupation_name,)).fetchone()

        return occupation_exists != None

    def verify_material_exists(self, material_name):
        material_exists = self.db.execute_sql(
            'SELECT * FROM material WHERE nome_material = %s', (material_name,)).fetchone()

        return material_exists != None

    def verify_subject_exists(self, subject_name):
        subject_exists = self.db.execute_sql(
            'SELECT * FROM assunto WHERE nome_assunto = %s', (subject_name,)).fetchone()

        return subject_exists != None

    def save_art(self, obj):
        try:
            self.db.execute_sql('INSERT INTO obra (num_objeto, nome, tecnica, tipo, descricao, url_obra) VALUES (%s, %s, %s, %s, %s, %s)', (
                obj['objectNumber'],
                obj['title'],
                obj['technique'],
                obj['type'],
                obj['description'],
                obj['image']))

            if len(obj['materials']) > 0:
                for material in obj['materials']:
                    material_id = uuid.uuid4()

                    if self.verify_material_exists(material):
                        material_exists = self.db.execute_sql(
                            'SELECT * FROM material WHERE nome_material = %s', (material,)).fetchone()

                        material_id = material_exists[0]
                    else:
                        self.db.execute_sql('INSERT INTO material (id_material, nome_material) VALUES (%s, %s)', (
                            material_id,
                            material))

                    self.db.execute_sql('INSERT INTO obra_material (id_material, num_objeto) VALUES (%s, %s)', (
                        material_id,
                        obj['objectNumber']))

            if len(obj['subject']) > 0:
                for subject in obj['subject']:
                    subject_id = uuid.uuid4()

                    if self.verify_subject_exists(subject):
                        subject_exists = self.db.execute_sql(
                            'SELECT * FROM assunto WHERE nome_assunto = %s', (subject,)).fetchone()

                        subject_id = subject_exists[0]
                    else:
                        self.db.execute_sql('INSERT INTO assunto (id_assunto, nome_assunto) VALUES (%s, %s)', (
                            subject_id,
                            subject))

                    self.db.execute_sql('INSERT INTO obra_assunto (id_assunto, num_objeto) VALUES (%s, %s)', (
                        subject_id,
                        obj['objectNumber']))
        except Exception as e:
            print('Erro ao salvar obra ' + obj['objectNumber'] + '!')
            print('Erro: ' + str(e))
            print(sys.exc_info()[-1].tb_lineno)
            raise e

    def save_artists(self, obj):
        for maker in obj['makers']:
            try:
                maker_id = uuid.uuid4()

                if self.verify_artist_exists(maker['name']):
                    maker_exists = self.db.execute_sql(
                        'SELECT * FROM autor WHERE nome = %s', (maker['name'],)).fetchone()
                    maker_id = maker_exists[0]
                else:
                    self.db.execute_sql('INSERT INTO autor (id_autor, nome, nacionalidade, ano_nascimento, local_nascimento, ano_morte, local_morte) VALUES (%s, %s, %s, %s, %s, %s, %s)', (
                        maker_id,
                        maker['name'],
                        maker['nationality'],
                        maker['yearOfBirth'],
                        maker['placeOfBirth'],
                        maker['yearOfDeath'],
                        maker['placeOfDeath']))

                    if len(maker['occupation']) > 0:
                        for occupation in maker['occupation']:
                            occupation_id = uuid.uuid4()

                            if self.verify_occupation_exists(occupation):
                                occupation_exists = self.db.execute_sql(
                                    'SELECT * FROM ocupacao WHERE nome_ocupacao = %s', (occupation,)).fetchone()
                                occupation_id = occupation_exists[0]
                            else:
                                self.db.execute_sql('INSERT INTO ocupacao (id_ocupacao, nome_ocupacao) VALUES (%s, %s)', (
                                    occupation_id,
                                    occupation))

                            self.db.execute_sql('INSERT INTO possui_ocupacao (id_autor, id_ocupacao) VALUES (%s, %s)', (
                                maker_id,
                                occupation_id))

                self.db.execute_sql('INSERT INTO criacao_obra (id_autor, num_objeto, ano_criacao) VALUES (%s, %s, %s)', (
                    maker_id,
                    obj['objectNumber'],
                    obj['year']))

            except Exception as e:
                print('Erro ao salvar autor ' + maker['name'] + '!')
                print('Erro: ' + str(e))
                print(sys.exc_info()[-1].tb_lineno)
                raise e


# Coleta e tratamento de dados
def collect_data(page=0):
    consumer = Consumer()

    if not os.path.exists('data'):
        os.makedirs('data')

    print('Coletando página ' + str(page) + '...')

    objects = []
    data = consumer.request_page(page)

    if data['count'] == 0:
        print('Página ' + str(page) + ' não possui dados!')
        return

    for art in data['artObjects']:
        objectToSave = {}

        # Coletando dados de cada obra
        data = consumer.request_art(art['objectNumber'])

        print('Coletando dados da obra ' + art['objectNumber'] + '...')

        if 'artObject' not in data:
            print('Obra ' + art['objectNumber'] + ' não possui dados!')
            continue

        objectToSave['objectNumber'] = data['artObject']['objectNumber']
        objectToSave['title'] = data['artObject']['title']
        objectToSave['technique'] = ''

        if data['artObject']['physicalMedium'] != None:
            objectToSave['technique'] = data['artObject']['physicalMedium']

        objectToSave['type'] = data['artObject']['objectTypes'][0] if len(
            data['artObject']['objectTypes']) > 0 else ''
        objectToSave['description'] = ''

        if data['artObject']['label']['description'] != None:
            objectToSave['description'] = data['artObject']['label']['description']

        objectToSave['subject'] = data['artObject']['classification']['iconClassDescription']
        objectToSave['image'] = data['artObject']['webImage']['url'] if 'webImage' in data[
            'artObject'] and data['artObject']['webImage'] != None else ''
        objectToSave['materials'] = data['artObject']['materials']

        if data['artObject']['dating']['sortingDate'] != None:
            objectToSave['year'] = data['artObject']['dating']['sortingDate']
        else:
            objectToSave['year'] = None

        # Coletando dados de cada autor
        objectToSave['makers'] = []

        if len(data['artObject']['principalMakers']) > 0:
            for maker in data['artObject']['principalMakers']:
                if maker['name'] == 'anonymous':
                    continue

                makerToSave = {}

                makerToSave['name'] = maker['name']
                makerToSave['nationality'] = maker['nationality']
                makerToSave['placeOfBirth'] = maker['placeOfBirth']
                makerToSave['placeOfDeath'] = maker['placeOfDeath']
                makerToSave['occupation'] = maker['occupation']

                if maker['dateOfBirth'] != None and len(maker['dateOfBirth']) == 4:
                    makerToSave['yearOfBirth'] = int(maker['dateOfBirth'])
                elif maker['dateOfBirth'] != None and len(maker['dateOfBirth']) > 4:
                    makerToSave['yearOfBirth'] = int(maker['dateOfBirth'][:4])
                else:
                    makerToSave['yearOfBirth'] = None

                if maker['dateOfDeath'] != None and len(maker['dateOfDeath']) == 4:
                    makerToSave['yearOfDeath'] = int(maker['dateOfDeath'])
                elif maker['dateOfDeath'] != None and len(maker['dateOfDeath']) > 4:
                    makerToSave['yearOfDeath'] = int(maker['dateOfDeath'][:4])
                else:
                    makerToSave['yearOfDeath'] = None

                objectToSave['makers'].append(makerToSave)

        objects.append(objectToSave)
        time.sleep(1)

    print('Coleta de dados finalizada!')

    # Salvando dados no arquivo
    with open('data/data-' + str(page) + '.json', 'w') as outfile:
        json.dump(objects, outfile)

    return objects


# Salvamento de dados
def save_data(objects):
    print('Iniciando salvamento de dados...')

    publisher = Publisher()

    for obj in objects:
        print('Salvando obra ' + obj['objectNumber'] + '...')

        try:
            if publisher.verify_art_exists(obj['objectNumber']):
                print('Obra ' + obj['objectNumber'] + ' já existe!')
                continue

            # Salvando dados da obra
            publisher.save_art(obj)

            # Salvando dados dos autores
            publisher.save_artists(obj)

            print('Obra ' + obj['objectNumber'] + ' salva com sucesso!')
        except Exception as e:
            print('Erro: ' + str(e))


# Função principal
def main():
    for page in range(0, 101):
        start_time = time.time()
        
        objects = collect_data(page)
        save_data(objects)

        print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    main()
