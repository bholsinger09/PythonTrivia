"""
Unit tests for enhanced database models
"""
import pytest
from datetime import datetime, timezone
from models import db, User, Question, GameSession, Answer, Score, Category, Difficulty
from db_service import UserService, QuestionService, GameSessionService
from app import app


@pytest.fixture
def test_app():
    """Create a test Flask app"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


class TestUser:
    """Test the User model"""
    
    def test_create_user(self, test_app):
        """Test creating a user"""
        with test_app.app_context():
            user = User(
                username="testuser",
                email="test@example.com"
            )
            user.set_password("testpass123")
            
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.password_hash is not None
            assert user.check_password("testpass123")
            assert not user.check_password("wrongpass")
    
    def test_user_password_hashing(self, test_app):
        """Test password hashing functionality"""
        with test_app.app_context():
            user = User(username="test", email="test@example.com")
            user.set_password("secret123")
            
            # Password should be hashed
            assert user.password_hash != "secret123"
            assert user.check_password("secret123")
            assert not user.check_password("wrong")
    
    def test_user_unique_constraints(self, test_app):
        """Test unique constraints on username and email"""
        with test_app.app_context():
            # Create first user
            user1 = User(username="unique", email="unique@example.com")
            user1.set_password("pass123")
            db.session.add(user1)
            db.session.commit()
            
            # Try to create user with same username
            user2 = User(username="unique", email="different@example.com")
            user2.set_password("pass123")
            db.session.add(user2)
            
            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()


class TestQuestion:
    """Test the Question model"""
    
    def test_create_question(self, test_app):
        """Test creating a question"""
        with test_app.app_context():
            question = Question(
                question_text="What is Python?",
                correct_answer="A programming language",
                correct_choice_index=0,
                category=Category.BASICS,
                difficulty=Difficulty.EASY,
                explanation="Python is a high-level programming language"
            )
            question.set_choices(["A programming language", "A snake"])
            
            db.session.add(question)
            db.session.commit()
            
            assert question.id is not None
            assert question.question_text == "What is Python?"
            assert question.category == Category.BASICS
            assert question.difficulty == Difficulty.EASY
            assert question.get_choices() == ["A programming language", "A snake"]
            assert question.is_active is True
    
    def test_question_statistics(self, test_app):
        """Test question statistics tracking"""
        with test_app.app_context():
            question = Question(
                question_text="Test question",
                correct_answer="Test answer",
                correct_choice_index=0,
                category=Category.BASICS,
                difficulty=Difficulty.EASY
            )
            question.set_choices(["Test answer", "Wrong answer"])
            
            db.session.add(question)
            db.session.commit()
            
            # Initial stats
            assert question.times_asked == 0
            assert question.times_correct == 0
            assert question.times_incorrect == 0
            
            # Update stats
            question.times_asked = 5
            question.times_correct = 3
            question.times_incorrect = 2
            db.session.commit()
            
            assert question.get_accuracy_percentage() == 60.0


class TestGameSession:
    """Test the GameSession model"""
    
    def test_create_game_session(self, test_app):
        """Test creating a game session"""
        with test_app.app_context():
            session = GameSession(
                session_token="test-token-123",
                difficulty=Difficulty.MEDIUM,
                time_limit=30
            )
            
            db.session.add(session)
            db.session.commit()
            
            assert session.id is not None
            assert session.session_token == "test-token-123"
            assert session.difficulty == Difficulty.MEDIUM
            assert session.time_limit == 30
            assert session.is_completed is False
    
    def test_game_session_with_user(self, test_app):
        """Test game session with associated user"""
        with test_app.app_context():
            # Create user
            user = User(username="gamer", email="gamer@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            # Create session for user
            session = GameSession(
                user_id=user.id,
                session_token="user-session-123",
                difficulty=Difficulty.HARD
            )
            
            db.session.add(session)
            db.session.commit()
            
            assert session.user == user
            assert session.user_id == user.id


class TestUserService:
    """Test the UserService class"""
    
    def test_create_user_service(self, test_app):
        """Test creating user through service"""
        with test_app.app_context():
            user = UserService.create_user(
                username="serviceuser",
                email="service@example.com",
                password="service123"
            )
            
            assert user.id is not None
            assert user.username == "serviceuser"
            assert user.email == "service@example.com"
            assert user.check_password("service123")
    
    def test_get_user_by_username(self, test_app):
        """Test getting user by username"""
        with test_app.app_context():
            # Create user
            UserService.create_user("findme", "findme@example.com", "password123")
            
            # Find user
            found_user = UserService.get_user_by_username("findme")
            assert found_user is not None
            assert found_user.username == "findme"
            
            # Try to find non-existent user
            not_found = UserService.get_user_by_username("nonexistent")
            assert not_found is None


class TestQuestionService:
    """Test the QuestionService class"""
    
    def test_create_question_service(self, test_app):
        """Test creating question through service"""
        with test_app.app_context():
            question = QuestionService.create_question(
                question_text="Service test question?",
                correct_answer="Service answer",
                choices=["Service answer", "Wrong answer"],
                correct_choice_index=0,
                category=Category.BASICS,
                difficulty=Difficulty.EASY,
                explanation="This is a test question created through service"
            )
            
            assert question.id is not None
            assert question.question_text == "Service test question?"
            assert question.get_choices() == ["Service answer", "Wrong answer"]
    
    def test_get_questions_by_criteria(self, test_app):
        """Test filtering questions by criteria"""
        with test_app.app_context():
            # Create test questions
            QuestionService.create_question(
                "Easy basics question?", "Answer", ["Answer", "Wrong"],
                0, Category.BASICS, Difficulty.EASY
            )
            QuestionService.create_question(
                "Hard advanced question?", "Answer", ["Answer", "Wrong"],
                0, Category.ADVANCED, Difficulty.HARD
            )
            
            # Test filtering by category
            basics_questions = QuestionService.get_questions_by_criteria(
                categories=[Category.BASICS]
            )
            assert len(basics_questions) == 1
            assert basics_questions[0].category == Category.BASICS
            
            # Test filtering by difficulty
            easy_questions = QuestionService.get_questions_by_criteria(
                difficulty=Difficulty.EASY
            )
            assert len(easy_questions) == 1
            assert easy_questions[0].difficulty == Difficulty.EASY


class TestGameSessionService:
    """Test the GameSessionService class"""
    
    def test_create_session_service(self, test_app):
        """Test creating session through service"""
        with test_app.app_context():
            session = GameSessionService.create_session(
                categories=[Category.BASICS],
                difficulty=Difficulty.MEDIUM,
                time_limit=45
            )
            
            assert session.id is not None
            assert session.session_token is not None
            assert session.difficulty == Difficulty.MEDIUM
            assert session.time_limit == 45
    
    def test_get_session_by_token(self, test_app):
        """Test getting session by token"""
        with test_app.app_context():
            # Create session
            session = GameSessionService.create_session()
            token = session.session_token
            
            # Find session by token
            found_session = GameSessionService.get_session_by_token(token)
            assert found_session is not None
            assert found_session.id == session.id
            assert found_session.session_token == token