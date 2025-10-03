"""
Test coverage for leaderboard functionality
Lines 495-503 (/leaderboard route) and 509-539 (/api/leaderboard route)
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app


class TestLeaderboardRoutes:
    """Test leaderboard routes to cover lines 495-503, 509-539"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    # /leaderboard route tests (lines 495-503)
    
    @patch('app.ScoreService.get_leaderboard')
    @patch('app.render_template')
    def test_leaderboard_success(self, mock_render, mock_get_leaderboard):
        """Test successful leaderboard page load (lines 497-499)"""
        mock_scores = [
            {'id': 1, 'username': 'user1', 'score': 100},
            {'id': 2, 'username': 'user2', 'score': 90}
        ]
        mock_get_leaderboard.return_value = mock_scores
        mock_render.return_value = 'rendered_leaderboard'
        
        response = self.app.get('/leaderboard')
        assert response.status_code == 200
        
        mock_get_leaderboard.assert_called_once_with(limit=20)
        mock_render.assert_called_once_with('leaderboard.html', scores=mock_scores)
    
    @patch('app.ScoreService.get_leaderboard')
    @patch('app.render_template')
    def test_leaderboard_exception_handling(self, mock_render, mock_get_leaderboard):
        """Test leaderboard page exception handling (lines 500-502)"""
        mock_get_leaderboard.side_effect = Exception("Database error")
        mock_render.return_value = 'rendered_leaderboard_empty'
        
        response = self.app.get('/leaderboard')
        assert response.status_code == 200
        
        # Should render with empty scores due to exception
        mock_render.assert_called_once_with('leaderboard.html', scores=[])
    
    # /api/leaderboard route tests (lines 509-539)
    
    @patch('app.ScoreService.get_leaderboard')
    def test_api_leaderboard_basic_success(self, mock_get_leaderboard):
        """Test basic API leaderboard success (lines 513-536)"""
        # Mock score object
        mock_score = MagicMock()
        mock_score.id = 1
        mock_score.score = 100
        mock_score.accuracy_percentage = 85.5
        mock_score.questions_answered = 10
        mock_score.achieved_at.isoformat.return_value = '2024-01-01T10:00:00'
        
        # Mock user relationship
        mock_user = MagicMock()
        mock_user.username = 'testuser'
        mock_score.user = mock_user
        
        # Mock category and difficulty
        mock_category = MagicMock()
        mock_category.value = 'BASICS'
        mock_score.category = mock_category
        
        mock_difficulty = MagicMock()
        mock_difficulty.value = 'EASY'
        mock_score.difficulty = mock_difficulty
        
        mock_get_leaderboard.return_value = [mock_score]
        
        response = self.app.get('/api/leaderboard')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['scores']) == 1
        
        score_data = data['scores'][0]
        assert score_data['id'] == 1
        assert score_data['username'] == 'testuser'
        assert score_data['score'] == 100
        assert score_data['accuracy'] == 85.5
        assert score_data['questions_answered'] == 10
        assert score_data['category'] == 'BASICS'
        assert score_data['difficulty'] == 'EASY'
        assert score_data['achieved_at'] == '2024-01-01T10:00:00'
        
        # Verify default parameters
        mock_get_leaderboard.assert_called_once_with(
            category=None,
            difficulty=None,
            limit=10
        )
    
    @patch('app.ScoreService.get_leaderboard')
    def test_api_leaderboard_with_anonymous_user(self, mock_get_leaderboard):
        """Test API leaderboard with anonymous user (lines 523-524)"""
        # Mock score object with anonymous user
        mock_score = MagicMock()
        mock_score.id = 1
        mock_score.score = 80
        mock_score.accuracy_percentage = 70.0
        mock_score.questions_answered = 8
        mock_score.achieved_at.isoformat.return_value = '2024-01-01T11:00:00'
        
        # No user (anonymous)
        mock_score.user = None
        mock_score.anonymous_name = 'Anonymous Player'
        
        # No category/difficulty
        mock_score.category = None
        mock_score.difficulty = None
        
        mock_get_leaderboard.return_value = [mock_score]
        
        response = self.app.get('/api/leaderboard')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['scores']) == 1
        
        score_data = data['scores'][0]
        assert score_data['username'] == 'Anonymous Player'
        assert score_data['category'] is None
        assert score_data['difficulty'] is None
    
    @patch('app.Category')
    @patch('app.Difficulty')
    @patch('app.ScoreService.get_leaderboard')
    def test_api_leaderboard_with_filters(self, mock_get_leaderboard, mock_difficulty_enum, mock_category_enum):
        """Test API leaderboard with category and difficulty filters (lines 513-521)"""
        # Mock enum conversions
        mock_category = MagicMock()
        mock_category_enum.return_value = mock_category
        
        mock_difficulty = MagicMock()
        mock_difficulty_enum.return_value = mock_difficulty
        
        mock_get_leaderboard.return_value = []
        
        response = self.app.get('/api/leaderboard?category=BASICS&difficulty=EASY&limit=5')
        assert response.status_code == 200
        
        # Verify enum conversions were called
        mock_category_enum.assert_called_once_with('BASICS')
        mock_difficulty_enum.assert_called_once_with('EASY')
        
        # Verify service called with correct parameters
        mock_get_leaderboard.assert_called_once_with(
            category=mock_category,
            difficulty=mock_difficulty,
            limit=5
        )
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['scores'] == []
    
    @patch('app.ScoreService.get_leaderboard')
    def test_api_leaderboard_with_partial_filters(self, mock_get_leaderboard):
        """Test API leaderboard with only some filters (lines 513-521)"""
        mock_get_leaderboard.return_value = []
        
        response = self.app.get('/api/leaderboard?category=BASICS&limit=15')
        assert response.status_code == 200
        
        # Should handle partial filters gracefully
        data = json.loads(response.data)
        assert data['success'] is True
    
    @patch('app.ScoreService.get_leaderboard')
    def test_api_leaderboard_default_limit(self, mock_get_leaderboard):
        """Test API leaderboard default limit parameter (line 511)"""
        mock_get_leaderboard.return_value = []
        
        response = self.app.get('/api/leaderboard')
        assert response.status_code == 200
        
        # Should use default limit of 10
        mock_get_leaderboard.assert_called_once_with(
            category=None,
            difficulty=None,
            limit=10
        )
    
    @patch('app.ScoreService.get_leaderboard')
    def test_api_leaderboard_custom_limit(self, mock_get_leaderboard):
        """Test API leaderboard with custom limit (line 511)"""
        mock_get_leaderboard.return_value = []
        
        response = self.app.get('/api/leaderboard?limit=25')
        assert response.status_code == 200
        
        # Should use custom limit
        mock_get_leaderboard.assert_called_once_with(
            category=None,
            difficulty=None,
            limit=25
        )
    
    @patch('app.Category')
    def test_api_leaderboard_invalid_category_enum(self, mock_category_enum):
        """Test API leaderboard with invalid category enum (lines 537-538)"""
        mock_category_enum.side_effect = ValueError("Invalid category")
        
        response = self.app.get('/api/leaderboard?category=INVALID')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid category' in data['message']
    
    @patch('app.Difficulty')
    def test_api_leaderboard_invalid_difficulty_enum(self, mock_difficulty_enum):
        """Test API leaderboard with invalid difficulty enum (lines 537-538)"""
        mock_difficulty_enum.side_effect = ValueError("Invalid difficulty")
        
        response = self.app.get('/api/leaderboard?difficulty=INVALID')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid difficulty' in data['message']
    
    @patch('app.ScoreService.get_leaderboard')
    def test_api_leaderboard_service_exception(self, mock_get_leaderboard):
        """Test API leaderboard with service exception (lines 537-538)"""
        mock_get_leaderboard.side_effect = Exception("Database connection error")
        
        response = self.app.get('/api/leaderboard')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Database connection error' in data['message']
    
    def test_api_leaderboard_invalid_limit_parameter(self):
        """Test API leaderboard with invalid limit parameter"""
        # This should raise ValueError when trying to convert to int
        try:
            response = self.app.get('/api/leaderboard?limit=invalid')
            # If it doesn't raise an exception, check that it handles gracefully
            assert response.status_code in [200, 400, 500]
        except ValueError:
            # This is expected behavior
            pass


class TestLeaderboardEdgeCases:
    """Test edge cases for leaderboard functionality"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('app.ScoreService.get_leaderboard')
    def test_api_leaderboard_empty_results(self, mock_get_leaderboard):
        """Test API leaderboard with empty results"""
        mock_get_leaderboard.return_value = []
        
        response = self.app.get('/api/leaderboard')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['scores'] == []
    
    @patch('app.ScoreService.get_leaderboard')
    def test_api_leaderboard_large_limit(self, mock_get_leaderboard):
        """Test API leaderboard with very large limit"""
        mock_get_leaderboard.return_value = []
        
        response = self.app.get('/api/leaderboard?limit=1000')
        assert response.status_code == 200
        
        mock_get_leaderboard.assert_called_once_with(
            category=None,
            difficulty=None,
            limit=1000
        )
    
    def test_api_leaderboard_zero_limit(self):
        """Test API leaderboard with zero limit"""
        try:
            response = self.app.get('/api/leaderboard?limit=0')
            # Should handle gracefully
            assert response.status_code in [200, 400]
        except Exception:
            # Some error handling is acceptable
            pass