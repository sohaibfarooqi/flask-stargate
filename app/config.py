import os


class ApplicationConfig:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_ECHO=False #print SQL Query to Console
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_MAX_OVERFLOW = 5
    DEBUG = os.environ.get('FLASK_DEBUG', False)
    SECRET_KEY = 'qi8H8R7OM4xMUNMPuRAZxlY'
    TOKEN_EXPIRATION = 30 #Time in minutes
    SERVER_NAME = 'localhost:5000'
