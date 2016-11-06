import os


class ApplicationConfig:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    #SQLALCHEMY_ECHO=True #print SQL Query to Console
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get('FLASK_DEBUG', False)
    SECRET_KEY = 'qi8H8R7OM4xMUNMPuRAZxlY'
    AUTH_EXPIRY = 30 #Time in minutes
