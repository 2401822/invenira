from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.observer import Observable, Logger
import os

# Instâncias globais
db = SQLAlchemy()
migrate = Migrate()
observable = Observable()

class SingletonApp:
    """Singleton para criar uma única instância do app Flask."""
    _instance = None

    @staticmethod
    def get_instance():
        if SingletonApp._instance is None:
            app = Flask(__name__)
            BASE_DIR = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'invenira.db')}"
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            app.config['SECRET_KEY'] = 'sua-chave-secreta'

            db.init_app(app)
            migrate.init_app(app, db)

            # Registrar activity_provider
            from app.activity_provider import activity_provider
            app.register_blueprint(activity_provider, url_prefix='/api')

            # Registrar Observer
            logger = Logger()
            observable.add_observer(logger)

            # Registrar rotas
            from app.routes import register_routes
            register_routes(app)

            SingletonApp._instance = app
        return SingletonApp._instance
