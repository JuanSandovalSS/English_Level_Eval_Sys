# init_db.py
from app import app
from models import db

with app.app_context():
    print("📁 Creando tablas...")
    db.create_all()
    print("✅ Tablas creadas correctamente")
    print("📋 Tablas existentes:", db.engine.table_names())