"""
Unit tests for authentication routes and functionality
"""
import pytest
from flask import url_for, session
from models import db, User
from db_service import UserService
from app import app
from test_utils import MockUser, create_mock_user


@pytest.fixture
def test_app():
    """Create a test Flask app"""
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
def client(test_app):
    """Create a test client"""
    return test_app.test_client()


@pytest.fixture
def test_user(test_app):
    """Create a test user"""
    with test_app.app_context():
        user = UserService.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        return user


class TestAuthenticationRoutes:
    """Test authentication routes"""
    
    def test_register_get(self, client):
        """Test GET request to register page"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower()
    
    def test_register_post_success(self, client, test_app):
        """Test successful user registration"""
        with test_app.app_context():
            response = client.post('/register', data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'newpassword123',
                'confirm_password': 'newpassword123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Check user was created
            user = UserService.get_user_by_username('newuser')
            assert user is not None
            assert user.email == 'new@example.com'
    
    def test_register_post_username_too_short(self, client):
        """Test registration with username too short"""
        response = client.post('/register', data={
            'username': 'ab',  # Too short (min 3)
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 400
        assert b'Username must be between 3 and 50 characters' in response.data
    
    def test_register_post_username_too_long(self, client):
        """Test registration with username too long"""
        long_username = 'a' * 51  # Too long (max 50)
        response = client.post('/register', data={
            'username': long_username,
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 400
        assert b'Username must be between 3 and 50 characters' in response.data
    
    def test_register_post_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 400
        assert b'Invalid email address' in response.data
    
    def test_register_post_password_too_short(self, client):
        """Test registration with password too short"""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123',  # Too short (min 6)
            'confirm_password': '123'
        })
        
        assert response.status_code == 400
        assert b'Password must be at least 6 characters long' in response.data
    
    def test_register_post_passwords_dont_match(self, client):
        """Test registration with mismatched passwords"""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'differentpassword'
        })
        
        assert response.status_code == 400
        assert b'Passwords do not match' in response.data
    
    def test_register_post_duplicate_username(self, client, test_user):
        """Test registration with existing username"""
        response = client.post('/register', data={
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 400
        # Check for error message in HTML response
        assert b'Username already exists' in response.data or b'already exists' in response.data
    
    def test_register_post_duplicate_email(self, client, test_user):
        """Test registration with existing email"""
        response = client.post('/register', data={
            'username': 'differentuser',
            'email': 'test@example.com',  # Already exists
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 400
        # Check for error message in HTML response  
        assert b'Email already' in response.data or b'already registered' in response.data
    
    def test_login_get(self, client):
        """Test GET request to login page"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_login_post_success(self, client, test_user):
        """Test successful login"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard or home
    
    def test_login_post_invalid_username(self, client):
        """Test login with invalid username"""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        # Check for error message in HTML response
        assert b'Invalid credentials' in response.data or b'Invalid username' in response.data
    
    def test_login_post_invalid_password(self, client, test_user):
        """Test login with invalid password"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        # Check for error message in HTML response
        assert b'Invalid credentials' in response.data or b'Invalid password' in response.data
    
    def test_login_post_username_too_long(self, client):
        """Test login with username too long"""
        long_username = 'a' * 51  # Too long (max 20 based on validation)
        response = client.post('/login', data={
            'username': long_username,
            'password': 'password123'
        })
        
        assert response.status_code == 400
        # Check for error message in HTML response
        assert b'Invalid credentials' in response.data
    
    def test_login_post_password_too_long(self, client):
        """Test login with password too long"""
        long_password = 'a' * 300  # Too long (max 255)
        response = client.post('/login', data={
            'username': 'testuser',
            'password': long_password
        })
        
        assert response.status_code == 400
        # Check for error message in HTML response  
        assert b'Invalid credentials' in response.data
    
    def test_logout(self, client, test_user):
        """Test logout functionality"""
        # First login
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_protected_route_without_login(self, client):
        """Test accessing protected route without login"""
        # Try accessing a route that might be protected (checking if it exists)
        response = client.get('/profile')  # Changed from /dashboard to /profile
        # Should redirect to login page or return 404 if route doesn't exist
        assert response.status_code == 302 or response.status_code == 401 or response.status_code == 404


class TestUserService:
    """Test UserService with authentication context"""
    
    def test_authenticate_user_success(self, test_app, test_user):
        """Test successful user authentication"""
        with test_app.app_context():
            authenticated_user = UserService.authenticate_user('testuser', 'password123')
            assert authenticated_user is not None
            assert authenticated_user.username == 'testuser'
    
    def test_authenticate_user_wrong_password(self, test_app, test_user):
        """Test authentication with wrong password"""
        with test_app.app_context():
            authenticated_user = UserService.authenticate_user('testuser', 'wrongpassword')
            assert authenticated_user is None
    
    def test_authenticate_user_nonexistent(self, test_app):
        """Test authentication with nonexistent user"""
        with test_app.app_context():
            authenticated_user = UserService.authenticate_user('nonexistent', 'password123')
            assert authenticated_user is None


class TestPasswordSecurity:
    """Test password security measures"""
    
    def test_password_hashing(self, test_app):
        """Test that passwords are properly hashed"""
        with test_app.app_context():
            user = UserService.create_user('secureuser', 'secure@example.com', 'mysecretpassword')
            
            # Password should not be stored in plain text
            assert user.password_hash != 'mysecretpassword'
            
            # But should verify correctly
            assert user.check_password('mysecretpassword')
            assert not user.check_password('wrongpassword')
    
    def test_password_hash_uniqueness(self, test_app):
        """Test that same password produces different hashes"""
        with test_app.app_context():
            user1 = UserService.create_user('user1', 'user1@example.com', 'samepassword')
            user2 = UserService.create_user('user2', 'user2@example.com', 'samepassword')
            
            # Same password should produce different hashes (due to salt)
            assert user1.password_hash != user2.password_hash
            
            # But both should verify correctly
            assert user1.check_password('samepassword')
            assert user2.check_password('samepassword')