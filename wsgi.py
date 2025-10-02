#!/usr/bin/env python3
"""
Production WSGI server configuration for Python Trivia Game
"""
import os
from app import app

# Initialize database for production if needed
def create_tables():
    """Initialize database tables on first deployment"""
    with app.app_context():
        try:
            from models import db
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Database initialization warning: {e}")

# Create tables on import for production
if os.environ.get('FLASK_ENV') == 'production':
    create_tables()

# For gunicorn: this exposes the Flask app
if __name__ == "__main__":
    # Only for local testing - gunicorn doesn't use this
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)