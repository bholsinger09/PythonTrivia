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
from src.models import TriviaGame, TriviaQuestion
from models import db, User, Question, GameSession, Answer, Score, Category, Difficulty, UserBackup
from config import DevelopmentConfig, ProductionConfig, TestingConfig
from db_service import (
    QuestionService, GameSessionService, AnswerService, 
    ScoreService, UserService, DatabaseSeeder
)
from user_persistence import smart_database_init, user_data_manager
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

if HAS_LOGIN:
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
else:
    # Mock current_user for when Flask-Login is not available
    class MockUser:
        is_authenticated = False
        id = None
    current_user = MockUser()

# Global game instance (for backward compatibility)
game = TriviaGame()


def get_or_create_game_session() -> Optional[GameSession]:
    """
    Get or create a game session for the current user or anonymous session.
    
    This function implements session management for both authenticated and
    anonymous users, maintaining game state across requests.
    
    Returns:
        GameSession: Active game session for the current user/session
        None: If session creation fails
        
    PEP 20: "Explicit is better than implicit" - clear return type and behavior
    """
    try:
        session_token = session.get('game_session_token')
        game_session = None
        
        if session_token:
            game_session = GameSessionService.get_session_by_token(session_token)
        
        if not game_session:
            # Create new session
            user_id = current_user.id if HAS_LOGIN and current_user.is_authenticated else None
            game_session = GameSessionService.create_session(user_id=user_id)
            session['game_session_token'] = game_session.session_token
        
        return game_session
    except Exception as e:
        print(f"Error managing game session: {e}")
        return None


def load_questions_from_db(
    categories: Optional[List[Category]] = None,
    difficulty: Optional[Difficulty] = None,
    limit: int = 20
) -> List[TriviaQuestion]:
    """
    Load questions from database with optional filtering.
    
    Args:
        categories: List of categories to filter by (optional)
        difficulty: Difficulty level to filter by (optional)  
        limit: Maximum number of questions to return (default: 20)
        
    Returns:
        List[TriviaQuestion]: List of trivia questions from database
        
    Raises:
        RuntimeError: If no application context is available
        
    PEP 20: "Simple is better than complex" - focused single responsibility
    """
    try:
        # Ensure we're in app context
        if not app.app_context:
            raise RuntimeError("No application context")
            
        questions = QuestionService.get_questions_by_criteria(
            categories=categories,
            difficulty=difficulty,
            limit=limit
        )
        
        # Convert DB questions to TriviaQuestion objects for compatibility
        trivia_questions = []
        for q in questions:
            trivia_q = TriviaQuestion(
                question=q.question_text,
                answer=q.correct_answer,
                category=q.category,
                difficulty=q.difficulty,
                explanation=q.explanation or "",
                choices=q.get_choices(),
                correct_choice_index=q.correct_choice_index
            )
            trivia_questions.append(trivia_q)
        
        return trivia_questions
    except Exception as e:
        print(f"Error loading questions from DB: {e}")
        return load_sample_questions_fallback()


