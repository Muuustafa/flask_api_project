from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .utils import configure_swagger
from flask_jwt_extended import JWTManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder='../static')

    # Charger la configuration
    app.config.from_object('config.Config')
    
    # Configuration de JWT
    app.config['JWT_SECRET_KEY'] = 'votre_clé_secrète'
    jwt = JWTManager(app)


    # Initialiser l'extension SQLAlchemy avec l'application
    db.init_app(app)
    
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    # Initialiser l'extension Migrate avec l'application et la base de données
    Migrate(app, db)

    # Enregistrer les blueprints (routes API)
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Configurer Swagger
    configure_swagger(app)

    return app
