import pandas as pd
import numpy as np
import json
import os
from nlp_service import NLPService
from classifier_service import ClassifierService
import random
from datetime import datetime

class TrainingPipeline:
    def __init__(self):
        self.nlp_service = NLPService()
        self.classifier_service = ClassifierService()
        self.data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    def generate_synthetic_corpus(self, num_samples=10000):
        """
        Genera un corpus sintético para entrenamiento.
        En un entorno real, usarías un corpus como UniversalCEFR.
        """
        print(f"Generando {num_samples} muestras sintéticas...")
        
        # Textos de ejemplo por nivel
        level_texts = {
            'A1': [
                "My name is Juan. I live in Guatemala City. I am a student. I like to study English.",
                "Hello! I am Maria. I have a cat. The cat is black and white. I love my cat.",
                "This is my house. It is small. There are two bedrooms. I live with my family.",
                "I go to school every day. I learn English and Math. My teacher is nice.",
                "I like pizza and hamburgers. My favorite food is pizza. I eat pizza on Friday."
            ],
            'A2': [
                "I usually wake up at 7 o'clock in the morning. Then I have breakfast and go to work. I work in a office near my house.",
                "Yesterday I went to the supermarket. I bought some fruits and vegetables. The apples were very expensive.",
                "I have two brothers and one sister. My sister lives in Antigua. She works as a teacher in a school.",
                "On weekends I like to go to the park. I play soccer with my friends. We have fun together.",
                "I am studying English because I want to travel. Next year I want to visit the United States."
            ],
            'B1': [
                "I have been studying English for three years now. I think my English is improving slowly but steadily. I can understand most conversations, although I sometimes struggle with fast speakers.",
                "Last summer I traveled to Mexico with my family. We visited several cities and tried different types of food. The people were very friendly and helpful.",
                "I work as an accountant in a large company. My job involves preparing financial reports and analyzing data. I use English to communicate with international clients.",
                "I believe that learning languages opens many doors. It allows you to understand different cultures and perspectives. That's why I'm committed to improving my English.",
                "The movie was very interesting. It told the story of a young woman who traveled around the world. She met many people and learned valuable lessons."
            ],
            'B2': [
                "The economic situation in Guatemala has been challenging for many families. Despite these difficulties, there are opportunities for those who are willing to work hard and adapt to changing circumstances.",
                "In my opinion, education is one of the most important factors in a country's development. It provides people with the skills and knowledge they need to improve their lives and contribute to society.",
                "Climate change is one of the most pressing issues of our time. It affects every aspect of our lives, from agriculture to public health. We need to take action now to protect our planet.",
                "Technology has transformed the way we communicate and interact with each other. While it offers many benefits, it also presents challenges that we need to address.",
                "I have a strong interest in politics and international relations. I follow global news closely and try to understand different perspectives on complex issues."
            ],
            'C1': [
                "The concept of sustainable development has gained significant traction in recent years, as policymakers and businesses increasingly recognize the need to balance economic growth with environmental protection and social responsibility.",
                "Neuroscience has made remarkable progress in understanding the human brain, yet many aspects of consciousness and cognition remain elusive. The complexity of neural networks continues to challenge researchers worldwide.",
                "The proliferation of digital technologies has fundamentally altered traditional business models, compelling organizations to adapt their strategies and operations to remain competitive in an increasingly interconnected marketplace.",
                "Cultural diversity enriches our societies and fosters innovation. By embracing different perspectives and experiences, we can develop more creative solutions to the complex challenges we face.",
                "The transition to renewable energy sources represents one of the most significant challenges of the 21st century. It requires unprecedented collaboration between governments, industries, and communities."
            ],
            'C2': [
                "The dialectical relationship between technological advancement and societal transformation manifests itself in increasingly complex ways, challenging our conventional understanding of progress and its implications for human welfare.",
                "Contemporary discourse on global governance grapples with the tension between national sovereignty and the imperative for collective action on transnational issues, from climate change to economic inequality.",
                "The hermeneutics of modern literature reveal profound insights into the human condition, reflecting the existential preoccupations that characterize our postmodern era.",
                "Epistemological frameworks in the social sciences continue to evolve, incorporating insights from diverse disciplines to construct more nuanced understandings of social phenomena.",
                "The philosophical implications of artificial intelligence extend beyond technical considerations, raising fundamental questions about consciousness, agency, and the nature of human cognition."
            ]
        }
        
        corpus = []
        
        for level, texts in level_texts.items():
            # Duplicar textos con variaciones
            for i in range(num_samples // len(level_texts)):
                base_text = random.choice(texts)
                
                # Crear variaciones
                variations = [
                    base_text,
                    base_text + " " + " ".join(random.sample(texts[0].split(), min(5, len(texts[0].split())))),
                    "In addition to what I said, " + base_text,
                    base_text + " I think this is very important to consider."
                ]
                
                selected_text = random.choice(variations)
                corpus.append({
                    'texto': selected_text,
                    'nivel': level,
                    'fuente': 'sintetico'
                })
        
        # Asegurar que tenemos suficientes muestras
        while len(corpus) < num_samples:
            level = random.choice(list(level_texts.keys()))
            texts = level_texts[level]
            base_text = random.choice(texts)
            corpus.append({
                'texto': base_text + " " + "This is a generated sample for training.",
                'nivel': level,
                'fuente': 'sintetico'
            })
        
        # Guardar corpus
        os.makedirs(self.data_path, exist_ok=True)
        corpus_file = os.path.join(self.data_path, 'corpus_sintetico.json')
        with open(corpus_file, 'w', encoding='utf-8') as f:
            json.dump(corpus, f, ensure_ascii=False, indent=2)
        
        print(f"Corpus guardado en: {corpus_file}")
        print(f"Total de muestras: {len(corpus)}")
        
        return corpus
    
    def prepare_training_data(self, corpus):
        """Prepara los datos para el entrenamiento."""
        print("Preparando datos para entrenamiento...")
        
        X = []
        y = []
        
        for item in corpus:
            text = item['texto']
            level = item['nivel']
            
            try:
                # Procesar texto con NLP
                features = self.nlp_service.process(text)
                
                # Preparar vector de características
                feature_vector = {
                    'num_palabras': features['num_palabras'],
                    'num_oraciones': features['num_oraciones'],
                    'riqueza_lexica': features['riqueza_lexica'],
                    'densidad_lexica': features['densidad_lexica'],
                    'longitud_promedio': features['longitud_promedio'],
                    'vocabulario_diverso': features['vocabulario_diverso'],
                    'embedding': features['embedding']
                }
                
                X.append(feature_vector)
                y.append(level)
            except Exception as e:
                print(f"Error procesando texto: {e}")
                continue
        
        # Guardar datos preparados
        prepared_file = os.path.join(self.data_path, 'datos_preparados.json')
        with open(prepared_file, 'w', encoding='utf-8') as f:
            json.dump({
                'X': X,
                'y': y,
                'total_muestras': len(X)
            }, f, ensure_ascii=False, indent=2)
        
        print(f"Datos preparados guardados en: {prepared_file}")
        print(f"Total de muestras procesadas: {len(X)}")
        
        return X, y
    
    def train_and_save_model(self, X, y):
        """Entrena el modelo y lo guarda."""
        print("Iniciando entrenamiento de modelos...")
        
        # Entrenar modelos
        results = self.classifier_service.train(X, y)
        
        # Guardar resultados
        results_file = os.path.join(self.data_path, 'resultados_entrenamiento.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Resultados de entrenamiento guardados en: {results_file}")
        
        # Guardar modelo
        model_file = os.path.join(self.data_path, 'models', 'classifier_model.pkl')
        self.classifier_service.save_model(model_file)
        
        # Mostrar resultados
        print("\n=== RESULTADOS DEL ENTRENAMIENTO ===")
        for model_name, metrics in results.items():
            print(f"\n{model_name.upper()}:")
            print(f"  Accuracy: {metrics['accuracy']:.4f}")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall: {metrics['recall']:.4f}")
            print(f"  F1-Score: {metrics['f1']:.4f}")
        
        return results
    
    def run_pipeline(self, num_samples=10000):
        """Ejecuta el pipeline completo de entrenamiento."""
        print("="*50)
        print("INICIANDO PIPELINE DE ENTRENAMIENTO")
        print("="*50)
        
        # Paso 1: Generar corpus
        corpus = self.generate_synthetic_corpus(num_samples)
        
        # Paso 2: Preparar datos
        X, y = self.prepare_training_data(corpus)
        
        # Paso 3: Entrenar y guardar modelo
        results = self.train_and_save_model(X, y)
        
        print("\n" + "="*50)
        print("PIPELINE DE ENTRENAMIENTO COMPLETADO")
        print("="*50)
        
        return results

if __name__ == "__main__":
    pipeline = TrainingPipeline()
    pipeline.run_pipeline(num_samples=5000)