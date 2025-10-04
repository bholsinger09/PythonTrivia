"""
Simple db_service tests to improve coverage
"""
import pytest
from app import app
from models import db, User, Question, GameSession, Category, Difficulty
from db_service import UserService, DatabaseSeeder, QuestionService, GameSessionService


class TestUserServiceSimple:
    """Simple tests for UserService"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.drop_all()
    
    def test_create_user(self, client):
        """Test creating a user"""
        with app.app_context():
            user = UserService.create_user('testuser', 'test@example.com', 'password123')
            assert user is not None
            assert user.username == 'testuser'
    
    def test_get_user_by_username(self, client):
        """Test getting user by username"""
        with app.app_context():
            user = UserService.create_user('testuser', 'test@example.com', 'password123')
            found_user = UserService.get_user_by_username('testuser')
            assert found_user is not None
            assert found_user.username == 'testuser'
    
    def test_authenticate_user(self, client):
        """Test user authentication"""
        with app.app_context():
            user = UserService.create_user('testuser', 'test@example.com', 'password123')
            auth_user = UserService.authenticate_user('testuser', 'password123')
            assert auth_user is not None
            assert auth_user.username == 'testuser'


class TestDatabaseSeederSimple:
    """Simple tests for DatabaseSeeder"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.drop_all()
    
    def test_seed_sample_questions(self, client):
        """Test seeding sample questions"""
        with app.app_context():
            initial_count = Question.query.count()
            DatabaseSeeder.seed_sample_questions()
            final_count = Question.query.count()
            assert final_count > initial_count
    
    def test_create_admin_user(self, client):
        """Test creating admin user"""
        with app.app_context():
            admin = DatabaseSeeder.create_admin_user()
            # The method might return None but still create the user
            # Let's check if the admin user was created
            admin_user = User.query.filter_by(username='admin').first()
            assert admin_user is not None
            assert admin_user.username == 'admin'


class TestQuestionServiceSimple:
    """Simple tests for QuestionService"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                # Seed some questions
                DatabaseSeeder.seed_sample_questions()
                yield client
                db.drop_all()
    
    def test_get_questions_by_criteria(self, client):
        """Test getting questions by criteria"""
        with app.app_context():
            questions = QuestionService.get_questions_by_criteria()
            assert isinstance(questions, list)
    
    def test_get_questions_with_category(self, client):
        """Test getting questions with category filter"""
        with app.app_context():
            questions = QuestionService.get_questions_by_criteria(categories=[Category.BASICS])
            assert isinstance(questions, list)
    
    def test_get_questions_with_difficulty(self, client):
        """Test getting questions with difficulty filter"""
        with app.app_context():
            questions = QuestionService.get_questions_by_criteria(difficulty=Difficulty.EASY)
            assert isinstance(questions, list)


class TestGameSessionServiceSimple:
    """Simple tests for GameSessionService"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.drop_all()
    
    def test_create_session(self, client):
        """Test creating a game session"""
        with app.app_context():
            session = GameSessionService.create_session()
            assert session is not None
            assert session.session_token is not None
    
    def test_create_session_with_user(self, client):
        """Test creating a game session with user"""
        with app.app_context():
            user = UserService.create_user('testuser', 'test@example.com', 'password123')
            session = GameSessionService.create_session(user_id=user.id)
            assert session is not None
            assert session.user_id == user.id
    
    def test_get_session_by_token(self, client):
        """Test getting session by token"""
        with app.app_context():
            session = GameSessionService.create_session()
            found_session = GameSessionService.get_session_by_token(session.session_token)
            assert found_session is not None
            assert found_session.id == session.id


if __name__ == '__main__':
    pytest.main([__file__])