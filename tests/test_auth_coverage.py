"""
Test coverage for authentication error handling paths
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app, check_user_exists, validate_username, validate_email, validate_password


class TestAuthErrorHandling:
    """Test authentication error handling paths to cover lines 379-485"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_check_user_exists_username_taken(self):
        """Test check_user_exists when username exists (line 379-380)"""
        with patch('app.UserService.get_user_by_username') as mock_get_username:
            mock_get_username.return_value = MagicMock()  # User exists
            
            error = check_user_exists('existing_user', 'new@email.com')
            assert error == 'Username already exists'
    
    def test_check_user_exists_email_taken(self):
        """Test check_user_exists when email exists (line 382-383)"""
        with patch('app.UserService.get_user_by_username') as mock_get_username, \
             patch('app.UserService.get_user_by_email') as mock_get_email:
            
            mock_get_username.return_value = None  # Username available
            mock_get_email.return_value = MagicMock()  # Email exists
            
            error = check_user_exists('new_user', 'existing@email.com')
            assert error == 'Email already registered'
    
    def test_check_user_exists_available(self):
        """Test check_user_exists when both username and email are available (line 385)"""
        with patch('app.UserService.get_user_by_username') as mock_get_username, \
             patch('app.UserService.get_user_by_email') as mock_get_email:
            
            mock_get_username.return_value = None  # Username available
            mock_get_email.return_value = None  # Email available
            
            error = check_user_exists('new_user', 'new@email.com')
            assert error is None
    
    def test_register_validation_error_json(self):
        """Test register with validation error in JSON format (line 413-415)"""
        # Send invalid data via JSON
        response = self.app.post('/register', 
                                json={'username': 'xy', 'email': 'invalid', 'password': '123'},
                                content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        # Should get username length error
        assert 'Username must be 3-20 characters' in data['message']
    
    def test_register_validation_error_form(self):
        """Test register with validation error in form format (line 416)"""
        response = self.app.post('/register', data={
            'username': 'xy',  # Too short
            'email': 'test@test.com',
            'password': '123456',
            'confirm_password': '123456'
        })
        
        assert response.status_code == 400
        assert b'Username must be 3-20 characters' in response.data
    
    @patch('app.UserService.create_user')
    def test_register_creation_exception_json(self, mock_create_user):
        """Test register when user creation fails with JSON (line 427-429)"""
        mock_create_user.side_effect = Exception("Database error")
        
        response = self.app.post('/register',
                                json={'username': 'testuser', 'email': 'test@test.com', 
                                     'password': '123456', 'confirm_password': '123456'},
                                content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Registration failed'
    
    @patch('app.UserService.create_user')  
    def test_register_creation_exception_form(self, mock_create_user):
        """Test register when user creation fails with form (line 430-431)"""
        mock_create_user.side_effect = Exception("Database error")
        
        response = self.app.post('/register', data={
            'username': 'testuser',
            'email': 'test@test.com', 
            'password': '123456',
            'confirm_password': '123456'
        })
        
        assert response.status_code == 500
        assert b'Registration failed' in response.data
    
    def test_login_missing_username_json(self):
        """Test login with missing username in JSON (line 452-454)"""
        response = self.app.post('/login',
                                json={'password': '123456'},
                                content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Username and password required'
    
    def test_login_missing_password_form(self):
        """Test login with missing password in form (line 455)"""
        response = self.app.post('/login', data={'username': 'testuser'})
        
        assert response.status_code == 400
        assert b'Username and password required' in response.data
    
    def test_login_username_too_long_json(self):
        """Test login with username too long in JSON (line 457-459)"""
        long_username = 'a' * 21  # Over 20 character limit
        
        response = self.app.post('/login',
                                json={'username': long_username, 'password': '123456'},
                                content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Invalid credentials'
    
    def test_login_password_too_long_form(self):
        """Test login with password too long in form (line 460-461)"""
        long_password = 'a' * 256  # Over 255 character limit
        
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': long_password
        })
        
        assert response.status_code == 400
        assert b'Invalid credentials' in response.data
    
    @patch('app.UserService.get_user_by_username')
    def test_login_user_not_found_json(self, mock_get_user):
        """Test login with non-existent user in JSON (line 471-473)"""
        mock_get_user.return_value = None
        
        response = self.app.post('/login',
                                json={'username': 'nonexistent', 'password': '123456'},
                                content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['message'] == 'Invalid credentials'
    
    @patch('app.UserService.get_user_by_username')
    def test_login_wrong_password_form(self, mock_get_user):
        """Test login with wrong password in form (line 474-475)"""
        mock_user = MagicMock()
        mock_user.check_password.return_value = False
        mock_get_user.return_value = mock_user
        
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        assert b'Invalid credentials' in response.data
    
    @patch('app.UserService.get_user_by_username')
    def test_login_database_exception_json(self, mock_get_user):
        """Test login when database exception occurs in JSON (line 476-479)"""
        mock_get_user.side_effect = Exception("Database connection failed")
        
        response = self.app.post('/login',
                                json={'username': 'testuser', 'password': '123456'},
                                content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['message'] == 'Login failed'
    
    @patch('app.UserService.get_user_by_username')
    def test_login_database_exception_form(self, mock_get_user):
        """Test login when database exception occurs in form (line 480-481)"""
        mock_get_user.side_effect = Exception("Database connection failed")
        
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': '123456'
        })
        
        assert response.status_code == 500
        assert b'Login failed' in response.data
    
    def test_login_get_request(self):
        """Test login GET request (line 483)"""
        response = self.app.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()  # Should render login template
    
    @patch('app.UserService.create_user')
    @patch('app.HAS_LOGIN', True)
    @patch('app.login_user')
    def test_register_success_with_login_json(self, mock_login_user, mock_create_user):
        """Test successful registration with login enabled JSON (line 421-422)"""
        mock_user = MagicMock()
        mock_create_user.return_value = mock_user
        
        response = self.app.post('/register',
                                json={'username': 'newuser', 'email': 'new@test.com',
                                     'password': '123456', 'confirm_password': '123456'},
                                content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Registration successful'
    
    @patch('app.UserService.create_user')
    @patch('app.HAS_LOGIN', True)
    @patch('app.login_user')
    def test_register_success_with_login_form(self, mock_login_user, mock_create_user):
        """Test successful registration with login enabled form (line 424-425)"""
        mock_user = MagicMock()
        mock_create_user.return_value = mock_user
        
        with patch('app.redirect') as mock_redirect:
            response = self.app.post('/register', data={
                'username': 'newuser',
                'email': 'new@test.com',
                'password': '123456',
                'confirm_password': '123456'
            })
            
            # Should call login_user and redirect
            mock_login_user.assert_called_once_with(mock_user)


class TestValidationHelperCoverage:
    """Test validation helper functions for edge cases"""
    
    def test_validate_username_empty(self):
        """Test validate_username with empty string"""
        error = validate_username('')
        assert error == 'Username is required'
    
    def test_validate_username_too_short(self):
        """Test validate_username with too short username"""
        error = validate_username('xy')
        assert error == 'Username must be 3-20 characters'
    
    def test_validate_username_too_long(self):
        """Test validate_username with too long username"""
        error = validate_username('a' * 21)
        assert error == 'Username must be 3-20 characters'
    
    def test_validate_email_empty(self):
        """Test validate_email with empty string"""
        error = validate_email('')
        assert error == 'Email is required'
    
    def test_validate_email_invalid_format(self):
        """Test validate_email with invalid format"""
        error = validate_email('invalid-email')
        assert error == 'Please enter a valid email address'
    
    def test_validate_password_empty(self):
        """Test validate_password with empty password"""
        error = validate_password('', '123456')
        assert error == 'Password is required'
    
    def test_validate_password_too_short(self):
        """Test validate_password with too short password"""
        error = validate_password('123', '123')
        assert error == 'Password must be at least 6 characters'
    
    def test_validate_password_mismatch(self):
        """Test validate_password with mismatched confirmation"""
        error = validate_password('123456', '123457')
        assert error == 'Passwords do not match'
    
    def test_validate_password_valid(self):
        """Test validate_password with valid input"""
        error = validate_password('123456', '123456')
        assert error is None