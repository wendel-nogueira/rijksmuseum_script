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