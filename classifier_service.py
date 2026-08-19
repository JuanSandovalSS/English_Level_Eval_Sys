# classifier_service.py - Versión con scikit-learn
import pickle
import os
import numpy as np

class ClassifierService:
    def __init__(self):
        self.model_loaded = False
        self.model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cefr_sklearn_model')
        
        # Intentar cargar el modelo entrenado
        try:
            model_file = os.path.join(self.model_path, 'model.pkl')
            vectorizer_file = os.path.join(self.model_path, 'vectorizer.pkl')
            id_to_label_file = os.path.join(self.model_path, 'id_to_label.pkl')
            
            if os.path.exists(model_file) and os.path.exists(vectorizer_file):
                with open(model_file, 'rb') as f:
                    self.model = pickle.load(f)
                with open(vectorizer_file, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                with open(id_to_label_file, 'rb') as f:
                    self.id_to_label = pickle.load(f)
                self.model_loaded = True
                print("✅ Modelo scikit-learn cargado correctamente")
            else:
                print("⚠️ No se encontró modelo entrenado. Usando clasificación simple.")
        except Exception as e:
            print(f"⚠️ Error cargando modelo: {e}")
            self.model_loaded = False
    
    def predict(self, features):
        """Predice el nivel MCER para un texto."""
        # Si tenemos el modelo cargado, usarlo
        if self.model_loaded and 'texto_limpio' in features:
            try:
                return self._predict_with_model(features['texto_limpio'])
            except Exception as e:
                print(f"Error en modelo: {e}, usando método simple")
                return self._predict_simple(features)
        else:
            return self._predict_simple(features)
    
    def _predict_with_model(self, texto):
        """Predicción con el modelo scikit-learn."""
        # Vectorizar el texto
        X = self.vectorizer.transform([texto]).toarray()
        
        # Predecir
        pred = self.model.predict(X)[0]
        nivel = self.id_to_label[pred]
        
        # Obtener probabilidades si el modelo lo soporta
        if hasattr(self.model, 'predict_proba'):
            probas = self.model.predict_proba(X)[0].tolist()
        else:
            probas = None
        
        return {
            'nivel': nivel,
            'probabilidades': probas
        }
    
    def _predict_simple(self, features):
        """Clasificación simple basada en características (fallback)."""
        num_palabras = features.get('num_palabras', 0)
        riqueza_lexica = features.get('riqueza_lexica', 0)
        
        if num_palabras < 20:
            nivel = 'A1'
        elif num_palabras < 40:
            nivel = 'A2'
        elif num_palabras < 60:
            nivel = 'B1'
        elif num_palabras < 80:
            nivel = 'B2'
        elif num_palabras < 100:
            nivel = 'C1'
        else:
            nivel = 'C2'
        
        # Ajuste por riqueza léxica
        if riqueza_lexica > 0.7 and nivel in ['A1', 'A2']:
            niveles = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
            idx = niveles.index(nivel)
            if idx < 4:
                nivel = niveles[idx + 1]
        
        return {
            'nivel': nivel,
            'probabilidades': None
        }
    
    def load_model(self, path):
        """Carga un modelo guardado."""
        try:
            with open(os.path.join(path, 'model.pkl'), 'rb') as f:
                self.model = pickle.load(f)
            with open(os.path.join(path, 'vectorizer.pkl'), 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open(os.path.join(path, 'id_to_label.pkl'), 'rb') as f:
                self.id_to_label = pickle.load(f)
            self.model_loaded = True
            print(f"✅ Modelo cargado desde {path}")
        except Exception as e:
            print(f"⚠️ Error cargando modelo: {e}")