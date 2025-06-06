from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_restx import Api as RestXApi

from .modelos.modelo import db, Personal
from .modelos.esquemas import ma  # ✅ Importar ma correctamente
from .vistas.vistas import (
    VistaAmbulancias,
    VistaFormularioAccidente,
    VistaSignin,
    VistalogIn,
    VistaReporteViajes,
    VistaPersonal,
    VistaHospitales,
    VistaAsignacionAmbulancia
)

def create_app(config_name='default'):
    app = Flask(__name__)

    # Configuración de base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_xfD8Iy0eEkbd@ep-nameless-hall-a8iljzhy-pooler.eastus2.azure.neon.tech/neondb?sslmode=require'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    ma.init_app(app)  # ✅ Inicializa Marshmallow aquí
    migrate = Migrate(app, db)

    # JWT
    app.config['JWT_SECRET_KEY'] = 'supersecretkey'
    jwt = JWTManager(app)

    # CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Swagger RESTX
    restx_api = RestXApi(app,
                         version='1.0',
                         title='Documentación de tu API',
                         description='Swagger generado con Flask-RESTX',
                         doc='/docs')

    # Registro de rutas
    restx_api.add_resource(VistaFormularioAccidente, '/accidentes', '/accidentes/<int:id>')
    restx_api.add_resource(VistaPersonal, '/personal', '/personal/<int:id>')
    restx_api.add_resource(VistaAmbulancias, '/ambulancias', '/ambulancias/<int:id>')
    restx_api.add_resource(VistaHospitales, '/hospitales', '/hospitales/<int:id>')
    restx_api.add_resource(VistaAsignacionAmbulancia, '/asignacion', '/asignacion/<int:id>')
    restx_api.add_resource(VistaReporteViajes, '/reportes', '/reportes/<int:id>')
    restx_api.add_resource(VistaSignin, '/signin')
    restx_api.add_resource(VistalogIn, '/login')

    @app.route('/')
    def index():
        return '🚑 Ambusos API está corriendo correctamente. Visita /docs para la documentación Swagger.'

    return app
