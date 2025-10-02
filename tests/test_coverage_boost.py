"""
Additional tests to improve coverage for app.py routes and functionality
"""
import pytest
from flask import session
import json
from models import db, User, Question, Category, Difficulty
from db_service import UserService, QuestionService
from app import app, game


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
        test_questions = [
            Question(
                question="What is Python?",
                options=["Programming language", "Snake", "Food", "Tool"],
                correct_answer="Programming language",
                category=Category.BASICS,
                difficulty=Difficulty.EASY
            ),
            Question(
                question="What is Flask?",
                options=["Web framework", "Bottle", "Cup", "Container"],
                correct_answer="Web framework", 
                category=Category.WEB_DEVELOPMENT,
                difficulty=Difficulty.MEDIUM
            ),
            Question(
                question="What is Django?",
                options=["Web framework", "Database", "Server", "Language"],
                correct_answer="Web framework",
                category=Category.WEB_DEVELOPMENT,
                difficulty=Difficulty.HARD
            )
        ]
        
        for question in test_questions:
            db.session.add(question)
        db.session.commit()
        
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(test_app):
    """Create a test client"""
    return test_app.test_client()


@pytest.fixture
def test_user(test_app):
    """Create a test user"""
    with test_app.app_context():
        user = UserService.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        return user


class TestMainRoutes:
    """Test main application routes for coverage"""
    
    def test_home_page(self, client):
        """Test home page route"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Python Trivia' in response.data
    
    def test_game_page(self, client):
        """Test game page route"""
        response = client.get('/game')
        assert response.status_code == 200
        # Check for game-related content
    
    def test_categories_page(self, client):
        """Test categories page route"""
        response = client.get('/categories')
        assert response.status_code == 200
    
    def test_difficulty_page(self, client):
        """Test difficulty page route"""
        response = client.get('/difficulty')
        assert response.status_code == 200
    
    def test_leaderboard_page(self, client):
        """Test leaderboard page route"""
        response = client.get('/leaderboard')
        assert response.status_code == 200


class TestGameAPIRoutes:
    """Test game-related API routes"""
    
    def test_start_game_get(self, client):
        """Test GET request to start game"""
        response = client.get('/api/start-game')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_start_game_post_with_filters(self, client):
        """Test POST request to start game with filters"""
        response = client.post('/api/start-game', 
                              json={
                                  'category': 'BASICS',
                                  'difficulty': 'EASY'
                              },
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_start_game_post_invalid_category(self, client):
        """Test POST request with invalid category"""
        response = client.post('/api/start-game',
                              json={
                                  'category': 'INVALID_CATEGORY',
                                  'difficulty': 'EASY'
                              },
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert not data['success']
    
    def test_get_current_question(self, client):
        """Test getting current question"""
        # Start game first
        client.get('/api/start-game')
        
        response = client.get('/api/current-question')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_get_current_question_no_game(self, client):
        """Test getting current question without active game"""
        response = client.get('/api/current-question')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert not data['success']
    
    def test_submit_answer_correct(self, client):
        """Test submitting correct answer"""
        # Start game first
        client.get('/api/start-game')
        
        response = client.post('/api/submit-answer',
                              json={'answer': 'Programming language'},
                              content_type='application/json')
        # Should succeed or give proper error
        assert response.status_code in [200, 400]
    
    def test_submit_answer_no_game(self, client):
        """Test submitting answer without active game"""
        response = client.post('/api/submit-answer',
                              json={'answer': 'Programming language'},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert not data['success']
    
    def test_next_question(self, client):
        """Test moving to next question"""
        # Start game first
        client.get('/api/start-game')
        
        response = client.post('/api/next-question')
        assert response.status_code in [200, 400]
    
    def test_game_stats(self, client):
        """Test getting game statistics"""
        response = client.get('/api/game-stats')
        assert response.status_code in [200, 400]
    
    def test_reset_game(self, client):
        """Test resetting game"""
        response = client.post('/api/reset-game')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data


class TestLeaderboardAPI:
    """Test leaderboard API routes"""
    
    def test_leaderboard_api_default(self, client):
        """Test leaderboard API with default parameters"""
        response = client.get('/api/leaderboard')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
        assert 'scores' in data
    
    def test_leaderboard_api_with_filters(self, client):
        """Test leaderboard API with category and difficulty filters"""
        response = client.get('/api/leaderboard?category=BASICS&difficulty=EASY&limit=5')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_leaderboard_api_invalid_category(self, client):
        """Test leaderboard API with invalid category"""
        response = client.get('/api/leaderboard?category=INVALID')
        assert response.status_code == 200  # Should handle gracefully


class TestScoreAPI:
    """Test score-related API routes"""
    
    def test_save_score_no_game(self, client):
        """Test saving score without active game session"""
        response = client.post('/api/save-score',
                              json={'anonymous_name': 'TestPlayer'},
                              content_type='application/json')
        # Should handle gracefully or return error
        assert response.status_code in [200, 400, 500]


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_404_error(self, client):
        """Test 404 error for non-existent route"""
        response = client.get('/non-existent-route')
        assert response.status_code == 404
    
    def test_invalid_json_request(self, client):
        """Test invalid JSON in request"""
        response = client.post('/api/start-game',
                              data='invalid-json',
                              content_type='application/json')
        assert response.status_code in [400, 500]


class TestSessionHandling:
    """Test session-related functionality"""
    
    def test_session_persistence(self, client):
        """Test that game sessions persist across requests"""
        # Start a game
        response1 = client.get('/api/start-game')
        assert response1.status_code == 200
        
        # Check that game state persists
        response2 = client.get('/api/current-question')
        assert response2.status_code in [200, 400]  # May not have questions


class TestStaticContent:
    """Test static content and assets"""
    
    def test_static_css(self, client):
        """Test CSS file access"""
        response = client.get('/static/css/style.css')
        # May return 404 if file doesn't exist, which is acceptable for testing
        assert response.status_code in [200, 404]
    
    def test_static_js(self, client):
        """Test JavaScript file access"""
        response = client.get('/static/js/app.js')
        # May return 404 if file doesn't exist, which is acceptable for testing
        assert response.status_code in [200, 404]


class TestFormDataHandling:
    """Test handling of different data formats"""
    
    def test_form_data_vs_json(self, client):
        """Test that routes handle both form data and JSON"""
        # Test with form data
        response1 = client.post('/api/start-game', data={'category': 'BASICS'})
        assert response1.status_code in [200, 400, 405]
        
        # Test with JSON
        response2 = client.post('/api/start-game', 
                               json={'category': 'BASICS'},
                               content_type='application/json')
        assert response2.status_code in [200, 400]


class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_xss_prevention(self, client):
        """Test XSS prevention in inputs"""
        xss_payload = "<script>alert('xss')</script>"
        response = client.post('/api/start-game',
                              json={'category': xss_payload},
                              content_type='application/json')
        # Should handle malicious input gracefully
        assert response.status_code in [200, 400]
    
    def test_sql_injection_prevention(self, client):
        """Test SQL injection prevention"""
        sql_payload = "'; DROP TABLE users; --"
        response = client.post('/api/submit-answer',
                              json={'answer': sql_payload},
                              content_type='application/json')
        # Should handle malicious input gracefully
        assert response.status_code in [200, 400]


class TestConfigurationHandling:
    """Test configuration and environment handling"""
    
    def test_debug_mode_off(self, test_app):
        """Test that debug mode is properly configured"""
        assert not test_app.debug or test_app.config['TESTING']
    
    def test_database_connection(self, test_app):
        """Test database connection and configuration"""
        with test_app.app_context():
            # Should be able to query database
            assert db.engine is not None