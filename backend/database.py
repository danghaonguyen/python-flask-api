from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate


db = SQLAlchemy()
migrate = Migrate()

