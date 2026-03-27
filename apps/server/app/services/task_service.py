"""
Task service - business logic for task operations.
"""
from typing import List, Optional, Dict, Any
from app.models import Task
from app.extensions import db

class TaskService:
    """Service class for task-related business logic."""

    @staticmethod
    def create_task(title: str, description: str) -> Task:
        """
        Create a new task.

        Args:
            title: Task title
            description: Task description

        Returns:
            Created Task object

        Raises:
            ValueError: If validation fails
        """
        if not title or not title.strip():
            raise ValueError("Title is required")

        if not description or not description.strip():
            raise ValueError("Description is required")

        task = Task(
            title=title.strip(),
            description=description.strip()
        )

        db.session.add(task)
        db.session.commit()

        return task

    @staticmethod
    def get_all_tasks() -> List[Task]:
        """Get all tasks."""
        return Task.query.order_by(Task.created_at.desc()).all()

    @staticmethod
    def get_task_by_id(task_id: int) -> Optional[Task]:
        """Get a specific task by ID."""
        return Task.query.get(task_id)

    @staticmethod
    def update_task(task_id: int, data: Dict[str, Any]) -> Optional[Task]:
        """
        Update a task.

        Args:
            task_id: ID of task to update
            data: Dictionary with fields to update

        Returns:
            Updated Task object or None if not found
        """
        task = Task.query.get(task_id)
        if not task:
            return None

        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'completed' in data:
            task.completed = data['completed']

        db.session.commit()
        return task

    @staticmethod
    def delete_task(task_id: int) -> bool:
        """
        Delete a task.

        Args:
            task_id: ID of task to delete

        Returns:
            True if deleted, False if not found
        """
        task = Task.query.get(task_id)
        if not task:
            return False

        db.session.delete(task)
        db.session.commit()
        return True
