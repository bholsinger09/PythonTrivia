"""
PEP 20 compliance improvements for app.py

This module demonstrates improved code following the Zen of Python principles:
- Beautiful is better than ugly
- Explicit is better than implicit  
- Simple is better than complex
- Readability counts
- If the implementation is hard to explain, it's a bad idea
"""

from typing import Dict, List, Optional, Tuple, Union
from flask import request, jsonify, render_template
from models import Category, Difficulty
from db_service import UserService

# PEP 20 Improvement: Extract validation logic into separate functions
# "Simple is better than complex" - break down complex functions

def validate_username(username: str) -> Optional[str]:
    """
    Validate username according to business rules.
    
    Returns error message if invalid, None if valid.
    PEP 20: "Explicit is better than implicit" - clear return type and behavior
    """
    if not username:
        return 'Username is required'
    
    username = username.strip()
    
    if len(username) < 3:
        return 'Username must be at least 3 characters'
    
    if len(username) > 20:
        return 'Username must be no more than 20 characters'
    
    if not username.replace('_', '').isalnum():
        return 'Username can only contain letters, numbers, and underscores'
    
    return None


def validate_email(email: str) -> Optional[str]:
    """
    Validate email format according to business rules.
    
    Returns error message if invalid, None if valid.
    PEP 20: "Readability counts" - clear, single-purpose function
    """
    if not email:
        return 'Email is required'
    
    email = email.strip().lower()
    
    # Basic email validation
    if '@' not in email:
        return 'Please enter a valid email address'
    
    parts = email.split('@')
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return 'Please enter a valid email address'
    
    if '.' not in parts[1]:
        return 'Please enter a valid email address'
    
    return None


def validate_password(password: str, confirm_password: str = None) -> Optional[str]:
    """
    Validate password according to business rules.
    
    Returns error message if invalid, None if valid.
    PEP 20: "Simple is better than complex" - handle one concern at a time
    """
    if not password:
        return 'Password is required'
    
    if len(password) < 6:
        return 'Password must be at least 6 characters'
    
    # Only check confirmation if provided
    if confirm_password is not None and password != confirm_password:
        return 'Passwords do not match'
    
    return None


def create_validation_response(error: str, is_json: bool) -> Tuple[Union[Dict, str], int]:
    """
    Create appropriate error response based on request type.
    
    PEP 20: "Don't repeat yourself" - centralize response creation
    """
    if is_json:
        return jsonify({'success': False, 'message': error}), 400
    return render_template('register.html', error=error), 400


def validate_registration_data(data: Dict) -> Optional[str]:
    """
    Validate all registration data and return first error found.
    
    PEP 20: "Flat is better than nested" - reduce nesting in main function
    """
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    # Check required fields first
    if not username or not email or not password:
        return 'All fields are required'
    
    # Validate each field
    username_error = validate_username(username)
    if username_error:
        return username_error
    
    email_error = validate_email(email)
    if email_error:
        return email_error
    
    password_error = validate_password(password, confirm_password)
    if password_error:
        return password_error
    
    return None


def check_user_exists(username: str, email: str) -> Optional[str]:
    """
    Check if user already exists with given username or email.
    
    PEP 20: "Explicit is better than implicit" - clear function purpose
    """
    if UserService.get_user_by_username(username):
        return 'Username already exists'
    
    if UserService.get_user_by_email(email):
        return 'Email already registered'
    
    return None


def improved_register_function():
    """
    Improved registration function following PEP 20 principles.
    
    This is how the register function could be refactored:
    - Simpler logic flow
    - Clear separation of concerns
    - Better readability
    - Explicit error handling
    """
    if request.method == 'GET':
        return render_template('register.html')
    
    # Handle POST request
    data = request.get_json() if request.is_json else request.form
    is_json_request = request.is_json
    
    # Validate input data
    validation_error = validate_registration_data(data)
    if validation_error:
        return create_validation_response(validation_error, is_json_request)
    
    # Extract clean data
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Check if user already exists
    existence_error = check_user_exists(username, email)
    if existence_error:
        return create_validation_response(existence_error, is_json_request)
    
    # Create user
    try:
        user = UserService.create_user(username, email, password)
        
        if is_json_request:
            return jsonify({'success': True, 'message': 'Registration successful'})
        else:
            # Handle login and redirect for form submissions
            if HAS_LOGIN:
                login_user(user)
            return redirect(url_for('game_page'))
            
    except Exception as e:
        app.logger.error(f"Registration error: {e}")
        error_msg = 'Registration failed. Please try again.'
        return create_validation_response(error_msg, is_json_request)


# PEP 20 Improvement: Extract common patterns
# "Don't repeat yourself" principle

