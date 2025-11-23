"""
Application entry point.
Run this file to start the Flask development server.
"""
import os
from app import create_app
from dotenv import load_dotenv

# Load local .env file into environment variables for development convenience.
# Ensure `apps/server/.env` is gitignored so secrets are not committed.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Get config from environment variable, default to development
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5001
    )
