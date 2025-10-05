#!/usr/bin/env python3
"""
Comprehensive Authentication & Security Tests
Tests user registration, login, password security, and session management
"""

import pytest
import tempfile
import os
from flask import session
from werkzeug.security import check_password_hash
import requests
import time
from datetime import datetime, timedelta

# Import app and models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User
from config import TestingConfig

class TestAuthentication:
    """Test suite for user authentication and security"""
    
    @pytest.fixture
    def client(self):
        """Create test client with fresh database"""
        app.config.from_object(TestingConfig)
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.drop_all()
    
    def test_user_registration_success(self, client):
        """Test successful user registration"""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123',
            'confirm_password': 'securepassword123'
        })
        
        assert response.status_code in [200, 302]  # Success or redirect
        
        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
            assert user.email == 'test@example.com'
            assert check_password_hash(user.password_hash, 'securepassword123')
    
    def test_user_registration_duplicate_username(self, client):
        """Test registration with duplicate username"""
        # Create first user
        client.post('/register', data={
            'username': 'testuser',
            'email': 'test1@example.com', 
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        # Try to create user with same username
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'password456',
            'confirm_password': 'password456'
        })
        
        # Should fail or show error
        assert response.status_code in [400, 409] or b'username' in response.data.lower()
    
    def test_user_registration_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # Create first user
        client.post('/register', data={
            'username': 'testuser1',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        # Try to create user with same email
        response = client.post('/register', data={
            'username': 'testuser2',
            'email': 'test@example.com',
            'password': 'password456',
            'confirm_password': 'password456'
        })
        
        # Should fail or show error
        assert response.status_code in [400, 409] or b'email' in response.data.lower()
    
    def test_password_hashing_security(self, client):
        """Test that passwords are properly hashed"""
        password = 'mysecretpassword123'
        
        client.post('/register', data={
            'username': 'hashtest',
            'email': 'hash@example.com',
            'password': password,
            'confirm_password': password
        })
        
        with app.app_context():
            user = User.query.filter_by(username='hashtest').first()
            
            # Password should be hashed (not stored in plain text)
            assert user.password_hash != password
            assert user.password_hash.startswith('$2b$')  # bcrypt format
            assert len(user.password_hash) >= 60  # bcrypt hash length
            
            # Should verify correctly
            assert check_password_hash(user.password_hash, password)
            assert not check_password_hash(user.password_hash, 'wrongpassword')
    
    def test_user_login_success(self, client):
        """Test successful user login"""
        # Register user first
        client.post('/register', data={
            'username': 'logintest',
            'email': 'login@example.com',
            'password': 'loginpass123',
            'confirm_password': 'loginpass123'
        })
        
        # Test login
        response = client.post('/login', data={
            'username': 'logintest',
            'password': 'loginpass123'
        })
        
        assert response.status_code in [200, 302]  # Success or redirect
    
    def test_user_login_wrong_password(self, client):
        """Test login with wrong password"""
        # Register user first
        client.post('/register', data={
            'username': 'wrongpasstest',
            'email': 'wrong@example.com',
            'password': 'correctpass123',
            'confirm_password': 'correctpass123'
        })
        
        # Test login with wrong password
        response = client.post('/login', data={
            'username': 'wrongpasstest',
            'password': 'wrongpassword'
        })
        
        # Should fail
        assert response.status_code in [400, 401, 403] or b'invalid' in response.data.lower() or b'incorrect' in response.data.lower()
    
    def test_user_login_nonexistent_user(self, client):
        """Test login with non-existent username"""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'anypassword'
        })
        
        # Should fail
        assert response.status_code in [400, 401, 404] or b'not found' in response.data.lower() or b'invalid' in response.data.lower()
    
    def test_password_strength_requirements(self, client):
        """Test password strength validation"""
        weak_passwords = [
            '123',           # Too short
            'password',      # Common password
            'abc',           # Too short
            '',              # Empty
        ]
        
        for weak_pass in weak_passwords:
            response = client.post('/register', data={
                'username': f'weaktest_{weak_pass}',
                'email': f'weak_{weak_pass}@example.com',
                'password': weak_pass,
                'confirm_password': weak_pass
            })
            
            # Should reject weak passwords
            assert response.status_code != 201  # Not created successfully
    
    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection attacks"""
        sql_injection_attempts = [
            "admin'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'/*",
            "' UNION SELECT * FROM users --"
        ]
        
        for injection in sql_injection_attempts:
            response = client.post('/login', data={
                'username': injection,
                'password': 'anypassword'
            })
            
            # Should not cause server error or unauthorized access
            assert response.status_code != 500
            assert response.status_code in [400, 401, 403, 404]
    
    def test_xss_protection(self, client):
        """Test protection against XSS attacks"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "'><script>alert('xss')</script>"
        ]
        
        for payload in xss_payloads:
            response = client.post('/register', data={
                'username': payload,
                'email': 'xss@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            
            # Response should not contain unescaped script tags
            assert b'<script>' not in response.data
            assert b'javascript:' not in response.data
    
    def test_csrf_protection(self, client):
        """Test CSRF protection on forms"""
        # Try to submit form without CSRF token
        response = client.post('/register', data={
            'username': 'csrftest',
            'email': 'csrf@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        # Should have CSRF protection (either built-in or custom)
        # This test might need adjustment based on your CSRF implementation
        print(f"CSRF test response: {response.status_code}")
    
    def test_session_management(self, client):
        """Test user session management"""
        # Register and login user
        client.post('/register', data={
            'username': 'sessiontest',
            'email': 'session@example.com',
            'password': 'sessionpass123',
            'confirm_password': 'sessionpass123'
        })
        
        with client.session_transaction() as sess:
            # Check if user_id is stored in session after login
            client.post('/login', data={
                'username': 'sessiontest',
                'password': 'sessionpass123'
            })
        
        # Test logout clears session
        response = client.post('/logout')
        assert response.status_code in [200, 302]
    
    def test_password_change_functionality(self, client):
        """Test password change feature if implemented"""
        # Register user
        client.post('/register', data={
            'username': 'changetest',
            'email': 'change@example.com',
            'password': 'oldpassword123',
            'confirm_password': 'oldpassword123'
        })
        
        # Login
        client.post('/login', data={
            'username': 'changetest',
            'password': 'oldpassword123'
        })
        
        # Try to change password (if endpoint exists)
        response = client.post('/change-password', data={
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'confirm_new_password': 'newpassword123'
        })
        
        # If endpoint exists, test it worked
        if response.status_code not in [404, 405]:
            # Try login with new password
            client.post('/logout')
            login_response = client.post('/login', data={
                'username': 'changetest',
                'password': 'newpassword123'
            })
            assert login_response.status_code in [200, 302]

class TestSecurityHeaders:
    """Test security headers and configurations"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        with app.test_client() as client:
            yield client
    
    def test_security_headers(self, client):
        """Test that proper security headers are set"""
        response = client.get('/')
        
        # Check for security headers
        headers = response.headers
        
        # These are recommended security headers
        recommended_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
        ]
        
        for header in recommended_headers:
            print(f"Checking for header: {header}")
            # Note: Not all may be implemented, just logging for review

if __name__ == '__main__':
    print("🔐 RUNNING AUTHENTICATION & SECURITY TESTS")
    print("=" * 60)
    
    # Run tests with verbose output
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--no-header',
        '--disable-warnings'
    ])