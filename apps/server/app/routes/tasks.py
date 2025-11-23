"""
Task routes blueprint.
Handles all /api/tasks endpoints.
"""
from flask import Blueprint, jsonify, request
from app.services import TaskService
from app.services.llm_service import TaskClusteringService
from app.models import Task
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


@tasks_bp.route('/seed', methods=['POST'])
def seed_tasks():
    """Generate mock tasks for testing clustering."""
    try:
        # Delete existing tasks (optional)
        Task.query.delete()
        db.session.commit()
        
        mock_tasks = [
            # Work tasks
            {"title": "Fix login bug", "description": "Users can't reset password"},
            {"title": "Code review PR #42", "description": "Review backend changes"},
            {"title": "Write API docs", "description": "Document new endpoints"},
            {"title": "Update dependencies", "description": "npm update all packages"},
            {"title": "Deploy to staging", "description": "Test build on staging server"},
            {"title": "Attend standup", "description": "Daily team standup 10am"},
            {"title": "Refactor auth module", "description": "Split into smaller functions"},
            {"title": "Write unit tests", "description": "Tests for user service"},
            {"title": "Set up CI/CD", "description": "Configure GitHub Actions"},
            {"title": "Review security audit", "description": "Check penetration test results"},
            
            # Home tasks
            {"title": "Buy groceries", "description": "Milk, eggs, bread, chicken"},
            {"title": "Clean kitchen", "description": "Wash dishes, wipe counters"},
            {"title": "Fix bathroom sink", "description": "Unclog drain"},
            {"title": "Water plants", "description": "All indoor plants need water"},
            {"title": "Vacuum living room", "description": "Carpet is dirty"},
            {"title": "Do laundry", "description": "Whites and darks"},
            {"title": "Pay electricity bill", "description": "Due by 30th"},
            {"title": "Call plumber", "description": "Schedule for next week"},
            {"title": "Organize garage", "description": "Sort tools and boxes"},
            {"title": "Paint bedroom", "description": "Light blue color"},
            
            # Shopping tasks
            {"title": "Buy winter coat", "description": "Navy blue, size M"},
            {"title": "Get new shoes", "description": "Running shoes for gym"},
            {"title": "Buy birthday gift", "description": "For Sarah's party next weekend"},
            {"title": "Order laptop stand", "description": "Adjustable, under $50"},
            {"title": "Shop for headphones", "description": "Wireless, noise-cancelling"},
            {"title": "Get coffee machine", "description": "French press or espresso"},
            {"title": "Buy desk lamp", "description": "LED, adjustable brightness"},
            
            # Health/Gym
            {"title": "Go to gym", "description": "Chest and triceps day"},
            {"title": "Schedule dentist", "description": "For teeth cleaning"},
            {"title": "Refill prescriptions", "description": "Pick up from pharmacy"},
            {"title": "Buy vitamins", "description": "Vitamin D and B12"},
            {"title": "Yoga class", "description": "Monday 7pm session"},
            {"title": "Book massage", "description": "Deep tissue massage"},
            
            # Personal projects
            {"title": "Learn Python", "description": "Complete Udemy course"},
            {"title": "Read book", "description": "Finish 'Atomic Habits'"},
            {"title": "Practice guitar", "description": "30 min practice session"},
            {"title": "Plan vacation", "description": "Flights and hotels for Aug"},
            {"title": "Build portfolio site", "description": "Showcase projects"},
            {"title": "Take photos", "description": "For LinkedIn profile"},
            
            # Finance
            {"title": "Review budget", "description": "Check spending this month"},
            {"title": "Invest in index fund", "description": "Monthly $500 contribution"},
            {"title": "File taxes", "description": "Gather receipts and documents"},
            {"title": "Cancel unused subscription", "description": "Netflix family plan"},
            {"title": "Compare insurance", "description": "Get quotes for auto"},
            
            # Social
            {"title": "Call mom", "description": "Weekly catch-up"},
            {"title": "Plan dinner with friends", "description": "Saturday 7pm Italian place"},
            {"title": "Send thank you cards", "description": "Wedding guests"},
            {"title": "RSVP to birthday", "description": "John's party on 15th"},
            {"title": "Organize team outing", "description": "Book hiking trip"},
        ]
        
        # Add more to reach ~70
        for i in range(25):
            mock_tasks.append({
                "title": f"Task {i+1}",
                "description": f"Sample task #{i+1} for testing"
            })
        
        # Create and commit tasks
        for task_data in mock_tasks:
            task = Task(
                title=task_data["title"],
                description=task_data["description"],
                completed=False
            )
            db.session.add(task)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Created {len(mock_tasks)} mock tasks',
            'count': len(mock_tasks)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error seeding tasks: {str(e)}'
        }), 500


@tasks_bp.route('/cluster', methods=['POST'])
def cluster_tasks():
    """
    Cluster tasks using LLM.
    Returns: { "clusters": { "Work": [...tasks], "Home": [...tasks] } }
    """
    try:
        # Get all tasks
        tasks = Task.query.all()
        
        if not tasks:
            return jsonify({
                'status': 'error',
                'message': 'No tasks to cluster'
            }), 400
        
        # Use LLM service to cluster
        clusters = TaskClusteringService.cluster_tasks(tasks)
        
        return jsonify({
            'status': 'success',
            'clusters': clusters
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error clustering tasks: {str(e)}'
        }), 500
