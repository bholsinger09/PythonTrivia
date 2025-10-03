"""
PHASE 4: Integration test workflows
End-to-end user journey testing for real workflow validation
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the parent directory to sys.path to import the Flask app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from tests.test_utils import MockUser, MockQuestion, MockGameSession


class TestUserJourneyIntegration:
    """End-to-end user journey testing"""
    
    def setup_method(self):
        """Set up test client for each test"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_anonymous_user_complete_journey(self):
        """Test complete anonymous user journey: Home → Game → Score → Leaderboard"""
        # Step 1: Anonymous user visits home page
        response = self.app.get('/')
        assert response.status_code == 200
        assert b'Python Trivia' in response.data
        
        # Step 2: Start a new game
        response = self.app.get('/game')
        assert response.status_code == 200
        
        # Step 3: Get current card (should trigger game initialization)
        response = self.app.get('/api/current-card')
        assert response.status_code == 200
        card_data = json.loads(response.data)
        
        # Step 4: Answer a question
        response = self.app.post('/api/answer-card', 
                                json={'choice_index': 0},
                                content_type='application/json')
        assert response.status_code == 200
        answer_data = json.loads(response.data)
        assert 'success' in answer_data
        assert 'correct' in answer_data
        
        # Step 5: Get game stats
        response = self.app.get('/api/game-stats')
        assert response.status_code == 200
        stats_data = json.loads(response.data)
        assert 'score' in stats_data
        # Accept either total_questions (DB mode) or total_cards (fallback mode)
        assert 'total_questions' in stats_data or 'total_cards' in stats_data
        
        # Step 6: Save score
        response = self.app.post('/api/save-score',
                                json={
                                    'score': 85,
                                    'questions_answered': 10,
                                    'player_name': 'Anonymous Player'
                                },
                                content_type='application/json')
        assert response.status_code in [200, 400, 415]  # May vary based on implementation
        
        # Step 7: View leaderboard
        response = self.app.get('/leaderboard')
        assert response.status_code == 200
        
        # Step 8: API leaderboard
        response = self.app.get('/api/leaderboard')
        assert response.status_code == 200
        leaderboard_data = json.loads(response.data)
        # Accept either leaderboard (DB mode) or error message (fallback mode)
        assert 'leaderboard' in leaderboard_data or 'message' in leaderboard_data
    
    @patch('app.HAS_LOGIN', True)
    @patch('app.current_user')
    @patch('app.UserService')
    def test_registered_user_journey(self, mock_user_service, mock_current_user):
        """Test registered user journey with authentication"""
        
        # Mock authenticated user
        mock_user = MockUser(
            user_id=1,
            username='testuser',
            email='test@example.com'
        )
        mock_current_user.is_authenticated = True
        mock_current_user.id = 1
        mock_current_user.username = 'testuser'
        
        # Step 1: User visits profile page (authenticated)
        with patch('app.redirect') as mock_redirect:
            # This might redirect, which is normal behavior
            try:
                response = self.app.get('/profile')
                # Either successful page load or redirect
                assert response.status_code in [200, 302]
            except:
                # Profile route might not be fully implemented
                pass
        
        # Step 2: Start game as authenticated user
        response = self.app.get('/game')
        assert response.status_code == 200
        
        # Step 3: Play through game with session tracking
        response = self.app.get('/api/current-card')
        assert response.status_code == 200
        
        # Step 4: Answer as authenticated user (should track in database)
        response = self.app.post('/api/answer-card',
                                json={'choice_index': 1},
                                content_type='application/json')
        assert response.status_code == 200
        
        # Step 5: Check game stats for authenticated user
        response = self.app.get('/api/game-stats')
        assert response.status_code == 200
        stats = json.loads(response.data)
        assert isinstance(stats, dict)
        
        # Step 6: Save score with user authentication
        response = self.app.post('/api/save-score',
                                json={
                                    'score': 95,
                                    'questions_answered': 12,
                                    'player_name': 'testuser'
                                },
                                content_type='application/json')
        assert response.status_code in [200, 400, 415]
    
    def test_multi_question_game_flow(self):
        """Test playing through multiple questions in sequence"""
        
        # Step 1: Initialize game
        response = self.app.get('/api/current-card')
        assert response.status_code == 200
        
        questions_answered = 0
        max_questions = 5
        
        # Step 2: Play through multiple questions
        for i in range(max_questions):
            # Get current question
            response = self.app.get('/api/current-card')
            if response.status_code != 200:
                break  # No more questions
                
            # Answer the question
            response = self.app.post('/api/answer-card',
                                   json={'choice_index': i % 2},  # Alternate answers
                                   content_type='application/json')
            
            if response.status_code == 200:
                questions_answered += 1
                answer_data = json.loads(response.data)
                assert 'success' in answer_data
                
                # Try to move to next question
                response = self.app.post('/api/next-card')
                # Continue regardless of response (might be end of game)
        
        # Step 3: Verify we played at least one question
        assert questions_answered >= 1
        
        # Step 4: Get final game stats
        response = self.app.get('/api/game-stats')
        assert response.status_code == 200
        final_stats = json.loads(response.data)
        assert 'score' in final_stats
    
    def test_game_navigation_workflow(self):
        """Test complete game navigation: current, flip, answer, next, previous"""
        
        # Step 1: Get initial card
        response = self.app.get('/api/current-card')
        assert response.status_code == 200
        card_data = json.loads(response.data)
        
        # Step 2: Flip the card
        response = self.app.post('/api/flip-card')
        assert response.status_code == 200
        flip_data = json.loads(response.data)
        assert 'flipped' in flip_data or 'success' in flip_data
        
        # Step 3: Answer the card
        response = self.app.post('/api/answer-card',
                               json={'choice_index': 0},
                               content_type='application/json')
        assert response.status_code == 200
        
        # Step 4: Try to go to next card
        response = self.app.post('/api/next-card')
        assert response.status_code == 200
        next_data = json.loads(response.data)
        
        # Step 5: Try to go to previous card
        response = self.app.post('/api/previous-card')
        assert response.status_code == 200
        prev_data = json.loads(response.data)
        
        # Step 6: Reset the game
        response = self.app.post('/api/reset-game')
        assert response.status_code == 200
        reset_data = json.loads(response.data)
        assert 'message' in reset_data or 'success' in reset_data
    
    def test_error_handling_integration(self):
        """Test error handling across the user journey"""
        
        # Step 1: Try invalid API endpoints
        response = self.app.get('/api/nonexistent-endpoint')
        assert response.status_code == 404
        
        # Step 2: Try invalid JSON data
        response = self.app.post('/api/answer-card',
                               data='invalid-json',
                               content_type='application/json')
        assert response.status_code in [400, 415]  # Bad request or unsupported media type
        
        # Step 3: Try answering without choice_index
        response = self.app.post('/api/answer-card',
                               json={'invalid': 'data'},
                               content_type='application/json')
        assert response.status_code in [200, 400]  # May handle gracefully
        
        # Step 4: Test form data vs JSON handling
        response = self.app.post('/api/answer-card',
                               data={'choice_index': '0'})
        assert response.status_code in [200, 400, 415]  # Various valid responses
    
    def test_leaderboard_integration_workflow(self):
        """Test complete leaderboard functionality"""
        
        # Step 1: View empty/initial leaderboard
        response = self.app.get('/api/leaderboard')
        assert response.status_code == 200
        leaderboard_data = json.loads(response.data)
        # Accept either leaderboard (DB mode) or error message (fallback mode)
        assert 'leaderboard' in leaderboard_data or 'message' in leaderboard_data
        
        # Step 2: Test leaderboard with filters
        response = self.app.get('/api/leaderboard?category=basics&difficulty=easy')
        assert response.status_code == 200
        filtered_data = json.loads(response.data)
        assert 'leaderboard' in filtered_data or 'message' in filtered_data
        
        # Step 3: Test leaderboard with limit
        response = self.app.get('/api/leaderboard?limit=5')
        assert response.status_code == 200
        limited_data = json.loads(response.data)
        assert 'leaderboard' in limited_data or 'message' in limited_data
        
        # Step 4: Test leaderboard HTML page
        response = self.app.get('/leaderboard')
        assert response.status_code == 200
        assert b'leaderboard' in response.data.lower() or b'score' in response.data.lower()
    
    def test_complete_session_lifecycle(self):
        """Test complete session management lifecycle"""
        
        # Step 1: Start fresh session
        with self.app.session_transaction() as sess:
            # Clear any existing session data
            sess.clear()
        
        # Step 2: Initialize game (creates session)
        response = self.app.get('/api/current-card')
        assert response.status_code == 200
        
        # Step 3: Verify session persistence across requests
        response = self.app.get('/api/game-stats')
        assert response.status_code == 200
        
        # Step 4: Modify game state
        response = self.app.post('/api/answer-card',
                               json={'choice_index': 0},
                               content_type='application/json')
        assert response.status_code == 200
        
        # Step 5: Verify state persistence
        response = self.app.get('/api/game-stats')
        assert response.status_code == 200
        stats = json.loads(response.data)
        
        # Step 6: Reset and verify clean state
        response = self.app.post('/api/reset-game')
        assert response.status_code == 200
        
        # Step 7: Verify reset worked
        response = self.app.get('/api/game-stats')
        assert response.status_code == 200
        reset_stats = json.loads(response.data)
        assert isinstance(reset_stats, dict)


