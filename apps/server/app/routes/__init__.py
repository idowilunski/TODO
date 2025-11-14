"""
Routes package.
Registers all blueprints with the Flask app.
"""
from app.routes.main import main_bp
from app.routes.tasks import tasks_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp)
