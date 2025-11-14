"""
Task routes blueprint.
Handles all /api/tasks endpoints.
"""
from flask import Blueprint, jsonify, request
from app.services import TaskService
from app.extensions import db

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@tasks_bp.route('', methods=['GET'])
def get_tasks():
    """Get all tasks."""
    try:
        tasks = TaskService.get_all_tasks()
        return jsonify({
            'status': 'success',
            'data': [task.to_dict() for task in tasks]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving tasks: {str(e)}'
        }), 500

@tasks_bp.route('', methods=['POST'])
def create_task():
    """Create a new task."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        # Service handles validation and creation
        task = TaskService.create_task(
            title=data.get('title', ''),
            description=data.get('description', '')
        )

        return jsonify({
            'status': 'success',
            'message': 'Task created successfully',
            'data': task.to_dict()
        }), 201

    except ValueError as e:
        # Validation errors from service
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error creating task: {str(e)}'
        }), 500

@tasks_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task."""
    try:
        task = TaskService.get_task_by_id(task_id)
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404

        return jsonify({
            'status': 'success',
            'data': task.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving task: {str(e)}'
        }), 500

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        task = TaskService.update_task(task_id, data)
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404

        return jsonify({
            'status': 'success',
            'message': 'Task updated successfully',
            'data': task.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error updating task: {str(e)}'
        }), 500

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    try:
        success = TaskService.delete_task(task_id)
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404

        return jsonify({
            'status': 'success',
            'message': 'Task deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error deleting task: {str(e)}'
        }), 500
