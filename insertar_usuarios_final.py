# insertar_usuarios_final.py - VERSIÓN CORRECTA
from app import app
from models import db, Usuario
from werkzeug.security import generate_password_hash

def insertar_usuarios():
    with app.app_context():
        usuarios_data = [
            ('Carlos', 'López', 'carlos.lopez@gmail.com'),
            ('María', 'García', 'maria.garcia@gmail.com'),
            ('José', 'Martínez', 'jose.martinez@gmail.com'),
            ('Ana', 'Pérez', 'ana.perez@gmail.com'),
            ('Luis', 'Rodríguez', 'luis.rodriguez@gmail.com'),
            ('Marta', 'Fernández', 'marta.fernandez@gmail.com'),
            ('Juan', 'Hernández', 'juan.hernandez@gmail.com'),
            ('Patricia', 'Ramírez', 'patricia.ramirez@gmail.com'),
            ('Francisco', 'Morales', 'francisco.morales@gmail.com'),
            ('Laura', 'Mendoza', 'laura.mendoza@gmail.com'),
            ('Manuel', 'Ortega', 'manuel.ortega@gmail.com'),
            ('Karen', 'Reyes', 'karen.reyes@gmail.com'),
            ('Roberto', 'Guzmán', 'roberto.guzman@gmail.com'),
            ('Andrea', 'Castro', 'andrea.castro@gmail.com'),
            ('Antonio', 'Romero', 'antonio.romero@gmail.com'),
            ('Gabriela', 'Sandoval', 'gabriela.sandoval@gmail.com'),
            ('Jorge', 'Alvarado', 'jorge.alvarado@gmail.com'),
            ('Carolina', 'Cruz', 'carolina.cruz@gmail.com'),
            ('Fernando', 'Soto', 'fernando.soto@gmail.com'),
            ('Paola', 'Núñez', 'paola.nunez@gmail.com')
        ]
        
        contador = 0
        for nombre, apellido, email in usuarios_data:
            if not Usuario.query.filter_by(correo=email).first():
                usuario = Usuario(
                    nombre=nombre,
                    apellido=apellido,
                    correo=email,
                    password=generate_password_hash('password123'),
                    rol='ESTUDIANTE'
                )
                db.session.add(usuario)
                contador += 1
                print(f"✅ Usuario añadido: {nombre} {apellido} - {email}")
        
        db.session.commit()
        print(f"\n✅ Total de usuarios insertados: {contador}")

if __name__ == "__main__":
    insertar_usuarios()