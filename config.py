from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()  # prende le variabili d'ambiente dal file .env

# configuration goes here
class Config:

    # Your regular (production) database URI
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///posts.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key') # Use a safe default for development
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    AUTHORIZATION = os.getenv('AUTHORIZATION')
    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
    YOUR_REDIRECT_URI = os.getenv('YOUR_REDIRECT_URI')
    FB_PAGE_ID = os.getenv('FB_PAGE_ID')
	# Imposta l'URL preferito su HTTPS
    PREFERRED_URL_SCHEME = 'https'

    # regis
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')


class TestConfig(Config):
    # Your testing database URI
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db')
    SECRET_KEY = os.getenv('TEST_SECRET_KEY', 'default_test_secret_key') # Use a safe default for testing
    OPENAI_API_KEY = os.getenv('TEST_OPENAI_API_KEY', '')
