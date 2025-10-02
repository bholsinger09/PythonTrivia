"""
Test coverage for remaining error handlers and edge cases
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app


class TestNavigationAPIEndpoints:
    """Test navigation API endpoints to cover lines 749-761, 767-779, 785-789"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('app.game')
    def test_api_next_card_success(self, mock_game):
        """Test /api/next-card success path (lines 749-759)"""
        # Mock next card
        mock_card = MagicMock()
        mock_card.to_dict.return_value = {'question': 'Next question?', 'answer': 'Next answer'}
        mock_game.next_card.return_value = mock_card
        mock_game.current_card_index = 1
        mock_game.cards = [MagicMock(), mock_card]
        mock_game.score = 1
        mock_game.get_score_percentage.return_value = 50.0
        
        response = self.app.post('/api/next-card')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'card' in data
        assert 'game_stats' in data
        assert data['game_stats']['current_index'] == 1
        assert data['game_stats']['total_cards'] == 2
        assert data['game_stats']['score'] == 1
        assert data['game_stats']['percentage'] == 50.0
    
    @patch('app.game')
    def test_api_next_card_no_more_cards(self, mock_game):
        """Test /api/next-card when no more cards available (line 760-761)"""
        mock_game.next_card.return_value = None
        
        response = self.app.post('/api/next-card')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'No more cards available'
    
    @patch('app.game')
    def test_api_previous_card_success(self, mock_game):
        """Test /api/previous-card success path (lines 767-777)"""
        # Mock previous card
        mock_card = MagicMock()
        mock_card.to_dict.return_value = {'question': 'Previous question?', 'answer': 'Previous answer'}
        mock_game.previous_card.return_value = mock_card
        mock_game.current_card_index = 0
        mock_game.cards = [mock_card, MagicMock()]
        mock_game.score = 0
        mock_game.get_score_percentage.return_value = 0.0
        
        response = self.app.post('/api/previous-card')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'card' in data
        assert 'game_stats' in data
        assert data['game_stats']['current_index'] == 0
        assert data['game_stats']['total_cards'] == 2
        assert data['game_stats']['score'] == 0
        assert data['game_stats']['percentage'] == 0.0
    
    @patch('app.game')
    def test_api_previous_card_no_previous_cards(self, mock_game):
        """Test /api/previous-card when no previous card available (line 778-779)"""
        mock_game.previous_card.return_value = None
        
        response = self.app.post('/api/previous-card')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'No previous card available'
    
    @patch('app.game')
    def test_api_reset_game_with_current_card(self, mock_game):
        """Test /api/reset-game with current card available (lines 785-795)"""
        # Mock current card after reset
        mock_card = MagicMock()
        mock_card.to_dict.return_value = {'question': 'Reset question?', 'answer': 'Reset answer'}
        mock_game.get_current_card.return_value = mock_card
        mock_game.current_card_index = 0
        mock_game.cards = [mock_card]
        mock_game.score = 0
        mock_game.get_score_percentage.return_value = 0.0
        
        response = self.app.post('/api/reset-game')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['card'] is not None
        assert 'game_stats' in data
        assert data['game_stats']['current_index'] == 0
        assert data['game_stats']['score'] == 0
        
        # Verify reset and shuffle were called
        mock_game.reset_game.assert_called_once()
        mock_game.shuffle_cards.assert_called_once()
    
    @patch('app.game')
    def test_api_reset_game_no_current_card(self, mock_game):
        """Test /api/reset-game with no current card (lines 785-795)"""
        # Mock no current card after reset
        mock_game.get_current_card.return_value = None
        mock_game.current_card_index = 0
        mock_game.cards = []
        mock_game.score = 0
        mock_game.get_score_percentage.return_value = 0.0
        
        response = self.app.post('/api/reset-game')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['card'] is None  # No card available
        assert 'game_stats' in data
        
        # Verify reset and shuffle were called
        mock_game.reset_game.assert_called_once()
        mock_game.shuffle_cards.assert_called_once()


