"""
Flask extensions initialization.
Extensions are initialized here without binding to app instance.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()
cors = CORS()
