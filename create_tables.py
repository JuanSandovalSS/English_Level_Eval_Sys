-- create_tables.sql
-- Eliminar tablas si existen (en orden inverso por dependencias)
DROP TABLE IF EXISTS predicciones CASCADE;
DROP TABLE IF EXISTS analisis_nlp CASCADE;
DROP TABLE IF EXISTS respuestas CASCADE;
DROP TABLE IF EXISTS evaluaciones CASCADE;
DROP TABLE IF EXISTS preguntas CASCADE;
DROP TABLE IF EXISTS modelos CASCADE;
DROP TABLE IF EXISTS historial_niveles CASCADE;
DROP TABLE IF EXISTS categorias CASCADE;
DROP TABLE IF EXISTS niveles_mcer CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

-- Tabla de usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'ESTUDIANTE',
    estado BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP
);

-- Tabla de niveles MCER
CREATE TABLE niveles_mcer (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(2) UNIQUE NOT NULL,
    nombre VARCHAR(50),
    descripcion TEXT
);

-- Tabla de categorías
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT
);

-- Tabla de preguntas
CREATE TABLE preguntas (
    id SERIAL PRIMARY KEY,
    texto TEXT NOT NULL,
    instrucciones TEXT,
    nivel_id INTEGER NOT NULL REFERENCES niveles_mcer(id),
    categoria_id INTEGER NOT NULL REFERENCES categorias(id),
    dificultad INTEGER DEFAULT 1,
    activa BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de evaluaciones
CREATE TABLE evaluaciones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP,
    nivel_estimado_id INTEGER REFERENCES niveles_mcer(id),
    estado VARCHAR(30) DEFAULT 'EN_PROCESO',
    accuracy NUMERIC(5,2),
    precision NUMERIC(5,2),
    recall NUMERIC(5,2),
    f1_score NUMERIC(5,2)
);

-- Tabla de respuestas
CREATE TABLE respuestas (
    id SERIAL PRIMARY KEY,
    evaluacion_id INTEGER NOT NULL REFERENCES evaluaciones(id),
    pregunta_id INTEGER NOT NULL REFERENCES preguntas(id),
    texto TEXT NOT NULL,
    embedding TEXT,
    caracteristicas TEXT,
    nivel_predicho_id INTEGER REFERENCES niveles_mcer(id),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de modelos IA
CREATE TABLE modelos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    version VARCHAR(30),
    accuracy NUMERIC(5,2),
    precision NUMERIC(5,2),
    recall NUMERIC(5,2),
    f1 NUMERIC(5,2),
    fecha_entrenamiento TIMESTAMP,
    activo BOOLEAN DEFAULT FALSE
);

-- Tabla de historial
CREATE TABLE historial_niveles (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    evaluacion_id INTEGER REFERENCES evaluaciones(id),
    nivel_id INTEGER REFERENCES niveles_mcer(id),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar niveles MCER
INSERT INTO niveles_mcer (codigo, nombre) VALUES 
('A1', 'Principiante'),
('A2', 'Elemental'),
('B1', 'Intermedio'),
('B2', 'Intermedio Alto'),
('C1', 'Avanzado'),
('C2', 'Competente');

-- Insertar categorías
INSERT INTO categorias (nombre) VALUES 
('Gramática'),
('Vocabulario'),
('Escritura'),
('Lectura');

-- Insertar administrador
INSERT INTO usuarios (nombre, apellido, correo, password, rol) VALUES 
('Administrador', 'Sistema', 'admin@system.com', 'scrypt:32768:8:1$f4k5N...', 'ADMINISTRADOR');