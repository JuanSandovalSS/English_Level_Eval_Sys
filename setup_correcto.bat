@echo off
echo ========================================
echo INSTALANDO DEPENDENCIAS CORRECTAS
echo ========================================

echo 1. Actualizando pip...
python -m pip install --upgrade pip

echo 2. Desinstalando versiones problemáticas...
python -m pip uninstall flask flask-sqlalchemy sqlalchemy flask-login werkzeug -y

echo 3. Instalando versiones compatibles...
python -m pip install flask==2.2.3
python -m pip install flask-sqlalchemy==2.5.1
python -m pip install sqlalchemy==1.4.46
python -m pip install flask-login==0.6.2
python -m pip install werkzeug==2.2.3
python -m pip install psycopg2-binary==2.9.9

echo 4. Instalando otras dependencias...
python -m pip install numpy==1.23.5
python -m pip install pandas==2.0.3
python -m pip install scikit-learn==1.3.0
python -m pip install nltk==3.8.1
python -m pip install sentence-transformers==2.2.2
python -m pip install matplotlib==3.7.2
python -m pip install seaborn==0.12.2

echo 5. Verificando instalacion...
python -c "from flask_sqlalchemy import SQLAlchemy; print('✅ Flask-SQLAlchemy OK')"
python -c "import sqlalchemy; print(f'✅ SQLAlchemy {sqlalchemy.__version__}')"
python -c "from flask_login import LoginManager; print('✅ Flask-Login OK')"

echo ========================================
echo INSTALACION COMPLETADA
echo ========================================
pause