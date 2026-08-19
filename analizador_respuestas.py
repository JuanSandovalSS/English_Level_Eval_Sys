# analizador_respuestas.py
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter

# Descargar recursos de NLTK (solo primera vez)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')

class AnalizadorRespuestas:
    def __init__(self):
        self.stopwords = set(stopwords.words('english'))
    
    def analizar(self, texto, nivel_esperado):
        """
        Analiza una respuesta y determina si cumple con el nivel esperado.
        
        Returns:
            dict: {
                'cumple': bool,
                'nivel_estimado': str,
                'metricas': dict,
                'feedback': list
            }
        """
        # Limpiar y tokenizar
        texto_limpio = self._limpiar_texto(texto)
        palabras = word_tokenize(texto_limpio)
        oraciones = sent_tokenize(texto_limpio)
        
        # Métricas
        num_palabras = len(palabras)
        num_oraciones = len(oraciones)
        
        # Riqueza léxica (Type-Token Ratio)
        palabras_unicas = set([p.lower() for p in palabras if p.isalpha()])
        riqueza_lexica = len(palabras_unicas) / num_palabras if num_palabras > 0 else 0
        
        # Longitud promedio de oraciones
        longitud_promedio = num_palabras / num_oraciones if num_oraciones > 0 else 0
        
        # Palabras con stopwords removidas
        palabras_sin_stop = [p for p in palabras if p.lower() not in self.stopwords and p.isalpha()]
        
        # Densidad léxica (palabras de contenido vs. total)
        # POS tagging para identificar palabras de contenido
        try:
            from nltk.tag import pos_tag
            tags = pos_tag(palabras)
            content_tags = ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS']
            palabras_contenido = [t for t, tag in tags if tag in content_tags]
            densidad_lexica = len(palabras_contenido) / num_palabras if num_palabras > 0 else 0
        except:
            densidad_lexica = 0.4  # Valor por defecto
        
        # Determinar nivel estimado
        nivel_estimado = self._estimar_nivel({
            'num_palabras': num_palabras,
            'riqueza_lexica': riqueza_lexica,
            'longitud_promedio': longitud_promedio,
            'densidad_lexica': densidad_lexica,
            'num_oraciones': num_oraciones
        })
        
        # Verificar si cumple con el nivel esperado
        niveles = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        idx_esperado = niveles.index(nivel_esperado)
        idx_estimado = niveles.index(nivel_estimado)
        
        cumple = idx_estimado >= idx_esperado - 1  # Permite un nivel por debajo
        
        # Generar feedback
        feedback = self._generar_feedback({
            'num_palabras': num_palabras,
            'riqueza_lexica': riqueza_lexica,
            'longitud_promedio': longitud_promedio,
            'densidad_lexica': densidad_lexica,
            'num_oraciones': num_oraciones,
            'nivel_esperado': nivel_esperado,
            'nivel_estimado': nivel_estimado
        })
        
        return {
            'cumple': cumple,
            'nivel_estimado': nivel_estimado,
            'metricas': {
                'num_palabras': num_palabras,
                'num_oraciones': num_oraciones,
                'riqueza_lexica': round(riqueza_lexica, 3),
                'longitud_promedio': round(longitud_promedio, 1),
                'densidad_lexica': round(densidad_lexica, 3)
            },
            'feedback': feedback
        }
    
    def _limpiar_texto(self, texto):
        """Limpia el texto para análisis"""
        texto = texto.lower()
        texto = re.sub(r'[^a-zA-Z0-9\s.,!?\']', '', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto
    
    def _estimar_nivel(self, metricas):
        """Estima el nivel basado en métricas"""
        num_palabras = metricas['num_palabras']
        riqueza_lexica = metricas['riqueza_lexica']
        longitud_promedio = metricas['longitud_promedio']
        densidad_lexica = metricas['densidad_lexica']
        
        # Puntuación basada en múltiples criterios
        puntuacion = 0
        
        # Criterio 1: Número de palabras
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
        
        # Criterio 2: Riqueza léxica
        if riqueza_lexica < 0.4:
            pass
        elif riqueza_lexica < 0.6:
            puntuacion += 1
        elif riqueza_lexica < 0.7:
            puntuacion += 2
        else:
            puntuacion += 3
        
        # Criterio 3: Longitud promedio de oraciones
        if longitud_promedio < 8:
            pass
        elif longitud_promedio < 12:
            puntuacion += 1
        elif longitud_promedio < 16:
            puntuacion += 2
        else:
            puntuacion += 3
        
        # Mapear puntuación a nivel
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
        """Genera feedback para el usuario"""
        feedback = []
        nivel_esperado = data['nivel_esperado']
        nivel_estimado = data['nivel_estimado']
        
        # Feedback sobre el nivel
        if nivel_estimado == nivel_esperado:
            feedback.append("✅ ¡Excelente! Tu respuesta corresponde al nivel esperado.")
        elif self._nivel_mayor(nivel_estimado, nivel_esperado):
            feedback.append(f"🌟 ¡Buen trabajo! Tu respuesta parece de nivel {nivel_estimado}, superior al esperado.")
        else:
            feedback.append(f"📚 Tu respuesta se acerca al nivel {nivel_estimado}. Practica más para alcanzar el nivel {nivel_esperado}.")
        
        # Feedback sobre métricas específicas
        if data['num_palabras'] < self._palabras_minimas(nivel_esperado):
            feedback.append(f"💡 Escribe respuestas más largas (mínimo {self._palabras_minimas(nivel_esperado)} palabras).")
        
        if data['riqueza_lexica'] < 0.5:
            feedback.append("📖 Usa vocabulario más variado. Evita repetir las mismas palabras.")
        
        if data['longitud_promedio'] < 8:
            feedback.append("✍️ Intenta escribir oraciones más largas y complejas.")
        
        if data['num_oraciones'] < 3:
            feedback.append("📝 Divide tu respuesta en más oraciones para mejor estructura.")
        
        if not feedback:
            feedback.append("🎯 ¡Buen trabajo! Sigue practicando para mejorar.")
        
        return feedback
    
    def _nivel_mayor(self, nivel1, nivel2):
        """Determina si nivel1 es mayor que nivel2"""
        niveles = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        return niveles.index(nivel1) > niveles.index(nivel2)
    
    def _palabras_minimas(self, nivel):
        """Palabras mínimas esperadas por nivel"""
        minimos = {
            'A1': 15,
            'A2': 25,
            'B1': 45,
            'B2': 75,
            'C1': 120,
            'C2': 175
        }
        return minimos.get(nivel, 30)

# Test rápido
if __name__ == "__main__":
    analizador = AnalizadorRespuestas()
    
    # Probar con un ejemplo
    texto = "I think that education is very important for everyone. It gives us the opportunity to learn new things and get better jobs. When we have good education, we can help our families and our communities."
    resultado = analizador.analizar(texto, 'B1')
    
    print("📊 Análisis de respuesta:")
    print(f"  Nivel esperado: B1")
    print(f"  Nivel estimado: {resultado['nivel_estimado']}")
    print(f"  ¿Cumple? {resultado['cumple']}")
    print(f"\n📈 Métricas: {resultado['metricas']}")
    print(f"\n💬 Feedback:")
    for f in resultado['feedback']:
        print(f"  {f}")