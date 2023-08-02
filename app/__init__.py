from flask import Flask
from flask_login import LoginManager
from config import Config, TestConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from celery import Celery

db = SQLAlchemy()
login_manager = LoginManager()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)

def make_celery(app):
    celery.config_from_object(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    
    celery.Task = ContextTask
    return celery

def create_app():
    app = Flask(__name__)
    config_name = os.getenv('FLASK_CONFIG', 'Config')
    if config_name == 'TestConfig':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)
    make_celery(app)  # This will configure celery to use Flask's context

    with app.app_context():
        from .main import models, auth
        db.create_all()

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
