from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Task {self.id}: {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/hello")
def api_hello():
    return jsonify({
        "message": "Hello from the backend!",
        "status": "success"
    })

@app.route("/api/tasks", methods=['POST'])
def create_task():
    try:
        # Get JSON data from request
        data = request.get_json()

        # Validate that data exists
        if not data:
            return jsonify({
                "message": "No data provided",
                "status": "error"
            }), 400

        # Extract and validate required fields
        title = data.get('title')
        description = data.get('description')

        if not title:
            return jsonify({
                "message": "Title is required",
                "status": "error"
            }), 400

        if not description:
            return jsonify({
                "message": "Description is required",
                "status": "error"
            }), 400

        # Create new task
        new_task = Task(title=title, description=description)

        # Add to database and commit
        db.session.add(new_task)
        db.session.commit()

        # Log the saved task
        print(f"Saved task - ID: {new_task.id}, Title: {new_task.title}")

        # Return success response with created task data
        return jsonify({
            "message": "Task created successfully",
            "status": "success",
            "data": new_task.to_dict()
        }), 201

    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        return jsonify({
            "message": f"Error creating task: {str(e)}",
            "status": "error"
        }), 500



if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

    app.run(debug=True, host='0.0.0.0', port=5001)
