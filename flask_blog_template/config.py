from datetime import timedelta

# configuration goes here
class Config:
    # Your regular (production) database URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'vX6kUc4Z7pR4cL8aC3kZ7pR8vN2dP6xZ'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    OPENAI_API_KEY = ''

class TestConfig(Config):
    # Your testing database URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SECRET_KEY = ''