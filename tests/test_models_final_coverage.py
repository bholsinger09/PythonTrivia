"""
Final comprehensive model tests to achieve 90%+ coverage
Target the remaining uncovered lines in models.py
"""
import pytest
import json
from datetime import datetime
from app import app
from models import (
    db, User, Question, GameSession, Answer, Score, 
    Category, Difficulty
)


class TestModelFinalCoverage:
    """Target remaining uncovered lines for 90%+ coverage"""
    
    @pytest.fixture
    def app_context(self):
        """Create app context"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()

    def test_user_password_methods(self, app_context):
        """Test User password methods - lines 62-68"""
        user = User(username='testuser', email='test@example.com')
        
        # Test set_password
        user.set_password('mypassword123')
        assert user.password_hash is not None
        assert len(user.password_hash) > 10
        
        # Test check_password
        assert user.check_password('mypassword123') is True
        assert user.check_password('wrongpassword') is False
        
    def test_user_preferred_categories_edge_cases(self, app_context):
        """Test User preferred categories edge cases - lines 74-78, 82"""
        user = User(username='testuser', email='test@example.com')
        
        # Test with invalid JSON - should return all categories
        user.preferred_categories = "invalid json"
        categories = user.get_preferred_categories()
        assert len(categories) == len(Category)
        
        # Test with invalid category values
        user.preferred_categories = json.dumps(["invalid_category", "basics"])
        categories = user.get_preferred_categories()
        assert Category.BASICS in categories
        
    def test_user_accuracy_with_zero_questions(self, app_context):
        """Test User accuracy with zero questions - line 87"""
        user = User(username='testuser', email='test@example.com')
        user.total_questions_answered = 0
        user.total_correct_answers = 0
        
        accuracy = user.get_accuracy_percentage()
        assert accuracy == 0.0

    def test_question_choices_edge_cases(self, app_context):
        """Test Question choices edge cases - lines 136-139"""
        question = Question(
            question_text='Test question?',
            correct_answer='Answer',
            choices='invalid json',  # Invalid JSON
            correct_choice_index=0,
            category=Category.BASICS,
            difficulty=Difficulty.EASY
        )
        
        # Test get_choices with invalid JSON
        choices = question.get_choices()
        assert choices == []
        
    def test_question_difficulty_methods(self, app_context):
        """Test Question difficulty methods - lines 147-149, 153"""
        question = Question(
            question_text='Test question?',
            correct_answer='Answer',
            choices=json.dumps(['A', 'B', 'C', 'Answer']),
            correct_choice_index=3,
            category=Category.BASICS,
            difficulty=Difficulty.EASY,
            times_asked=10,
            times_correct=7
        )
        db.session.add(question)
        db.session.commit()
        
        # Test get_difficulty_percentage
        difficulty_pct = question.get_difficulty_percentage()
        assert difficulty_pct == 70.0
        
        # Test get_accuracy_percentage (alias)
        accuracy_pct = question.get_accuracy_percentage()
        assert accuracy_pct == 70.0
        
    def test_question_zero_times_asked(self, app_context):
        """Test Question with zero times asked - line 143"""
        question = Question(
            question_text='Test question?',
            correct_answer='Answer',
            choices=json.dumps(['A', 'B', 'C', 'Answer']),
            correct_choice_index=3,
            category=Category.BASICS,
            difficulty=Difficulty.EASY,
            times_asked=0,
            times_correct=0
        )
        
        difficulty_pct = question.get_difficulty_percentage()
        assert difficulty_pct == 0.0

    def test_question_to_dict_complete(self, app_context):
        """Test Question to_dict method completely - line 157"""
        question = Question(
            question_text='Test question?',
            correct_answer='Answer',
            choices=json.dumps(['A', 'B', 'C', 'Answer']),
            correct_choice_index=3,
            category=Category.BASICS,
            difficulty=Difficulty.EASY,
            times_asked=5,
            times_correct=3,
            explanation='Test explanation'
        )
        db.session.add(question)
        db.session.commit()
        
        question_dict = question.to_dict()
        
        assert question_dict['id'] == question.id
        assert question_dict['question'] == 'Test question?'
        assert question_dict['answer'] == 'Answer'
        assert question_dict['choices'] == ['A', 'B', 'C', 'Answer']
        assert question_dict['correct_choice_index'] == 3
        assert question_dict['explanation'] == 'Test explanation'
        assert question_dict['category'] == 'basics'
        assert question_dict['difficulty'] == 'easy'
        assert question_dict['times_asked'] == 5
        assert question_dict['times_correct'] == 3
        assert question_dict['success_rate'] == 60.0

    def test_game_session_methods(self, app_context):
        """Test GameSession methods - lines 203-209, 213, 217-220, 224"""
        session = GameSession(
            session_token='test_token_123',
            total_questions=10,
            correct_answers=7,
            incorrect_answers=3,
            current_question_index=5,
            is_completed=False,
            current_streak=3,
            best_streak=5,
            total_score=350,
            difficulty=Difficulty.MEDIUM
        )
        db.session.add(session)
        db.session.commit()
        
        # Test get_accuracy_percentage
        accuracy = session.get_accuracy_percentage()
        assert accuracy == 70.0
        
        # Test get_categories (should return empty list if no categories set)
        categories = session.get_categories()
        assert isinstance(categories, list)
        
        # Test to_dict
        session_dict = session.to_dict()
        assert session_dict['session_token'] == 'test_token_123'
        assert session_dict['total_questions'] == 10
        assert session_dict['correct_answers'] == 7
        assert session_dict['accuracy_percentage'] == 70.0
        assert session_dict['difficulty'] == 'medium'

    def test_answer_to_dict(self, app_context):
        """Test Answer to_dict method - line 263"""
        # Create a question first
        question = Question(
            question_text='Test question?',
            correct_answer='Answer',
            choices=json.dumps(['A', 'B', 'C', 'Answer']),
            correct_choice_index=3,
            category=Category.BASICS,
            difficulty=Difficulty.EASY
        )
        db.session.add(question)
        db.session.flush()  # Get the ID
        
        # Create a game session (required for answer)
        session = GameSession(
            session_token='test_token_answer',
            total_questions=1,
            correct_answers=0
        )
        db.session.add(session)
        db.session.flush()  # Get the ID
        
        answer = Answer(
            game_session_id=session.id,  # Add required game_session_id
            question_id=question.id,
            selected_choice_index=2,
            is_correct=False,
            time_taken=15.5,
            answered_at=datetime.now(),
            points_earned=0,
            streak_bonus=0
        )
        db.session.add(answer)
        db.session.commit()
        
        answer_dict = answer.to_dict()
        
        assert answer_dict['question_id'] == question.id
        assert answer_dict['selected_choice_index'] == 2
        assert answer_dict['is_correct'] is False
        assert answer_dict['time_taken'] == 15.5
        assert answer_dict['points_earned'] == 0
        assert answer_dict['streak_bonus'] == 0

    def test_score_to_dict(self, app_context):
        """Test Score to_dict method - line 299"""
        # Create a user and game session
        user = User(username='testuser', email='test@example.com', password_hash='hashedpassword')
        db.session.add(user)
        db.session.flush()
        
        session = GameSession(
            session_token='test_token_456',
            user_id=user.id,
            total_questions=5,
            correct_answers=4
        )
        db.session.add(session)
        db.session.flush()
        
        score = Score(
            user_id=user.id,
            game_session_id=session.id,
            score=850,
            accuracy_percentage=80.0,
            questions_answered=5,
            time_taken=120,
            streak=4,
            category=Category.BASICS,
            difficulty=Difficulty.MEDIUM,
            achieved_at=datetime.now()
        )
        db.session.add(score)
        db.session.commit()
        
        score_dict = score.to_dict()
        
        assert score_dict['score'] == 850
        assert score_dict['accuracy_percentage'] == 80.0
        assert score_dict['questions_answered'] == 5
        assert score_dict['time_taken'] == 120
        assert score_dict['streak'] == 4
        assert score_dict['category'] == 'basics'
        assert score_dict['difficulty'] == 'medium'
        assert score_dict['username'] == 'testuser'
        assert score_dict['user_id'] == user.id

    def test_score_anonymous_user(self, app_context):
        """Test Score with anonymous user"""
        # Create a game session without user
        session = GameSession(
            session_token='test_token_anon',
            total_questions=3,
            correct_answers=2
        )
        db.session.add(session)
        db.session.flush()
        
        score = Score(
            user_id=None,
            game_session_id=session.id,
            score=400,
            accuracy_percentage=66.7,
            questions_answered=3,
            time_taken=90,
            streak=2,
            anonymous_name='Anonymous Player',
            achieved_at=datetime.now()
        )
        db.session.add(score)
        db.session.commit()
        
        score_dict = score.to_dict()
        
        assert score_dict['username'] == 'Anonymous Player'
        assert score_dict['user_id'] is None