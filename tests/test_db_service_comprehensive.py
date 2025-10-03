"""
PHASE 3: Comprehensive database service testing
Testing all service layer components with proper mocking
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime, timezone

# Add the parent directory to sys.path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_service import QuestionService, GameSessionService, AnswerService, ScoreService, UserService
from models import Category, Difficulty


class TestQuestionService:
    """Comprehensive tests for QuestionService"""
    
    @patch('db_service.Question')
    def test_get_questions_by_criteria_all_filters(self, mock_question):
        """Test get_questions_by_criteria with all filters"""
        # Mock the query chain
        mock_query = Mock()
        mock_question.query.filter.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = ['question1', 'question2']
        
        # Test with all parameters
        result = QuestionService.get_questions_by_criteria(
            categories=[Category.BASICS, Category.FUNCTIONS],
            difficulty=Difficulty.EASY,
            limit=10,
            exclude_ids=[1, 2, 3]
        )
        
        assert result == ['question1', 'question2']
        mock_query.all.assert_called_once()
    
    @patch('db_service.Question')
    def test_get_questions_by_criteria_no_filters(self, mock_question):
        """Test get_questions_by_criteria with no filters"""
        mock_query = Mock()
        mock_question.query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = ['all_questions']
        
        result = QuestionService.get_questions_by_criteria()
        
        assert result == ['all_questions']
        mock_query.all.assert_called_once()
    
    @patch('db_service.Question')
    def test_get_question_by_id_found(self, mock_question):
        """Test get_question_by_id when question exists"""
        mock_question.query.filter_by.return_value.first.return_value = 'found_question'
        
        result = QuestionService.get_question_by_id(1)
        
        assert result == 'found_question'
        mock_question.query.filter_by.assert_called_once_with(id=1, is_active=True)
    
    @patch('db_service.Question')
    def test_get_question_by_id_not_found(self, mock_question):
        """Test get_question_by_id when question doesn't exist"""
        mock_question.query.filter_by.return_value.first.return_value = None
        
        result = QuestionService.get_question_by_id(999)
        
        assert result is None
    
    @patch('db_service.db.session')
    @patch('db_service.Question')
    def test_create_question_success(self, mock_question, mock_session):
        """Test successful question creation"""
        mock_question.return_value = 'new_question'
        
        result = QuestionService.create_question(
            question_text="Test question?",
            correct_answer="Test answer",
            choices=["A", "B", "C", "D"],
            correct_choice_index=0,
            category=Category.BASICS,
            difficulty=Difficulty.EASY,
            explanation="Test explanation",
            created_by=1
        )
        
        assert result == 'new_question'
        mock_session.add.assert_called_once_with('new_question')
        mock_session.commit.assert_called_once()
    
    @patch('db_service.db.session')
    @patch('db_service.Question')
    def test_create_question_exception(self, mock_question, mock_session):
        """Test question creation with database exception"""
        mock_session.commit.side_effect = Exception("Database error")
        
        result = QuestionService.create_question(
            question_text="Test question?",
            correct_answer="Test answer", 
            choices=["A", "B"],
            correct_choice_index=0,
            category=Category.BASICS,
            difficulty=Difficulty.EASY
        )
        
        assert result is None
        mock_session.rollback.assert_called_once()


