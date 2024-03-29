from flask import Flask
from flask_login import LoginManager
from config import Config, TestConfig
from flask_sqlalchemy import SQLAlchemy
from flask_executor import Executor  # Import Executor
from flask_migrate import Migrate
import os




db = SQLAlchemy()
login_manager = LoginManager()  # Initialize login_manager here
executor = Executor()  # Initialize executor here




def create_app():

    
    app = Flask(__name__)
    config_name = os.getenv('FLASK_CONFIG', 'Config')  # use 'Config' as the default config name
    if config_name == 'TestConfig':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)  # Add this line to initialize login_manager with the app
    executor.init_app(app)  # Add this line to initialize executor with the app
    migrate = Migrate(app, db)



    with app.app_context():
        from .main import models, auth    # import here
        db.create_all()

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    return app