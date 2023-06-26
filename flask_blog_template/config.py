from datetime import timedelta
import os

# configuration goes here
class Config:
    # Your regular (production) database URI
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///posts.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key') # Use a safe default for development
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    AUTHORIZATION = os.getenv('AUTHORIZATION')


class TestConfig(Config):
    # Your testing database URI
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db')
    SECRET_KEY = os.getenv('TEST_SECRET_KEY', 'default_test_secret_key') # Use a safe default for testing
    OPENAI_API_KEY = os.getenv('TEST_OPENAI_API_KEY', '')
