"""
MINIMAL WORKING Flask application for deployment testing
This is a simplified version to get basic routes working on Render
"""

from flask import Flask, render_template, request, jsonify, session, redirect
import os
from datetime import datetime

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configure for production
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

# Helper function to create user object for templates
def get_current_user():
    """Get current user from session for template compatibility"""
    user = session.get('user')
    if user:
        return {
            'username': user,
            'is_authenticated': True
        }
    return None

# Add template context processor to make current_user available in all templates
@app.context_processor
def inject_user():
    return {'current_user': get_current_user()}

# Basic routes
@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Simple validation for minimal app
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # For minimal app, just accept any credentials
        # In production, this would check against database
        if len(username) > 0 and len(password) > 0:
            session['user'] = username
            return jsonify({
                'message': 'Login successful',
                'user': username
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Server error during login'}), 500

@app.route('/logout')
def logout():
    """Logout endpoint"""
    session.pop('user', None)
    return redirect('/')

@app.route('/game')
def game():
    """Game page with minimal stats"""
    game_stats = {
        'current_index': 0,
        'total_cards': 10,
        'score': 0,
        'percentage': 0
    }
    return render_template('game.html', game_stats=game_stats, current_card=None)

@app.route('/categories')
def categories():
    """Categories page"""
    return render_template('categories.html')

@app.route('/difficulty')
def difficulty():
    """Difficulty page"""
    return render_template('difficulty.html')

@app.route('/leaderboard')
def leaderboard():
    """Leaderboard page"""
    return render_template('leaderboard.html')

@app.route('/simple-debug')
def simple_debug():
    """Debug endpoint to check deployment"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(str(rule.rule))
    
    current_user = get_current_user()
    
    return jsonify({
        'message': 'MINIMAL APP WORKING on Render',
        'timestamp': datetime.now().isoformat(),
        'total_routes': len(routes),
        'routes': sorted(routes),
        'session_user': session.get('user'),
        'current_user': current_user,
        'deployment_info': {
            'version': 'minimal-v1.2-with-session-fix',
            'flask_debug': app.debug,
            'flask_env': app.config.get('ENV', 'not-set')
        }
    })

@app.route('/sw.js')
def service_worker():
    """Service worker"""
    return app.send_static_file('sw.js')

# Startup
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting minimal app on port {port}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )