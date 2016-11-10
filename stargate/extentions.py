from flask_migrate import Migrate
from .models import db

def configure_extensions(app):
    db.init_app(app)
    Migrate(app, db)