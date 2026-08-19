# train_cefr_sklearn.py - Clasificador con scikit-learn (NO necesita PyTorch)
import json
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

def generar_corpus_ejemplo(num_samples=3000):
    """Genera un corpus de ejemplo para entrenamiento"""
    levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    
    textos_por_nivel = {
        'A1': [
            "My name is Juan. I live in Guatemala City. I am a student.",
            "Hello I am Maria. I have a cat. The cat is black and white.",
            "This is my house. It is small. There are two bedrooms.",
            "I go to school every day. I learn English and Math.",
            "I like pizza and hamburgers. My favorite food is pizza.",
            "My mother is a teacher. My father is an engineer.",
            "I wake up at seven o'clock. Then I have breakfast.",
            "The weather is nice today. The sun is shining."
        ],
        'A2': [
            "I wake up at 7 o'clock. Then I have breakfast and go to work.",
            "Yesterday I went to the supermarket. I bought some fruits.",
            "I have two brothers and one sister. My sister lives in Antigua.",
            "On weekends I like to go to the park. I play soccer with my friends.",
            "I am studying English because I want to travel to the United States.",
            "My favorite hobby is reading books. I like to read novels.",
            "Last weekend I visited my grandmother in her small town.",
            "I want to learn English well because it is important for my career."
        ],
        'B1': [
            "I have been studying English for three years now. I can understand most conversations.",
            "Last summer I traveled to Mexico with my family. We visited several cities.",
            "I work as an accountant in a large company. I use English with international clients.",
            "I believe that learning languages opens many doors. It allows you to understand different cultures.",
            "The movie was very interesting. It told the story of a woman who traveled around the world.",
            "I think technology has changed our lives in many ways.",
            "My goal is to become fluent in English. I practice every day.",
            "Education is very important. It gives people the opportunity to have a better life."
        ],
        'B2': [
            "The economic situation in Guatemala has been challenging for many families. Despite these difficulties, there are opportunities.",
            "In my opinion, education is one of the most important factors in a country's development.",
            "Climate change is one of the most pressing issues of our time. We need to take action now.",
            "Technology has transformed the way we communicate. While it offers many benefits, it also presents challenges.",
            "I have a strong interest in international relations. I follow global news closely.",
            "Sustainable development is crucial for future generations.",
            "Globalization has created new opportunities for trade and cultural exchange.",
            "The education system needs to adapt to the changing needs of society."
        ],
        'C1': [
            "Sustainable development has gained significant traction in recent years, as policymakers recognize the need to balance economic growth with environmental protection.",
            "Neuroscience has made remarkable progress in understanding the human brain, yet many aspects of consciousness remain elusive.",
            "Digital technologies have fundamentally altered traditional business models, compelling organizations to adapt their strategies.",
            "Cultural diversity enriches our societies and fosters innovation. By embracing different perspectives, we can develop creative solutions.",
            "The transition to renewable energy represents one of the most significant challenges of the 21st century.",
            "The digital divide remains a significant barrier to equal access to education and economic opportunities.",
            "Urban planning must consider the environmental impact of new developments.",
            "The role of media in shaping public opinion has become increasingly complex."
        ],
        'C2': [
            "The dialectical relationship between technological advancement and societal transformation manifests itself in increasingly complex ways.",
            "Contemporary discourse on global governance grapples with the tension between national sovereignty and collective action.",
            "The hermeneutics of modern literature reveal profound insights into the human condition.",
            "Epistemological frameworks in the social sciences continue to evolve, incorporating insights from diverse disciplines.",
            "The philosophical implications of artificial intelligence extend beyond technical considerations.",
            "The intersection of economic policy and social welfare presents a complex challenge for modern states.",
            "Postcolonial theory has transformed our understanding of cultural identity in globalized societies.",
            "The ethics of data collection and usage have become central to discussions about privacy and autonomy."
        ]
    }
    
    corpus = []
    for level, texts in textos_por_nivel.items():
        for i in range(num_samples // 6):
            base_text = random.choice(texts)
            variaciones = [
                base_text,
                base_text + " " + " ".join(random.sample(texts[0].split(), 3)),
                "I think that " + base_text,
                base_text + " This is my opinion.",
                "In my experience, " + base_text,
                base_text + " This is very important to consider."
            ]
            texto = random.choice(variaciones)
            corpus.append({'text': texto, 'label': level})
    
    return corpus

# 1. Generar datos
print("="*50)
print("📝 Generando corpus de ejemplo para entrenamiento...")
print("="*50)
corpus = generar_corpus_ejemplo(3000)
print(f"✅ Corpus generado: {len(corpus)} textos")

# 2. Preparar features con TF-IDF
print("\n📊 Preparando características con TF-IDF...")
textos = [item['text'] for item in corpus]
labels = [item['label'] for item in corpus]

vectorizer = TfidfVectorizer(
    max_features=100, 
    stop_words='english', 
    ngram_range=(1, 2),
    min_df=2
)
X = vectorizer.fit_transform(textos).toarray()
print(f"✅ Características: {X.shape[1]} dimensiones")

# Mapear labels a números
label_to_id = {'A1': 0, 'A2': 1, 'B1': 2, 'B2': 3, 'C1': 4, 'C2': 5}
id_to_label = {v: k for k, v in label_to_id.items()}
y = [label_to_id[l] for l in labels]

# 3. Dividir datos
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✅ Entrenamiento: {len(X_train)} | Prueba: {len(X_test)}")

# 4. Entrenar modelos
print("\n🧠 Entrenando modelos...")
print("-"*30)

modelos = {
    'svm': SVC(kernel='rbf', C=1.0, probability=True, random_state=42),
    'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'logistic': LogisticRegression(max_iter=1000, random_state=42)
}

resultados = {}
mejor_modelo = None
mejor_accuracy = 0

for nombre, modelo in modelos.items():
    print(f"  Entrenando {nombre}...")
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    resultados[nombre] = acc
    print(f"    ✅ {nombre}: {acc:.4f}")
    
    if acc > mejor_accuracy:
        mejor_accuracy = acc
        mejor_modelo = modelo

# 5. Guardar modelo y vectorizer
print("\n💾 Guardando modelo...")
os.makedirs('./cefr_sklearn_model', exist_ok=True)

with open('./cefr_sklearn_model/model.pkl', 'wb') as f:
    pickle.dump(mejor_modelo, f)

with open('./cefr_sklearn_model/vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

with open('./cefr_sklearn_model/label_map.pkl', 'wb') as f:
    pickle.dump(label_to_id, f)

with open('./cefr_sklearn_model/id_to_label.pkl', 'wb') as f:
    pickle.dump(id_to_label, f)

print("✅ Modelo guardado en ./cefr_sklearn_model")

# 6. Mostrar resultados
print("\n" + "="*50)
print("📊 RESULTADOS DEL ENTRENAMIENTO")
print("="*50)
for nombre, acc in resultados.items():
    print(f"  {nombre}: {acc:.4f}")

print(f"\n🏆 Mejor modelo: {max(resultados, key=resultados.get)}")
print(f"   Accuracy: {mejor_accuracy:.4f}")

# 7. Probar con ejemplos
print("\n📝 Probando el modelo con ejemplos...")
print("-"*30)

ejemplos = [
    "My name is Juan. I am from Guatemala. I like to study English.",
    "I have been studying English for five years. I can understand most conversations and read newspapers.",
    "The economic implications of climate change are significant and require immediate policy responses.",
    "The dialectical relationship between economic growth and environmental sustainability is a central concern of our time."
]

for texto in ejemplos:
    X_test = vectorizer.transform([texto]).toarray()
    pred = mejor_modelo.predict(X_test)[0]
    nivel = id_to_label[pred]
    print(f"  Texto: {texto[:50]}...")
    print(f"  Nivel estimado: {nivel}")
    print()

print("="*50)
print("✅ ENTRENAMIENTO COMPLETADO")
print("="*50)