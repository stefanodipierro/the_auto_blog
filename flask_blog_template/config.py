# configuration goes here
class Config:
    # Your regular (production) database URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig(Config):
    # Your testing database URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
