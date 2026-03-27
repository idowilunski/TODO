"""
Task model definition.
"""
from datetime import datetime
from app.extensions import db

class Task(db.Model):
    """Task model for todo items."""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    research_result = db.Column(db.JSON, nullable=True)  # Stores agent research: {recommendation, iterations, timestamp}
    research_status = db.Column(db.String(20), default='none', nullable=False)  # none | pending | processing | completed | failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}: {self.title}>'

    def to_dict(self):
        """Serialize task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'research_result': self.research_result,
            'research_status': self.research_status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
