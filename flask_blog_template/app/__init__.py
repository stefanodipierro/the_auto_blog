from flask import Flask
from flask_login import LoginManager
from config import Config, TestConfig
from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()
login_manager = LoginManager()  # Initialize login_manager here

def create_app(config_class):
    app = Flask(__name__)
    if config_class == 'testing':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)  # Add this line to initialize login_manager with the app

    with app.app_context():
        from .main import models, auth    # import here
        db.create_all()

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    return app