def load_sample_questions_fallback():
    """Load sample trivia questions into the game (fallback for when DB is not available)"""
    sample_questions = [
        TriviaQuestion(
            "What is the output of print(type([]))?",
            "<class 'list'>",
            Category.BASICS,
            Difficulty.EASY,
            "The type() function returns the type of an object. An empty list [] is of type 'list'.",
            choices=["<class 'list'>", "<class 'array'>"],
            correct_choice_index=0
        ),
        TriviaQuestion(
            "Which Python keyword is used to define a function?",
            "def",
            Category.FUNCTIONS,
            Difficulty.EASY,
            "The 'def' keyword is used to define functions in Python.",
            choices=["def", "function"],
            correct_choice_index=0
        ),
        TriviaQuestion(
            "What does PEP stand for in Python?",
            "Python Enhancement Proposal",
            Category.BASICS,
            Difficulty.MEDIUM,
            "PEP stands for Python Enhancement Proposal, which are design documents for Python.",
            choices=["Python Enhancement Proposal", "Python Executable Package"],
            correct_choice_index=0
        ),
        TriviaQuestion(
            "What is the difference between a list and a tuple in Python?",
            "Lists are mutable, tuples are immutable",
            Category.DATA_STRUCTURES,
            Difficulty.MEDIUM,
            "Lists can be modified after creation (mutable), while tuples cannot be changed (immutable).",
            choices=["Lists are mutable, tuples are immutable", "Lists are immutable, tuples are mutable"],
            correct_choice_index=0
        ),
        TriviaQuestion(
            "What is a decorator in Python?",
            "A function that modifies another function",
            Category.ADVANCED,
            Difficulty.HARD,
            "Decorators are a way to modify or enhance functions without permanently modifying their code.",
            choices=["A function that modifies another function", "A special type of class"],
            correct_choice_index=0
        ),
        TriviaQuestion(
            "What does the __init__ method do in a Python class?",
            "Initializes a new instance of the class",
            Category.OOP,
            Difficulty.MEDIUM,
            "The __init__ method is the constructor that initializes new objects when they are created.",
            choices=["Initializes a new instance of the class", "Destroys an instance of the class"],
            correct_choice_index=0
        ),
        TriviaQuestion(
            "Which library is commonly used for data analysis in Python?",
            "pandas",
            Category.LIBRARIES,
            Difficulty.EASY,
            "Pandas is the most popular library for data manipulation and analysis in Python.",
            choices=["pandas", "numpy"],
            correct_choice_index=0
        ),
        TriviaQuestion(
            "What is the Global Interpreter Lock (GIL) in Python?",
            "A mutex that prevents multiple threads from executing Python code simultaneously",
            Category.ADVANCED,
            Difficulty.HARD,
            "The GIL ensures that only one thread executes Python bytecode at a time, affecting multi-threading performance.",
            choices=["A mutex that prevents multiple threads from executing Python code simultaneously", "A feature that speeds up multi-threaded programs"],
            correct_choice_index=0
        )
    ]
    
    return sample_questions


def initialize_game_with_questions() -> None:
    """
    Initialize the global game instance with questions from database.
    
    Fallback to hardcoded questions if database unavailable.
    
    PEP 20: "Errors should never pass silently" - proper exception handling
    """
    try:
        # Try to load from database first
        questions = load_questions_from_db()
        for question in questions:
            game.add_question(question)
    except Exception as e:
        print(f"Failed to load from database, using fallback: {e}")
        # Fallback to hardcoded questions
        questions = load_sample_questions_fallback()
        for question in questions:
            game.add_question(question)
    
    game.shuffle_cards()


# Database initialization
def init_db() -> None:
    """
    Initialize database tables and seed data if needed.
    
    PEP 20: "Simple is better than complex" - focused initialization
    """
    try:
        with app.app_context():
            smart_database_init(preserve_users=True)
            
            # Check if we need to seed data
            if Question.query.count() == 0:
                print("Seeding database with initial data...")
                DatabaseSeeder.seed_sample_questions()

            # Log user persistence status
            user_count = User.query.count()
            if user_count > 0:
                print(f"Database initialized with {user_count} existing users preserved")
            else:
                print("Database initialized - no existing users found")                
    except Exception as e:
        print(f"Database initialization error: {e}")


# Initialize database when module is imported
def initialize_app():
    """Initialize the app with database and sample data"""
    with app.app_context():
        try:
            if app.config.get('SQLALCHEMY_DATABASE_URI'):
                init_db()
        except Exception as e:
            print(f"Failed to initialize database: {e}")
        
        # Initialize game with questions
        initialize_game_with_questions()


# PEP 20 Validation helpers following "Simple is better than complex"
def validate_username(username: str) -> Optional[str]:
    """
    Validate username according to application rules.
    
    Args:
        username: Username string to validate
        
    Returns:
        str: Error message if validation fails, None if valid
        
    PEP 20: "Simple is better than complex" - single responsibility validation
    """
    if not username or not username.strip():
        return 'Username is required'
    
    username = username.strip()
    if len(username) < 3 or len(username) > 20:
        return 'Username must be 3-20 characters'
    
    if not username.replace('_', '').isalnum():
        return 'Username can only contain letters, numbers, and underscores'
    
    return None


def validate_email(email: str) -> Optional[str]:
    """
    Validate email according to application rules.
    
    Args:
        email: Email string to validate
        
    Returns:
        str: Error message if validation fails, None if valid
        
    PEP 20: "Explicit is better than implicit" - clear validation logic
    """
    if not email or not email.strip():
        return 'Email is required'
    
    email = email.strip().lower()
    if '@' not in email or '.' not in email.split('@')[-1]:
        return 'Please enter a valid email address'
    
    return None


