"""
Comprehensive model tests to achieve 90%+ coverage
"""
import pytest
import json
from datetime import datetime
from app import app
from models import (
    db, User, Question, GameSession, Answer, Score, 
    Category, Difficulty
)


class TestUserModelMethods:
    """Test User model methods for coverage"""
    
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
                
    @pytest.fixture
    def app_context(self):
        """Create app context"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    def test_user_preferred_categories(self, client):
        """Test user preferred categories methods"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Test getting default categories (when none set)
            categories = user.get_preferred_categories()
            assert isinstance(categories, list)
            assert len(categories) > 0
            
            # Test setting categories
            new_categories = [Category.BASICS, Category.FUNCTIONS]
            user.set_preferred_categories(new_categories)
            db.session.commit()
            
            # Test getting set categories
            retrieved_categories = user.get_preferred_categories()
            assert len(retrieved_categories) == 2
            assert Category.BASICS in retrieved_categories
            assert Category.FUNCTIONS in retrieved_categories
    
    def test_user_preferred_categories_invalid_json(self, client):
        """Test user preferred categories with invalid JSON"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            # Set invalid JSON directly
            user.preferred_categories = "invalid json"
            db.session.add(user)
            db.session.commit()
            
            # Should return all categories as default
            categories = user.get_preferred_categories()
            assert isinstance(categories, list)
            assert len(categories) > 0
    
    def test_user_accuracy_percentage(self, client):
        """Test user accuracy percentage calculation"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Test with no questions answered
            accuracy = user.get_accuracy_percentage()
            assert accuracy == 0.0
            
            # Test with some questions answered
            user.total_questions_answered = 10
            user.total_correct_answers = 7
            db.session.commit()
            
            accuracy = user.get_accuracy_percentage()
            assert accuracy == 70.0
    
    def test_user_to_dict(self, app_context):
        """Test User.to_dict method"""
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashedpassword',
            total_games_played=5,
            total_questions_answered=50,
            total_correct_answers=35,
            best_streak=8,
            total_points=350
        )
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict()
        
        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['total_games_played'] == 5


class TestQuestionModelMethods:
    """Test Question model methods for coverage"""
    
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
    
    def test_question_choices_methods(self, client):
        """Test question choices get/set methods"""
        with app.app_context():
            question = Question(
                question_text="Test question?",
                correct_answer="Option A",
                category=Category.BASICS,
                difficulty=Difficulty.EASY
            )
            db.session.add(question)
            db.session.commit()
            
            # Test setting choices
            choices = ["Option A", "Option B", "Option C", "Option D"]
            question.set_choices(choices)
            db.session.commit()
            
            # Test getting choices
            retrieved_choices = question.get_choices()
            assert retrieved_choices == choices
    
    def test_question_choices_invalid_json(self, client):
        """Test question choices with invalid JSON"""
        with app.app_context():
            question = Question(
                question_text="Test question?",
                correct_answer="Option A",
                choices="invalid json",  # Invalid JSON
                category=Category.BASICS,
                difficulty=Difficulty.EASY
            )
            db.session.add(question)
            db.session.commit()
            
            # Should return empty list for invalid JSON
            choices = question.get_choices()
            assert choices == []
    
    def test_question_difficulty_percentage(self, client):
        """Test question difficulty percentage calculation"""
        with app.app_context():
            question = Question(
                question_text="Test question?",
                correct_answer="Option A",
                category=Category.BASICS,
                difficulty=Difficulty.EASY
            )
            db.session.add(question)
            db.session.commit()
            
            # Test with no attempts
            difficulty = question.get_difficulty_percentage()
            assert difficulty == 0.0
            
            # Test with some attempts
            question.times_asked = 10
            question.times_correct = 3
            db.session.commit()
            
            difficulty = question.get_difficulty_percentage()
            assert difficulty == 30.0
    
    def test_question_accuracy_percentage_alias(self, client):
        """Test question accuracy percentage (alias method)"""
        with app.app_context():
            question = Question(
                question_text="Test question?",
                correct_answer="Option A",
                category=Category.BASICS,
                difficulty=Difficulty.EASY,
                times_asked=20,
                times_correct=15
            )
            db.session.add(question)
            db.session.commit()
            
            # Should be the same as difficulty percentage
            accuracy = question.get_accuracy_percentage()
            difficulty = question.get_difficulty_percentage()
            assert accuracy == difficulty
            assert accuracy == 75.0
    
    def test_question_to_dict(self, client):
        """Test question to_dict method"""
        with app.app_context():
            question = Question(
                question_text="Test question?",
                correct_answer="Option A",
                category=Category.BASICS,
                difficulty=Difficulty.EASY,
                explanation="Test explanation",
                times_asked=5,
                times_correct=3
            )
            question.set_choices(["Option A", "Option B", "Option C", "Option D"])
            db.session.add(question)
            db.session.commit()
            
            question_dict = question.to_dict()
            assert question_dict['question'] == 'Test question?'
            assert question_dict['answer'] == 'Option A'
            assert question_dict['explanation'] == 'Test explanation'
            assert question_dict['category'] == Category.BASICS.value
            assert question_dict['difficulty'] == Difficulty.EASY.value


