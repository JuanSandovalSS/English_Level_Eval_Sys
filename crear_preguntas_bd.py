# crear_preguntas_bd.py
from app import app, db, Pregunta, NivelMCER, Categoria
from datetime import datetime

def crear_preguntas():
    with app.app_context():
        # Obtener niveles y categorías
        niveles = {n.codigo: n.id for n in NivelMCER.query.all()}
        categorias = {c.nombre: c.id for c in Categoria.query.all()}
        
        # Verificar que existan
        if not niveles or not categorias:
            print("❌ Primero ejecuta 'python app.py' para crear niveles y categorías")
            return
        
        # ============================================
        # PREGUNTAS POR NIVEL
        # ============================================
        
        preguntas_por_nivel = {
            'A1': [
                {
                    'texto': "What is your name? How old are you? Where are you from?",
                    'instrucciones': "Write 3-5 sentences about yourself.",
                    'palabras_min': 15,
                    'palabras_max': 40
                },
                {
                    'texto': "Describe your family. Who are they and what do they do?",
                    'instrucciones': "Write about your family members.",
                    'palabras_min': 20,
                    'palabras_max': 50
                },
                {
                    'texto': "What do you do every day? Describe your daily routine.",
                    'instrucciones': "Write about your daily activities.",
                    'palabras_min': 20,
                    'palabras_max': 50
                },
                {
                    'texto': "Describe your house or apartment. What rooms does it have?",
                    'instrucciones': "Write about where you live.",
                    'palabras_min': 20,
                    'palabras_max': 50
                },
                {
                    'texto': "What is your favorite food? Why do you like it?",
                    'instrucciones': "Write about your favorite food.",
                    'palabras_min': 15,
                    'palabras_max': 40
                },
                {
                    'texto': "Describe a friend. What are they like? What do you do together?",
                    'instrucciones': "Write about a friend.",
                    'palabras_min': 20,
                    'palabras_max': 50
                },
                {
                    'texto': "What do you like to do in your free time?",
                    'instrucciones': "Write about your hobbies.",
                    'palabras_min': 15,
                    'palabras_max': 40
                },
                {
                    'texto': "Describe the weather in your city. What is it like?",
                    'instrucciones': "Write about the weather.",
                    'palabras_min': 15,
                    'palabras_max': 40
                }
            ],
            'A2': [
                {
                    'texto': "Write about a recent trip or vacation you took. Where did you go? What did you do?",
                    'instrucciones': "Describe your trip in detail.",
                    'palabras_min': 30,
                    'palabras_max': 60
                },
                {
                    'texto': "Describe your job or studies. What do you do every day? What do you like about it?",
                    'instrucciones': "Write about your work or studies.",
                    'palabras_min': 30,
                    'palabras_max': 60
                },
                {
                    'texto': "What did you do last weekend? Write about your activities.",
                    'instrucciones': "Describe your weekend.",
                    'palabras_min': 25,
                    'palabras_max': 55
                },
                {
                    'texto': "Describe your hometown. What is it like? What are the people like?",
                    'instrucciones': "Write about your hometown.",
                    'palabras_min': 30,
                    'palabras_max': 60
                },
                {
                    'texto': "What are your plans for the future? What do you want to do?",
                    'instrucciones': "Write about your future plans.",
                    'palabras_min': 25,
                    'palabras_max': 55
                },
                {
                    'texto': "What is your favorite movie or book? Why do you like it?",
                    'instrucciones': "Write about a movie or book you like.",
                    'palabras_min': 25,
                    'palabras_max': 55
                },
                {
                    'texto': "Describe a special celebration in your country. What do people do?",
                    'instrucciones': "Write about a celebration.",
                    'palabras_min': 30,
                    'palabras_max': 60
                },
                {
                    'texto': "What kind of music do you like? Why do you like it?",
                    'instrucciones': "Write about your music preferences.",
                    'palabras_min': 20,
                    'palabras_max': 50
                }
            ],
            'B1': [
                {
                    'texto': "Describe a memorable event or experience in your life. What happened and why was it important?",
                    'instrucciones': "Write a personal story.",
                    'palabras_min': 50,
                    'palabras_max': 90
                },
                {
                    'texto': "What are your career goals? How do you plan to achieve them?",
                    'instrucciones': "Write about your professional aspirations.",
                    'palabras_min': 50,
                    'palabras_max': 90
                },
                {
                    'texto': "Write about a problem in your community. What is it and how could it be solved?",
                    'instrucciones': "Describe a local problem and propose solutions.",
                    'palabras_min': 55,
                    'palabras_max': 95
                },
                {
                    'texto': "Describe a person who has influenced you. What did they teach you?",
                    'instrucciones': "Write about an influential person.",
                    'palabras_min': 50,
                    'palabras_max': 90
                },
                {
                    'texto': "What are the advantages and disadvantages of social media?",
                    'instrucciones': "Write about the pros and cons of social media.",
                    'palabras_min': 55,
                    'palabras_max': 95
                },
                {
                    'texto': "Describe your favorite place to relax. Why do you like it?",
                    'instrucciones': "Write about your favorite place.",
                    'palabras_min': 45,
                    'palabras_max': 85
                },
                {
                    'texto': "What is the most important thing you have learned in life? Why?",
                    'instrucciones': "Write about an important life lesson.",
                    'palabras_min': 50,
                    'palabras_max': 90
                },
                {
                    'texto': "How has technology changed the way people communicate?",
                    'instrucciones': "Write about technology and communication.",
                    'palabras_min': 55,
                    'palabras_max': 95
                }
            ],
            'B2': [
                {
                    'texto': "Discuss the impact of technology on modern society. What are the benefits and risks?",
                    'instrucciones': "Write a balanced discussion.",
                    'palabras_min': 80,
                    'palabras_max': 130
                },
                {
                    'texto': "What are the most important challenges facing your country today?",
                    'instrucciones': "Write about national challenges.",
                    'palabras_min': 80,
                    'palabras_max': 130
                },
                {
                    'texto': "Write about the importance of education in today's world.",
                    'instrucciones': "Write about the value of education.",
                    'palabras_min': 75,
                    'palabras_max': 125
                },
                {
                    'texto': "Describe a controversial issue and present both sides of the argument.",
                    'instrucciones': "Write about a controversial topic.",
                    'palabras_min': 85,
                    'palabras_max': 135
                },
                {
                    'texto': "How has the workplace changed in recent years? What about the future?",
                    'instrucciones': "Write about changes in the workplace.",
                    'palabras_min': 80,
                    'palabras_max': 130
                },
                {
                    'texto': "Write about the role of culture in shaping our identity.",
                    'instrucciones': "Write about culture and identity.",
                    'palabras_min': 75,
                    'palabras_max': 125
                },
                {
                    'texto': "What are the main causes of environmental problems? What can be done?",
                    'instrucciones': "Write about environmental issues.",
                    'palabras_min': 80,
                    'palabras_max': 130
                },
                {
                    'texto': "Discuss the advantages and disadvantages of globalization.",
                    'instrucciones': "Write about globalization.",
                    'palabras_min': 80,
                    'palabras_max': 130
                }
            ],
            'C1': [
                {
                    'texto': "Analyze the relationship between economic development and environmental sustainability. Is it possible to have both?",
                    'instrucciones': "Write a critical analysis.",
                    'palabras_min': 120,
                    'palabras_max': 180
                },
                {
                    'texto': "Discuss the future of work in an increasingly automated world. What jobs will survive?",
                    'instrucciones': "Write about the future of employment.",
                    'palabras_min': 120,
                    'palabras_max': 180
                },
                {
                    'texto': "Write about the challenges and opportunities of globalization for developing countries.",
                    'instrucciones': "Write about globalization's impact.",
                    'palabras_min': 120,
                    'palabras_max': 180
                },
                {
                    'texto': "Examine the role of media in shaping public opinion. Is it positive or negative?",
                    'instrucciones': "Write about media influence.",
                    'palabras_min': 120,
                    'palabras_max': 180
                },
                {
                    'texto': "Discuss the ethical implications of artificial intelligence. What are the main concerns?",
                    'instrucciones': "Write about AI ethics.",
                    'palabras_min': 120,
                    'palabras_max': 180
                },
                {
                    'texto': "Write about the importance of intercultural understanding in a globalized world.",
                    'instrucciones': "Write about cultural understanding.",
                    'palabras_min': 115,
                    'palabras_max': 175
                },
                {
                    'texto': "What are the main challenges of urban planning in the 21st century?",
                    'instrucciones': "Write about urban planning.",
                    'palabras_min': 120,
                    'palabras_max': 180
                },
                {
                    'texto': "Discuss the relationship between language and thought. Does language shape our thinking?",
                    'instrucciones': "Write about language and cognition.",
                    'palabras_min': 120,
                    'palabras_max': 180
                }
            ],
            'C2': [
                {
                    'texto': "Explore the complexities of achieving sustainable development in a globalized world. What are the main tensions?",
                    'instrucciones': "Write a comprehensive analysis.",
                    'palabras_min': 180,
                    'palabras_max': 250
                },
                {
                    'texto': "Analyze the tension between national sovereignty and international cooperation. How can these be balanced?",
                    'instrucciones': "Write about sovereignty and cooperation.",
                    'palabras_min': 180,
                    'palabras_max': 250
                },
                {
                    'texto': "Discuss the epistemological challenges in contemporary social sciences. What are the main debates?",
                    'instrucciones': "Write about epistemology.",
                    'palabras_min': 180,
                    'palabras_max': 250
                },
                {
                    'texto': "Examine the philosophical implications of technological advancement. What are the key questions?",
                    'instrucciones': "Write about philosophy and technology.",
                    'palabras_min': 180,
                    'palabras_max': 250
                },
                {
                    'texto': "Write about the role of language in shaping thought and culture. How do they interact?",
                    'instrucciones': "Write about language and culture.",
                    'palabras_min': 175,
                    'palabras_max': 245
                },
                {
                    'texto': "Analyze the challenges of governing in an age of information overload. What are the main issues?",
                    'instrucciones': "Write about governance and information.",
                    'palabras_min': 180,
                    'palabras_max': 250
                },
                {
                    'texto': "Discuss the relationship between individual rights and collective responsibility. How can they be balanced?",
                    'instrucciones': "Write about rights and responsibility.",
                    'palabras_min': 180,
                    'palabras_max': 250
                },
                {
                    'texto': "What are the main challenges of the 21st century? How can they be addressed?",
                    'instrucciones': "Write about global challenges.",
                    'palabras_min': 180,
                    'palabras_max': 250
                }
            ]
        }
        
        # Insertar preguntas
        contador = 0
        for nivel_codigo, preguntas in preguntas_por_nivel.items():
            nivel_id = niveles.get(nivel_codigo)
            if not nivel_id:
                print(f"⚠️ Nivel {nivel_codigo} no encontrado")
                continue
            
            categoria_id = categorias.get('Escritura')
            
            for p in preguntas:
                if not Pregunta.query.filter_by(texto=p['texto']).first():
                    pregunta = Pregunta(
                        texto=p['texto'],
                        instrucciones=p['instrucciones'],
                        nivel_id=nivel_id,
                        categoria_id=categoria_id,
                        dificultad=3,
                        activa=True
                    )
                    db.session.add(pregunta)
                    contador += 1
        
        db.session.commit()
        print(f"✅ {contador} preguntas creadas exitosamente")
        
        # Mostrar resumen
        print("\n📊 Resumen por nivel:")
        for nivel_codigo in niveles:
            count = Pregunta.query.join(NivelMCER).filter(NivelMCER.codigo == nivel_codigo).count()
            print(f"  {nivel_codigo}: {count} preguntas")

if __name__ == "__main__":
    crear_preguntas()