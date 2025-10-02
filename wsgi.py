#!/usr/bin/env python3
"""
Production WSGI server configuration for Python Trivia Game
"""
import os
from app import app

# For gunicorn: this exposes the Flask app
if __name__ == "__main__":
    # Only for local testing - gunicorn doesn't use this
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)