def validate_password(password: str) -> Optional[str]:
    """
    Validate password according to application rules.
    
    Args:
        password: Password string to validate
        
    Returns:
        str: Error message if validation fails, None if valid
        
    PEP 20: "Readability counts" - clear password validation
    """
    if not password:
        return 'Password is required'
    
    if len(password) < 6:
        return 'Password must be at least 6 characters'
    
    return None


def validate_password_confirmation(password: str, confirm_password: str) -> Optional[str]:
    """
    Validate password confirmation matches.
    
    Args:
        password: Original password
        confirm_password: Password confirmation
        
    Returns:
        str: Error message if passwords don't match, None if valid
    """
    if confirm_password and password != confirm_password:
        return 'Passwords do not match'
    
    return None


def check_user_exists(username: str, email: str) -> Optional[str]:
    """
    Check if user already exists in system.
    
    Args:
        username: Username to check
        email: Email to check
        
    Returns:
        str: Error message if user exists, None if available
        
    PEP 20: "Simple is better than complex" - focused existence check
    """
    if UserService.get_user_by_username(username):
        return 'Username already exists'
    
    if UserService.get_user_by_email(email):
        return 'Email already registered'
    
    return None


# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration with PEP 20 compliant validation.
    
    Following "Simple is better than complex" - uses helper functions for validation.
    Following "Explicit is better than implicit" - clear error handling.
    
    Returns:
        Response: JSON or HTML response based on request type
    """
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validate empty fields first
        if not all([username, email, password]):
            error = 'All fields required'
        else:
            # PEP 20: "Simple is better than complex" - use validation helpers
            # Check individual validations before checking existence
            error = (validate_username(username) or 
                    validate_email(email) or 
                    validate_password(password) or
                    check_user_exists(username, email) or
                    validate_password_confirmation(password, confirm_password))
        
        if error:
            if request.is_json:
                return jsonify({'success': False, 'message': error}), 400
            return render_template('register.html', error=error), 400
        
        # Create user
        try:
            user = UserService.create_user(username, email, password)
            if request.is_json:
                return jsonify({'success': True, 'message': 'Registration successful'})
            else:
                if HAS_LOGIN:
                    login_user(user)
                return redirect(url_for('game_page'))
        except Exception as e:
            app.logger.error(f"Registration error: {e}")
            if request.is_json:
                return jsonify({'success': False, 'message': 'Registration failed'}), 500
            return render_template('register.html', error='Registration failed'), 500
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login() -> Union[str, Response]:
    """
    User login with enhanced validation.
    
    Returns:
        Union[str, Response]: HTML template or JSON response
        
    PEP 20: "Explicit is better than implicit" - clear return types
    """
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Input validation
        if not username or not password:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Username and password required'}), 400
            return render_template('login.html', error='Username and password required'), 400
        
        if len(username) > 20 or len(password) > 255:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid username or password'}), 400
            return render_template('login.html', error='Invalid username or password'), 400
        
        try:
            user = UserService.get_user_by_username(username)
            
            if user and user.check_password(password):
                if HAS_LOGIN:
                    login_user(user)
                if request.is_json:
                    return jsonify({'success': True, 'message': 'Login successful'})
                else:
                    return redirect(url_for('game_page'))
            else:
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Invalid username or password'}), 400
                else:
                    return render_template('login.html', error='Invalid username or password'), 400
        except Exception as e:
            app.logger.error(f"Login error: {e}")
            if request.is_json:
                return jsonify({'success': False, 'message': 'Login failed'}), 500
            else:
                return render_template('login.html', error='Login failed'), 500
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    if HAS_LOGIN:
        logout_user()
    return redirect(url_for('index'))


@app.route('/leaderboard')
def leaderboard():
    """Display leaderboard"""
    try:
        scores = ScoreService.get_leaderboard(limit=20)
        return render_template('leaderboard.html', scores=scores)
    except Exception as e:
        print(f"Error loading leaderboard: {e}")
        return render_template('leaderboard.html', scores=[])


@app.route('/api/leaderboard')
def api_leaderboard():
    """API endpoint for leaderboard data"""
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    limit = int(request.args.get('limit', 10))
    
    try:
        # Convert string parameters to enums if provided
        category_enum = Category(category) if category else None
        difficulty_enum = Difficulty(difficulty) if difficulty else None
        
        scores = ScoreService.get_leaderboard(
            category=category_enum,
            difficulty=difficulty_enum,
            limit=limit
        )
        
        scores_data = []
        for score in scores:
            scores_data.append({
                'id': score.id,
                'username': score.user.username if score.user else score.anonymous_name,
                'score': score.score,
                'accuracy': score.accuracy_percentage,
                'questions_answered': score.questions_answered,
                'category': score.category.value if score.category else None,
                'difficulty': score.difficulty.value if score.difficulty else None,
                'achieved_at': score.achieved_at.isoformat()
            })
        
        return jsonify({'success': True, 'scores': scores_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/save-score', methods=['POST'])
def save_score():
    """Save game score to database"""
    data = request.get_json()
    
    try:
        # Get current game session
        game_session = get_or_create_game_session()
        
        # Calculate game statistics
        total_questions = len(game.cards)
        correct_answers = game.score
        accuracy = game.get_score_percentage()
        
        # Mark session as completed
        GameSessionService.complete_session(game_session.id)
        
        # Save score
        score_record = ScoreService.save_score(
            game_session_id=game_session.id,
            score=correct_answers * 10,  # Basic scoring: 10 points per correct answer
            accuracy_percentage=accuracy,
            questions_answered=total_questions,
            user_id=current_user.id if HAS_LOGIN and current_user.is_authenticated else None,
            anonymous_name=data.get('anonymous_name', 'Anonymous')
        )
        
        # Update user statistics if authenticated
        if HAS_LOGIN and current_user.is_authenticated:
            UserService.update_user_stats(current_user.id, game_session)
        
        return jsonify({
            'success': True,
            'score_id': score_record.id,
            'final_score': score_record.score,
            'accuracy': score_record.accuracy_percentage
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/profile')
def profile():
    """User profile page"""
    if not HAS_LOGIN or not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    try:
        # Get user's recent sessions and best scores
        recent_sessions = GameSessionService.get_user_sessions(current_user.id)
        best_scores = ScoreService.get_user_best_scores(current_user.id)
        
        return render_template('profile.html', 
                             user=current_user,
                             recent_sessions=recent_sessions,
                             best_scores=best_scores)
    except Exception as e:
        print(f"Error loading profile: {e}")
        return render_template('profile.html', user=current_user, 
                             recent_sessions=[], best_scores=[])


@app.route('/')
def index() -> str:
    """
    Home page route.
    
    Returns:
        str: Rendered HTML template
        
    PEP 20: "Simple is better than complex" - single responsibility
    """
    return render_template('index.html')


@app.route('/debug')
def debug_page():
    """Debug page to test question display"""
    return render_template('debug.html')


@app.route('/game')
def game_page() -> str:
    """
    Main game page route.
    
    Returns:
        str: Rendered HTML template
        
    PEP 20: "Beautiful is better than ugly" - clean route organization
    """
    if not game.cards:
        initialize_game_with_questions()
    
    current_card = game.get_current_card()
    return render_template('game.html', 
                         current_card=current_card,
                         game_stats={
                             'current_index': game.current_card_index,
                             'total_cards': len(game.cards),
                             'score': game.score,
                             'percentage': round(game.get_score_percentage(), 1)
                         })


@app.route('/api/current-card', methods=['GET', 'POST'])
def get_current_card():
    """API endpoint to get current card data"""
    if request.method == 'POST':
        # POST method not supported for this endpoint, return 400
        return jsonify({'error': 'POST method not supported for this endpoint'}), 400
    
    current_card = game.get_current_card()
    if current_card:
        return jsonify({
            'success': True,
            'card': current_card.to_dict(),
            'game_stats': {
                'current_index': game.current_card_index,
                'total_cards': len(game.cards),
                'score': game.score,
                'percentage': round(game.get_score_percentage(), 1)
            }
        })
    return jsonify({'success': False, 'message': 'No current card available'})


@app.route('/api/flip-card', methods=['POST'])
def flip_card():
    """API endpoint to flip the current card"""
    current_card = game.get_current_card()
    if current_card:
        current_card.flip_card()
        return jsonify({
            'success': True,
            'card': current_card.to_dict()
        })
    return jsonify({'success': False, 'message': 'No card to flip'})


@app.route('/api/answer-card', methods=['POST'])
def answer_card():
    """API endpoint to handle answer choice selection"""
    data = request.get_json()
    choice_index = data.get('choice_index')
    
    if choice_index is None:
        return jsonify({'success': False, 'message': 'No choice provided'})
    
    current_card = game.get_current_card()
    if not current_card:
        return jsonify({'success': False, 'message': 'No current card'})
    
    # Check if the selected choice is correct
    is_correct = choice_index == current_card.trivia_question.correct_choice_index
    
    # Mark the card as answered
    game.answer_current_card(is_correct)
    
    # Record in database if available
    try:
        game_session = get_or_create_game_session()
        
        # Find the corresponding question in the database
        question = Question.query.filter_by(
            question_text=current_card.trivia_question.question
        ).first()
        
        if question:
            # Record the answer
            AnswerService.record_answer(
                game_session_id=game_session.id,
                question_id=question.id,
                selected_choice_index=choice_index,
                is_correct=is_correct,
                user_id=current_user.id if HAS_LOGIN and current_user.is_authenticated else None
            )
            
            # Update session progress
            GameSessionService.update_session_progress(
                session_id=game_session.id,
                current_question_index=game.current_card_index,
                correct_answers=game.score,
                incorrect_answers=len([c for c in game.cards if c.is_answered_correctly is False]),
                total_score=game.score * 10  # Basic scoring
            )
    except Exception as e:
        print(f"Failed to record answer in database: {e}")
    
    # Get the correct answer text
    correct_answer = current_card.trivia_question.answer
    
    return jsonify({
        'success': True,
        'correct': is_correct,
        'correct_answer': correct_answer,
        'selected_choice': choice_index,
        'card': current_card.to_dict(),
        'game_stats': {
            'current_index': game.current_card_index,
            'total_cards': len(game.cards),
            'score': game.score,
            'percentage': round(game.get_score_percentage(), 1)
        }
    })


@app.route('/api/next-card', methods=['POST'])
def next_card():
    """API endpoint to move to next card"""
    next_card = game.next_card()
    if next_card:
        return jsonify({
            'success': True,
            'card': next_card.to_dict(),
            'game_stats': {
                'current_index': game.current_card_index,
                'total_cards': len(game.cards),
                'score': game.score,
                'percentage': round(game.get_score_percentage(), 1)
            }
        })
    return jsonify({'success': False, 'message': 'No more cards available'})


@app.route('/api/previous-card', methods=['POST'])
def previous_card():
    """API endpoint to move to previous card"""
    prev_card = game.previous_card()
    if prev_card:
        return jsonify({
            'success': True,
            'card': prev_card.to_dict(),
            'game_stats': {
                'current_index': game.current_card_index,
                'total_cards': len(game.cards),
                'score': game.score,
                'percentage': round(game.get_score_percentage(), 1)
            }
        })
    return jsonify({'success': False, 'message': 'No previous card available'})


@app.route('/api/reset-game', methods=['POST'])
def reset_game():
    """API endpoint to reset the game"""
    game.reset_game()
    game.shuffle_cards()
    current_card = game.get_current_card()
    
    return jsonify({
        'success': True,
        'card': current_card.to_dict() if current_card else None,
        'game_stats': {
            'current_index': game.current_card_index,
            'total_cards': len(game.cards),
            'score': game.score,
            'percentage': round(game.get_score_percentage(), 1)
        }
    })


@app.route('/api/game-stats')
def get_game_stats():
    """API endpoint to get current game statistics"""
    return jsonify({
        'current_index': game.current_card_index,
        'total_cards': len(game.cards),
        'score': game.score,
        'percentage': round(game.get_score_percentage(), 1),
        'answered_cards': sum(1 for card in game.cards if card.is_answered_correctly is not None)
    })


@app.route('/categories')
def categories():
    """Categories filter page"""
    categories_data = {}
    for category in Category:
        category_cards = game.filter_by_category(category)
        categories_data[category.value] = {
            'name': category.value.replace('_', ' ').title(),
            'count': len(category_cards)
        }
    return render_template('categories.html', categories=categories_data)


@app.route('/difficulty')
def difficulty():
    """Difficulty filter page"""
    difficulty_data = {}
    for diff in Difficulty:
        diff_cards = game.filter_by_difficulty(diff)
        difficulty_data[diff.value] = {
            'name': diff.value.title(),
            'count': len(diff_cards)
        }
    return render_template('difficulty.html', difficulties=difficulty_data)


@app.route('/api/start-game', methods=['GET', 'POST'])
def start_game_api():
    """
    API endpoint to start a new game with optional filters
    
    Returns:
        JSON: Game token and success status
        
    GET: Start game with all questions
    POST: Start game with category/difficulty filters
    """
    try:
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            categories_filter = data.get('categories', [])
            difficulty_filter = data.get('difficulty')
            
            # Validate categories
            if categories_filter:
                valid_categories = [cat.value for cat in Category]
                for cat in categories_filter:
                    if cat.upper() not in [c.upper() for c in valid_categories]:
                        return jsonify({'error': f'Invalid category: {cat}'}), 400
            
            # Validate difficulty
            if difficulty_filter:
                valid_difficulties = [diff.value for diff in Difficulty]
                if difficulty_filter.lower() not in [d.lower() for d in valid_difficulties]:
                    return jsonify({'error': f'Invalid difficulty: {difficulty_filter}'}), 400
        
        # Get or create game session
        game_session = get_or_create_game_session()
        if not game_session:
            return jsonify({'error': 'Failed to create game session'}), 500
        
        # Return the game token
        return jsonify({
            'game_token': game_session.session_token,
            'success': True
        }), 200
        
    except Exception as e:
        app.logger.error(f"Start game API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/sw.js')
def service_worker():
    """Serve the service worker from root path"""
    return app.send_static_file('sw.js')


@app.route('/manifest.json')
def manifest():
    """Serve the PWA manifest"""
    return app.send_static_file('manifest.json')


if __name__ == '__main__':
    # Initialize app when run directly
    initialize_app()
    
    # Use PORT from environment (Render provides this) or default to 5001
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)

def backup_user_data() -> bool:
    """Manually backup user data"""
    with app.app_context():
        return user_data_manager.backup_users()


def restore_user_data() -> bool:
    """Manually restore user data"""
    with app.app_context():
        return user_data_manager.restore_users()
@app.route('/admin/database-status')
def admin_database_status():
    """
    Simple admin endpoint to check database status in production
    Shows users and backup information
    """
    try:
        # Get current users
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat(),
                'games_played': user.total_games_played,
                'points': user.total_points
            })
        
        # Get backup status
        from user_persistence import get_user_backup_status
        backup_status = get_user_backup_status()
        
        # Get all backups
        all_backups = user_data_manager.list_backups()
        
        return f"""
        <html>
        <head>
            <title>Database Status - Python Trivia</title>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; padding: 20px; background: #f5f7fa; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .status {{ background: #e7f5e7; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .user {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #007bff; }}
                .backup {{ background: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #ffc107; }}
                h1, h2 {{ color: #333; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🗄️ Database Status - Python Trivia</h1>
                <div class="timestamp">Last checked: {datetime.now(timezone.utc).isoformat()}</div>
                
                <div class="status">
                    <strong>✅ Database Connected</strong><br>
                    Total Users: {len(user_list)}<br>
                    Storage Type: Database (Deployment Compatible)<br>
                    Total Backups: {backup_status.get('total_backups', 0)}
                </div>
                
                <h2>👥 Registered Users ({len(user_list)})</h2>
                {''.join([f'<div class="user"><strong>{user["username"]}</strong> ({user["email"]})<br>Created: {user["created_at"]}<br>Games: {user["games_played"]}, Points: {user["points"]}</div>' for user in user_list]) if user_list else '<p>No users found</p>'}
                
                <h2>💾 Backup Status</h2>
                <div class="backup">
                    <strong>Total Backups:</strong> {backup_status.get('total_backups', 0)}<br>
                    <strong>Has Default Backup:</strong> {backup_status.get('has_backup', False)}<br>
                    <strong>Storage Type:</strong> {backup_status.get('storage_type', 'database')}
                </div>
                
                <h2>🔧 All Backups</h2>
                {''.join([f'<div class="backup"><strong>{backup["backup_name"]}</strong><br>Users: {backup["user_count"]}<br>Created: {backup["created_at"]}</div>' for backup in all_backups]) if all_backups else '<p>No backups found</p>'}
                
                <p><a href="/game">← Back to Game</a> | <a href="/">← Home</a></p>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"""
        <html>
        <head><title>Database Error</title></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1>❌ Database Error</h1>
            <p>Error checking database status: {str(e)}</p>
            <p><a href="/game">← Back to Game</a></p>
        </body>
        </html>
        """, 500
