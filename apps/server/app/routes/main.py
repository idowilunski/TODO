"""
Main routes blueprint.
Handles general endpoints like health checks.
"""
from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Server is running'
    }), 200