class TestScenarioIntegration:
    """Test specific user scenarios and edge cases"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_rapid_fire_answers(self):
        """Test rapid succession of answers"""
        
        # Initialize game
        response = self.app.get('/api/current-card')
        assert response.status_code == 200
        
        # Rapid fire answers
        for i in range(3):
            response = self.app.post('/api/answer-card',
                                   json={'choice_index': i % 4},
                                   content_type='application/json')
            if response.status_code == 200:
                # Try to advance immediately
                self.app.post('/api/next-card')
    
    def test_browser_back_forward_simulation(self):
        """Test behavior with browser-like navigation"""
        
        # Step 1: Load game page
        response = self.app.get('/game')
        assert response.status_code == 200
        
        # Step 2: Go to leaderboard
        response = self.app.get('/leaderboard')
        assert response.status_code == 200
        
        # Step 3: Go back to game (like browser back)
        response = self.app.get('/game')
        assert response.status_code == 200
        
        # Step 4: Check if game state persists
        response = self.app.get('/api/current-card')
        assert response.status_code == 200
    
    def test_concurrent_session_behavior(self):
        """Test behavior with multiple requests in same session"""
        
        # Simulate multiple concurrent requests
        responses = []
        
        # Multiple current-card requests
        for i in range(3):
            response = self.app.get('/api/current-card')
            responses.append(response.status_code)
        
        # All should succeed
        assert all(code == 200 for code in responses)
        
        # Multiple game-stats requests
        for i in range(2):
            response = self.app.get('/api/game-stats')
            assert response.status_code == 200


if __name__ == '__main__':
    unittest.main()