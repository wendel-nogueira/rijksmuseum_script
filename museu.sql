CREATE TABLE autor (
    id_autor varchar(36) NOT NULL,
    nome varchar(500) NOT NULL,
    nacionalidade varchar(20),
    ano_nascimento smallint,
    local_nascimento varchar(50),
    ano_morte smallint,
    local_morte varchar(50),
    CONSTRAINT autor_pkey PRIMARY KEY (id_autor)
);

CREATE TABLE ocupacao (
    id_ocupacao varchar(36) NOT NULL,
    nome_ocupacao varchar(50) NOT NULL,
    CONSTRAINT ocupacao_pkey PRIMARY KEY (id_ocupacao)
);

CREATE TABLE obra (
    num_objeto varchar(36) NOT NULL,
    nome varchar(500) NOT NULL,
    tecnica varchar(500) NOT NULL,
    tipo varchar(500) NOT NULL,
    descricao text NOT NULL,
    url_obra text NOT NULL,
    CONSTRAINT obra_pkey PRIMARY KEY (num_objeto)
);

CREATE TABLE assunto (
    id_assunto varchar(36) NOT NULL,
    nome_assunto varchar(500) NOT NULL,
    CONSTRAINT assunto_pkey PRIMARY KEY (id_assunto)
);

CREATE TABLE material (
    id_material varchar(36) NOT NULL,
    nome_material varchar(500) NOT NULL,
    CONSTRAINT material_pkey PRIMARY KEY (id_material)
);

CREATE TABLE criacao_obra (
    id_autor varchar(36) NOT NULL,
    num_objeto varchar(36) NOT NULL,
    ano_criacao smallint,
    CONSTRAINT criacao_obra_id_autor_fkey FOREIGN KEY (id_autor)
        REFERENCES autor (id_autor) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT criacao_obra_num_objeto_fkey FOREIGN KEY (num_objeto)
        REFERENCES obra (num_objeto) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE possui_ocupacao (
    id_autor varchar(36) NOT NULL,
    id_ocupacao varchar(36) NOT NULL,
    CONSTRAINT possui_ocupacao_id_autor_fkey FOREIGN KEY (id_autor)
        REFERENCES autor (id_autor) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT possui_ocupacao_id_ocupacao_fkey FOREIGN KEY (id_ocupacao)
        REFERENCES ocupacao (id_ocupacao) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE obra_material (
    id_material varchar(36) NOT NULL,
    num_objeto varchar(36) NOT NULL,
    CONSTRAINT obra_material_id_material_fkey FOREIGN KEY (id_material)
        REFERENCES material (id_material) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT obra_material_num_objeto_fkey FOREIGN KEY (num_objeto)
        REFERENCES obra (num_objeto) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE obra_assunto (
    id_assunto varchar(36) NOT NULL,
    num_objeto varchar(36) NOT NULL,
    CONSTRAINT obra_assunto_id_assunto_fkey FOREIGN KEY (id_assunto)
        REFERENCES assunto (id_assunto) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT obra_assunto_num_objeto_fkey FOREIGN KEY (num_objeto)
        REFERENCES obra (num_objeto) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


CREATE ROLE dba_db;
GRANT ALL ON SCHEMA public TO dba_db;
CREATE USER admin_user WITH PASSWORD 'admin';
GRANT dba_db TO admin_user;

CREATE ROLE insert_db;
GRANT INSERT ON ALL TABLES IN SCHEMA public TO insert_db;
CREATE USER app_user WITH PASSWORD 'app';
GRANT insert_db TO app_user;

CREATE ROLE select_db;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO select_db;
CREATE USER relatorio_user WITH PASSWORD 'relatorio';
GRANT select_db TO relatorio_user;


CREATE INDEX "idx_nome_obra" ON obra USING btree (nome);
CREATE INDEX "idx_tipo_obra" ON obra USING btree (tipo);
CREATE INDEX "idx_nome_autor" ON autor USING btree (nome);
CREATE INDEX "idx_ano_criacao_obra" ON criacao_obra USING btree (ano_criacao);


CREATE OR REPLACE VIEW public.busca_obra AS 
	SELECT 
		o.num_objeto,
		o.nome,
		o.tipo,
		o.tecnica,
		o.descricao,
		o.url_obra,
		ARRAY(
			SELECT a.nome_assunto 
			FROM assunto a 
			INNER JOIN obra_assunto oa ON a.id_assunto = oa.id_assunto
			WHERE oa.num_objeto = o.num_objeto
		) AS assuntos,
		ARRAY(
			SELECT m.nome_material 
			FROM material m 
			INNER JOIN obra_material om ON m.id_material = om.id_material
			WHERE om.num_objeto = o.num_objeto
		) AS materiais,
		a.nome as autor,
		co.ano_criacao
	FROM obra o 
	FULL JOIN criacao_obra co on co.num_objeto = o.num_objeto
	FULL JOIN autor a on a.id_autor = co.id_autor
	ORDER BY random() LIMIT 1;










