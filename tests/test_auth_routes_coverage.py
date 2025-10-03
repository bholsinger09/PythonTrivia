"""
Test coverage for authentication route endpoints
Lines 400-433 (register POST) and 446-484 (login POST)
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app


class TestAuthenticationRoutes:
    """Test authentication routes to cover lines 400-433, 446-484"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    # Register route tests (lines 400-433)
    
    @patch('app.validate_username')
    @patch('app.validate_email') 
    @patch('app.validate_password')
    @patch('app.check_user_exists')
    @patch('app.UserService.create_user')
    @patch('app.HAS_LOGIN', True)
    @patch('app.login_user')
    @patch('app.url_for')
    @patch('app.redirect')
    def test_register_successful_form_submission(self, mock_redirect, mock_url_for, mock_login_user, 
                                                 mock_create_user, mock_check_exists, mock_validate_pass,
                                                 mock_validate_email, mock_validate_username):
        """Test successful registration form submission (lines 400-433)"""
        # Setup mocks - all validations pass
        mock_validate_username.return_value = None
        mock_validate_email.return_value = None  
        mock_validate_pass.return_value = None
        mock_check_exists.return_value = None
        
        mock_user = MagicMock()
        mock_create_user.return_value = mock_user
        mock_url_for.return_value = '/game'
        mock_redirect.return_value = MagicMock()
        
        # Test form submission
        response = self.app.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        # Verify all validation functions were called
        mock_validate_username.assert_called_with('testuser')
        mock_validate_email.assert_called_with('test@example.com')
        mock_validate_pass.assert_called_with('password123', 'password123')
        mock_check_exists.assert_called_with('testuser', 'test@example.com')
        
        # Verify user creation and login
        mock_create_user.assert_called_once()
        mock_login_user.assert_called_once_with(mock_user)
        mock_redirect.assert_called_once()
    
    @patch('app.validate_username')
    @patch('app.validate_email')
    @patch('app.validate_password') 
    @patch('app.check_user_exists')
    @patch('app.UserService.create_user')
    def test_register_successful_json_submission(self, mock_create_user, mock_check_exists, 
                                                 mock_validate_pass, mock_validate_email, 
                                                 mock_validate_username):
        """Test successful registration JSON submission (lines 400-433)"""
        # Setup mocks - all validations pass
        mock_validate_username.return_value = None
        mock_validate_email.return_value = None
        mock_validate_pass.return_value = None
        mock_check_exists.return_value = None
        
        mock_user = MagicMock()
        mock_create_user.return_value = mock_user
        
        # Test JSON submission
        response = self.app.post('/register', 
                                json={
                                    'username': 'testuser',
                                    'email': 'test@example.com', 
                                    'password': 'password123',
                                    'confirm_password': 'password123'
                                },
                                content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Registration successful'
    
    @patch('app.validate_username')
    def test_register_validation_error_json(self, mock_validate_username):
        """Test registration validation error with JSON (lines 413-415)"""
        mock_validate_username.return_value = 'Username too short'
        
        response = self.app.post('/register',
                                json={
                                    'username': 'ab',
                                    'email': 'test@example.com',
                                    'password': 'password123',
                                    'confirm_password': 'password123'
                                },
                                content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Username too short'
    
    @patch('app.validate_username')
    @patch('app.render_template')
    def test_register_validation_error_form(self, mock_render, mock_validate_username):
        """Test registration validation error with form (lines 413-415)"""
        mock_validate_username.return_value = 'Username too short'
        mock_render.return_value = 'rendered_template'
        
        response = self.app.post('/register', data={
            'username': 'ab',
            'email': 'test@example.com', 
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 400
        mock_render.assert_called_with('register.html', error='Username too short')
    
    @patch('app.validate_username')
    @patch('app.validate_email')
    @patch('app.validate_password')
    @patch('app.check_user_exists')
    @patch('app.UserService.create_user')
    @patch('app.app.logger')
    def test_register_creation_exception_json(self, mock_logger, mock_create_user, 
                                             mock_check_exists, mock_validate_pass,
                                             mock_validate_email, mock_validate_username):
        """Test registration creation exception with JSON (lines 425-431)"""
        # Setup mocks - validations pass but creation fails
        mock_validate_username.return_value = None
        mock_validate_email.return_value = None
        mock_validate_pass.return_value = None
        mock_check_exists.return_value = None
        mock_create_user.side_effect = Exception("Database error")
        
        response = self.app.post('/register',
                                json={
                                    'username': 'testuser',
                                    'email': 'test@example.com',
                                    'password': 'password123', 
                                    'confirm_password': 'password123'
                                },
                                content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Registration failed'
        
        # Verify error was logged
        mock_logger.error.assert_called_once()
    
    @patch('app.validate_username')
    @patch('app.validate_email') 
    @patch('app.validate_password')
    @patch('app.check_user_exists')
    @patch('app.UserService.create_user')
    @patch('app.app.logger')
    @patch('app.render_template')
    def test_register_creation_exception_form(self, mock_render, mock_logger, mock_create_user,
                                             mock_check_exists, mock_validate_pass,
                                             mock_validate_email, mock_validate_username):
        """Test registration creation exception with form (lines 425-431)"""
        # Setup mocks - validations pass but creation fails
        mock_validate_username.return_value = None
        mock_validate_email.return_value = None
        mock_validate_pass.return_value = None
        mock_check_exists.return_value = None
        mock_create_user.side_effect = Exception("Database error")
        mock_render.return_value = 'rendered_template'
        
        response = self.app.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 500
        mock_render.assert_called_with('register.html', error='Registration failed')
        mock_logger.error.assert_called_once()
    
    @patch('app.render_template')
    def test_register_get_request(self, mock_render):
        """Test register GET request (line 433)"""
        mock_render.return_value = 'rendered_template'
        
        response = self.app.get('/register')
        assert response.status_code == 200
        mock_render.assert_called_with('register.html')
    
    # Login route tests (lines 446-484)
    
    def test_login_missing_username_json(self):
        """Test login with missing username JSON (lines 452-454)"""
        response = self.app.post('/login',
                                json={'password': 'password123'},
                                content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Username and password required'
    
    def test_login_missing_password_json(self):
        """Test login with missing password JSON (lines 452-454)"""
        response = self.app.post('/login',
                                json={'username': 'testuser'},
                                content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Username and password required'
    
    @patch('app.render_template')
    def test_login_missing_credentials_form(self, mock_render):
        """Test login with missing credentials form (lines 452-454)"""
        mock_render.return_value = 'rendered_template'
        
        response = self.app.post('/login', data={'username': 'testuser'})
        assert response.status_code == 400
        mock_render.assert_called_with('login.html', error='Username and password required')
    
    def test_login_username_too_long_json(self):
        """Test login with username too long JSON (lines 456-458)"""
        long_username = 'a' * 25  # Over 20 character limit
        
        response = self.app.post('/login',
                                json={
                                    'username': long_username,
                                    'password': 'password123'
                                },
                                content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Invalid credentials'
    
    def test_login_password_too_long_json(self):
        """Test login with password too long JSON (lines 456-458)"""
        long_password = 'a' * 300  # Over 255 character limit
        
        response = self.app.post('/login',
                                json={
                                    'username': 'testuser',
                                    'password': long_password
                                },
                                content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Invalid credentials'
    
    @patch('app.render_template')
    def test_login_credentials_too_long_form(self, mock_render):
        """Test login with credentials too long form (lines 456-458)"""
        mock_render.return_value = 'rendered_template'
        long_username = 'a' * 25
        
        response = self.app.post('/login', data={
            'username': long_username,
            'password': 'password123'
        })
        
        assert response.status_code == 400
        mock_render.assert_called_with('login.html', error='Invalid credentials')
    
    @patch('app.UserService.get_user_by_username')
    @patch('app.HAS_LOGIN', True)
    @patch('app.login_user')
    @patch('app.url_for')
    @patch('app.redirect')
    def test_login_successful_form(self, mock_redirect, mock_url_for, mock_login_user,
                                  mock_get_user):
        """Test successful login form submission (lines 460-470)"""
        # Setup mock user
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        mock_get_user.return_value = mock_user
        mock_url_for.return_value = '/game'
        mock_redirect.return_value = MagicMock()
        
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        mock_get_user.assert_called_with('testuser')
        mock_user.check_password.assert_called_with('password123')
        mock_login_user.assert_called_with(mock_user)
        mock_redirect.assert_called_once()
    
    @patch('app.UserService.get_user_by_username')
    def test_login_successful_json(self, mock_get_user):
        """Test successful login JSON submission (lines 460-470)"""
        # Setup mock user
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        mock_get_user.return_value = mock_user
        
        response = self.app.post('/login',
                                json={
                                    'username': 'testuser',
                                    'password': 'password123'
                                },
                                content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Login successful'
    
    @patch('app.UserService.get_user_by_username')
    def test_login_invalid_credentials_json(self, mock_get_user):
        """Test login with invalid credentials JSON (lines 471-475)"""
        # Return None user (not found)
        mock_get_user.return_value = None
        
        response = self.app.post('/login',
                                json={
                                    'username': 'nonexistent',
                                    'password': 'password123'
                                },
                                content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Invalid credentials'
    
    @patch('app.UserService.get_user_by_username')
    def test_login_wrong_password_json(self, mock_get_user):
        """Test login with wrong password JSON (lines 471-475)"""
        # Setup mock user with wrong password
        mock_user = MagicMock()
        mock_user.check_password.return_value = False
        mock_get_user.return_value = mock_user
        
        response = self.app.post('/login',
                                json={
                                    'username': 'testuser',
                                    'password': 'wrongpassword'
                                },
                                content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Invalid credentials'
    
    @patch('app.UserService.get_user_by_username')
    @patch('app.render_template')
    def test_login_invalid_credentials_form(self, mock_render, mock_get_user):
        """Test login with invalid credentials form (lines 471-475)"""
        mock_get_user.return_value = None
        mock_render.return_value = 'rendered_template'
        
        response = self.app.post('/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        mock_render.assert_called_with('login.html', error='Invalid credentials')
    
    @patch('app.UserService.get_user_by_username')
    @patch('app.app.logger')
    def test_login_database_exception_json(self, mock_logger, mock_get_user):
        """Test login database exception JSON (lines 476-481)"""
        mock_get_user.side_effect = Exception("Database error")
        
        response = self.app.post('/login',
                                json={
                                    'username': 'testuser',
                                    'password': 'password123'
                                },
                                content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Login failed'
        mock_logger.error.assert_called_once()
    
    @patch('app.UserService.get_user_by_username')
    @patch('app.app.logger')
    @patch('app.render_template')
    def test_login_database_exception_form(self, mock_render, mock_logger, mock_get_user):
        """Test login database exception form (lines 476-481)"""
        mock_get_user.side_effect = Exception("Database error")
        mock_render.return_value = 'rendered_template'
        
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        assert response.status_code == 500
        mock_render.assert_called_with('login.html', error='Login failed')
        mock_logger.error.assert_called_once()
    
    @patch('app.render_template')
    def test_login_get_request(self, mock_render):
        """Test login GET request (line 483)"""
        mock_render.return_value = 'rendered_template'
        
        response = self.app.get('/login')
        assert response.status_code == 200
        mock_render.assert_called_with('login.html')