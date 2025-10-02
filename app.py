"""
Flask application for Python Trivia Flip Card Game
"""
from flask import Flask, render_template, request, jsonify, session, g, redirect, url_for
import json
import os
import uuid
from datetime import datetime, timezone

# Import both old and new models for compatibility
from src.models import TriviaGame, TriviaQuestion
from models import db, User, Question, GameSession, Answer, Score, Category, Difficulty
from config import DevelopmentConfig, ProductionConfig, TestingConfig
from db_service import (
    QuestionService, GameSessionService, AnswerService, 
    ScoreService, UserService, DatabaseSeeder
)

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


def get_or_create_game_session():
    """Get or create a game session for the current user/session"""
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


def load_questions_from_db(categories=None, difficulty=None, limit=20):
    """Load questions from database instead of hardcoded list"""
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


def initialize_game_with_questions():
    """Initialize game with questions from database or fallback"""
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
def init_db():
    """Initialize database tables and seed data if needed"""
    try:
        with app.app_context():
            db.create_all()
            
            # Check if we need to seed data
            if Question.query.count() == 0:
                print("Seeding database with initial data...")
                DatabaseSeeder.seed_sample_questions()
                
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


# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Basic validation
        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'All fields required'})
        
        # Check if user exists
        if UserService.get_user_by_username(username):
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        if UserService.get_user_by_email(email):
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        # Create user
        try:
            user = UserService.create_user(username, email, password)
            if request.is_json:
                return jsonify({'success': True, 'message': 'Registration successful'})
            else:
                login_user(user)
                return redirect(url_for('game_page'))
        except Exception as e:
            return jsonify({'success': False, 'message': 'Registration failed'})
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        user = UserService.get_user_by_username(username)
        
        if user and user.check_password(password):
            login_user(user)
            if request.is_json:
                return jsonify({'success': True, 'message': 'Login successful'})
            else:
                return redirect(url_for('game_page'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid credentials'})
            else:
                return render_template('login.html', error='Invalid credentials')
    
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
def index():
    """Home page route"""
    return render_template('index.html')


@app.route('/debug')
def debug_page():
    """Debug page to test question display"""
    return render_template('debug.html')


@app.route('/game')
def game_page():
    """Main game page route"""
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


@app.route('/api/current-card')
def get_current_card():
    """API endpoint to get current card data"""
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


if __name__ == '__main__':
    # Initialize app when run directly
    initialize_app()
    
    # Use PORT from environment (Render provides this) or default to 5001
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)