class TestGameSessionService:
    """Comprehensive tests for GameSessionService"""
    
    @patch('db_service.db.session')
    @patch('db_service.GameSession')
    @patch('db_service.uuid.uuid4')
    def test_create_session_with_user(self, mock_uuid, mock_session_class, mock_db_session):
        """Test creating session with authenticated user"""
        mock_uuid.return_value.hex = 'test_token'
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        result = GameSessionService.create_session(user_id=1)
        
        assert result == mock_session
        mock_db_session.add.assert_called_once_with(mock_session)
        mock_db_session.commit.assert_called_once()
    
    @patch('db_service.db.session')
    @patch('db_service.GameSession')
    @patch('db_service.uuid.uuid4')
    def test_create_session_anonymous(self, mock_uuid, mock_session_class, mock_db_session):
        """Test creating session for anonymous user"""
        mock_uuid.return_value.hex = 'anon_token'
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        result = GameSessionService.create_session(user_id=None)
        
        assert result == mock_session
        mock_db_session.add.assert_called_once_with(mock_session)
        mock_db_session.commit.assert_called_once()
    
    @patch('db_service.db.session')
    @patch('db_service.GameSession')
    def test_create_session_exception(self, mock_session_class, mock_db_session):
        """Test session creation with database exception"""
        mock_db_session.commit.side_effect = Exception("DB error")
        
        result = GameSessionService.create_session(user_id=1)
        
        assert result is None
        mock_db_session.rollback.assert_called_once()
    
    @patch('db_service.GameSession')
    def test_get_session_by_token_found(self, mock_session):
        """Test getting session by token when exists"""
        mock_session.query.filter_by.return_value.first.return_value = 'found_session'
        
        result = GameSessionService.get_session_by_token('test_token')
        
        assert result == 'found_session'
        mock_session.query.filter_by.assert_called_once_with(session_token='test_token')
    
    @patch('db_service.GameSession')
    def test_get_session_by_token_not_found(self, mock_session):
        """Test getting session by token when doesn't exist"""
        mock_session.query.filter_by.return_value.first.return_value = None
        
        result = GameSessionService.get_session_by_token('invalid_token')
        
        assert result is None
    
    @patch('db_service.db.session')
    def test_update_session_progress_success(self, mock_db_session):
        """Test successful session progress update"""
        mock_session = Mock()
        mock_db_session.get.return_value = mock_session
        
        result = GameSessionService.update_session_progress(
            session_id=1,
            current_question_index=5,
            correct_answers=3,
            incorrect_answers=2,
            total_score=30
        )
        
        assert result is True
        assert mock_session.current_question_index == 5
        assert mock_session.correct_answers == 3
        assert mock_session.incorrect_answers == 2
        assert mock_session.total_score == 30
        mock_db_session.commit.assert_called_once()
    
    @patch('db_service.db.session')
    def test_update_session_progress_not_found(self, mock_db_session):
        """Test session progress update when session not found"""
        mock_db_session.get.return_value = None
        
        result = GameSessionService.update_session_progress(
            session_id=999,
            current_question_index=0,
            correct_answers=0,
            incorrect_answers=0,
            total_score=0
        )
        
        assert result is False


class TestAnswerService:
    """Comprehensive tests for AnswerService"""
    
    @patch('db_service.db.session')
    @patch('db_service.Answer')
    def test_record_answer_success(self, mock_answer, mock_db_session):
        """Test successful answer recording"""
        mock_answer.return_value = 'new_answer'
        
        result = AnswerService.record_answer(
            game_session_id=1,
            question_id=1,
            selected_choice_index=2,
            is_correct=True,
            user_id=1
        )
        
        assert result == 'new_answer'
        mock_db_session.add.assert_called_once_with('new_answer')
        mock_db_session.commit.assert_called_once()
    
    @patch('db_service.db.session')
    @patch('db_service.Answer')
    def test_record_answer_anonymous(self, mock_answer, mock_db_session):
        """Test answer recording for anonymous user"""
        mock_answer.return_value = 'anon_answer'
        
        result = AnswerService.record_answer(
            game_session_id=1,
            question_id=1,
            selected_choice_index=0,
            is_correct=False,
            user_id=None
        )
        
        assert result == 'anon_answer'
        mock_db_session.add.assert_called_once_with('anon_answer')
        mock_db_session.commit.assert_called_once()
    
    @patch('db_service.db.session')
    @patch('db_service.Answer')
    def test_record_answer_exception(self, mock_answer, mock_db_session):
        """Test answer recording with database exception"""
        mock_db_session.commit.side_effect = Exception("DB error")
        
        result = AnswerService.record_answer(
            game_session_id=1,
            question_id=1,
            selected_choice_index=0,
            is_correct=True
        )
        
        assert result is None
        mock_db_session.rollback.assert_called_once()
    
    @patch('db_service.Answer')
    def test_get_session_answers(self, mock_answer):
        """Test getting answers for a session"""
        mock_answer.query.filter_by.return_value.all.return_value = ['answer1', 'answer2']
        
        result = AnswerService.get_session_answers(1)
        
        assert result == ['answer1', 'answer2']
        mock_answer.query.filter_by.assert_called_once_with(game_session_id=1)


