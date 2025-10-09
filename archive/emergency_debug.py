#!/usr/bin/env python3
"""
EMERGENCY DEBUG APP - Minimal Flask to diagnose Render deployment issues
"""

from flask import Flask, jsonify
import os
import sys
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'status': 'EMERGENCY DEBUG APP WORKING',
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'flask_version': getattr(app, '__version__', 'unknown')
    })

@app.route('/debug-deployment')
def debug_deployment():
    """Emergency debug endpoint"""
    try:
        import_status = {}
        
        # Test critical imports
        try:
            import flask
            import_status['flask'] = f"✅ {flask.__version__}"
        except Exception as e:
            import_status['flask'] = f"❌ {str(e)}"
            
        try:
            from datetime import datetime
            import_status['datetime'] = "✅ Working"
        except Exception as e:
            import_status['datetime'] = f"❌ {str(e)}"
            
        try:
            import json
            import_status['json'] = "✅ Working"
        except Exception as e:
            import_status['json'] = f"❌ {str(e)}"
        
        return jsonify({
            'status': 'Emergency debug working',
            'timestamp': datetime.now().isoformat(),
            'environment': {
                'PORT': os.environ.get('PORT', 'Not set'),
                'PYTHON_PATH': sys.path[:3],  # First 3 entries
                'WORKING_DIR': os.getcwd()
            },
            'imports': import_status,
            'message': 'If you can see this, basic Flask is working on Render'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'Debug endpoint failed'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 EMERGENCY DEBUG APP starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)