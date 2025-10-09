"""
Simple Flask app for debugging Render deployment issues
This minimal app will help identify what's happening with route registration
"""

from flask import Flask, jsonify, request
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Debug deployment working',
        'timestamp': datetime.now().isoformat(),
        'environment': dict(os.environ),
        'request_info': {
            'method': request.method,
            'path': request.path,
            'url': request.url,
            'base_url': request.base_url
        }
    })

@app.route('/debug')
def debug():
    """Debug endpoint to check what routes are registered"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'rule': str(rule.rule),
            'endpoint': rule.endpoint,
            'methods': list(rule.methods)
        })
    
    return jsonify({
        'total_routes': len(routes),
        'routes': routes,
        'app_info': {
            'name': app.name,
            'debug': app.debug,
            'environment': app.config.get('ENV', 'production')
        }
    })

@app.route('/test-login')
def test_login():
    """Test login route to see if this works"""
    return jsonify({
        'message': 'Test login route working',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)