class TestScoreService:
    """Comprehensive tests for ScoreService"""
    
    @patch('db_service.db.session')
    @patch('db_service.Score')
    def test_save_score_success(self, mock_score, mock_db_session):
        """Test successful score saving"""
        mock_score.return_value = 'new_score'
        
        result = ScoreService.save_score(
            user_id=1,
            player_name="Test Player",
            score=85,
            questions_answered=10,
            category=Category.BASICS,
            difficulty=Difficulty.EASY
        )
        
        assert result == 'new_score'
        mock_db_session.add.assert_called_once_with('new_score')
        mock_db_session.commit.assert_called_once()
    
    @patch('db_service.db.session')
    @patch('db_service.Score')
    def test_save_score_exception(self, mock_score, mock_db_session):
        """Test score saving with database exception"""
        mock_db_session.commit.side_effect = Exception("DB error")
        
        result = ScoreService.save_score(
            user_id=None,
            player_name="Anonymous", 
            score=50,
            questions_answered=5
        )
        
        assert result is None
        mock_db_session.rollback.assert_called_once()
    
    @patch('db_service.Score')
    def test_get_leaderboard_filtered(self, mock_score):
        """Test getting filtered leaderboard"""
        mock_query = Mock()
        mock_score.query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = ['score1', 'score2']
        
        result = ScoreService.get_leaderboard(
            category=Category.BASICS,
            difficulty=Difficulty.EASY,
            limit=10
        )
        
        assert result == ['score1', 'score2']
        mock_query.all.assert_called_once()
    
    @patch('db_service.Score')
    def test_get_leaderboard_no_filters(self, mock_score):
        """Test getting unfiltered leaderboard"""
        mock_query = Mock()
        mock_score.query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = ['all_scores']
        
        result = ScoreService.get_leaderboard(limit=50)
        
        assert result == ['all_scores']
        mock_query.all.assert_called_once()


class TestUserService:
    """Comprehensive tests for UserService"""
    
    @patch('db_service.db.session')
    @patch('db_service.User')
    def test_create_user_success(self, mock_user, mock_db_session):
        """Test successful user creation"""
        mock_user.return_value = 'new_user'
        
        result = UserService.create_user(
            username="testuser",
            email="test@example.com", 
            password="password123"
        )
        
        assert result == 'new_user'
        mock_db_session.add.assert_called_once_with('new_user')
        mock_db_session.commit.assert_called_once()
    
    @patch('db_service.db.session')
    @patch('db_service.User')
    def test_create_user_exception(self, mock_user, mock_db_session):
        """Test user creation with database exception"""
        mock_db_session.commit.side_effect = Exception("DB error")
        
        result = UserService.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        assert result is None
        mock_db_session.rollback.assert_called_once()
    
    @patch('db_service.User')
    def test_get_user_by_username_found(self, mock_user):
        """Test getting user by username when exists"""
        mock_user.query.filter_by.return_value.first.return_value = 'found_user'
        
        result = UserService.get_user_by_username('testuser')
        
        assert result == 'found_user'
        mock_user.query.filter_by.assert_called_once_with(username='testuser')
    
    @patch('db_service.User')
    def test_get_user_by_username_not_found(self, mock_user):
        """Test getting user by username when doesn't exist"""
        mock_user.query.filter_by.return_value.first.return_value = None
        
        result = UserService.get_user_by_username('nonexistent')
        
        assert result is None
    
    @patch('db_service.User')
    def test_get_user_by_email_found(self, mock_user):
        """Test getting user by email when exists"""
        mock_user.query.filter_by.return_value.first.return_value = 'found_user'
        
        result = UserService.get_user_by_email('test@example.com')
        
        assert result == 'found_user'
        mock_user.query.filter_by.assert_called_once_with(email='test@example.com')
    
    @patch('db_service.User')
    def test_get_user_by_email_not_found(self, mock_user):
        """Test getting user by email when doesn't exist"""
        mock_user.query.filter_by.return_value.first.return_value = None
        
        result = UserService.get_user_by_email('nonexistent@example.com')
        
        assert result is None


if __name__ == '__main__':
    unittest.main()