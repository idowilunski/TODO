"""
Task routes blueprint.
Handles all /api/tasks endpoints.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import threading

import logging
from app.services import TaskService
from app.services.llm_service import TaskClusteringService
from app.services.agent_service import AgentServiceFactory
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


@tasks_bp.route('/bulk-delete', methods=['DELETE'])
def bulk_delete_tasks():
    """Delete all tasks in one database query."""
    try:
        count = Task.query.delete()
        db.session.commit()
        
        logging.info(f"Bulk deleted {count} tasks")
        
        return jsonify({
            'status': 'success',
            'message': f'Deleted {count} tasks',
            'count': count
        }), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error bulk deleting tasks: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error deleting tasks: {str(e)}'
        }), 500


@tasks_bp.route('/seed', methods=['POST'])
def seed_tasks():
    """Generate mock tasks for testing clustering."""
    try:

        # If caller requests LLM-generated tasks, use the configured provider
        use_llm = request.args.get('source', '').lower() == 'llm'
        count = int(request.args.get('n', 20))  # Default to 20 tasks
        mock_tasks = []
        if use_llm:
            try:
                from app.services.llm_service import LLMServiceFactory
                provider = LLMServiceFactory.get_provider()
                generated = provider.generate_tasks(count)
                # generated is list of {title, description}
                mock_tasks = generated
            except Exception as e:
                import traceback
                logging.error(f"Error generating tasks with LLM: {e}")
                logging.error(traceback.format_exc())
                db.session.rollback()
                return jsonify({
                    'status': 'error',
                    'message': f'Error generating tasks with LLM: {str(e)}'
                }), 500
        else:
            # No LLM - return error (only LLM generation supported)
            return jsonify({
                'status': 'error',
                'message': 'Only LLM task generation is supported. Use ?source=llm'
            }), 400
            
            # Old hardcoded tasks removed - keeping structure for reference
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
        ]  # This block is now unreachable due to error return above
        
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
        # Log full exception with stack trace for debugging
        logging.exception("Error clustering tasks")
        # Return a concise message to the client; check server logs for details
        return jsonify({
            'status': 'error',
            'message': 'Error clustering tasks; see server logs for details.'
        }), 500


def _research_task_background(task_id: int, app):
    """Background worker to run agent research."""
    with app.app_context():
        try:
            task = Task.query.get(task_id)
            if not task:
                logging.error(f"Task {task_id} not found in background worker")
                return
            
            # Update status
            task.research_status = 'processing'
            db.session.commit()
            
            logging.info(f"[Background] Starting agent research for task {task_id}: {task.title}")
            
            # Run the agent
            agent = AgentServiceFactory.get_agent()
            result = agent.research_task(task.title, task.description)
            
            # Store result
            task.research_result = {
                'recommendation': result.get('recommendation'),
                'iterations': result.get('iterations'),
                'timestamp': datetime.utcnow().isoformat()
            }
            task.research_status = 'completed'
            db.session.commit()
            
            logging.info(f"[Background] Research completed for task {task_id}")
            
        except Exception as e:
            logging.exception(f"[Background] Error researching task {task_id}")
            try:
                task = Task.query.get(task_id)
                if task:
                    task.research_status = 'failed'
                    task.research_result = {
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    db.session.commit()
            except:
                pass


@tasks_bp.route('/<int:task_id>/research', methods=['POST'])
def research_task(task_id):
    """
    Start async agent research on a task.
    Returns immediately with status='pending'.
    Client should poll GET /tasks/{id} to check research_status.
    
    Returns: {
        status: 'success',
        message: 'Research started',
        data: task with research_status='pending'
    }
    """
    try:
        # Get the task
        task = Task.query.get(task_id)
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404
        
        # Check if already processing
        if task.research_status == 'processing':
            return jsonify({
                'status': 'info',
                'message': 'Research already in progress',
                'data': task.to_dict()
            }), 200
        
        # Mark as pending
        task.research_status = 'pending'
        task.research_result = None  # Clear old results
        db.session.commit()
        
        logging.info(f"Starting background research for task {task_id}: {task.title}")
        
        # Start background thread
        from flask import current_app
        thread = threading.Thread(
            target=_research_task_background,
            args=(task_id, current_app._get_current_object())
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Research started',
            'data': task.to_dict()
        }), 202  # 202 Accepted
    
    except Exception as e:
        logging.exception(f"Error starting research for task {task_id}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to start research: {str(e)}'
        }), 500
