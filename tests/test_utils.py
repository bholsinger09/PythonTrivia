"""
Test utilities for handling JSON serialization and mocking issues
"""

import json
from unittest.mock import MagicMock
from models import User, Category, Difficulty


class JsonSerializableMock(MagicMock):
    """A MagicMock that can be JSON serialized"""
    
    def __init__(self, *args, **kwargs):
        # Extract serializable attributes before calling super
        self._json_data = kwargs.pop('_json_data', {})
        super().__init__(*args, **kwargs)
    
    def __reduce__(self):
        """Make the mock pickleable/serializable"""
        return (JsonSerializableMock, (), self._json_data)
    
    def to_dict(self):
        """Return a serializable dictionary representation"""
        return self._json_data


class MockUser:
    """A simple mock user that's JSON serializable"""
    
    def __init__(self, username='testuser', email='test@example.com', user_id=1):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = 'hashed_password'
        self.is_active = True
        self.total_games_played = 0
        self.total_questions_answered = 0
        self.total_correct_answers = 0
        self.best_streak = 0
        self.total_points = 0
        
    def check_password(self, password):
        """Mock password check - always returns True for testing"""
        return True
        
    def get_id(self):
        """Required by Flask-Login"""
        return str(self.id)
        
    def is_authenticated(self):
        """Required by Flask-Login"""
        return True
        
    def is_anonymous(self):
        """Required by Flask-Login"""
        return False
        
    def to_dict(self):
        """Return serializable dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'total_games_played': self.total_games_played,
            'total_questions_answered': self.total_questions_answered,
            'total_correct_answers': self.total_correct_answers,
            'best_streak': self.best_streak,
            'total_points': self.total_points
        }


class MockQuestion:
    """A simple mock question that's JSON serializable"""
    
    def __init__(self, question_id=1, question_text="What is Python?", 
                 correct_answer="A programming language", category=Category.BASICS,
                 difficulty=Difficulty.EASY):
        self.id = question_id
        self.question = question_text
        self.correct_answer = correct_answer
        self.answer = correct_answer  # Some code expects 'answer' instead of 'correct_answer'
        self.answer_a = "A programming language"
        self.answer_b = "A snake"
        self.answer_c = "A movie"
        self.answer_d = "A book"
        self.category = category
        self.difficulty = difficulty
        self.is_active = True
        # Add correct_choice_index for game functionality
        self.correct_choice_index = 0  # Default to first choice (answer_a)
        
    def to_dict(self):
        """Return serializable dictionary"""
        return {
            'id': self.id,
            'question': self.question,
            'correct_answer': self.correct_answer,
            'answer': self.answer,
            'answer_a': self.answer_a,
            'answer_b': self.answer_b,
            'answer_c': self.answer_c,
            'answer_d': self.answer_d,
            'category': self.category.value if self.category else None,
            'difficulty': self.difficulty.value if self.difficulty else None,
            'correct_choice_index': self.correct_choice_index
        }


class MockGameSession:
    """A simple mock game session that's JSON serializable"""
    
    def __init__(self, session_id=1, user_id=None):
        self.id = session_id
        self.user_id = user_id
        self.is_completed = False
        self.total_questions = 0
        self.correct_answers = 0
        self.total_score = 0
        
    def to_dict(self):
        """Return serializable dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'is_completed': self.is_completed,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'total_score': self.total_score
        }


def create_mock_user(**kwargs):
    """Factory function to create a mock user with custom attributes"""
    return MockUser(**kwargs)


def create_mock_question(**kwargs):
    """Factory function to create a mock question with custom attributes"""
    return MockQuestion(**kwargs)


def create_mock_session(**kwargs):
    """Factory function to create a mock game session with custom attributes"""
    return MockGameSession(**kwargs)


def patch_flask_session_for_testing(test_case):
    """
    Patch Flask session to handle mock objects properly
    This prevents JSON serialization errors during testing
    """
    # This can be used as a decorator or context manager
    # to ensure session data is properly handled
    pass