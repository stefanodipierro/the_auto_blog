from flask import Flask
from config import Config, TestConfig
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_class):
    app = Flask(__name__)
    if config_class == 'testing':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)
    
    db.init_app(app)

    with app.app_context():
        from .main import models  # import here
        db.create_all()

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
