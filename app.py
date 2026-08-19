# app.py - VERSIÓN FINAL CORREGIDA (CON TODOS LOS ARREGLOS)
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os
import random
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter

# ============================================
# CONFIGURACIÓN
# ============================================

class Config:
    SECRET_KEY = 'dev-secret-key-12345'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///evaluacion_ingles.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# ============================================
# INICIALIZAR APLICACIÓN
# ============================================

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar base de datos
db = SQLAlchemy(app)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión.'

# Descargar recursos de NLTK (solo primera vez)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')

# ============================================
# MODELOS
# ============================================

class Usuario(db.Model):
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
    
    # Nivel autopercibido
    nivel_autopercibido_id = db.Column(db.Integer, db.ForeignKey('niveles_mcer.id'), nullable=True)
    nivel_autopercibido = db.relationship('NivelMCER', foreign_keys=[nivel_autopercibido_id])

    evaluaciones = db.relationship('Evaluacion', backref='usuario', lazy=True)
    
    def is_authenticated(self):
        return True
    def is_active(self):
        return self.estado
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.id)

class NivelMCER(db.Model):
    __tablename__ = 'niveles_mcer'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(2), unique=True, nullable=False)
    nombre = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    preguntas = db.relationship('Pregunta', backref='nivel', lazy=True)

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    preguntas = db.relationship('Pregunta', backref='categoria', lazy=True)

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

