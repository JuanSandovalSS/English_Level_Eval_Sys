# insertar_usuarios.py
import json
from app import app
from models import db, Usuario
from werkzeug.security import generate_password_hash

def insertar_usuarios():
    with app.app_context():
        try:
            with open('data/usuarios_validacion.json', 'r', encoding='utf-8') as f:
                usuarios_data = json.load(f)
            
            contador = 0
            for user_data in usuarios_data:
                existente = Usuario.query.filter_by(correo=user_data['email']).first()
                if not existente:
                    usuario = Usuario(
                        nombre=user_data['nombre'],
                        apellido=user_data['apellido'],
                        correo=user_data['email'],
                        password=generate_password_hash('password123'),
                        rol='ESTUDIANTE'
                    )
                    db.session.add(usuario)
                    contador += 1
                    print(f"✅ Usuario añadido: {user_data['nombre_completo']} ({user_data['email']})")
            
            db.session.commit()
            print(f"\n✅ Total de usuarios insertados: {contador}")
            
        except FileNotFoundError:
            print("❌ Archivo 'data/usuarios_validacion.json' no encontrado.")
            print("   Ejecuta primero: python generate_test_data.py")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    insertar_usuarios()