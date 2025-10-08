"""
WSGI entry point for Render deployment
This ensures Render uses the correct Flask app with all routes
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the main Flask application
from app import app

# Ensure all routes are registered
if __name__ != "__main__":
    # When imported by WSGI server, this will run
    print("🚀 WSGI: Importing Flask app with all routes...")
    
    # Debug: Print registered routes
    print(f"📋 WSGI: Total routes registered: {len(list(app.url_map.iter_rules()))}")
    for rule in list(app.url_map.iter_rules())[:10]:  # First 10 routes
        print(f"   - {rule.rule} -> {rule.endpoint}")

# WSGI application
application = app

# REMOVED: Direct execution to prevent conflicts with gunicorn
# if __name__ == "__main__":
#     # For direct execution
#     port = int(os.environ.get('PORT', 5000))
#     print(f"🚀 Direct execution: Starting on port {port}")
#     app.run(host='0.0.0.0', port=port)