class Respuesta(db.Model):
    __tablename__ = 'respuestas'
    id = db.Column(db.Integer, primary_key=True)
    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluaciones.id'), nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas.id'), nullable=True)
    texto = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.Text)
    caracteristicas = db.Column(db.Text)
    nivel_predicho_id = db.Column(db.Integer, db.ForeignKey('niveles_mcer.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    nivel_predicho = db.relationship('NivelMCER', foreign_keys=[nivel_predicho_id])

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ============================================
# SERVICIO NLP
# ============================================

class NLPService:
    def process(self, text):
        palabras = text.split()
        return {
            'num_palabras': len(palabras),
            'num_oraciones': text.count('.') + text.count('!') + text.count('?'),
            'riqueza_lexica': len(set(palabras)) / len(palabras) if palabras else 0,
            'longitud_promedio': len(palabras) / (text.count('.') + 1) if text else 0,
            'texto_limpio': text,
            'embedding': [0.0] * 10
        }

nlp_service = NLPService()

# ============================================
# ANALIZADOR DE RESPUESTAS
# ============================================

class AnalizadorRespuestas:
    def __init__(self):
        self.stopwords = set(stopwords.words('english'))
        self.sinonimos = {
            'good': ['great', 'excellent', 'positive', 'beneficial'],
            'bad': ['poor', 'negative', 'harmful', 'detrimental'],
            'big': ['large', 'huge', 'massive', 'enormous'],
            'small': ['little', 'tiny', 'minor', 'compact'],
            'important': ['crucial', 'vital', 'significant', 'essential'],
            'think': ['believe', 'consider', 'reckon', 'suppose'],
            'like': ['enjoy', 'appreciate', 'admire', 'favor'],
            'help': ['assist', 'support', 'aid', 'facilitate'],
            'make': ['create', 'produce', 'generate', 'construct'],
            'get': ['obtain', 'acquire', 'secure', 'receive']
        }
    
    def analizar(self, texto, nivel_esperado):
        texto_limpio = self._limpiar_texto(texto)
        palabras = word_tokenize(texto_limpio)
        oraciones = sent_tokenize(texto_limpio)
        
        num_palabras = len(palabras)
        num_oraciones = len(oraciones)
        
        palabras_unicas = set([p.lower() for p in palabras if p.isalpha()])
        riqueza_lexica = len(palabras_unicas) / num_palabras if num_palabras > 0 else 0
        longitud_promedio = num_palabras / num_oraciones if num_oraciones > 0 else 0
        
        try:
            from nltk.tag import pos_tag
            tags = pos_tag(palabras)
            content_tags = ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS']
            palabras_contenido = [t for t, tag in tags if tag in content_tags]
            densidad_lexica = len(palabras_contenido) / num_palabras if num_palabras > 0 else 0
        except:
            densidad_lexica = 0.4
        
        nivel_estimado = self._estimar_nivel({
            'num_palabras': num_palabras,
            'riqueza_lexica': riqueza_lexica,
            'longitud_promedio': longitud_promedio,
            'densidad_lexica': densidad_lexica,
            'num_oraciones': num_oraciones
        })
        
        niveles = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        idx_esperado = niveles.index(nivel_esperado)
        idx_estimado = niveles.index(nivel_estimado)
        cumple = idx_estimado >= idx_esperado - 1
        
        # Detectar palabras repetidas
        contador_palabras = Counter([p.lower() for p in palabras if p.isalpha() and p.lower() not in self.stopwords])
        palabras_repetidas = [p for p, count in contador_palabras.items() if count > 2 and len(p) > 3]
        sugerencias = []
        for p in palabras_repetidas:
            if p in self.sinonimos:
                sugerencias.append(f"'{p}' → {', '.join(self.sinonimos[p][:2])}")
        
        feedback = self._generar_feedback({
            'num_palabras': num_palabras,
            'riqueza_lexica': riqueza_lexica,
            'longitud_promedio': longitud_promedio,
            'densidad_lexica': densidad_lexica,
            'num_oraciones': num_oraciones,
            'nivel_esperado': nivel_esperado,
            'nivel_estimado': nivel_estimado,
            'palabras_repetidas': palabras_repetidas,
            'sugerencias': sugerencias
        })
        
        return {
            'cumple': cumple,
            'nivel_estimado': nivel_estimado,
            'nivel_esperado': nivel_esperado,
            'metricas': {
                'num_palabras': num_palabras,
                'num_oraciones': num_oraciones,
                'riqueza_lexica': round(riqueza_lexica, 3),
                'longitud_promedio': round(longitud_promedio, 1),
                'densidad_lexica': round(densidad_lexica, 3)
            },
            'feedback': feedback,
            'texto_usuario': texto,
            'palabras_repetidas': palabras_repetidas,
            'sugerencias': sugerencias
        }
    
    def _limpiar_texto(self, texto):
        texto = texto.lower()
        texto = re.sub(r'[^a-zA-Z0-9\s.,!?\']', '', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto
    
    def _estimar_nivel(self, metricas):
        num_palabras = metricas['num_palabras']
        riqueza_lexica = metricas['riqueza_lexica']
        longitud_promedio = metricas['longitud_promedio']
        
        puntuacion = 0
        
        if num_palabras < 20:
            puntuacion += 0
        elif num_palabras < 40:
            puntuacion += 1
        elif num_palabras < 60:
            puntuacion += 2
        elif num_palabras < 80:
            puntuacion += 3
        elif num_palabras < 100:
            puntuacion += 4
        else:
            puntuacion += 5
        
        if riqueza_lexica < 0.4:
            pass
        elif riqueza_lexica < 0.6:
            puntuacion += 1
        elif riqueza_lexica < 0.7:
            puntuacion += 2
        else:
            puntuacion += 3
        
        if longitud_promedio < 8:
            pass
        elif longitud_promedio < 12:
            puntuacion += 1
        elif longitud_promedio < 16:
            puntuacion += 2
        else:
            puntuacion += 3
        
        niveles = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        if puntuacion <= 2:
            return 'A1'
        elif puntuacion <= 4:
            return 'A2'
        elif puntuacion <= 6:
            return 'B1'
        elif puntuacion <= 8:
            return 'B2'
        elif puntuacion <= 10:
            return 'C1'
        else:
            return 'C2'
    
    def _generar_feedback(self, data):
        feedback = []
        nivel_esperado = data['nivel_esperado']
        nivel_estimado = data['nivel_estimado']
        num_palabras = data['num_palabras']
        riqueza_lexica = data['riqueza_lexica']
        longitud_promedio = data['longitud_promedio']
        num_oraciones = data['num_oraciones']
        palabras_repetidas = data.get('palabras_repetidas', [])
        sugerencias = data.get('sugerencias', [])
        
        if nivel_estimado == nivel_esperado:
            feedback.append("✅ ¡Excelente! Tu respuesta corresponde al nivel esperado.")
        elif self._nivel_mayor(nivel_estimado, nivel_esperado):
            feedback.append(f"🌟 ¡Buen trabajo! Tu respuesta supera el nivel esperado ({nivel_estimado} > {nivel_esperado}). Sigue así.")
        else:
            feedback.append(f"📚 Tu respuesta está por debajo del nivel esperado ({nivel_estimado} < {nivel_esperado}). Practica más.")
        
        palabras_minimas = self._palabras_minimas(nivel_esperado)
        if num_palabras < palabras_minimas:
            feedback.append(f"💡 Extensión: Escribe al menos {palabras_minimas} palabras. Intenta desarrollar más tus ideas con ejemplos o explicaciones adicionales.")
        
        if riqueza_lexica < 0.4:
            feedback.append("📖 Vocabulario: Usa palabras más variadas. Evita repetir las mismas palabras. Busca sinónimos para expresar ideas similares.")
        elif riqueza_lexica < 0.6:
            feedback.append("📖 Vocabulario: Bueno, pero puedes mejorarlo incorporando términos más específicos y variados.")
        
        if longitud_promedio < 8:
            feedback.append("✍️ Estructura: Tus oraciones son cortas. Intenta combinarlas con conectores (and, but, because, although) para hacerlas más complejas.")
        elif longitud_promedio < 12:
            feedback.append("✍️ Estructura: Buen equilibrio de longitud de oraciones. Puedes añadir alguna oración más compleja para mejorar la fluidez.")
        
        if num_oraciones < 3:
            feedback.append("📝 Organización: Divide tu respuesta en al menos 3 oraciones (introducción, desarrollo, conclusión) para mejor estructura.")
        
        if sugerencias:
            feedback.append(f"🔁 Palabras repetidas: {', '.join(palabras_repetidas)}. Prueba con: {'; '.join(sugerencias)}.")
        
        if not feedback:
            feedback.append("🎯 ¡Excelente respuesta! Sigue practicando para mantener tu nivel.")
        
        return feedback
    
    def _nivel_mayor(self, nivel1, nivel2):
        niveles = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        return niveles.index(nivel1) > niveles.index(nivel2)
    
    def _palabras_minimas(self, nivel):
        minimos = {'A1': 15, 'A2': 25, 'B1': 45, 'B2': 75, 'C1': 120, 'C2': 175}
        return minimos.get(nivel, 30)

analizador = AnalizadorRespuestas()

# ============================================
# SERVICIO DE EVALUACIÓN Y DIPLOMA
# ============================================

class EvaluacionService:
    def __init__(self):
        self.descripciones_nivel = {
            'A1': {'nombre': 'Principiante (Beginner)', 'descripcion': 'Puede comprender y utilizar expresiones cotidianas de uso muy frecuente.', 'color': '#6c757d'},
            'A2': {'nombre': 'Elemental (Elementary)', 'descripcion': 'Puede comprender frases y expresiones de uso frecuente.', 'color': '#5b8c5a'},
            'B1': {'nombre': 'Intermedio (Intermediate)', 'descripcion': 'Puede comprender los puntos principales de textos claros.', 'color': '#4a9fb5'},
            'B2': {'nombre': 'Intermedio Alto (Upper Intermediate)', 'descripcion': 'Puede comprender las ideas principales de textos complejos.', 'color': '#3a8fd4'},
            'C1': {'nombre': 'Avanzado (Advanced)', 'descripcion': 'Puede comprender una amplia variedad de textos extensos.', 'color': '#6b5b8a'},
            'C2': {'nombre': 'Competente (Proficient)', 'descripcion': 'Puede comprender con facilidad prácticamente todo lo que oye o lee.', 'color': '#8b4b6a'}
        }
    
    def obtener_descripcion_nivel(self, nivel):
        return self.descripciones_nivel.get(nivel, {'nombre': 'No determinado', 'descripcion': 'Nivel no especificado', 'color': '#999999'})
    
    def generar_diploma(self, usuario, nivel, fecha=None):
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        import os
        from datetime import datetime

        if fecha is None:
            fecha = datetime.now()

        os.makedirs('./diplomas', exist_ok=True)
        nombre_archivo = f"diploma_{usuario.nombre}_{usuario.apellido}_{fecha.strftime('%Y%m%d')}.pdf"
        ruta_pdf = os.path.join('./diplomas', nombre_archivo)

        info_nivel = self.obtener_descripcion_nivel(nivel)
        width, height = A4

        c = canvas.Canvas(ruta_pdf, pagesize=A4)

        c.setStrokeColor(colors.HexColor('#2c3e50'))
        c.setLineWidth(3)
        c.rect(40, 40, width-80, height-80)

        c.setStrokeColor(colors.HexColor('#3498db'))
        c.setLineWidth(1)
        c.rect(50, 50, width-100, height-100)

        c.setFont('Helvetica-Bold', 28)
        c.setFillColor(colors.HexColor('#2c3e50'))
        c.drawCentredString(width/2, height-100, "CERTIFICADO DE NIVEL DE INGLÉS")

        c.setFont('Helvetica', 14)
        c.setFillColor(colors.HexColor('#7f8c8d'))
        c.drawCentredString(width/2, height-130, "Sistema de Evaluación Automática con NLP")

        c.setStrokeColor(colors.HexColor('#3498db'))
        c.setLineWidth(2)
        c.line(width/2-150, height-145, width/2+150, height-145)

        c.setFont('Helvetica', 14)
        c.setFillColor(colors.HexColor('#7f8c8d'))
        c.drawCentredString(width/2, height-190, "Otorgado a:")

        c.setFont('Helvetica-Bold', 26)
        c.setFillColor(colors.HexColor('#2c3e50'))
        c.drawCentredString(width/2, height-230, f"{usuario.nombre} {usuario.apellido}")

        color_original = info_nivel['color']
        if not color_original.startswith('#'):
            color_original = '#' + color_original
        try:
            color_nivel = colors.HexColor(color_original)
        except:
            color_nivel = colors.HexColor('#3498db')

        c.setFont('Helvetica-Bold', 80)
        c.setFillColor(color_nivel)
        c.drawCentredString(width/2, height-340, f"{nivel}")

        c.setFont('Helvetica-Bold', 18)
        c.setFillColor(colors.HexColor('#34495e'))
        c.drawCentredString(width/2, height-375, f"{info_nivel['nombre']}")

        c.setStrokeColor(colors.HexColor('#3498db'))
        c.setLineWidth(1)
        c.line(width/2-200, height-395, width/2+200, height-395)

        c.setFont('Helvetica', 11)
        c.setFillColor(colors.HexColor('#555555'))
        desc = info_nivel['descripcion']
        words = desc.split()
        lines = []
        current = ""
        for word in words:
            if len(current + " " + word) < 70:
                current += " " + word if current else word
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)

        y_pos = height-420
        for line in lines:
            c.drawCentredString(width/2, y_pos, line)
            y_pos -= 20

        c.setFont('Helvetica', 12)
        c.setFillColor(colors.HexColor('#7f8c8d'))
        c.drawCentredString(width/2, height-520, f"Fecha: {fecha.strftime('%d de %B de %Y')}")

        c.setFont('Helvetica', 9)
        c.setFillColor(colors.HexColor('#bdc3c7'))
        c.drawCentredString(width/2, 100, "Este certificado ha sido generado automáticamente por el Sistema de Evaluación de Inglés")
        c.drawCentredString(width/2, 80, "Basado en el Marco Común Europeo de Referencia para las Lenguas (MCER)")
        c.drawCentredString(width/2, 60, f"ID: {datetime.now().strftime('%Y%m%d%H%M%S')}")

        c.save()
        return ruta_pdf

# ============================================
# INSTANCIAR SERVICIOS
# ============================================

eval_service = EvaluacionService()

# ============================================
# RUTAS PRINCIPALES
# ============================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Usuario.query.filter_by(correo=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            user.ultimo_login = datetime.utcnow()
            db.session.commit()
            
            # Redirigir según rol
            if user.rol == 'ADMINISTRADOR':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        
        flash('Correo o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        nivel_autopercibido = request.form.get('nivel_autopercibido')

        if password != confirm:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('register.html', niveles=NivelMCER.query.all())

        if Usuario.query.filter_by(correo=email).first():
            flash('El correo ya está registrado.', 'danger')
            return render_template('register.html', niveles=NivelMCER.query.all())

        nivel_obj = None
        if nivel_autopercibido:
            nivel_obj = NivelMCER.query.filter_by(codigo=nivel_autopercibido).first()

        user = Usuario(
            nombre=nombre,
            apellido=apellido,
            correo=email,
            password=generate_password_hash(password),
            rol='ESTUDIANTE',
            nivel_autopercibido_id=nivel_obj.id if nivel_obj else None
        )

        db.session.add(user)
        db.session.commit()

        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    niveles = NivelMCER.query.all()
    return render_template('register.html', niveles=niveles)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/historial')
@login_required
def historial():
    evaluaciones = Evaluacion.query.filter_by(usuario_id=current_user.id).order_by(Evaluacion.fecha_inicio.desc()).all()
    return render_template('historial.html', evaluaciones=evaluaciones)

# ============================================
# RUTAS DE EVALUACIÓN (CORREGIDAS)
# ============================================

@app.route('/evaluacion/iniciar')
@login_required
def iniciar_evaluacion():
    nivel_auto = current_user.nivel_autopercibido
    nivel_codigo = nivel_auto.codigo if nivel_auto else None
    
    preguntas_seleccionadas = []
    niveles_cercanos = []  # 🔥 Inicializado aquí
    
    if nivel_codigo:
        niveles = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        idx = niveles.index(nivel_codigo)
        niveles_cercanos = []
        if idx > 0:
            niveles_cercanos.append(niveles[idx-1])
        niveles_cercanos.append(niveles[idx])
        if idx < len(niveles)-1:
            niveles_cercanos.append(niveles[idx+1])
        
        for nivel in niveles_cercanos:
            preguntas_nivel = Pregunta.query.filter_by(activa=True)\
                .join(NivelMCER).filter(NivelMCER.codigo == nivel).all()
            if preguntas_nivel:
                cantidad = 2 if nivel == nivel_codigo else 1
                seleccion = random.sample(preguntas_nivel, min(cantidad, len(preguntas_nivel)))
                preguntas_seleccionadas.extend(seleccion)
        
        if len(preguntas_seleccionadas) < 5:
            preguntas_nivel = Pregunta.query.filter_by(activa=True)\
                .join(NivelMCER).filter(NivelMCER.codigo == nivel_codigo).all()
            restantes = random.sample(preguntas_nivel, min(5 - len(preguntas_seleccionadas), len(preguntas_nivel)))
            preguntas_seleccionadas.extend(restantes)
    
    if len(preguntas_seleccionadas) < 5:
        preguntas = Pregunta.query.filter_by(activa=True).all()
        if len(preguntas) >= 5:
            preguntas_seleccionadas = random.sample(preguntas, 5)
        else:
            flash('No hay suficientes preguntas disponibles.', 'warning')
            return redirect(url_for('dashboard'))
    
    random.shuffle(preguntas_seleccionadas)
    
    evaluacion = Evaluacion(
        usuario_id=current_user.id,
        estado='EN_PROCESO'
    )
    db.session.add(evaluacion)
    db.session.commit()
    
    session['evaluacion_id'] = evaluacion.id
    session['pregunta_actual'] = 0
    session['preguntas'] = [p.id for p in preguntas_seleccionadas]
    session['respuestas'] = []
    
    # 🔥 Mensaje condicional
    if niveles_cercanos:
        flash(f'¡Evaluación iniciada! Las preguntas son de niveles {", ".join(niveles_cercanos)}.', 'success')
    else:
        flash('¡Evaluación iniciada! Responde las siguientes preguntas.', 'success')
    
    return redirect(url_for('evaluar_pregunta'))

@app.route('/evaluacion/pregunta')
@login_required
def evaluar_pregunta():
    pregunta_idx = session.get('pregunta_actual', 0)
    preguntas_ids = session.get('preguntas', [])
    
    if pregunta_idx >= len(preguntas_ids):
        return redirect(url_for('finalizar_evaluacion'))
    
    pregunta = Pregunta.query.get(preguntas_ids[pregunta_idx])
    if not pregunta:
        flash('Pregunta no encontrada.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('evaluacion.html',
                         pregunta=pregunta,
                         pregunta_numero=pregunta_idx + 1,
                         total_preguntas=len(preguntas_ids))

@app.route('/evaluacion/responder', methods=['POST'])
@login_required
def responder_pregunta():
    texto = request.form.get('respuesta', '').strip()
    
    if len(texto) < 20:
        flash('La respuesta debe tener al menos 20 caracteres.', 'warning')
        return redirect(url_for('evaluar_pregunta'))
    
    evaluacion_id = session.get('evaluacion_id')
    pregunta_idx = session.get('pregunta_actual', 0)
    preguntas_ids = session.get('preguntas', [])
    
    if pregunta_idx >= len(preguntas_ids):
        return redirect(url_for('finalizar_evaluacion'))
    
    pregunta = Pregunta.query.get(preguntas_ids[pregunta_idx])
    features = nlp_service.process(texto)
    
    respuesta = Respuesta(
        evaluacion_id=evaluacion_id,
        pregunta_id=pregunta.id,
        texto=texto,
        embedding=json.dumps(features.get('embedding', [])),
        caracteristicas=json.dumps(features)
    )
    db.session.add(respuesta)
    db.session.commit()
    
    respuestas = session.get('respuestas', [])
    respuestas.append({
        'pregunta_id': pregunta.id,
        'respuesta_id': respuesta.id,
        'nivel_pregunta': pregunta.nivel.codigo
    })
    session['respuestas'] = respuestas
    session['pregunta_actual'] = pregunta_idx + 1
    
    if session['pregunta_actual'] >= len(preguntas_ids):
        return redirect(url_for('finalizar_evaluacion'))
    
    return redirect(url_for('evaluar_pregunta'))

@app.route('/evaluacion/finalizar')
@login_required
def finalizar_evaluacion():
    evaluacion_id = session.get('evaluacion_id')
    respuestas_data = session.get('respuestas', [])
    
    if not evaluacion_id or not respuestas_data:
        flash('No hay evaluación en progreso.', 'warning')
        return redirect(url_for('dashboard'))
    
    evaluacion = Evaluacion.query.get(evaluacion_id)
    if not evaluacion:
        flash('Evaluación no encontrada.', 'danger')
        return redirect(url_for('dashboard'))
    
    respuestas = Respuesta.query.filter_by(evaluacion_id=evaluacion_id).all()
    if not respuestas:
        flash('No se encontraron respuestas.', 'warning')
        return redirect(url_for('dashboard'))
    
    resultados = []
    niveles_estimados = []
    
    for respuesta in respuestas:
        try:
            pregunta = Pregunta.query.get(respuesta.pregunta_id)
            nivel_esperado = pregunta.nivel.codigo if pregunta else 'B1'
            resultado = analizador.analizar(respuesta.texto, nivel_esperado)
            resultados.append(resultado)
            niveles_estimados.append(resultado['nivel_estimado'])
            
            # Guardar nivel estimado por pregunta en la BD
            nivel_estimado = resultado['nivel_estimado']
            nivel_obj = NivelMCER.query.filter_by(codigo=nivel_estimado).first()
            if nivel_obj:
                respuesta.nivel_predicho_id = nivel_obj.id
                db.session.commit()
                
        except Exception as e:
            print(f"Error analizando respuesta {respuesta.id}: {e}")
    
    if niveles_estimados:
        nivel_estimado = Counter(niveles_estimados).most_common(1)[0][0]
        nivel_obj = NivelMCER.query.filter_by(codigo=nivel_estimado).first()
        if nivel_obj:
            evaluacion.nivel_estimado_id = nivel_obj.id
        evaluacion.estado = 'COMPLETADA'
        evaluacion.fecha_fin = datetime.utcnow()
        db.session.commit()
        
        ruta_diploma = eval_service.generar_diploma(current_user, nivel_estimado, datetime.now())
        info_nivel = eval_service.obtener_descripcion_nivel(nivel_estimado)
        
        nivel_auto = current_user.nivel_autopercibido
        coincide = False
        mensaje_coincidencia = ""
        
        if nivel_auto:
            if nivel_auto.codigo == nivel_estimado:
                coincide = True
                mensaje_coincidencia = "✅ ¡Coincidencia perfecta! Tu nivel autopercibido coincide con el estimado por el sistema."
            else:
                coincide = False
                mensaje_coincidencia = f"📊 Tu nivel autopercibido es {nivel_auto.codigo}, pero el sistema estimó {nivel_estimado}. Revisa tus respuestas o actualiza tu percepción."
        else:
            mensaje_coincidencia = "ℹ️ No definiste un nivel autopercibido. Puedes actualizarlo en tu perfil."
        
        session.pop('evaluacion_id', None)
        session.pop('pregunta_actual', None)
        session.pop('preguntas', None)
        session.pop('respuestas', None)
        
        feedback_detallado = []
        for i, r in enumerate(resultados):
            feedback_detallado.append({
                'pregunta_numero': i + 1,
                'nivel_esperado': r.get('nivel_esperado', 'N/A'),
                'nivel_estimado': r['nivel_estimado'],
                'cumple': r['cumple'],
                'metricas': r['metricas'],
                'feedback': r['feedback'],
                'texto_usuario': r.get('texto_usuario', ''),
                'palabras_repetidas': r.get('palabras_repetidas', []),
                'sugerencias': r.get('sugerencias', [])
            })
        
        return render_template('resultado.html',
                             nivel=nivel_estimado,
                             info_nivel=info_nivel,
                             evaluacion=evaluacion,
                             diploma_path=ruta_diploma,
                             feedback_detallado=feedback_detallado,
                             coincide=coincide,
                             mensaje_coincidencia=mensaje_coincidencia)
    
    flash('No se pudo determinar el nivel.', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/evaluacion/detalle/<int:evaluacion_id>')
@login_required
def detalle_evaluacion(evaluacion_id):
    evaluacion = Evaluacion.query.get(evaluacion_id)
    if not evaluacion:
        flash('Evaluación no encontrada.', 'danger')
        return redirect(url_for('historial'))
    
    if evaluacion.usuario_id != current_user.id and current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('historial'))
    
    respuestas = Respuesta.query.filter_by(evaluacion_id=evaluacion_id).all()
    
    detalles = []
    for i, respuesta in enumerate(respuestas):
        pregunta = Pregunta.query.get(respuesta.pregunta_id)
        try:
            caracteristicas = json.loads(respuesta.caracteristicas) if respuesta.caracteristicas else {}
        except:
            caracteristicas = {}
        
        # Si la respuesta tiene nivel guardado, usarlo; si no, recalcular
        if respuesta.nivel_predicho:
            nivel_estimado = respuesta.nivel_predicho.codigo
        else:
            try:
                if pregunta:
                    nivel_esperado = pregunta.nivel.codigo
                    resultado = analizador.analizar(respuesta.texto, nivel_esperado)
                    nivel_estimado = resultado['nivel_estimado']
                else:
                    nivel_estimado = "N/A"
            except:
                nivel_estimado = "N/A"
        
        nivel_esperado = pregunta.nivel.codigo if pregunta else "N/A"
        texto_pregunta = pregunta.texto if pregunta else "Pregunta no disponible"
        
        detalles.append({
            'numero': i + 1,
            'pregunta_texto': texto_pregunta,
            'nivel_esperado': nivel_esperado,
            'nivel_estimado': nivel_estimado,
            'texto_usuario': respuesta.texto,
            'metricas': caracteristicas,
        })
    
    return render_template('detalle_evaluacion.html',
                         evaluacion=evaluacion,
                         detalles=detalles)

@app.route('/diploma/<int:evaluacion_id>')
@login_required
def descargar_diploma(evaluacion_id):
    evaluacion = Evaluacion.query.get(evaluacion_id)
    if not evaluacion or (evaluacion.usuario_id != current_user.id and current_user.rol != 'ADMINISTRADOR'):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('historial'))
    
    if evaluacion.estado != 'COMPLETADA' or not evaluacion.nivel_estimado:
        flash('Esta evaluación no tiene un nivel definido.', 'warning')
        return redirect(url_for('historial'))
    
    nombre_archivo = f"diploma_{current_user.nombre}_{current_user.apellido}_{evaluacion.fecha_inicio.strftime('%Y%m%d')}.pdf"
    ruta_pdf = os.path.join('./diplomas', nombre_archivo)
    
    if not os.path.exists(ruta_pdf):
        ruta_pdf = eval_service.generar_diploma(current_user, evaluacion.nivel_estimado.codigo, evaluacion.fecha_inicio)
    
    return send_file(ruta_pdf, as_attachment=True, download_name=nombre_archivo)

# ============================================
# RUTAS DE ADMINISTRACIÓN
# ============================================

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    total_usuarios = Usuario.query.count()
    total_evaluaciones = Evaluacion.query.count()
    total_preguntas = Pregunta.query.count()
    total_respuestas = Respuesta.query.count()
    
    # Calcular evaluaciones por nivel
    niveles = NivelMCER.query.all()
    evaluaciones_por_nivel = {}
    for nivel in niveles:
        count = Evaluacion.query.filter_by(nivel_estimado_id=nivel.id, estado='COMPLETADA').count()
        evaluaciones_por_nivel[nivel.codigo] = count
    
    return render_template('admin/dashboard.html',
                         total_usuarios=total_usuarios,
                         total_evaluaciones=total_evaluaciones,
                         total_preguntas=total_preguntas,
                         total_respuestas=total_respuestas,
                         evaluaciones_por_nivel=evaluaciones_por_nivel)

@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/admin/usuario/<int:usuario_id>')
@login_required
def admin_usuario_detalle(usuario_id):
    if current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    evaluaciones = Evaluacion.query.filter_by(usuario_id=usuario_id).order_by(Evaluacion.fecha_inicio.desc()).all()
    return render_template('admin/usuario_detalle.html', usuario=usuario, evaluaciones=evaluaciones)

@app.route('/admin/usuario/editar/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
def admin_usuario_editar(usuario_id):
    if current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if request.method == 'POST':
        usuario.rol = request.form.get('rol')
        usuario.estado = request.form.get('estado') == 'activo'
        
        nivel_codigo = request.form.get('nivel_autopercibido')
        if nivel_codigo:
            nivel_obj = NivelMCER.query.filter_by(codigo=nivel_codigo).first()
            usuario.nivel_autopercibido_id = nivel_obj.id if nivel_obj else None
        else:
            usuario.nivel_autopercibido_id = None
        
        db.session.commit()
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('admin_usuario_detalle', usuario_id=usuario.id))
    
    niveles = NivelMCER.query.all()
    return render_template('admin/usuario_editar.html', usuario=usuario, niveles=niveles)

@app.route('/admin/usuario/eliminar/<int:usuario_id>', methods=['POST'])
@login_required
def admin_usuario_eliminar(usuario_id):
    if current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.id == current_user.id:
        flash('No puedes eliminarte a ti mismo.', 'danger')
        return redirect(url_for('admin_usuarios'))
    
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/preguntas')
@login_required
def admin_preguntas():
    if current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    preguntas = Pregunta.query.all()
    return render_template('admin/preguntas.html', preguntas=preguntas)

@app.route('/admin/pregunta/nueva', methods=['GET', 'POST'])
@login_required
def admin_pregunta_nueva():
    if current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        texto = request.form.get('texto')
        instrucciones = request.form.get('instrucciones')
        nivel_id = request.form.get('nivel_id')
        categoria_id = request.form.get('categoria_id')
        dificultad = request.form.get('dificultad', 1)
        activa = request.form.get('activa') == 'on'
        
        if not texto or not nivel_id or not categoria_id:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('admin_pregunta_nueva'))
        
        pregunta = Pregunta(
            texto=texto,
            instrucciones=instrucciones,
            nivel_id=int(nivel_id),
            categoria_id=int(categoria_id),
            dificultad=int(dificultad),
            activa=activa
        )
        db.session.add(pregunta)
        db.session.commit()
        flash('Pregunta creada exitosamente.', 'success')
        return redirect(url_for('admin_preguntas'))
    
    niveles = NivelMCER.query.all()
    categorias = Categoria.query.all()
    return render_template('admin/pregunta_form.html', 
                         pregunta=None, 
                         niveles=niveles, 
                         categorias=categorias,
                         titulo='Crear Nueva Pregunta')

@app.route('/admin/pregunta/editar/<int:pregunta_id>', methods=['GET', 'POST'])
@login_required
def admin_pregunta_editar(pregunta_id):
    if current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    pregunta = Pregunta.query.get_or_404(pregunta_id)
    
    if request.method == 'POST':
        pregunta.texto = request.form.get('texto')
        pregunta.instrucciones = request.form.get('instrucciones')
        pregunta.nivel_id = int(request.form.get('nivel_id'))
        pregunta.categoria_id = int(request.form.get('categoria_id'))
        pregunta.dificultad = int(request.form.get('dificultad', 1))
        pregunta.activa = request.form.get('activa') == 'on'
        
        db.session.commit()
        flash('Pregunta actualizada correctamente.', 'success')
        return redirect(url_for('admin_preguntas'))
    
    niveles = NivelMCER.query.all()
    categorias = Categoria.query.all()
    return render_template('admin/pregunta_form.html', 
                         pregunta=pregunta, 
                         niveles=niveles, 
                         categorias=categorias,
                         titulo='Editar Pregunta')

@app.route('/admin/pregunta/eliminar/<int:pregunta_id>', methods=['POST'])
@login_required
def admin_pregunta_eliminar(pregunta_id):
    if current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    pregunta = Pregunta.query.get_or_404(pregunta_id)
    db.session.delete(pregunta)
    db.session.commit()
    flash('Pregunta eliminada correctamente.', 'success')
    return redirect(url_for('admin_preguntas'))

@app.route('/admin/evaluaciones')
@login_required
def admin_evaluaciones():
    if current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    evaluaciones = Evaluacion.query.order_by(Evaluacion.fecha_inicio.desc()).all()
    return render_template('admin/evaluaciones.html', evaluaciones=evaluaciones)

@app.route('/admin/evaluacion/<int:evaluacion_id>')
@login_required
def admin_evaluacion_detalle(evaluacion_id):
    if current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    respuestas = Respuesta.query.filter_by(evaluacion_id=evaluacion_id).all()
    return render_template('admin/evaluacion_detalle.html', evaluacion=evaluacion, respuestas=respuestas)

@app.route('/admin/niveles')
@login_required
def admin_niveles():
    if current_user.rol != 'ADMINISTRADOR':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    niveles = NivelMCER.query.all()
    return render_template('admin/niveles.html', niveles=niveles)

# ============================================
# INICIALIZAR DB
# ============================================

def init_db():
    with app.app_context():
        db.create_all()
        niveles = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        for codigo in niveles:
            if not NivelMCER.query.filter_by(codigo=codigo).first():
                db.session.add(NivelMCER(codigo=codigo, nombre=f'Nivel {codigo}'))
        categorias = ['Gramática', 'Vocabulario', 'Escritura', 'Lectura']
        for nombre in categorias:
            if not Categoria.query.filter_by(nombre=nombre).first():
                db.session.add(Categoria(nombre=nombre))
        if not Usuario.query.filter_by(correo='admin@system.com').first():
            db.session.add(Usuario(
                nombre='Administrador', apellido='Sistema',
                correo='admin@system.com',
                password=generate_password_hash('admin123'),
                rol='ADMINISTRADOR'
            ))
        db.session.commit()
        print("✅ Base de datos inicializada")

# ============================================
# EJECUTAR
# ============================================

if __name__ == '__main__':
    if not os.path.exists('evaluacion_ingles.db'):
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)