class APIResponseHandler:
    """
    Handle API responses consistently across the application.
    
    PEP 20: "Beautiful is better than ugly" - consistent interface
    """
    
    @staticmethod
    def success(data: Dict = None, message: str = "Success") -> Dict:
        """Create successful API response."""
        response = {'success': True, 'message': message}
        if data:
            response.update(data)
        return response
    
    @staticmethod
    def error(message: str, data: Dict = None) -> Dict:
        """Create error API response."""
        response = {'success': False, 'message': message}
        if data:
            response.update(data)
        return response
    
    @staticmethod
    def json_response(success: bool, message: str, data: Dict = None, status_code: int = 200):
        """Create complete JSON response with status code."""
        if success:
            response_data = APIResponseHandler.success(data, message)
        else:
            response_data = APIResponseHandler.error(message, data)
        
        return jsonify(response_data), status_code


class GameStateManager:
    """
    Manage game state consistently across the application.
    
    PEP 20: "Namespaces are one honking great idea" - encapsulate related functionality
    """
    
    @staticmethod
    def is_game_active() -> bool:
        """Check if there's an active game session."""
        return hasattr(game, 'cards') and len(game.cards) > 0
    
    @staticmethod
    def get_current_card_data() -> Optional[Dict]:
        """Get current card data if game is active."""
        if not GameStateManager.is_game_active():
            return None
        
        current_card = game.get_current_card()
        if not current_card:
            return None
        
        return {
            'question': current_card.question,
            'choices': current_card.choices,
            'category': current_card.category.value,
            'difficulty': current_card.difficulty.value,
            'card_number': game.current_card_index + 1,
            'total_cards': len(game.cards),
            'is_flipped': current_card.is_flipped
        }
    
    @staticmethod
    def reset_game_state() -> Dict:
        """Reset game to initial state."""
        game.reset()
        return APIResponseHandler.success(
            {'game_reset': True},
            'Game has been reset'
        )


# PEP 20 Improvement: Add comprehensive docstrings
# "If the implementation is hard to explain, it's a bad idea"

def improved_error_handler():
    """
    Improved error handling following PEP 20 principles.
    
    PEP 20: "Errors should never pass silently" - explicit error handling
    """
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors gracefully."""
        if request.path.startswith('/api/'):
            return jsonify(APIResponseHandler.error('Endpoint not found')), 404
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors gracefully."""
        app.logger.error(f"Internal error: {error}")
        if request.path.startswith('/api/'):
            return jsonify(APIResponseHandler.error('Internal server error')), 500
        return render_template('500.html'), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors gracefully."""
        if request.path.startswith('/api/'):
            return jsonify(APIResponseHandler.error('Bad request')), 400
        return render_template('400.html'), 400


# PEP 20 Example: Complex function simplified
def calculate_game_statistics(game_session) -> Dict:
    """
    Calculate comprehensive game statistics.
    
    PEP 20: "Simple is better than complex" - break into logical steps
    """
    if not game_session:
        return {
            'total_questions': 0,
            'correct_answers': 0,
            'accuracy_percentage': 0.0,
            'time_played': 0,
            'average_time_per_question': 0.0
        }
    
    # Basic statistics
    total_questions = game_session.correct_answers + game_session.incorrect_answers
    correct_answers = game_session.correct_answers
    
    # Calculate accuracy
    accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0.0
    
    # Calculate time statistics
    if game_session.start_time and game_session.end_time:
        time_played = (game_session.end_time - game_session.start_time).total_seconds()
        avg_time = time_played / total_questions if total_questions > 0 else 0.0
    else:
        time_played = 0
        avg_time = 0.0
    
    return {
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'accuracy_percentage': round(accuracy, 2),
        'time_played': round(time_played, 2),
        'average_time_per_question': round(avg_time, 2)
    }


# PEP 20 Improvement: Type hints and documentation
# "Explicit is better than implicit"

def get_filtered_questions(
    category: Optional[Category] = None,
    difficulty: Optional[Difficulty] = None,
    limit: int = 10
) -> List[TriviaQuestion]:
    """
    Get questions filtered by category and difficulty.
    
    Args:
        category: Question category filter (optional)
        difficulty: Question difficulty filter (optional)  
        limit: Maximum number of questions to return
    
    Returns:
        List of TriviaQuestion objects
    
    Raises:
        ValueError: If limit is negative
        DatabaseError: If database query fails
    
    PEP 20: "Explicit is better than implicit" - clear interface
    """
    if limit < 0:
        raise ValueError("Limit cannot be negative")
    
    try:
        categories = [category] if category else None
        questions = QuestionService.get_questions_by_criteria(
            categories=categories,
            difficulty=difficulty,
            limit=limit
        )
        
        return [
            TriviaQuestion(
                question=q.question_text,
                answer=q.correct_answer,
                category=q.category,
                difficulty=q.difficulty,
                explanation=q.explanation or "",
                choices=q.get_choices(),
                correct_choice_index=q.correct_choice_index
            )
            for q in questions
        ]
        
    except Exception as e:
        app.logger.error(f"Error loading questions: {e}")
        raise DatabaseError(f"Failed to load questions: {e}")


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass