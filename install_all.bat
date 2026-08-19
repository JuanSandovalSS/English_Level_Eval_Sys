@echo off
echo ============================================================
echo INSTALANDO TODAS LAS DEPENDENCIAS COMPATIBLES
echo ============================================================

echo.
echo 1. Desinstalando versiones anteriores...
python -m pip uninstall numpy pandas matplotlib seaborn contourpy scikit-learn scipy nltk sentence-transformers flask flask-sqlalchemy sqlalchemy flask-login psycopg2-binary -y

echo.
echo 2. Instalando NumPy...
python -m pip install numpy==1.26.4

echo.
echo 3. Instalando Pandas y dependencias de visualizacion...
python -m pip install pandas==2.2.0
python -m pip install matplotlib==3.8.4
python -m pip install seaborn==0.13.2

echo.
echo 4. Instalando Machine Learning...
python -m pip install scikit-learn==1.5.0
python -m pip install scipy==1.13.0

echo.
echo 5. Instalando NLP...
python -m pip install nltk==3.8.1
python -m pip install sentence-transformers==2.2.2

echo.
echo 6. Instalando Flask y base de datos...
python -m pip install flask==2.2.3
python -m pip install flask-sqlalchemy==2.5.1
python -m pip install sqlalchemy==1.4.46
python -m pip install flask-login==0.6.2
python -m pip install psycopg2-binary==2.9.9

echo.
echo 7. Descargando recursos de NLTK...
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('stopwords')"

echo.
echo 8. Verificando instalacion...
python -c "import numpy; import pandas; import matplotlib; import seaborn; import sklearn; import nltk; from sentence_transformers import SentenceTransformer; print('✅ TODAS LAS LIBRERIAS INSTALADAS CORRECTAMENTE')"

echo.
echo ============================================================
echo INSTALACION COMPLETADA EXITOSAMENTE
echo ============================================================
pause