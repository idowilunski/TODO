"""
Application factory.
Creates and configures Flask app instance.
"""
from flask import Flask
from app.config import config
from app.extensions import db, cors
from app.routes import register_blueprints

def create_app(config_name='development'):
    """
    Application factory function.

    Args:
        config_name: Configuration name (development, testing, production)

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, resources=app.config['CORS_RESOURCES'])

    # Register blueprints
    register_blueprints(app)

    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

    return app
