"""
Unit tests for API endpoints
"""
import pytest
import json
from models import db, User, Question, GameSession, Category, Difficulty
from db_service import UserService, QuestionService, GameSessionService
from app import app


@pytest.fixture
def test_app():
    """Create a test Flask app"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        db.create_all()
        
        # Create test questions
        QuestionService.create_question(
            "What is Python?",
            "A programming language", 
            ["A programming language", "A snake", "A framework", "A database"],
            0,
            Category.BASICS,
            Difficulty.EASY,
            "Python is a high-level programming language"
        )
        
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(test_app):
    """Create a test client"""
    return test_app.test_client()


class TestAPIEndpoints:
    """Test basic API endpoint functionality"""
    
    def test_health_check(self, client):
        """Test basic health check"""
        response = client.get('/')
        assert response.status_code == 200