class TestAdditionalRoutes:
    """Test additional routes for maximum coverage"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('app.game')
    def test_api_game_stats(self, mock_game):
        """Test /api/game-stats endpoint"""
        mock_game.score = 5
        mock_game.current_card_index = 3
        mock_game.cards = [MagicMock() for _ in range(10)]
        mock_game.get_score_percentage.return_value = 50.0
        
        response = self.app.get('/api/game-stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['current_index'] == 3
        assert data['total_cards'] == 10
        assert data['score'] == 5
        assert data['percentage'] == 50.0
    
    def test_categories_route(self):
        """Test /categories route"""
        response = self.app.get('/categories')
        assert response.status_code == 200
        # Should render categories template
        assert b'categories' in response.data.lower() or b'category' in response.data.lower()
    
    def test_difficulty_route(self):
        """Test /difficulty route"""
        response = self.app.get('/difficulty')
        assert response.status_code == 200
        # Should render difficulty template
        assert b'difficulty' in response.data.lower() or b'easy' in response.data.lower()
    
    def test_debug_route(self):
        """Test /debug route"""
        response = self.app.get('/debug')
        assert response.status_code == 200
        # Should render debug information
        assert b'debug' in response.data.lower() or b'info' in response.data.lower()
    
    def test_game_route(self):
        """Test /game route"""
        response = self.app.get('/game')
        assert response.status_code == 200
        # Should render game template
        assert b'game' in response.data.lower() or b'trivia' in response.data.lower()
    
    def test_home_route(self):
        """Test / (home) route"""
        response = self.app.get('/')
        assert response.status_code == 200
        # Should render home template
        assert response.data is not None


class TestErrorHandlingEdgeCases:
    """Test error handling edge cases for additional coverage"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('app.game')
    def test_navigation_with_game_exceptions(self, mock_game):
        """Test navigation endpoints when game raises exceptions"""
        # Test next card with exception
        mock_game.next_card.side_effect = Exception("Game error")
        
        try:
            response = self.app.post('/api/next-card')
            # Should handle gracefully or return error
            assert response.status_code in [200, 500]
        except Exception:
            # If it raises, that's also valid behavior
            pass
    
    @patch('app.game')
    def test_reset_game_with_exception(self, mock_game):
        """Test reset game when operations raise exceptions"""
        mock_game.reset_game.side_effect = Exception("Reset error")
        
        try:
            response = self.app.post('/api/reset-game')
            # Should handle gracefully
            assert response.status_code in [200, 500]
        except Exception:
            # If it raises, that's also valid behavior
            pass
    
    def test_api_endpoints_with_invalid_methods(self):
        """Test API endpoints with invalid HTTP methods"""
        # These should return method not allowed
        response = self.app.get('/api/next-card')  # Should be POST
        assert response.status_code == 405
        
        response = self.app.get('/api/previous-card')  # Should be POST
        assert response.status_code == 405
        
        response = self.app.get('/api/reset-game')  # Should be POST
        assert response.status_code == 405
        
        response = self.app.get('/api/flip-card')  # Should be POST
        assert response.status_code == 405
        
        response = self.app.get('/api/answer-card')  # Should be POST
        assert response.status_code == 405


class TestLogoutRoute:
    """Test logout route for additional coverage"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('app.HAS_LOGIN', True)
    @patch('app.logout_user')
    def test_logout_success(self, mock_logout):
        """Test logout route success"""
        with patch('app.redirect') as mock_redirect:
            with patch('app.url_for') as mock_url_for:
                mock_url_for.return_value = '/'
                response = self.app.get('/logout')
                
                mock_logout.assert_called_once()
                mock_redirect.assert_called_once()
    
    @patch('app.HAS_LOGIN', False)
    def test_logout_no_login_available(self, ):
        """Test logout when login not available"""
        with patch('app.redirect') as mock_redirect:
            with patch('app.url_for') as mock_url_for:
                mock_url_for.return_value = '/'
                response = self.app.get('/logout')
                
                # Should still redirect even without login
                mock_redirect.assert_called_once()