# download_universalcefr.py - VERSIÓN CORREGIDA
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

print("="*50)
print("📥 DESCARGANDO MODELO PARA CLASIFICACIÓN CEFR")
print("="*50)

# Modelos alternativos que funcionan para clasificación de nivel de inglés
modelos_disponibles = {
    "bert-base": "bert-base-uncased",
    "distilbert": "distilbert-base-uncased",
    "roberta": "roberta-base",
    "albert": "albert-base-v2"
}

# Usar DistilBERT (más ligero y rápido)
model_name = "distilbert-base-uncased"
print(f"\n🧠 Usando modelo: {model_name}")

try:
    # Cargar tokenizer y modelo base
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=6)
    
    print("✅ Modelo cargado correctamente")
    
    # Guardar el modelo para usarlo después
    model.save_pretrained("./cefr_model")
    tokenizer.save_pretrained("./cefr_model")
    print("💾 Modelo guardado en ./cefr_model")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Intentando con pipeline...")
    
    # Usar pipeline como alternativa
    try:
        classifier = pipeline("text-classification", model="distilbert-base-uncased")
        print("✅ Pipeline cargado correctamente")
        
        # Probar
        resultado = classifier("My name is Juan. I like to study English.")
        print(f"\n📊 Prueba: {resultado}")
        
    except Exception as e2:
        print(f"❌ Error en pipeline: {e2}")