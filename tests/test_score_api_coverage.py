"""
Test coverage for score API functionality
Lines 545-581 (/api/save-score route)
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app


class TestScoreAPIRoutes:
    """Test score API routes to cover lines 545-581"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('app.get_or_create_game_session')
    @patch('app.game')
    @patch('app.GameSessionService.complete_session')
    @patch('app.ScoreService.save_score')
    @patch('app.HAS_LOGIN', False)
    def test_save_score_anonymous_user_success(self, mock_save_score, mock_complete_session,
                                              mock_game, mock_get_session):
        """Test successful score saving for anonymous user (lines 547-578)"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session.id = 1
        mock_get_session.return_value = mock_session
        
        mock_game.cards = [MagicMock() for _ in range(10)]  # 10 questions
        mock_game.score = 7  # 7 correct answers
        mock_game.get_score_percentage.return_value = 70.0
        
        mock_score_record = MagicMock()
        mock_score_record.id = 123
        mock_score_record.score = 70  # 7 * 10 points
        mock_score_record.accuracy_percentage = 70.0
        mock_save_score.return_value = mock_score_record
        
        # Test request
        response = self.app.post('/api/save-score',
                                json={'anonymous_name': 'Player123'},
                                content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['score_id'] == 123
        assert data['final_score'] == 70
        assert data['accuracy'] == 70.0
        
        # Verify function calls
        mock_get_session.assert_called_once()
        mock_complete_session.assert_called_once_with(1)
        mock_save_score.assert_called_once_with(
            game_session_id=1,
            score=70,  # 7 correct * 10 points
            accuracy_percentage=70.0,
            questions_answered=10,
            user_id=None,  # Anonymous user
            anonymous_name='Player123'
        )
    
    @patch('app.get_or_create_game_session')
    @patch('app.game')
    @patch('app.GameSessionService.complete_session')
    @patch('app.ScoreService.save_score')
    @patch('app.UserService.update_user_stats')
    @patch('app.HAS_LOGIN', True)
    @patch('app.current_user')
    def test_save_score_authenticated_user_success(self, mock_current_user, mock_update_stats,
                                                  mock_save_score, mock_complete_session,
                                                  mock_game, mock_get_session):
        """Test successful score saving for authenticated user (lines 547-578)"""
        # Setup authenticated user
        mock_current_user.is_authenticated = True
        mock_current_user.id = 42
        
        # Setup mocks
        mock_session = MagicMock()
        mock_session.id = 2
        mock_get_session.return_value = mock_session
        
        mock_game.cards = [MagicMock() for _ in range(5)]  # 5 questions
        mock_game.score = 4  # 4 correct answers
        mock_game.get_score_percentage.return_value = 80.0
        
        mock_score_record = MagicMock()
        mock_score_record.id = 456
        mock_score_record.score = 40  # 4 * 10 points
        mock_score_record.accuracy_percentage = 80.0
        mock_save_score.return_value = mock_score_record
        
        # Test request
        response = self.app.post('/api/save-score',
                                json={'anonymous_name': 'ShouldBeIgnored'},
                                content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['score_id'] == 456
        assert data['final_score'] == 40
        assert data['accuracy'] == 80.0
        
        # Verify function calls
        mock_save_score.assert_called_once_with(
            game_session_id=2,
            score=40,  # 4 correct * 10 points
            accuracy_percentage=80.0,
            questions_answered=5,
            user_id=42,  # Authenticated user ID
            anonymous_name='ShouldBeIgnored'
        )
        
        # Verify user stats were updated
        mock_update_stats.assert_called_once_with(42, mock_session)
    
    @patch('app.get_or_create_game_session')
    @patch('app.game')
    @patch('app.GameSessionService.complete_session')
    @patch('app.ScoreService.save_score')
    @patch('app.HAS_LOGIN', True)
    @patch('app.current_user')
    def test_save_score_unauthenticated_user_with_login(self, mock_current_user, mock_save_score,
                                                       mock_complete_session, mock_game, mock_get_session):
        """Test score saving for unauthenticated user when login is available (lines 563-566)"""
        # Setup unauthenticated user
        mock_current_user.is_authenticated = False
        
        # Setup mocks
        mock_session = MagicMock()
        mock_session.id = 3
        mock_get_session.return_value = mock_session
        
        mock_game.cards = [MagicMock() for _ in range(8)]
        mock_game.score = 6
        mock_game.get_score_percentage.return_value = 75.0
        
        mock_score_record = MagicMock()
        mock_score_record.id = 789
        mock_score_record.score = 60
        mock_score_record.accuracy_percentage = 75.0
        mock_save_score.return_value = mock_score_record
        
        # Test request
        response = self.app.post('/api/save-score',
                                json={'anonymous_name': 'GuestPlayer'},
                                content_type='application/json')
        
        assert response.status_code == 200
        
        # Should save with user_id=None even when login is available but user not authenticated
        mock_save_score.assert_called_once_with(
            game_session_id=3,
            score=60,
            accuracy_percentage=75.0,
            questions_answered=8,
            user_id=None,  # Not authenticated
            anonymous_name='GuestPlayer'
        )
    
    @patch('app.get_or_create_game_session')
    @patch('app.game')
    def test_save_score_default_anonymous_name(self, mock_game, mock_get_session):
        """Test score saving with default anonymous name (line 566)"""
        # Setup mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        mock_game.cards = [MagicMock()]
        mock_game.score = 1
        mock_game.get_score_percentage.return_value = 100.0
        
        with patch('app.GameSessionService.complete_session'):
            with patch('app.ScoreService.save_score') as mock_save_score:
                mock_score_record = MagicMock()
                mock_save_score.return_value = mock_score_record
                
                # Test request without anonymous_name
                response = self.app.post('/api/save-score',
                                        json={},
                                        content_type='application/json')
                
                assert response.status_code == 200
                
                # Should use default 'Anonymous'
                args, kwargs = mock_save_score.call_args
                assert kwargs['anonymous_name'] == 'Anonymous'
    
    @patch('app.get_or_create_game_session')
    def test_save_score_session_creation_exception(self, mock_get_session):
        """Test score saving when session creation fails (lines 579-580)"""
        mock_get_session.side_effect = Exception("Session creation failed")
        
        response = self.app.post('/api/save-score',
                                json={'anonymous_name': 'TestPlayer'},
                                content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Session creation failed' in data['message']
    
    @patch('app.get_or_create_game_session')
    @patch('app.game')
    @patch('app.GameSessionService.complete_session')
    def test_save_score_complete_session_exception(self, mock_complete_session, mock_game, mock_get_session):
        """Test score saving when session completion fails (lines 579-580)"""
        # Setup mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_game.cards = []
        mock_game.score = 0
        mock_game.get_score_percentage.return_value = 0.0
        
        mock_complete_session.side_effect = Exception("Session completion failed")
        
        response = self.app.post('/api/save-score',
                                json={'anonymous_name': 'TestPlayer'},
                                content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Session completion failed' in data['message']
    
    @patch('app.get_or_create_game_session')
    @patch('app.game')
    @patch('app.GameSessionService.complete_session')
    @patch('app.ScoreService.save_score')
    def test_save_score_save_exception(self, mock_save_score, mock_complete_session, mock_game, mock_get_session):
        """Test score saving when score saving fails (lines 579-580)"""
        # Setup mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_game.cards = [MagicMock() for _ in range(3)]
        mock_game.score = 2
        mock_game.get_score_percentage.return_value = 66.7
        
        mock_save_score.side_effect = Exception("Score saving failed")
        
        response = self.app.post('/api/save-score',
                                json={'anonymous_name': 'TestPlayer'},
                                content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Score saving failed' in data['message']
    
    @patch('app.get_or_create_game_session')
    @patch('app.game')
    @patch('app.GameSessionService.complete_session')
    @patch('app.ScoreService.save_score')
    @patch('app.UserService.update_user_stats')
    @patch('app.HAS_LOGIN', True)
    @patch('app.current_user')
    def test_save_score_user_stats_update_exception(self, mock_current_user, mock_update_stats,
                                                   mock_save_score, mock_complete_session,
                                                   mock_game, mock_get_session):
        """Test score saving when user stats update fails (lines 579-580)"""
        # Setup authenticated user
        mock_current_user.is_authenticated = True
        mock_current_user.id = 99
        
        # Setup mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_game.cards = [MagicMock()]
        mock_game.score = 1
        mock_game.get_score_percentage.return_value = 100.0
        
        mock_score_record = MagicMock()
        mock_save_score.return_value = mock_score_record
        
        # User stats update fails
        mock_update_stats.side_effect = Exception("User stats update failed")
        
        response = self.app.post('/api/save-score',
                                json={'anonymous_name': 'TestPlayer'},
                                content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'User stats update failed' in data['message']
    
    def test_save_score_no_json_data(self):
        """Test score saving with no JSON data"""
        response = self.app.post('/api/save-score')
        
        # Should handle gracefully (either succeed with empty data or fail)
        assert response.status_code in [200, 400]
    
    @patch('app.get_or_create_game_session')
    @patch('app.game')
    @patch('app.GameSessionService.complete_session')
    @patch('app.ScoreService.save_score')
    def test_save_score_scoring_calculation(self, mock_save_score, mock_complete_session, 
                                           mock_game, mock_get_session):
        """Test the scoring calculation logic (10 points per correct answer)"""
        # Setup mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        # Test different score scenarios
        test_cases = [
            (0, 0),    # 0 correct = 0 points
            (1, 10),   # 1 correct = 10 points
            (5, 50),   # 5 correct = 50 points
            (10, 100), # 10 correct = 100 points
        ]
        
        for correct_answers, expected_score in test_cases:
            mock_game.cards = [MagicMock() for _ in range(10)]
            mock_game.score = correct_answers
            mock_game.get_score_percentage.return_value = (correct_answers / 10) * 100
            
            mock_score_record = MagicMock()
            mock_score_record.id = 1
            mock_score_record.score = expected_score
            mock_score_record.accuracy_percentage = (correct_answers / 10) * 100
            mock_save_score.return_value = mock_score_record
            
            response = self.app.post('/api/save-score',
                                    json={'anonymous_name': 'TestPlayer'},
                                    content_type='application/json')
            
            # Verify the score calculation
            args, kwargs = mock_save_score.call_args
            assert kwargs['score'] == expected_score
            
            mock_save_score.reset_mock()


class TestScoreAPIEdgeCases:
    """Test edge cases for score API functionality"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('app.get_or_create_game_session')
    @patch('app.game')
    @patch('app.GameSessionService.complete_session')
    @patch('app.ScoreService.save_score')
    def test_save_score_zero_questions(self, mock_save_score, mock_complete_session, 
                                      mock_game, mock_get_session):
        """Test score saving with zero questions"""
        # Setup mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        mock_game.cards = []  # No questions
        mock_game.score = 0
        mock_game.get_score_percentage.return_value = 0.0
        
        mock_score_record = MagicMock()
        mock_score_record.id = 1
        mock_score_record.score = 0
        mock_score_record.accuracy_percentage = 0.0
        mock_save_score.return_value = mock_score_record
        
        response = self.app.post('/api/save-score',
                                json={'anonymous_name': 'TestPlayer'},
                                content_type='application/json')
        
        assert response.status_code == 200
        
        # Should handle zero questions gracefully
        args, kwargs = mock_save_score.call_args
        assert kwargs['questions_answered'] == 0
        assert kwargs['score'] == 0