"""
Test coverage for game API routes and flows
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from test_utils import MockUser, MockQuestion, MockGameSession, create_mock_user, create_mock_question, create_mock_session


class TestGameAPIRoutes:
    """Test game API routes to cover lines 587-601, 651-663, 669-676, 682-731"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('app.HAS_LOGIN', False)
    def test_profile_no_login_redirect(self):
        """Test profile route when login not available (line 587-588)"""
        with patch('app.redirect') as mock_redirect:
            with patch('app.url_for') as mock_url_for:
                mock_url_for.return_value = '/login'
                from app import profile
                result = profile()
                mock_redirect.assert_called_once()
    
    @patch('app.HAS_LOGIN', True)
    @patch('app.current_user')
    def test_profile_not_authenticated_redirect(self, mock_user):
        """Test profile route when user not authenticated (line 587-588)"""
        mock_user.is_authenticated = False
        
        with patch('app.redirect') as mock_redirect:
            with patch('app.url_for') as mock_url_for:
                mock_url_for.return_value = '/login'
                from app import profile
                result = profile()
                mock_redirect.assert_called_once()
    
    @patch('app.HAS_LOGIN', True)
    @patch('app.current_user')
    @patch('app.GameSessionService')
    @patch('app.ScoreService')
    def test_profile_success(self, mock_score_service, mock_session_service, mock_user):
        """Test profile route success path (lines 591-597)"""
        mock_user.is_authenticated = True
        mock_user.id = 1
        
        mock_sessions = [{'id': 1, 'score': 100}]
        mock_scores = [{'score': 100, 'date': '2024-01-01'}]
        
        mock_session_service.get_user_sessions.return_value = mock_sessions
        mock_score_service.get_user_best_scores.return_value = mock_scores
        
        with patch('app.render_template') as mock_render:
            from app import profile
            result = profile()
            
            mock_render.assert_called_once_with(
                'profile.html',
                user=mock_user,
                recent_sessions=mock_sessions,
                best_scores=mock_scores
            )
    
    @patch('app.HAS_LOGIN', True)
    @patch('app.current_user')
    @patch('app.GameSessionService')
    @patch('app.ScoreService')
    def test_profile_exception_handling(self, mock_score_service, mock_session_service, mock_user):
        """Test profile route exception handling (lines 598-601)"""
        mock_user.is_authenticated = True
        mock_user.id = 1
        
        # Mock service to raise exception
        mock_session_service.get_user_sessions.side_effect = Exception("Database error")
        
        with patch('app.render_template') as mock_render:
            from app import profile
            result = profile()
            
            # Should render with empty lists due to exception
            mock_render.assert_called_with(
                'profile.html',
                user=mock_user,
                recent_sessions=[],
                best_scores=[]
            )
    
    @patch('app.game')
    def test_api_current_card_success(self, mock_game):
        """Test /api/current-card success path (lines 651-661)"""
        # Mock card
        mock_card = MagicMock()
        mock_card.to_dict.return_value = {'question': 'Test?', 'answer': 'Test'}
        mock_game.get_current_card.return_value = mock_card
        mock_game.current_card_index = 0
        mock_game.cards = [mock_card]
        mock_game.score = 5
        mock_game.get_score_percentage.return_value = 50.0
        
        response = self.app.get('/api/current-card')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'card' in data
        assert 'game_stats' in data
        assert data['game_stats']['score'] == 5
        assert data['game_stats']['percentage'] == 50.0
    
    @patch('app.game')
    def test_api_current_card_no_card(self, mock_game):
        """Test /api/current-card when no card available (line 662-663)"""
        mock_game.get_current_card.return_value = None
        
        response = self.app.get('/api/current-card')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'No current card available'
    
    @patch('app.game')
    def test_api_flip_card_success(self, mock_game):
        """Test /api/flip-card success path (lines 669-675)"""
        mock_card = MagicMock()
        mock_card.to_dict.return_value = {'question': 'Test?', 'answer': 'Test'}
        mock_game.get_current_card.return_value = mock_card
        
        response = self.app.post('/api/flip-card')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'card' in data
        
        # Verify flip_card was called
        mock_card.flip_card.assert_called_once()
    
    @patch('app.game')
    def test_api_flip_card_no_card(self, mock_game):
        """Test /api/flip-card when no card available (line 676)"""
        mock_game.get_current_card.return_value = None
        
        response = self.app.post('/api/flip-card')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'No card to flip'
    
    def test_api_answer_card_no_choice(self):
        """Test /api/answer-card with no choice provided (lines 684-685)"""
        response = self.app.post('/api/answer-card', 
                                json={},
                                content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'No choice provided'
    
    @patch('app.game')
    def test_api_answer_card_no_current_card(self, mock_game):
        """Test /api/answer-card with no current card (lines 687-689)"""
        mock_game.get_current_card.return_value = None
        
        response = self.app.post('/api/answer-card',
                                json={'choice_index': 0},
                                content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'No current card'
    
    @patch('app.game')
    @patch('app.get_or_create_game_session')
    @patch('app.Question')
    @patch('app.AnswerService')
    @patch('app.GameSessionService')
    @patch('app.HAS_LOGIN', True)
    @patch('app.current_user')
    def test_api_answer_card_correct_answer(self, mock_user, mock_session_service, 
                                          mock_answer_service, mock_question, 
                                          mock_get_session, mock_game):
        """Test /api/answer-card with correct answer (lines 691-734)"""
        # Set up mocks with JSON-serializable objects
        mock_user_obj = create_mock_user(user_id=1)
        mock_user.is_authenticated = True
        mock_user.id = 1
        mock_user.to_dict = mock_user_obj.to_dict
        
        mock_trivia_question = create_mock_question(
            question_id=1,
            question_text="Test question?",
            correct_answer="Correct answer"
        )
        
        mock_card = MagicMock()
        mock_card.trivia_question = mock_trivia_question
        mock_card.is_answered_correctly = True
        # Add a proper to_dict method that returns serializable data
        mock_card.to_dict.return_value = {
            'question': "Test question?",
            'choices': ["Correct answer", "Wrong answer 1", "Wrong answer 2", "Wrong answer 3"],
            'is_answered': True,
            'is_correct': True
        }
        
        mock_game.get_current_card.return_value = mock_card
        mock_game.answer_current_card = MagicMock()
        mock_game.current_card_index = 0
        mock_game.score = 1
        mock_game.cards = [mock_card]
        # Add a proper get_score_percentage method that returns a number
        mock_game.get_score_percentage.return_value = 100.0
        
        mock_session = create_mock_session(session_id=1, user_id=1)
        mock_get_session.return_value = mock_session
        
        mock_db_question = create_mock_question(question_id=1)
        mock_question.query.filter_by.return_value.first.return_value = mock_db_question
        
        response = self.app.post('/api/answer-card',
                                json={'choice_index': 0},
                                content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['correct'] is True
        assert data['correct_answer'] == "Correct answer"
        assert data['selected_choice'] == 0
        
        # Verify database operations were called
        mock_answer_service.record_answer.assert_called_once()
        mock_session_service.update_session_progress.assert_called_once()
    
    @patch('app.game')
    @patch('app.get_or_create_game_session')
    def test_api_answer_card_database_exception(self, mock_get_session, mock_game):
        """Test /api/answer-card with database exception (lines 720-721)"""
        # Set up mocks with JSON-serializable objects
        mock_trivia_question = create_mock_question(
            question_id=1,
            question_text="Test question?",
            correct_answer="Correct answer"
        )
        # Override for wrong answer scenario
        mock_trivia_question.correct_choice_index = 1  # Wrong answer
        
        mock_card = MagicMock()
        mock_card.trivia_question = mock_trivia_question
        
        mock_game.get_current_card.return_value = mock_card
        mock_game.answer_current_card = MagicMock()
        mock_game.score = 0
        
        # Mock database session to raise exception
        mock_get_session.side_effect = Exception("Database error")
        
        response = self.app.post('/api/answer-card',
                                json={'choice_index': 0},
                                content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['correct'] is False  # Wrong choice (0 vs 1)
        assert data['correct_answer'] == "Correct answer"
        
        # Verify game.answer_current_card was still called despite DB error
        mock_game.answer_current_card.assert_called_once_with(False)


class TestGameUtilityFunctions:
    """Test utility functions related to game management"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('app.HAS_LOGIN', False)
    @patch('app.GameSession')
    def test_get_or_create_game_session_no_login(self, mock_session_class):
        """Test get_or_create_game_session without login"""
        from app import get_or_create_game_session
        
        # Should create anonymous session
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        with patch('app.db.session') as mock_db_session:
            result = get_or_create_game_session()
            
            # Verify session creation
            mock_session_class.assert_called_once()
            mock_db_session.add.assert_called_once_with(mock_session)
            mock_db_session.commit.assert_called_once()
    
    @patch('app.HAS_LOGIN', True)
    @patch('app.current_user')
    @patch('app.GameSession')
    def test_get_or_create_game_session_with_user(self, mock_session_class, mock_user):
        """Test get_or_create_game_session with authenticated user"""
        from app import get_or_create_game_session
        
        mock_user.is_authenticated = True
        mock_user.id = 1
        
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        with patch('app.db.session') as mock_db_session:
            result = get_or_create_game_session()
            
            # Verify session creation with user
            mock_session_class.assert_called_once()
            mock_db_session.add.assert_called_once_with(mock_session)
            mock_db_session.commit.assert_called_once()