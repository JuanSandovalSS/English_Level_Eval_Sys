# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='ESTUDIANTE')
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)
    
    evaluaciones = db.relationship('Evaluacion', backref='usuario', lazy=True)
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<Usuario {self.nombre} {self.apellido}>'

class NivelMCER(db.Model):
    __tablename__ = 'niveles_mcer'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(2), unique=True, nullable=False)
    nombre = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    
    preguntas = db.relationship('Pregunta', backref='nivel', lazy=True)
    
    def __repr__(self):
        return f'<Nivel {self.codigo}>'

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    
    preguntas = db.relationship('Pregunta', backref='categoria', lazy=True)
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'

class Pregunta(db.Model):
    __tablename__ = 'preguntas'
    
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    instrucciones = db.Column(db.Text)
    nivel_id = db.Column(db.Integer, db.ForeignKey('niveles_mcer.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    dificultad = db.Column(db.Integer, default=1)
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    respuestas = db.relationship('Respuesta', backref='pregunta', lazy=True)
    
    def __repr__(self):
        return f'<Pregunta {self.id}>'

class Evaluacion(db.Model):
    __tablename__ = 'evaluaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime)
    nivel_estimado_id = db.Column(db.Integer, db.ForeignKey('niveles_mcer.id'))
    estado = db.Column(db.String(30), default='EN_PROCESO')
    accuracy = db.Column(db.Numeric(5, 2))
    precision = db.Column(db.Numeric(5, 2))
    recall = db.Column(db.Numeric(5, 2))
    f1_score = db.Column(db.Numeric(5, 2))
    
    respuestas = db.relationship('Respuesta', backref='evaluacion', lazy=True)
    nivel_estimado = db.relationship('NivelMCER', foreign_keys=[nivel_estimado_id])
    
    def __repr__(self):
        return f'<Evaluacion {self.id}>'

class Respuesta(db.Model):
    __tablename__ = 'respuestas'
    
    id = db.Column(db.Integer, primary_key=True)
    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluaciones.id'), nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.Text)
    caracteristicas = db.Column(db.Text)
    nivel_predicho_id = db.Column(db.Integer, db.ForeignKey('niveles_mcer.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    nivel_predicho = db.relationship('NivelMCER', foreign_keys=[nivel_predicho_id])
    
    def __repr__(self):
        return f'<Respuesta {self.id}>'

class ModeloIA(db.Model):
    __tablename__ = 'modelos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    version = db.Column(db.String(30))
    accuracy = db.Column(db.Numeric(5, 2))
    precision = db.Column(db.Numeric(5, 2))
    recall = db.Column(db.Numeric(5, 2))
    f1 = db.Column(db.Numeric(5, 2))
    fecha_entrenamiento = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Modelo {self.nombre} v{self.version}>'