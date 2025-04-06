from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 1800
    }
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.blueprints.tasks.routes import tasks_bp
    app.register_blueprint(tasks_bp, url_prefix='/api')
    
    return app