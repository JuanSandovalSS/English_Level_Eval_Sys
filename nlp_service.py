# nlp_service.py - Versión sin Sentence-Transformers (usando TF-IDF)
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.corpus import stopwords
import numpy as np
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer

# Descargar recursos de NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('stopwords')
    nltk.download('wordnet')

class NLPService:
    def __init__(self):
        """Inicializa el servicio de NLP con NLTK (sin Sentence-Transformers)"""
        self.stopwords = set(stopwords.words('english'))
        self.tfidf = TfidfVectorizer(max_features=100, stop_words='english')
        self._tfidf_fitted = False
    
    def process(self, text):
        """
        Procesa un texto y extrae características lingüísticas.
        """
        if not text or len(text.strip()) < 3:
            return self._empty_features(text)
        
        # Limpieza básica
        text_clean = self._clean_text(text)
        
        try:
            # Tokenización
            tokens = word_tokenize(text_clean)
            sentences = sent_tokenize(text_clean)
            
            # POS tagging
            pos_tags = pos_tag(tokens)
            
            # Características básicas
            num_palabras = len(tokens)
            num_oraciones = len(sentences)
            
            # Riqueza léxica (type-token ratio)
            unique_tokens = set([t.lower() for t in tokens if t.isalpha()])
            riqueza_lexica = len(unique_tokens) / num_palabras if num_palabras > 0 else 0
            
            # Longitud promedio de oraciones
            longitud_promedio = np.mean([len(sent.split()) for sent in sentences]) if num_oraciones > 0 else 0
            
            # Densidad léxica (palabras de contenido)
            content_tags = ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 
                           'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS']
            content_words = [t for t, tag in pos_tags if tag in content_tags]
            densidad_lexica = len(content_words) / num_palabras if num_palabras > 0 else 0
            
            # Vocabulario diverso
            vocabulario_diverso = len(unique_tokens)
            
            # Palabras sin stopwords
            palabras_sin_stop = [t for t in tokens if t.lower() not in self.stopwords and t.isalpha()]
            num_palabras_sin_stop = len(palabras_sin_stop)
            
            # Generar embedding con TF-IDF (vector de 100 dimensiones)
            embedding = self._get_tfidf_embedding(text_clean)
            
            return {
                'texto_original': text,
                'texto_limpio': text_clean,
                'num_palabras': num_palabras,
                'num_oraciones': num_oraciones,
                'riqueza_lexica': round(riqueza_lexica, 4),
                'densidad_lexica': round(densidad_lexica, 4),
                'longitud_promedio': round(longitud_promedio, 2),
                'vocabulario_diverso': vocabulario_diverso,
                'num_palabras_sin_stop': num_palabras_sin_stop,
                'embedding': embedding
            }
        except Exception as e:
            print(f"⚠️ Error procesando texto: {e}")
            return self._empty_features(text)
    
    def _get_tfidf_embedding(self, text):
        """Genera embedding usando TF-IDF"""
        try:
            if not self._tfidf_fitted:
                # Usar un corpus pequeño para ajustar el vectorizador
                sample_texts = [
                    "Hello world this is a test",
                    "Natural language processing is interesting",
                    "Machine learning and artificial intelligence",
                    "The quick brown fox jumps over the lazy dog"
                ]
                self.tfidf.fit(sample_texts)
                self._tfidf_fitted = True
            
            # Transformar el texto
            vector = self.tfidf.transform([text])
            embedding = vector.toarray().flatten().tolist()
            
            # Asegurar que tenga 100 dimensiones
            if len(embedding) < 100:
                embedding = embedding + [0.0] * (100 - len(embedding))
            elif len(embedding) > 100:
                embedding = embedding[:100]
            
            return embedding
        except:
            # Si falla, devolver un vector de ceros
            return [0.0] * 100
    
    def _empty_features(self, text):
        """Retorna características vacías para texto inválido."""
        return {
            'texto_original': text,
            'texto_limpio': '',
            'num_palabras': 0,
            'num_oraciones': 0,
            'riqueza_lexica': 0,
            'densidad_lexica': 0,
            'longitud_promedio': 0,
            'vocabulario_diverso': 0,
            'num_palabras_sin_stop': 0,
            'embedding': [0.0] * 100
        }
    
    def _clean_text(self, text):
        """Realiza limpieza básica del texto."""
        if not text:
            return ""
        
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s,.!?\'\"-]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def get_feature_vector(self, text):
        """Obtiene el vector de características para clasificación."""
        features = self.process(text)
        return {
            'num_palabras': features['num_palabras'],
            'num_oraciones': features['num_oraciones'],
            'riqueza_lexica': features['riqueza_lexica'],
            'densidad_lexica': features['densidad_lexica'],
            'longitud_promedio': features['longitud_promedio'],
            'vocabulario_diverso': features['vocabulario_diverso'],
            'embedding': features['embedding']
        }

# Test rápido
if __name__ == "__main__":
    nlp = NLPService()
    test_text = "Hello, my name is Juan. I am from Guatemala. I like to study English."
    result = nlp.process(test_text)
    print(f"✅ Texto procesado correctamente")
    print(f"   Palabras: {result['num_palabras']}")
    print(f"   Oraciones: {result['num_oraciones']}")
    print(f"   Riqueza léxica: {result['riqueza_lexica']}")
    print(f"   Embedding dimension: {len(result['embedding'])}")