class TestGameSessionModelMethods:
    """Test GameSession model methods for coverage"""
    
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
    
    def test_session_accuracy_percentage(self, client):
        """Test session accuracy percentage calculation"""
        with app.app_context():
            session = GameSession()
            db.session.add(session)
            db.session.commit()
            
            # Test with no answers
            accuracy = session.get_accuracy_percentage()
            assert accuracy == 0.0
            
            # Test with answers
            session.correct_answers = 8
            session.incorrect_answers = 2
            db.session.commit()
            
            accuracy = session.get_accuracy_percentage()
            assert accuracy == 80.0
    
    def test_session_completion_time(self, client):
        """Test session completion time calculation"""
        with app.app_context():
            session = GameSession()
            session.started_at = datetime.utcnow()
            db.session.add(session)
            db.session.commit()
            
            # Test when not completed
            completion_time = session.get_completion_time()
            assert completion_time is None
            
            # Test when completed
            session.completed_at = datetime.utcnow()
            db.session.commit()
            
            completion_time = session.get_completion_time()
            assert completion_time is not None
            assert completion_time >= 0  # Should be positive time delta
    
    def test_session_to_dict(self, client):
        """Test session to_dict method"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            session = GameSession(user_id=user.id)
            session.current_question_index = 5
            session.correct_answers = 3
            session.incorrect_answers = 2
            session.total_score = 150
            db.session.add(session)
            db.session.commit()
            
            session_dict = session.to_dict()
            assert session_dict['user_id'] == user.id
            assert session_dict['current_question_index'] == 5
            assert session_dict['correct_answers'] == 3
            assert session_dict['total_score'] == 150


class TestScoreModelMethods:
    """Test Score model methods for coverage"""
    
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
    
    def test_score_to_dict(self, client):
        """Test score to_dict method"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            
            session = GameSession(user_id=user.id)
            db.session.add(session)
            db.session.commit()
            
            score = Score(
                game_session_id=session.id,
                user_id=user.id,
                score=95,
                accuracy_percentage=85.5,
                questions_answered=20,
                time_taken=300.0,
                category=Category.BASICS,
                difficulty=Difficulty.MEDIUM
            )
            db.session.add(score)
            db.session.commit()
            
            score_dict = score.to_dict()
            assert score_dict['score'] == 95
            assert score_dict['accuracy_percentage'] == 85.5
            assert score_dict['questions_answered'] == 20
            assert score_dict['time_taken'] == 300.0
            assert score_dict['category'] == Category.BASICS.value
            assert score_dict['difficulty'] == Difficulty.MEDIUM.value


class TestAnswerModelMethods:
    """Test Answer model methods for coverage"""
    
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
    
    def test_answer_to_dict(self, client):
        """Test answer to_dict method"""
        with app.app_context():
            question = Question(
                question_text="Test question?",
                correct_answer="Option A",
                category=Category.BASICS,
                difficulty=Difficulty.EASY
            )
            db.session.add(question)
            
            session = GameSession()
            db.session.add(session)
            db.session.commit()
            
            answer = Answer(
                game_session_id=session.id,
                question_id=question.id,
                user_answer="Option A",
                is_correct=True,
                time_taken=15.5
            )
            db.session.add(answer)
            db.session.commit()
            
            answer_dict = answer.to_dict()
            assert answer_dict['question_id'] == question.id
            assert answer_dict['user_answer'] == "Option A"
            assert answer_dict['is_correct'] is True
            assert answer_dict['time_taken'] == 15.5


if __name__ == '__main__':
    pytest.main([__file__])