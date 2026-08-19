# evaluacion_service.py - Servicio de evaluación y generación de diplomas
import json
import random
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import os

class EvaluacionService:
    def __init__(self):
        self.preguntas_por_nivel = {
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
        
        self.descripciones_nivel = {
            'A1': {
                'nombre': 'Principiante (Beginner)',
                'descripcion': 'Puede comprender y utilizar expresiones cotidianas de uso muy frecuente. Puede presentarse a sí mismo y a otros, y puede hacer preguntas básicas sobre información personal.',
                'color': '#6c757d'
            },
            'A2': {
                'nombre': 'Elemental (Elementary)',
                'descripcion': 'Puede comprender frases y expresiones de uso frecuente relacionadas con áreas de experiencia que le son especialmente relevantes. Puede comunicarse en tareas simples y rutinarias.',
                'color': '#5b8c5a'
            },
            'B1': {
                'nombre': 'Intermedio (Intermediate)',
                'descripcion': 'Puede comprender los puntos principales de textos claros y en lengua estándar. Puede producir textos sencillos y coherentes sobre temas que le son familiares.',
                'color': '#4a9fb5'
            },
            'B2': {
                'nombre': 'Intermedio Alto (Upper Intermediate)',
                'descripcion': 'Puede comprender las ideas principales de textos complejos que tratan de temas tanto concretos como abstractos. Puede interactuar con hablantes nativos con un grado suficiente de fluidez.',
                'color': '#3a8fd4'
            },
            'C1': {
                'nombre': 'Avanzado (Advanced)',
                'descripcion': 'Puede comprender una amplia variedad de textos extensos y con cierto nivel de exigencia. Puede expresarse de forma fluida y espontánea sin esfuerzo aparente.',
                'color': '#6b5b8a'
            },
            'C2': {
                'nombre': 'Competente (Proficient)',
                'descripcion': 'Puede comprender con facilidad prácticamente todo lo que oye o lee. Puede expresarse espontáneamente, con gran fluidez y precisión.',
                'color': '#8b4b6a'
            }
        }
    
    def obtener_preguntas(self, nivel=None, cantidad=5):
        """Obtiene preguntas para la evaluación"""
        if nivel and nivel in self.preguntas_por_nivel:
            preguntas_disponibles = self.preguntas_por_nivel[nivel]
        else:
            # Si no se especifica nivel, tomar de todos los niveles
            todas = []
            for preg in self.preguntas_por_nivel.values():
                todas.extend(preg)
            preguntas_disponibles = todas
        
        # Seleccionar aleatoriamente
        if len(preguntas_disponibles) < cantidad:
            cantidad = len(preguntas_disponibles)
        
        return random.sample(preguntas_disponibles, cantidad)
    
    def obtener_descripcion_nivel(self, nivel):
        """Obtiene la descripción completa de un nivel"""
        return self.descripciones_nivel.get(nivel, {
            'nombre': 'No determinado',
            'descripcion': 'Nivel no especificado',
            'color': '#999999'
        })
    
    def generar_diploma(self, usuario, nivel, respuestas=None, fecha=None):
        """Genera un diploma PDF para el usuario"""
        if fecha is None:
            fecha = datetime.now()
        
        # Crear directorio si no existe
        os.makedirs('./diplomas', exist_ok=True)
        
        # Nombre del archivo
        nombre_archivo = f"diploma_{usuario.nombre}_{usuario.apellido}_{fecha.strftime('%Y%m%d')}.pdf"
        ruta_pdf = os.path.join('./diplomas', nombre_archivo)
        
        # Obtener descripción del nivel
        info_nivel = self.obtener_descripcion_nivel(nivel)
        
        # Crear el PDF
        doc = SimpleDocTemplate(
            ruta_pdf,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo para título principal
        titulo_style = ParagraphStyle(
            'TituloStyle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para subtítulo
        subtitulo_style = ParagraphStyle(
            'SubtituloStyle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#34495e'),
            alignment=TA_CENTER,
            spaceAfter=15
        )
        
        # Estilo para el nivel (grande)
        nivel_style = ParagraphStyle(
            'NivelStyle',
            parent=styles['Heading1'],
            fontSize=72,
            textColor=colors.HexColor(info_nivel['color'].lstrip('#')),
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para nombre del usuario
        nombre_style = ParagraphStyle(
            'NombreStyle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para texto normal centrado
        centro_style = ParagraphStyle(
            'CentroStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        # Estilo para descripción
        descripcion_style = ParagraphStyle(
            'DescripcionStyle',
            parent=styles['Normal'],
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=15,
            leftIndent=20,
            rightIndent=20
        )
        
        # Construir contenido
        elementos = []
        
        # Título
        elementos.append(Paragraph("CERTIFICADO DE NIVEL DE INGLÉS", titulo_style))
        elementos.append(Spacer(1, 10))
        
        # Subtítulo
        elementos.append(Paragraph("Sistema de Evaluación Automática con NLP", subtitulo_style))
        elementos.append(Spacer(1, 20))
        
        # Nombre del usuario
        elementos.append(Paragraph(f"Otorgado a:", centro_style))
        elementos.append(Paragraph(f"{usuario.nombre} {usuario.apellido}", nombre_style))
        elementos.append(Spacer(1, 20))
        
        # Nivel
        elementos.append(Paragraph(f"Nivel {nivel}", nivel_style))
        elementos.append(Paragraph(f"{info_nivel['nombre']}", subtitulo_style))
        elementos.append(Spacer(1, 20))
        
        # Descripción del nivel
        elementos.append(Paragraph(f"<b>Descripción:</b>", centro_style))
        elementos.append(Paragraph(info_nivel['descripcion'], descripcion_style))
        elementos.append(Spacer(1, 20))
        
        # Fecha
        fecha_str = fecha.strftime("%d de %B de %Y")
        elementos.append(Paragraph(f"Fecha de evaluación: {fecha_str}", centro_style))
        elementos.append(Spacer(1, 10))
        
        # Pie de página
        elementos.append(Spacer(1, 30))
        elementos.append(Paragraph("---", centro_style))
        elementos.append(Paragraph(
            "Este certificado ha sido generado automáticamente por el Sistema de Evaluación de Inglés",
            centro_style
        ))
        elementos.append(Paragraph(
            "Basado en el Marco Común Europeo de Referencia para las Lenguas (MCER)",
            centro_style
        ))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph(
            f"ID de evaluación: {datetime.now().strftime('%Y%m%d%H%M%S')}",
            centro_style
        ))
        
        # Generar PDF
        doc.build(elementos)
        
        return ruta_pdf
    
    def generar_diploma_mejorado(self, usuario, nivel, respuestas=None, fecha=None):
        """Genera un diploma más elaborado con marco y diseño mejorado"""
        if fecha is None:
            fecha = datetime.now()
        
        os.makedirs('./diplomas', exist_ok=True)
        
        nombre_archivo = f"diploma_{usuario.nombre}_{usuario.apellido}_{fecha.strftime('%Y%m%d')}.pdf"
        ruta_pdf = os.path.join('./diplomas', nombre_archivo)
        
        info_nivel = self.obtener_descripcion_nivel(nivel)
        
        # Usar canvas para diseño más personalizado
        c = canvas.Canvas(ruta_pdf, pagesize=A4)
        width, height = A4
        
        # Marco decorativo
        c.setStrokeColor(colors.HexColor('#2c3e50'))
        c.setLineWidth(3)
        c.rect(40, 40, width-80, height-80)
        
        # Marco interior
        c.setStrokeColor(colors.HexColor('#3498db'))
        c.setLineWidth(1)
        c.rect(50, 50, width-100, height-100)
        
        # Título
        c.setFont('Helvetica-Bold', 28)
        c.setFillColor(colors.HexColor('#2c3e50'))
        c.drawCentredString(width/2, height-100, "CERTIFICADO DE NIVEL DE INGLÉS")
        
        # Subtítulo
        c.setFont('Helvetica', 14)
        c.setFillColor(colors.HexColor('#7f8c8d'))
        c.drawCentredString(width/2, height-130, "Sistema de Evaluación Automática con NLP")
        
        # Línea decorativa
        c.setStrokeColor(colors.HexColor('#3498db'))
        c.setLineWidth(2)
        c.line(width/2-150, height-145, width/2+150, height-145)
        
        # Texto "Otorgado a"
        c.setFont('Helvetica', 14)
        c.setFillColor(colors.HexColor('#7f8c8d'))
        c.drawCentredString(width/2, height-190, "Otorgado a:")
        
        # Nombre del usuario
        c.setFont('Helvetica-Bold', 26)
        c.setFillColor(colors.HexColor('#2c3e50'))
        c.drawCentredString(width/2, height-230, f"{usuario.nombre} {usuario.apellido}")
        
        # Nivel (GRANDE)
        c.setFont('Helvetica-Bold', 80)
        c.setFillColor(colors.HexColor(info_nivel['color'].lstrip('#')))
        c.drawCentredString(width/2, height-340, f"{nivel}")
        
        # Nombre del nivel
        c.setFont('Helvetica-Bold', 18)
        c.setFillColor(colors.HexColor('#34495e'))
        c.drawCentredString(width/2, height-375, f"{info_nivel['nombre']}")
        
        # Línea decorativa inferior
        c.setStrokeColor(colors.HexColor('#3498db'))
        c.setLineWidth(1)
        c.line(width/2-200, height-395, width/2+200, height-395)
        
        # Descripción
        c.setFont('Helvetica', 11)
        c.setFillColor(colors.HexColor('#555555'))
        descripcion = info_nivel['descripcion']
        # Dividir descripción en líneas
        palabras = descripcion.split()
        lineas = []
        linea_actual = ""
        for palabra in palabras:
            if len(linea_actual + " " + palabra) < 70:
                linea_actual += " " + palabra if linea_actual else palabra
            else:
                lineas.append(linea_actual)
                linea_actual = palabra
        if linea_actual:
            lineas.append(linea_actual)
        
        y_pos = height-420
        for linea in lineas:
            c.drawCentredString(width/2, y_pos, linea)
            y_pos -= 20
        
        # Fecha
        c.setFont('Helvetica', 12)
        c.setFillColor(colors.HexColor('#7f8c8d'))
        fecha_str = fecha.strftime("%d de %B de %Y")
        c.drawCentredString(width/2, height-520, f"Fecha de evaluación: {fecha_str}")
        
        # Pie de página
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.HexColor('#bdc3c7'))
        c.drawCentredString(width/2, 100, "Este certificado ha sido generado automáticamente por el Sistema de Evaluación de Inglés")
        c.drawCentredString(width/2, 80, "Basado en el Marco Común Europeo de Referencia para las Lenguas (MCER)")
        c.drawCentredString(width/2, 60, f"ID: {datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Sello decorativo
        c.setFillColor(colors.HexColor('#e74c3c'))
        c.setStrokeColor(colors.HexColor('#c0392b'))
        c.setLineWidth(2)
        c.circle(width-100, 150, 40)
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(colors.HexColor('#c0392b'))
        c.drawCentredString(width-100, 155, "VALIDADO")
        c.drawCentredString(width-100, 140, "POR IA")
        
        c.save()
        
        return ruta_pdf