"""
Flask application for Python Trivia Flip Card Game

This module implements a complete trivia game application with:
- Interactive flip card gameplay
- User authentication and session management  
- Database persistence for questions, users, and scores
- RESTful API endpoints for game operations
- Responsive web interface

PEP 20 Principles Applied:
- Beautiful is better than ugly: Clean, organized code structure
- Explicit is better than implicit: Clear function signatures and return types
- Simple is better than complex: Modular design with clear separation of concerns
- Readability counts: Comprehensive docstrings and meaningful variable names
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
from typing import Dict, List, Optional, Tuple, Union, Any
import os
from datetime import datetime, timezone

# Import both old and new models for compatibility
from models import db, User, Question, GameSession, Answer, Score, Category, Difficulty, UserBackup
from config import DevelopmentConfig, ProductionConfig, TestingConfig
from db_service import (
    QuestionService, GameSessionService, AnswerService, 
    ScoreService, UserService, DatabaseSeeder
)
from user_persistence import smart_database_init, user_data_manager

# Performance optimization imports
from cache_manager import (
    cached_questions, cached_leaderboard, 
    invalidate_leaderboard_cache, get_cache_stats
)
from smart_question_selector import get_smart_questions
from rate_limiter import (
    api_rate_limit, game_rate_limit, user_rate_limit, 
    create_rate_limit_routes
)
from scripts.database_connection_monitor import create_pool_monitoring_routes

try:
    from flask_login import LoginManager, login_user, logout_user, login_required, current_user
    HAS_LOGIN = True
except ImportError:
    HAS_LOGIN = False
    print("Flask-Login not available, authentication disabled")

# Create Flask app
app = Flask(__name__)

# Configuration
env = os.getenv('FLASK_ENV', 'development')
if env == 'production':
    app.config.from_object(ProductionConfig)
elif env == 'testing':
    app.config.from_object(TestingConfig)
else:
    app.config.from_object(DevelopmentConfig)

# Initialize extensions
db.init_app(app)

# Initialize performance monitoring routes
create_rate_limit_routes(app)
create_pool_monitoring_routes(app)

# Initialize Flask-Login if available
if HAS_LOGIN:
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

# Initialize services
question_service = QuestionService()
game_session_service = GameSessionService()
answer_service = AnswerService()
score_service = ScoreService()
user_service = UserService()
database_seeder = DatabaseSeeder()

def initialize_database():
    """Initialize database with smart migration support"""
    try:
        with app.app_context():
            smart_database_init(app, db)
            print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise


# MAIN ROUTES

@app.route('/')
@api_rate_limit
def index():
    """Main landing page with game interface"""
    return render_template('index.html')

@app.route('/game')
@api_rate_limit 
def game():
    """Interactive trivia game page"""
    return render_template('game.html')

@app.route('/leaderboard')
@api_rate_limit
def leaderboard():
    """Leaderboard display page"""
    return render_template('leaderboard.html')

# API ENDPOINTS

@app.route('/api/questions')
@api_rate_limit
@cached_questions()
def get_questions():
    """Get trivia questions with smart selection and caching"""
    try:
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        count = int(request.args.get('count', 20))
        
        # Get user ID if authenticated
        user_id = None
        if HAS_LOGIN and current_user.is_authenticated:
            user_id = current_user.id
        
        # Use smart question selector for better user experience
        questions = get_smart_questions(
            user_id=user_id,
            categories=[Category(category)] if category else None,
            difficulty=Difficulty(difficulty) if difficulty else None,
            count=count
        )
        
        if not questions:
            return jsonify({'error': 'No questions found'}), 404
        
        questions_data = [{
            'id': q.id,
            'question': q.question_text,
            'options': [q.option_a, q.option_b, q.option_c, q.option_d],
            'correct_answer': q.correct_option,
            'category': q.category.value if q.category else None,
            'difficulty': q.difficulty.value if q.difficulty else None,
            'explanation': q.explanation
        } for q in questions]
        
        return jsonify({
            'questions': questions_data,
            'count': len(questions_data),
            'smart_selection': user_id is not None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit-answer', methods=['POST'])
@game_rate_limit
def submit_answer():
    """Submit answer and get immediate feedback with performance tracking"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        selected_option = data.get('selected_option')
        session_id = data.get('session_id')
        
        if not all([question_id, selected_option]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get question
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        # Check if answer is correct
        is_correct = selected_option == question.correct_option
        
        # Save answer to database
        user_id = None
        if HAS_LOGIN and current_user.is_authenticated:
            user_id = current_user.id
        
        answer = Answer(
            question_id=question_id,
            user_id=user_id,
            session_id=session_id,
            selected_option=selected_option,
            is_correct=is_correct,
            answered_at=datetime.utcnow()
        )
        
        db.session.add(answer)
        db.session.commit()
        
        # Invalidate leaderboard cache on score changes
        if is_correct:
            invalidate_leaderboard_cache()
        
        return jsonify({
            'correct': is_correct,
            'correct_answer': question.correct_option,
            'explanation': question.explanation,
            'question_id': question_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leaderboard')
@api_rate_limit
@cached_leaderboard()
def get_leaderboard():
    """Get leaderboard with caching for performance"""
    try:
        category = request.args.get('category')
        limit = int(request.args.get('limit', 10))
        
        # Get top scores
        scores = score_service.get_top_scores(category=category, limit=limit)
        
        leaderboard_data = [{
            'username': score.user.username if score.user else 'Anonymous',
            'score': score.total_score,
            'games_played': score.games_played,
            'average_score': round(score.total_score / max(1, score.games_played), 1),
            'category': category or 'All Categories'
        } for score in scores]
        
        return jsonify({
            'leaderboard': leaderboard_data,
            'category': category or 'all',
            'cached': True  # Indicates this was served from cache
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# AUTHENTICATION ROUTES

@app.route('/api/login', methods=['POST'])
@user_rate_limit
def login():
    """User login with bulletproof persistence"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Special handling for code_monkey user - auto-create if not exists
        if username == 'code_monkey':
            user = User.query.filter_by(username=username).first()
            if not user:
                # Auto-create the code_monkey user
                user = User(
                    username=username,
                    email=f"{username}@example.com"
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                print(f"Auto-created user: {username}")
        
        # Regular authentication flow
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if HAS_LOGIN:
                login_user(user)
            
            session['user_id'] = user.id
            session['username'] = user.username
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 400
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/register', methods=['POST'])
@user_rate_limit
def register():
    """User registration with performance tracking"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'All fields required'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ADMIN ROUTES

@app.route('/api/admin/cache-stats')
@api_rate_limit
def cache_stats():
    """Get cache performance statistics"""
    if not app.debug:
        return jsonify({'error': 'Access denied'}), 403
    
    stats = get_cache_stats()
    return jsonify(stats)

# ERROR HANDLERS

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({'error': 'Rate limit exceeded'}), 429

# SERVICE WORKER ROUTE
@app.route('/sw.js')
def service_worker():
    """Serve service worker with correct headers"""
    try:
        with open(os.path.join(app.static_folder, 'sw.js'), 'r') as f:
            content = f.read()
        
        response = Response(content, mimetype='application/javascript')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except FileNotFoundError:
        return "Service worker not found", 404

if __name__ == '__main__':
    # Initialize database on startup
    initialize_database()
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )