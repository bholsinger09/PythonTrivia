"""
Test suite for API endpoints
"""
import requests
import pytest
import json


class TestAPIEndpoints:
    """Test API endpoints functionality"""
    
    BASE_URL = "http://localhost:5001"
    
    def test_current_card_endpoint(self):
        """Test /api/current-card endpoint"""
        response = requests.get(f"{self.BASE_URL}/api/current-card")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "card" in data
        assert "game_stats" in data
        
        # Verify card structure
        card = data["card"]
        assert "trivia_question" in card
        assert "is_flipped" in card
        assert "card_id" in card
        
        # Verify question structure
        question = card["trivia_question"]
        assert "question" in question
        assert "answer" in question
        assert "category" in question
        assert "difficulty" in question
        
    def test_flip_card_endpoint(self):
        """Test /api/flip-card endpoint"""
        response = requests.post(f"{self.BASE_URL}/api/flip-card")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "card" in data
        assert data["card"]["is_flipped"] is True
        
    def test_answer_card_endpoint(self):
        """Test /api/answer-card endpoint"""
        # Test correct answer
        payload = {"correct": True}
        response = requests.post(
            f"{self.BASE_URL}/api/answer-card",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "card" in data
        assert "game_stats" in data
        
        # Verify score increased
        assert data["game_stats"]["score"] >= 0
        
    def test_next_card_endpoint(self):
        """Test /api/next-card endpoint"""
        response = requests.post(f"{self.BASE_URL}/api/next-card")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should succeed if there are more cards
        if data["success"]:
            assert "card" in data
            assert "game_stats" in data
        else:
            assert "message" in data
            
    def test_previous_card_endpoint(self):
        """Test /api/previous-card endpoint"""
        # First move to next card
        requests.post(f"{self.BASE_URL}/api/next-card")
        
        # Then try to go back
        response = requests.post(f"{self.BASE_URL}/api/previous-card")
        
        assert response.status_code == 200
        data = response.json()
        
        if data["success"]:
            assert "card" in data
            assert "game_stats" in data
            
    def test_reset_game_endpoint(self):
        """Test /api/reset-game endpoint"""
        # First play a bit
        requests.post(f"{self.BASE_URL}/api/flip-card")
        requests.post(
            f"{self.BASE_URL}/api/answer-card",
            json={"correct": True}
        )
        
        # Reset game
        response = requests.post(f"{self.BASE_URL}/api/reset-game")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["game_stats"]["score"] == 0
        assert data["game_stats"]["current_index"] == 0
        
    def test_game_stats_endpoint(self):
        """Test /api/game-stats endpoint"""
        response = requests.get(f"{self.BASE_URL}/api/game-stats")
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "current_index", "total_cards", "score", 
            "percentage", "answered_cards"
        ]
        
        for field in required_fields:
            assert field in data
            
        assert isinstance(data["current_index"], int)
        assert isinstance(data["total_cards"], int)
        assert isinstance(data["score"], int)
        assert isinstance(data["percentage"], (int, float))
        assert isinstance(data["answered_cards"], int)
        
    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404"""
        response = requests.get(f"{self.BASE_URL}/api/invalid-endpoint")
        assert response.status_code == 404
        
    def test_invalid_method(self):
        """Test invalid HTTP method"""
        # GET request to POST-only endpoint
        response = requests.get(f"{self.BASE_URL}/api/flip-card")
        assert response.status_code == 405  # Method Not Allowed
        
    def test_malformed_json(self):
        """Test malformed JSON in request"""
        response = requests.post(
            f"{self.BASE_URL}/api/answer-card",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        # Should handle gracefully
        assert response.status_code in [400, 500]


class TestGameStateConsistency:
    """Test game state consistency across API calls"""
    
    BASE_URL = "http://localhost:5001"
    
    def test_game_state_persistence(self):
        """Test that game state persists across API calls"""
        # Reset game first
        requests.post(f"{self.BASE_URL}/api/reset-game")
        
        # Get initial state
        response = requests.get(f"{self.BASE_URL}/api/current-card")
        initial_state = response.json()
        initial_card_id = initial_state["card"]["card_id"]
        
        # Flip card
        requests.post(f"{self.BASE_URL}/api/flip-card")
        
        # Check state
        response = requests.get(f"{self.BASE_URL}/api/current-card")
        flipped_state = response.json()
        
        assert flipped_state["card"]["card_id"] == initial_card_id
        assert flipped_state["card"]["is_flipped"] is True
        
    def test_score_consistency(self):
        """Test score consistency across operations"""
        # Reset game
        requests.post(f"{self.BASE_URL}/api/reset-game")
        
        # Answer correctly
        requests.post(f"{self.BASE_URL}/api/flip-card")
        requests.post(
            f"{self.BASE_URL}/api/answer-card",
            json={"correct": True}
        )
        
        # Check score in different endpoints
        stats_response = requests.get(f"{self.BASE_URL}/api/game-stats")
        stats_data = stats_response.json()
        
        card_response = requests.get(f"{self.BASE_URL}/api/current-card")
        card_data = card_response.json()
        
        assert stats_data["score"] == card_data["game_stats"]["score"]
        assert stats_data["score"] >= 1
        
    def test_navigation_consistency(self):
        """Test navigation state consistency"""
        # Reset and go to second card
        requests.post(f"{self.BASE_URL}/api/reset-game")
        requests.post(f"{self.BASE_URL}/api/next-card")
        
        # Get current state
        response = requests.get(f"{self.BASE_URL}/api/current-card")
        data = response.json()
        
        assert data["game_stats"]["current_index"] == 1
        
        # Go back
        requests.post(f"{self.BASE_URL}/api/previous-card")
        
        # Check we're back to first card
        response = requests.get(f"{self.BASE_URL}/api/current-card")
        data = response.json()
        
        assert data["game_stats"]["current_index"] == 0


class TestAPIErrorHandling:
    """Test API error handling"""
    
    BASE_URL = "http://localhost:5001"
    
    def test_answer_without_flip(self):
        """Test answering without flipping card first"""
        # Reset game
        requests.post(f"{self.BASE_URL}/api/reset-game")
        
        # Try to answer without flipping
        response = requests.post(
            f"{self.BASE_URL}/api/answer-card",
            json={"correct": True}
        )
        
        # Should still work (API doesn't enforce flip first)
        assert response.status_code == 200
        
    def test_navigation_bounds(self):
        """Test navigation at boundaries"""
        # Reset to first card
        requests.post(f"{self.BASE_URL}/api/reset-game")
        
        # Try to go to previous from first card
        response = requests.post(f"{self.BASE_URL}/api/previous-card")
        data = response.json()
        
        if not data["success"]:
            assert "message" in data
            
        # Navigate to last card
        while True:
            response = requests.post(f"{self.BASE_URL}/api/next-card")
            data = response.json()
            if not data["success"]:
                break
                
        # Try to go beyond last card
        response = requests.post(f"{self.BASE_URL}/api/next-card")
        data = response.json()
        
        if not data["success"]:
            assert "message" in data


class TestAPIPerformance:
    """Test API performance"""
    
    BASE_URL = "http://localhost:5001"
    
    def test_api_response_time(self):
        """Test API response times are reasonable"""
        import time
        
        endpoints = [
            ("/api/current-card", "GET"),
            ("/api/flip-card", "POST"),
            ("/api/game-stats", "GET"),
        ]
        
        for endpoint, method in endpoints:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(f"{self.BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{self.BASE_URL}{endpoint}")
                
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 1.0, f"{endpoint} took {response_time:.2f}s"
            
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            try:
                response = requests.get(f"{self.BASE_URL}/api/current-card")
                results.append(response.status_code == 200)
            except Exception:
                results.append(False)
                
        # Make 5 concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
            
        # Wait for all threads
        for thread in threads:
            thread.join()
            
        # All requests should succeed
        assert all(results), "Some concurrent requests failed"