"""
Python Trivia Flask Application

A minimal, clean Flask application for a Python trivia game featuring:
- User authentication with session management
- Interactive game interface
- Multiple difficulty levels and categories
- Score tracking and leaderboards

Author: Python Trivia Team
Version: 2.0.0-clean
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect

# Constants
DEFAULT_SECRET_KEY = 'dev-secret-key-change-in-production'
DEFAULT_PORT = 5000
DEFAULT_GAME_CARDS = 10

class TriviaApp:
    """Main application class for Python Trivia game."""
    
    def __init__(self):
        """Initialize the Flask application with configuration."""
        self.app = Flask(__name__)
        self._configure_app()
        self._register_routes()
        self._register_context_processors()
    
    def _configure_app(self):
        """Configure Flask application settings."""
        self.app.secret_key = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)
        
        # Environment-based configuration
        is_production = os.environ.get('FLASK_ENV') == 'production'
        self.app.config['DEBUG'] = not is_production
        
        if is_production and self.app.secret_key == DEFAULT_SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production environment")
    
    def _register_context_processors(self):
        """Register template context processors."""
        @self.app.context_processor
        def inject_user():
            """Inject current user into all template contexts."""
            return {'current_user': self._get_current_user()}
    
    def _get_current_user(self):
        """
        Get current user from session for template compatibility.
        
        Returns:
            dict: User object with username and authentication status, or None
        """
        username = session.get('user')
        if username:
            return {
                'username': username,
                'is_authenticated': True
            }
        return None
    
    def _validate_login_data(self, data):
        """
        Validate login request data.
        
        Args:
            data (dict): Request data containing username and password
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not data:
            return False, 'No data provided'
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username:
            return False, 'Username is required'
        if not password:
            return False, 'Password is required'
        if len(username) < 2:
            return False, 'Username must be at least 2 characters'
        if len(password) < 3:
            return False, 'Password must be at least 3 characters'
            
        return True, None
    
    def _register_routes(self):
        """Register all application routes."""
        
        @self.app.route('/')
        def index():
            """Main landing page."""
            return render_template('index.html')
        
        @self.app.route('/login', methods=['GET'])
        def login():
            """Display login page."""
            return render_template('login.html')
        
        @self.app.route('/api/login', methods=['POST'])
        def api_login():
            """
            Handle login API requests.
            
            Returns:
                JSON response with login result
            """
            try:
                data = request.get_json()
                is_valid, error_message = self._validate_login_data(data)
                
                if not is_valid:
                    return jsonify({'error': error_message}), 400
                
                username = data['username'].strip()
                # Note: In a real application, password validation would be performed here
                # For this minimal version, we accept any valid username/password combination
                
                session['user'] = username
                return jsonify({
                    'message': 'Login successful',
                    'user': username
                })
                
            except Exception as e:
                # Log error in production
                return jsonify({'error': 'Server error during login'}), 500
        
        @self.app.route('/logout')
        def logout():
            """Handle user logout."""
            session.pop('user', None)
            return redirect('/')
        
        @self.app.route('/game')
        def game():
            """Display game page with initial stats."""
            game_stats = {
                'current_index': 0,
                'total_cards': DEFAULT_GAME_CARDS,
                'score': 0,
                'percentage': 0
            }
            return render_template('game.html', game_stats=game_stats, current_card=None)
        
        @self.app.route('/categories')
        def categories():
            """Display categories page."""
            return render_template('categories.html')
        
        @self.app.route('/difficulty')
        def difficulty():
            """Display difficulty selection page."""
            return render_template('difficulty.html')
        
        @self.app.route('/leaderboard')
        def leaderboard():
            """Display leaderboard page."""
            return render_template('leaderboard.html')
        
        @self.app.route('/api/debug')
        def api_debug():
            """
            Debug endpoint for deployment verification.
            
            Returns:
                JSON with system information and available routes
            """
            routes = [str(rule.rule) for rule in self.app.url_map.iter_rules()]
            current_user = self._get_current_user()
            
            return jsonify({
                'message': 'Python Trivia App - Clean Version',
                'timestamp': datetime.now().isoformat(),
                'total_routes': len(routes),
                'routes': sorted(routes),
                'session_user': session.get('user'),
                'current_user': current_user,
                'deployment_info': {
                    'version': '2.0.0-clean',
                    'flask_debug': self.app.debug,
                    'flask_env': self.app.config.get('ENV', 'not-set')
                }
            })
        
        @self.app.route('/sw.js')
        def service_worker():
            """Serve service worker for PWA functionality."""
            return self.app.send_static_file('sw.js')
    
    def run(self, host='0.0.0.0', port=None, debug=None):
        """
        Run the Flask application.
        
        Args:
            host (str): Host address
            port (int): Port number
            debug (bool): Debug mode
        """
        if port is None:
            port = int(os.environ.get('PORT', DEFAULT_PORT))
        
        if debug is None:
            debug = self.app.config['DEBUG']
        
        print(f"🚀 Starting Python Trivia App v2.0.0-clean on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

# Create application instance
trivia_app = TriviaApp()
app = trivia_app.app  # For WSGI compatibility

if __name__ == '__main__':
    trivia_app.run()