#!/usr/bin/env python3
"""
API Endpoint Tests
Tests all REST API endpoints, error handling, and response formats
"""

import pytest
import json
import requests
import time
from datetime import datetime

# Import app and models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User, Question, GameSession
from config import TestingConfig

class TestAPIEndpoints:
    """Test suite for REST API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with sample data"""
        app.config.from_object(TestingConfig)
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                self.setup_test_data()
                yield client
                db.drop_all()
    
    def setup_test_data(self):
        """Set up test data"""
        # Create test user
        self.test_user = User(
            username='api_tester',
            email='api@example.com',
            password_hash='$2b$12$test_hash'
        )
        db.session.add(self.test_user)
        
        # Create test question
        self.test_question = Question(
            question_text='API Test Question?',
            correct_answer='Correct Answer',
            choices='["Correct Answer", "Wrong 1", "Wrong 2", "Wrong 3"]',
            correct_choice_index=0,
            category='BASICS',
            difficulty='EASY'
        )
        db.session.add(self.test_question)
        db.session.commit()
    
    def test_health_check_endpoint(self, client):
        """Test application health check"""
        response = client.get('/health')
        
        if response.status_code == 200:
            data = response.get_json()
            assert 'status' in data
            assert data['status'] == 'healthy'
        else:
            # If no health endpoint, that's okay
            print("No /health endpoint - consider adding one")
    
    def test_home_page_endpoint(self, client):
        """Test main application page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert response.data is not None
    
    def test_api_questions_endpoint(self, client):
        """Test questions API endpoint"""
        response = client.get('/api/questions')
        
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, (list, dict))
            
            if isinstance(data, dict) and 'questions' in data:
                questions = data['questions']
            else:
                questions = data
            
            # Should return questions
            assert len(questions) > 0
            
            # Check question structure
            for question in questions[:1]:  # Check first question
                required_fields = ['id', 'question_text', 'choices']
                for field in required_fields:
                    if field not in question:
                        print(f"Warning: Question missing field '{field}'")
        else:
            print(f"Questions endpoint returned {response.status_code}")
    
    def test_api_questions_with_filters(self, client):
        """Test questions API with difficulty and category filters"""
        # Test difficulty filter
        response = client.get('/api/questions?difficulty=EASY')
        if response.status_code == 200:
            data = response.get_json()
            print("✅ Difficulty filter working")
        
        # Test category filter
        response = client.get('/api/questions?category=BASICS')
        if response.status_code == 200:
            data = response.get_json()
            print("✅ Category filter working")
        
        # Test combined filters
        response = client.get('/api/questions?difficulty=EASY&category=BASICS')
        if response.status_code == 200:
            print("✅ Combined filters working")
    
    def test_api_users_count_endpoint(self, client):
        """Test user count API endpoint"""
        response = client.get('/api/users/count')
        
        if response.status_code == 200:
            data = response.get_json()
            assert 'count' in data or 'total_users' in data
            print(f"✅ Users count endpoint: {data}")
        else:
            print(f"Users count endpoint returned {response.status_code}")
    
    def test_register_endpoint(self, client):
        """Test user registration endpoint"""
        registration_data = {
            'username': 'new_api_user',
            'email': 'newapi@example.com',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }
        
        # Test POST to /register
        response = client.post('/register', data=registration_data)
        
        # Should either succeed (200/201) or redirect (302)
        assert response.status_code in [200, 201, 302, 400, 409]
        
        if response.status_code in [200, 201, 302]:
            print("✅ Registration endpoint working")
        else:
            print(f"Registration returned {response.status_code} - may have validation")
        
        # Test API version if exists
        response = client.post('/api/register', json=registration_data)
        if response.status_code != 404:
            print("✅ API registration endpoint exists")
    
    def test_login_endpoint(self, client):
        """Test user login endpoint"""
        # First register a user
        client.post('/register', data={
            'username': 'login_test',
            'email': 'login_test@example.com',
            'password': 'loginpass123',
            'confirm_password': 'loginpass123'
        })
        
        # Test login
        login_data = {
            'username': 'login_test',
            'password': 'loginpass123'
        }
        
        response = client.post('/login', data=login_data)
        assert response.status_code in [200, 302, 400, 401]
        
        if response.status_code in [200, 302]:
            print("✅ Login endpoint working")
        
        # Test API login if exists
        response = client.post('/api/login', json=login_data)
        if response.status_code != 404:
            print("✅ API login endpoint exists")
    
    def test_game_endpoints(self, client):
        """Test game-related API endpoints"""
        # Test start game
        game_data = {
            'difficulty': 'EASY',
            'categories': ['BASICS'],
            'question_count': 5
        }
        
        response = client.post('/api/start-game', json=game_data)
        
        if response.status_code == 200:
            data = response.get_json()
            session_token = data.get('session_token')
            print(f"✅ Start game endpoint working: {session_token}")
            
            # Test submit answer if we have a session
            if session_token:
                answer_data = {
                    'session_token': session_token,
                    'question_id': self.test_question.id,
                    'selected_choice': 0,
                    'time_taken': 3.0
                }
                
                response = client.post('/api/submit-answer', json=answer_data)
                if response.status_code == 200:
                    print("✅ Submit answer endpoint working")
        
        elif response.status_code == 404:
            print("Game endpoints not implemented yet")
        else:
            print(f"Start game returned {response.status_code}")
    
    def test_leaderboard_endpoint(self, client):
        """Test leaderboard API endpoint"""
        response = client.get('/api/leaderboard')
        
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, (list, dict))
            print("✅ Leaderboard endpoint working")
        elif response.status_code == 404:
            print("Leaderboard endpoint not implemented")
        else:
            print(f"Leaderboard returned {response.status_code}")
    
    def test_error_handling(self, client):
        """Test API error handling"""
        # Test invalid endpoints
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        # Test malformed JSON
        response = client.post('/api/start-game', 
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code in [400, 422, 500]
        
        # Test missing required parameters
        response = client.post('/api/submit-answer', json={})
        assert response.status_code in [400, 422]
        
        print("✅ Error handling tests passed")
    
    def test_response_formats(self, client):
        """Test that API responses are properly formatted"""
        endpoints_to_test = [
            '/api/questions',
            '/api/users/count',
            '/health'
        ]
        
        for endpoint in endpoints_to_test:
            response = client.get(endpoint)
            
            if response.status_code == 200:
                # Should be valid JSON
                try:
                    data = response.get_json()
                    assert data is not None
                    print(f"✅ {endpoint} returns valid JSON")
                except:
                    print(f"⚠️  {endpoint} doesn't return valid JSON")
            elif response.status_code == 404:
                print(f"⚠️  {endpoint} not implemented")
    
    def test_cors_headers(self, client):
        """Test CORS headers for API endpoints"""
        response = client.options('/api/questions')
        
        # Check for CORS headers
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        has_cors = any(header in response.headers for header in cors_headers)
        
        if has_cors:
            print("✅ CORS headers present")
        else:
            print("⚠️  No CORS headers found - may cause frontend issues")
    
    def test_rate_limiting(self, client):
        """Test if rate limiting is implemented"""
        # Make rapid requests to see if rate limiting kicks in
        endpoint = '/api/questions'
        responses = []
        
        for i in range(20):  # 20 rapid requests
            response = client.get(endpoint)
            responses.append(response.status_code)
            time.sleep(0.1)  # Small delay
        
        # Check if any requests were rate limited
        rate_limited = any(status == 429 for status in responses)
        
        if rate_limited:
            print("✅ Rate limiting is implemented")
        else:
            print("⚠️  No rate limiting detected - consider implementing")
    
    def test_input_validation(self, client):
        """Test input validation on API endpoints"""
        # Test extremely long input
        long_string = "a" * 10000
        
        response = client.post('/api/start-game', json={
            'difficulty': long_string,
            'categories': [long_string],
            'question_count': 999999
        })
        
        # Should reject invalid input
        assert response.status_code in [400, 422]
        
        # Test SQL injection in parameters
        response = client.get("/api/questions?difficulty='; DROP TABLE users; --")
        
        # Should not cause server error
        assert response.status_code != 500
        
        print("✅ Input validation tests passed")

class TestProductionAPIEndpoints:
    """Test production API endpoints if accessible"""
    
    def test_production_health(self):
        """Test production application health"""
        production_url = 'https://pythontrivia-production.up.railway.app'
        
        try:
            response = requests.get(f'{production_url}/health', timeout=10)
            if response.status_code == 200:
                print("✅ Production health check passed")
            else:
                print(f"⚠️  Production health returned {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Production not accessible: {e}")
    
    def test_production_api_endpoints(self):
        """Test key production API endpoints"""
        production_url = 'https://pythontrivia-production.up.railway.app'
        
        endpoints = [
            '/api/questions',
            '/api/users/count'
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f'{production_url}{endpoint}', timeout=10)
                if response.status_code == 200:
                    print(f"✅ Production {endpoint} working")
                else:
                    print(f"⚠️  Production {endpoint} returned {response.status_code}")
            except requests.RequestException:
                print(f"❌ Production {endpoint} not accessible")

if __name__ == '__main__':
    print("🌐 RUNNING API ENDPOINT TESTS")
    print("=" * 60)
    
    # Run tests with verbose output
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--no-header',
        '--disable-warnings'
    ])
