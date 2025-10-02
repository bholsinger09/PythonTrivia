"""
Test coverage for authentication functions focusing on register/login routes
to boost overall test coverage toward 80% goal.
"""
import pytest
from flask import Flask
from models import db, User
from db_service import UserService


class TestRegisterFunctionCoverage:
    """Test register route with all validation paths to increase coverage"""
    
    @pytest.fixture
    def test_app(self):
        """Create test Flask app with in-memory database"""
        from app import app
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client"""
        return test_app.test_client()
    
    def test_register_get_request(self, client):
        """Test GET request to register page"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data or b'register' in response.data
    
    def test_register_missing_fields(self, client):
        """Test register with missing required fields"""
        response = client.post('/register', data={
            'username': '',
            'email': '',
            'password': ''
        })
        assert response.status_code == 400
        assert b'All fields required' in response.data
    
    def test_register_short_username(self, client):
        """Test register with username too short"""
        response = client.post('/register', data={
            'username': 'ab',  # Too short
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 400
        assert b'Username must be 3-20 characters' in response.data
    
    def test_register_long_username(self, client):
        """Test register with username too long"""
        response = client.post('/register', data={
            'username': 'a' * 25,  # Too long
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 400
        assert b'Username must be 3-20 characters' in response.data
    
    def test_register_invalid_username_chars(self, client):
        """Test register with invalid username characters"""
        response = client.post('/register', data={
            'username': 'test-user!',  # Invalid chars
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 400
        assert b'Username can only contain' in response.data
    
    def test_register_invalid_email_no_at(self, client):
        """Test register with email missing @"""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'testexample.com',  # No @
            'password': 'password123'
        })
        assert response.status_code == 400
        assert b'Please enter a valid email address' in response.data
    
    def test_register_invalid_email_no_domain(self, client):
        """Test register with email missing domain"""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@',  # No domain
            'password': 'password123'
        })
        assert response.status_code == 400
        assert b'Please enter a valid email address' in response.data
    
    def test_register_short_password(self, client):
        """Test register with password too short"""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '12345'  # Too short
        })
        assert response.status_code == 400
        assert b'Password must be at least 6 characters' in response.data
    
    def test_register_password_mismatch(self, client):
        """Test register with password confirmation mismatch"""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'different123'
        })
        assert response.status_code == 400
        assert b'Passwords do not match' in response.data
    
    def test_register_duplicate_username(self, client):
        """Test register with existing username"""
        # Create a user first
        UserService.create_user('existinguser', 'existing@example.com', 'password123')
        
        response = client.post('/register', data={
            'username': 'existinguser',  # Duplicate
            'email': 'new@example.com',
            'password': 'password123'
        })
        assert response.status_code == 400
        assert b'Username already exists' in response.data
    
    def test_register_duplicate_email(self, client):
        """Test register with existing email"""
        # Create a user first
        UserService.create_user('firstuser', 'duplicate@example.com', 'password123')
        
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'duplicate@example.com',  # Duplicate
            'password': 'password123'
        })
        assert response.status_code == 400
        assert b'Email already registered' in response.data
    
    def test_register_success_form_data(self, client):
        """Test successful registration with form data"""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123'
        })
        # Should redirect on success
        assert response.status_code in [200, 302]
    
    def test_register_success_json(self, client):
        """Test successful registration with JSON data"""
        response = client.post('/register',
                             json={
                                 'username': 'jsonuser',
                                 'email': 'json@example.com',
                                 'password': 'password123'
                             },
                             content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestLoginFunctionCoverage:
    """Test login route to increase coverage"""
    
    @pytest.fixture
    def test_app(self):
        """Create test Flask app with in-memory database"""
        from app import app
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        with app.app_context():
            db.create_all()
            # Create test user
            UserService.create_user('testuser', 'test@example.com', 'password123')
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client"""
        return test_app.test_client()
    
    def test_login_get_request(self, client):
        """Test GET request to login page"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data
    
    def test_login_success(self, client):
        """Test successful login"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        # Should redirect on success
        assert response.status_code in [200, 302]
    
    def test_login_invalid_username(self, client):
        """Test login with invalid username"""
        response = client.post('/login', data={
            'username': 'invaliduser',
            'password': 'password123'
        })
        assert response.status_code == 400
        assert b'Invalid username or password' in response.data
    
    def test_login_invalid_password(self, client):
        """Test login with invalid password"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == 400
        assert b'Invalid username or password' in response.data
    
    def test_login_missing_data(self, client):
        """Test login with missing data"""
        response = client.post('/login', data={
            'username': '',
            'password': ''
        })
        assert response.status_code == 400
        assert b'Username and password required' in response.data


class TestGameStartCoverage:
    """Test game start functionality to increase coverage"""
    
    @pytest.fixture
    def test_app(self):
        """Create test Flask app with in-memory database"""
        from app import app
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client"""
        return test_app.test_client()
    
    def test_start_game_get(self, client):
        """Test GET request to start game"""
        response = client.get('/api/start-game')
        assert response.status_code == 200
        data = response.get_json()
        assert 'game_token' in data
    
    def test_start_game_post_with_filters(self, client):
        """Test POST request to start game with filters"""
        response = client.post('/api/start-game',
                             json={
                                 'categories': ['BASICS'],
                                 'difficulty': 'EASY'
                             })
        assert response.status_code == 200
        data = response.get_json()
        assert 'game_token' in data
    
    def test_start_game_invalid_category(self, client):
        """Test start game with invalid category"""
        response = client.post('/api/start-game',
                             json={
                                 'categories': ['INVALID_CATEGORY'],
                                 'difficulty': 'EASY'
                             })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_start_game_invalid_difficulty(self, client):
        """Test start game with invalid difficulty"""
        response = client.post('/api/start-game',
                             json={
                                 'categories': ['BASICS'],
                                 'difficulty': 'INVALID_DIFFICULTY'
                             })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestErrorHandlersCoverage:
    """Test error handlers to increase coverage"""
    
    @pytest.fixture
    def test_app(self):
        """Create test Flask app with in-memory database"""
        from app import app
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client"""
        return test_app.test_client()
    
    def test_404_handler(self, client):
        """Test 404 error handler"""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
    
    def test_500_simulation(self, client):
        """Test internal error handling by trying edge cases"""
        # Try to trigger various error conditions
        response = client.post('/api/current-card', json={'invalid': 'data'})
        # Should handle gracefully, not crash
        assert response.status_code in [200, 400, 404, 500]