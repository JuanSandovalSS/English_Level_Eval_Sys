# config.py
import os

class Config:
    SECRET_KEY = 'dev-secret-key-12345'
    
    # CAMBIAR A SQLite (no necesita PostgreSQL)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///evaluacion_ingles.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'models')