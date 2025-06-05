import sys
import os
import pytest
from flask import Flask

# Agrega la ruta raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flaskr.modelos.modelo import db

@pytest.fixture(scope='session')
def app():
    app = Flask(__name__)
    
    # Cambia la conexión según tu configuración real
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/prueba'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True

    db.init_app(app)
    with app.app_context():
       # db.drop_all()   # Borra las tablas existentes (para tests limpios)
        db.create_all()
        yield app
        db.session.remove()
        #db.drop_all()  # Opcional: borra las tablas al final del test

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session
