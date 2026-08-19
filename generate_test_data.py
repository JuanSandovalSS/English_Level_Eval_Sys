import json
import random
import os
from datetime import datetime, timedelta
from nlp_service import NLPService
from classifier_service import ClassifierService

class TestDataGenerator:
    def __init__(self):
        self.nlp_service = NLPService()
        self.classifier_service = ClassifierService()
        self.data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        
        # Nombres comunes de Guatemala (no indígenas)
        self.nombres = [
            "Carlos", "María", "José", "Ana", "Luis", "Marta", "Juan", "Patricia",
            "Francisco", "Laura", "Manuel", "Karen", "Roberto", "Andrea", "Antonio",
            "Gabriela", "Jorge", "Carolina", "Fernando", "Paola", "Oscar", "Claudia",
            "Rafael", "Daniela", "Ricardo", "Valeria", "Hugo", "Melissa", "Samuel",
            "Sofía", "Mario", "Natalia", "Alberto", "Raquel", "Eduardo", "Pamela"
        ]
        
        self.apellidos = [
            "López", "García", "Martínez", "Pérez", "Rodríguez", "González", "Fernández",
            "Hernández", "Ramírez", "Morales", "Mendoza", "Ortega", "Reyes", "Guzmán",
            "Castro", "Romero", "Sandoval", "Alvarado", "Cruz", "Soto", "Núñez", "Jiménez",
            "Ruiz", "Castillo", "Díaz", "Rivera", "Pinto", "Rivas", "Molina", "Leiva",
            "González", "Vásquez", "Carrillo", "Espinoza", "Salazar", "Mejía"
        ]
        
        # Textos de ejemplo por nivel para usuarios
        self.user_texts = {
            'A1': [
                "Hello my name is {nombre}. I am from Guatemala. I live in {ciudad}. I like to read books and watch TV.",
                "My family is small. I have a mother and father. I have two brothers. We live together in a house.",
                "I go to school every day. I study English and Math. My favorite subject is English.",
                "I like to eat pizza and hamburgers. On weekends I go to the park with my friends.",
                "My house is near the school. I walk to school every morning. It takes 15 minutes."
            ],
            'A2': [
                "I work as a {profesion} in a company in {ciudad}. My job is interesting. I use English sometimes at work.",
                "Yesterday I visited my grandmother. She lives in {ciudad}. We talked about the family and our plans for the future.",
                "I have been studying English for {años} years. I think I am improving. I can now have basic conversations.",
                "My best friend is from Guatemala City. We met at university. We like to go to the movies together.",
                "I like to travel. Last year I visited {ciudad}. It was a beautiful place. I want to go again."
            ],
            'B1': [
                "I have worked in the {industria} industry for {años} years. My role is {profesion}. I enjoy my work because I like helping people.",
                "One of the most important experiences in my life was when I traveled to {ciudad}. I learned a lot about the culture and met wonderful people.",
                "I believe that education is the key to a better future. That's why I am constantly learning new things and improving my skills.",
                "In my free time, I enjoy reading, hiking, and spending time with my family. I think it's important to have a balance between work and personal life.",
                "My goal for this year is to improve my English to a B2 level. I am taking classes and practicing every day."
            ],
            'B2': [
                "The education system in Guatemala has many challenges, but there are also opportunities for those who are committed to learning. I believe that we need to invest more in education to ensure a better future for our children.",
                "Technology has transformed the way we live and work. While there are many benefits, we also need to consider the ethical implications of new technologies.",
                "In my opinion, sustainable development is crucial for the future of our planet. We need to find ways to grow economically while protecting the environment.",
                "I have been working as a {profesion} for over {años} years. Throughout my career, I have learned the importance of adaptability and continuous learning.",
                "One of the most challenging situations I have faced was when I had to work with an international team. It required me to improve my English significantly."
            ],
            'C1': [
                "The relationship between economic development and environmental sustainability presents one of the most significant challenges of our time. Policymakers must find innovative solutions that balance competing interests and ensure long-term prosperity.",
                "Contemporary society faces numerous challenges that require collaborative solutions. From climate change to social inequality, the issues we confront demand a coordinated approach from governments, businesses, and civil society.",
                "The evolution of digital technologies has fundamentally reshaped the landscape of modern work. Organizations must adapt their strategies to remain competitive while ensuring that their employees have the necessary skills.",
                "Cultural understanding is essential in our increasingly globalized world. By embracing diversity and fostering intercultural dialogue, we can create more inclusive and innovative societies.",
                "My professional experience as a {profesion} has taught me that effective communication is the key to success in any field. I continue to work on improving my skills and knowledge."
            ],
            'C2': [
                "The dialectical interplay between technological innovation and social transformation warrants careful examination, as it reveals profound implications for the trajectory of human development and the sustainability of our collective institutions.",
                "Contemporary discourse on global governance must reconcile the tension between national sovereignty and the imperative for transnational cooperation on issues that transcend traditional boundaries.",
                "The epistemological foundations of our knowledge systems are being challenged by new paradigms that emerge from diverse cultural and disciplinary perspectives, necessitating a more inclusive approach to scholarship.",
                "The ethical dimensions of artificial intelligence and its applications in society demand rigorous examination, as they raise fundamental questions about agency, responsibility, and the nature of human experience.",
                "The complex challenges of the 21st century require interdisciplinary approaches that integrate insights from multiple fields and foster innovative solutions to persistent problems."
            ]
        }
        
        # Ciudades de Guatemala
        self.ciudades = [
            "Guatemala City", "Antigua", "Quetzaltenango", "Escuintla", "Zacapa",
            "Huehuetenango", "Cobán", "Chiquimula", "Jalapa", "Retalhuleu",
            "Jutiapa", "Santa Rosa", "Suchitepéquez", "San Marcos", "Petén"
        ]
        
        # Profesiones
        self.profesiones = [
            "teacher", "engineer", "accountant", "architect", "designer", 
            "doctor", "nurse", "lawyer", "consultant", "manager",
            "programmer", "writer", "analyst", "director", "coordinator"
        ]
        
        # Industrias
        self.industrias = [
            "education", "technology", "finance", "healthcare", "construction",
            "marketing", "consulting", "manufacturing", "retail", "tourism"
        ]

    def generate_user_profiles(self, num_users=20):
        """Genera perfiles de usuario para validación."""
        print(f"Generando {num_users} perfiles de usuario...")
        
        users = []
        used_emails = set()
        
        for i in range(num_users):
            nombre = random.choice(self.nombres)
            apellido = random.choice(self.apellidos)
            
            # Evitar duplicados de nombres completos
            while True:
                first_name = random.choice(self.nombres)
                last_name = random.choice(self.apellidos)
                full_name = f"{first_name} {last_name}"
                if full_name not in [u['nombre_completo'] for u in users]:
                    break
            
            # Generar email
            email = f"{first_name.lower()}.{last_name.lower()}@gmail.com"
            while email in used_emails:
                email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1,100)}@gmail.com"
            used_emails.add(email)
            
            # Nivel autopercibido
            nivel_auto = random.choices(['A1', 'A2', 'B1', 'B2', 'C1', 'C2'], 
                                        weights=[15, 20, 30, 20, 10, 5])[0]
            
            # Generar textos de práctica (para evaluación)
            texts = []
            for nivel, text_list in self.user_texts.items():
                if nivel == nivel_auto or random.random() < 0.3:  # Incluir algunos textos de otros niveles
                    text_template = random.choice(text_list)
                    text = text_template.format(
                        nombre=first_name,
                        ciudad=random.choice(self.ciudades),
                        profesion=random.choice(self.profesiones),
                        años=random.randint(2, 15),
                        industria=random.choice(self.industrias)
                    )
                    texts.append({
                        'texto': text,
                        'nivel': nivel,
                        'es_correcto': nivel == nivel_auto
                    })
            
            # Asegurar que tenemos al menos algunos textos correctos
            if not any(t['es_correcto'] for t in texts):
                text_template = random.choice(self.user_texts[nivel_auto])
                text = text_template.format(
                    nombre=first_name,
                    ciudad=random.choice(self.ciudades),
                    profesion=random.choice(self.profesiones),
                    años=random.randint(2, 15),
                    industria=random.choice(self.industrias)
                )
                texts.append({
                    'texto': text,
                    'nivel': nivel_auto,
                    'es_correcto': True
                })
            
            # Asegurar que tenemos al menos 5 textos
            while len(texts) < 5:
                nivel = random.choice(list(self.user_texts.keys()))
                text_template = random.choice(self.user_texts[nivel])
                text = text_template.format(
                    nombre=first_name,
                    ciudad=random.choice(self.ciudades),
                    profesion=random.choice(self.profesiones),
                    años=random.randint(2, 15),
                    industria=random.choice(self.industrias)
                )
                texts.append({
                    'texto': text,
                    'nivel': nivel,
                    'es_correcto': nivel == nivel_auto
                })
            
            users.append({
                'id': i + 1,
                'nombre': first_name,
                'apellido': last_name,
                'nombre_completo': full_name,
                'email': email,
                'password': 'password123',
                'nivel_autopercibido': nivel_auto,
                'textos': texts,
                'edad': random.randint(18, 60),
                'profesion': random.choice(self.profesiones),
                'ciudad': random.choice(self.ciudades),
                'estudios': random.choice(['Secundaria', 'Técnico', 'Universidad', 'Postgrado'])
            })
        
        # Guardar perfiles
        os.makedirs(self.data_path, exist_ok=True)
        users_file = os.path.join(self.data_path, 'usuarios_validacion.json')
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        print(f"Perfiles guardados en: {users_file}")
        return users

    def generate_preguntas(self, num_preguntas=30):
        """Genera preguntas para el banco de preguntas."""
        print(f"Generando {num_preguntas} preguntas...")
        
        preguntas = []
        niveles = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        categorias = ['Gramática', 'Vocabulario', 'Escritura', 'Lectura']
        
        # Preguntas por nivel
        preguntas_por_nivel = {
            'A1': [
                "Describe your family. Who are they and what do they like to do?",
                "What do you do in your free time? Write about your hobbies.",
                "Describe your house or apartment. Where is it and what does it have?",
                "Write about your daily routine. What do you do every day?",
                "Describe your favorite food. Why do you like it?",
                "Write about a friend. What are they like?"
            ],
            'A2': [
                "Write about a recent trip or vacation you took. Where did you go?",
                "Describe your job or studies. What do you do every day?",
                "What did you do last weekend? Write about it.",
                "Describe your hometown. What is it like?",
                "Write about your future plans. What are you going to do?",
                "What's your favorite movie? Write about it."
            ],
            'B1': [
                "Describe a memorable event or experience in your life.",
                "What are your career goals and how do you plan to achieve them?",
                "Write about a problem in your community and suggest a solution.",
                "Describe a person who has influenced you. What did they teach you?",
                "What are the advantages and disadvantages of social media?",
                "Write about your favorite place to relax and why."
            ],
            'B2': [
                "Discuss the impact of technology on modern society.",
                "What are the most important challenges facing your country?",
                "Write about the importance of education in today's world.",
                "Describe a controversial issue and present both sides.",
                "How has the workplace changed in recent years?",
                "Write about the role of culture in shaping our identity."
            ],
            'C1': [
                "Analyze the relationship between economic development and environmental sustainability.",
                "Discuss the future of work in an increasingly automated world.",
                "Write about the challenges and opportunities of globalization.",
                "Examine the role of media in shaping public opinion.",
                "Discuss the ethical implications of artificial intelligence.",
                "Write about the importance of intercultural understanding."
            ],
            'C2': [
                "Explore the complexities of achieving sustainable development in a globalized world.",
                "Analyze the tension between national sovereignty and international cooperation.",
                "Discuss the epistemological challenges in contemporary social sciences.",
                "Examine the philosophical implications of technological advancement.",
                "Write about the role of language in shaping thought and culture.",
                "Analyze the challenges of governing in an age of information overload."
            ]
        }
        
        for nivel in niveles:
            preguntas_nivel = preguntas_por_nivel.get(nivel, [])
            for i, texto in enumerate(preguntas_nivel):
                if i >= num_preguntas // 6:
                    break
                
                # Crear variaciones
                instrucciones = [
                    "Write a response of at least 50 words.",
                    "Write a detailed response with examples.",
                    "Write a well-structured response.",
                    "Write a response demonstrating your level of English.",
                    "Write a clear and organized response."
                ]
                
                preguntas.append({
                    'texto': texto,
                    'instrucciones': random.choice(instrucciones),
                    'nivel': nivel,
                    'categoria': random.choice(categorias),
                    'dificultad': random.randint(1, 5),
                    'activa': True
                })
        
        # Guardar preguntas
        preguntas_file = os.path.join(self.data_path, 'preguntas.json')
        with open(preguntas_file, 'w', encoding='utf-8') as f:
            json.dump(preguntas, f, ensure_ascii=False, indent=2)
        
        print(f"Preguntas guardadas en: {preguntas_file}")
        return preguntas

    def run(self):
        """Ejecuta la generación de datos de prueba."""
        print("="*50)
        print("GENERANDO DATOS DE PRUEBA")
        print("="*50)
        
        # Generar perfiles de usuarios
        users = self.generate_user_profiles(20)
        
        # Generar preguntas
        preguntas = self.generate_preguntas(36)
        
        print("\n" + "="*50)
        print(f"DATOS GENERADOS:")
        print(f"  - {len(users)} usuarios")
        print(f"  - {len(preguntas)} preguntas")
        print("="*50)
        
        return users, preguntas

if __name__ == "__main__":
    generator = TestDataGenerator()
    generator.run()