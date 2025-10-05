"""
End-to-End Registration, Storage, Deployment, and Sign-in Tests
Tests the complete user lifecycle with deployment safety verification.
"""
import pytest
import json
import time
from datetime import datetime
from flask import url_for
from app import app
from models import db, User, UserBackup
from db_service import UserService
from user_persistence import user_data_manager, smart_database_init
import subprocess
import sys
import os


class TestUserLifecycleEndToEnd:
    """Test complete user lifecycle from registration through deployment to sign-in"""
    
    @pytest.fixture
    def test_app(self):
        """Create test application with isolated database"""
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key-lifecycle'
        })
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client"""
        return test_app.test_client()
    
    def test_complete_user_lifecycle_with_deployment(self, client, test_app):
        """
        Test complete user lifecycle:
        1. Register user
        2. Verify storage in database
        3. Simulate deployment (database persistence)
        4. Verify user still exists
        5. Test successful sign-in
        6. Test failed sign-in with wrong password
        """
        with test_app.app_context():
            
            # STEP 1: Register new user
            print("\n🔧 STEP 1: Testing user registration...")
            registration_data = {
                'username': 'lifecycle_test_user',
                'email': 'lifecycle@example.com',
                'password': 'SecurePassword123!',
                'confirm_password': 'SecurePassword123!'
            }
            
            response = client.post('/register', data=registration_data, follow_redirects=False)
            
            # Verify registration was successful
            assert response.status_code in [200, 302], f"Registration failed with status {response.status_code}"
            print("✅ Registration endpoint responded successfully")
            
            # STEP 2: Verify user is stored in database
            print("\n🔧 STEP 2: Verifying user storage in database...")
            user = User.query.filter_by(username='lifecycle_test_user').first()
            assert user is not None, "User was not stored in database after registration"
            assert user.username == 'lifecycle_test_user'
            assert user.email == 'lifecycle@example.com'
            assert user.check_password('SecurePassword123!') is True, "Password verification failed immediately after registration"
            print("✅ User correctly stored in database")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Password hash length: {len(user.password_hash)}")
            print(f"   Password verification: {'✅ Working' if user.check_password('SecurePassword123!') else '❌ Failed'}")
            
            # Get initial user count
            initial_user_count = User.query.count()
            print(f"   Total users in database: {initial_user_count}")
            
            # STEP 3: Simulate deployment (test database persistence)
            print("\n🔧 STEP 3: Simulating deployment with database persistence...")
            
            # Backup users before deployment simulation
            backup_success = user_data_manager.backup_users('deployment_test_backup')
            assert backup_success is True, "Failed to create backup before deployment"
            print("✅ User backup created successfully")
            
            # Verify backup contains our user
            backup = UserBackup.query.filter_by(backup_name='deployment_test_backup').first()
            assert backup is not None, "Backup not found in database"
            backup_data = json.loads(backup.backup_data)
            backup_usernames = [u['username'] for u in backup_data]
            assert 'lifecycle_test_user' in backup_usernames, "User not found in backup data"
            print("✅ User verified in backup data")
            
            # Simulate deployment by running smart database initialization
            # This is what happens during actual deployments
            smart_database_init(preserve_users=True)
            print("✅ Deployment simulation completed (smart_database_init)")
            
            # STEP 4: Verify user still exists after "deployment"
            print("\n🔧 STEP 4: Verifying user persistence after deployment...")
            post_deployment_user_count = User.query.count()
            assert post_deployment_user_count >= initial_user_count, f"Users lost during deployment! Before: {initial_user_count}, After: {post_deployment_user_count}"
            
            persisted_user = User.query.filter_by(username='lifecycle_test_user').first()
            assert persisted_user is not None, "User was removed during deployment simulation"
            assert persisted_user.username == 'lifecycle_test_user'
            assert persisted_user.email == 'lifecycle@example.com'
            assert persisted_user.check_password('SecurePassword123!') is True, "Password verification failed after deployment"
            print("✅ User successfully persisted through deployment")
            print(f"   Users before deployment: {initial_user_count}")
            print(f"   Users after deployment: {post_deployment_user_count}")
            print(f"   Persistence: {'✅ Success' if post_deployment_user_count >= initial_user_count else '❌ Failed'}")
            
            # STEP 5: Test successful sign-in after deployment
            print("\n🔧 STEP 5: Testing successful sign-in after deployment...")
            login_data_correct = {
                'username': 'lifecycle_test_user',
                'password': 'SecurePassword123!'
            }
            
            login_response = client.post('/login', data=login_data_correct, follow_redirects=False)
            assert login_response.status_code in [200, 302], f"Login failed with status {login_response.status_code}"
            
            # If 302, it's a redirect (successful login)
            if login_response.status_code == 302:
                print("✅ Login successful (302 redirect)")
                redirect_location = login_response.headers.get('Location', '')
                print(f"   Redirected to: {redirect_location}")
            else:
                # If 200, check that there's no error message
                response_text = login_response.data.decode('utf-8').lower()
                assert 'invalid' not in response_text and 'error' not in response_text, "Login returned error message"
                print("✅ Login successful (200 response)")
            
            # STEP 6: Test failed sign-in with wrong password
            print("\n🔧 STEP 6: Testing failed sign-in with wrong password...")
            login_data_wrong = {
                'username': 'lifecycle_test_user',
                'password': 'WrongPassword123!'
            }
            
            wrong_password_response = client.post('/login', data=login_data_wrong, follow_redirects=False)
            
            # Should return error (400, 401) or error page (200 with error message)
            if wrong_password_response.status_code in [400, 401]:
                print("✅ Wrong password correctly rejected (400/401 status)")
            elif wrong_password_response.status_code == 200:
                response_text = wrong_password_response.data.decode('utf-8').lower()
                assert any(word in response_text for word in ['invalid', 'incorrect', 'wrong', 'error']), "No error message shown for wrong password"
                print("✅ Wrong password correctly rejected (error message shown)")
            else:
                pytest.fail(f"Unexpected response for wrong password: {wrong_password_response.status_code}")
            
            print("\n🎉 ALL LIFECYCLE TESTS PASSED!")
            print("=" * 50)
            print("✅ User registration: Working")
            print("✅ Database storage: Working") 
            print("✅ Deployment persistence: Working")
            print("✅ Correct password login: Working")
            print("✅ Wrong password rejection: Working")


class TestMultipleUsersDeploymentSafety:
    """Test deployment safety with multiple users"""
    
    @pytest.fixture
    def test_app(self):
        """Create test application"""
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-multiple-users'
        })
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client"""
        return test_app.test_client()
    
    def test_multiple_users_deployment_persistence(self, client, test_app):
        """
        Test that multiple users all persist through deployment and can sign in
        """
        with test_app.app_context():
            
            # Create multiple users
            users_data = [
                ('user_alpha', 'alpha@example.com', 'AlphaPass123!'),
                ('user_beta', 'beta@example.com', 'BetaPass456!'),
                ('user_gamma', 'gamma@example.com', 'GammaPass789!'),
                ('user_delta', 'delta@example.com', 'DeltaPass000!')
            ]
            
            print(f"\n🔧 Registering {len(users_data)} users...")
            
            # Register all users
            for username, email, password in users_data:
                registration_data = {
                    'username': username,
                    'email': email,
                    'password': password,
                    'confirm_password': password
                }
                
                response = client.post('/register', data=registration_data)
                assert response.status_code in [200, 302], f"Registration failed for {username}"
                
                # Verify immediate storage
                user = User.query.filter_by(username=username).first()
                assert user is not None, f"User {username} not stored immediately after registration"
                assert user.check_password(password) is True, f"Password verification failed for {username}"
                
                print(f"✅ {username} registered and verified")
            
            initial_count = User.query.count()
            print(f"📊 Total users before deployment: {initial_count}")
            
            # Simulate deployment
            print("\n🔧 Simulating deployment with multiple users...")
            smart_database_init(preserve_users=True)
            
            # Verify all users still exist
            final_count = User.query.count()
            assert final_count >= initial_count, f"Users lost! Before: {initial_count}, After: {final_count}"
            print(f"📊 Total users after deployment: {final_count}")
            
            # Test login for each user
            print("\n🔧 Testing login for all users after deployment...")
            for username, email, password in users_data:
                # Test correct password
                login_data = {
                    'username': username,
                    'password': password
                }
                
                response = client.post('/login', data=login_data, follow_redirects=False)
                assert response.status_code in [200, 302], f"Login failed for {username} after deployment"
                print(f"✅ {username} login successful after deployment")
                
                # Test wrong password
                wrong_login_data = {
                    'username': username,
                    'password': 'WrongPassword123!'
                }
                
                wrong_response = client.post('/login', data=wrong_login_data)
                if wrong_response.status_code in [400, 401]:
                    print(f"✅ {username} wrong password correctly rejected")
                elif wrong_response.status_code == 200:
                    response_text = wrong_response.data.decode('utf-8').lower()
                    assert any(word in response_text for word in ['invalid', 'incorrect', 'wrong', 'error']), f"No error message for {username} wrong password"
                    print(f"✅ {username} wrong password correctly rejected (error shown)")
            
            print(f"\n🎉 ALL {len(users_data)} USERS PASSED DEPLOYMENT AND LOGIN TESTS!")


class TestDatabaseIntegrityAcrossDeployments:
    """Test database integrity and consistency across multiple deployments"""
    
    @pytest.fixture
    def test_app(self):
        """Create test application"""
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-db-integrity'
        })
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client"""
        return test_app.test_client()
    
    def test_database_integrity_multiple_deployments(self, client, test_app):
        """
        Test database integrity across multiple deployment cycles
        """
        with test_app.app_context():
            
            # Initial user creation
            print("\n🔧 Creating initial users...")
            initial_users = [
                ('integrity_user1', 'int1@example.com', 'IntegrityPass1!'),
                ('integrity_user2', 'int2@example.com', 'IntegrityPass2!')
            ]
            
            for username, email, password in initial_users:
                registration_data = {
                    'username': username,
                    'email': email,
                    'password': password,
                    'confirm_password': password
                }
                
                response = client.post('/register', data=registration_data)
                assert response.status_code in [200, 302]
                print(f"✅ {username} registered")
            
            initial_count = User.query.count()
            
            # Simulate multiple deployment cycles
            deployment_cycles = 3
            print(f"\n🔧 Simulating {deployment_cycles} deployment cycles...")
            
            for cycle in range(1, deployment_cycles + 1):
                print(f"\n--- Deployment Cycle {cycle} ---")
                
                # Simulate deployment
                smart_database_init(preserve_users=True)
                
                # Verify user count maintained
                current_count = User.query.count()
                assert current_count >= initial_count, f"Users lost in cycle {cycle}! Expected: {initial_count}, Got: {current_count}"
                
                # Verify each user still works
                for username, email, password in initial_users:
                    user = User.query.filter_by(username=username).first()
                    assert user is not None, f"User {username} missing after cycle {cycle}"
                    assert user.email == email, f"Email corrupted for {username} in cycle {cycle}"
                    assert user.check_password(password) is True, f"Password broken for {username} in cycle {cycle}"
                    
                    # Test login still works
                    login_data = {'username': username, 'password': password}
                    response = client.post('/login', data=login_data, follow_redirects=False)
                    assert response.status_code in [200, 302], f"Login failed for {username} in cycle {cycle}"
                
                print(f"✅ Cycle {cycle}: All users intact and functional")
                
                # Add a user mid-deployment testing
                if cycle == 2:
                    mid_username = f'mid_deployment_user'
                    mid_data = {
                        'username': mid_username,
                        'email': 'mid@example.com',
                        'password': 'MidPass123!',
                        'confirm_password': 'MidPass123!'
                    }
                    
                    response = client.post('/register', data=mid_data)
                    assert response.status_code in [200, 302]
                    initial_users.append((mid_username, 'mid@example.com', 'MidPass123!'))
                    initial_count += 1
                    print(f"✅ Added user during deployment cycle {cycle}")
            
            final_count = User.query.count()
            print(f"\n📊 Final Results:")
            print(f"   Users at start: {len(initial_users) - 1}")  # -1 because we added one mid-cycle
            print(f"   Users at end: {final_count}")
            print(f"   Deployments survived: {deployment_cycles}")
            print(f"   Integrity: {'✅ Perfect' if final_count >= len(initial_users) else '❌ Compromised'}")
            
            assert final_count >= len(initial_users), "User data integrity compromised across deployments"
            print("\n🎉 DATABASE INTEGRITY MAINTAINED ACROSS ALL DEPLOYMENTS!")


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    @pytest.fixture
    def test_app(self):
        """Create test application"""
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-real-world'
        })
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client"""
        return test_app.test_client()
    
    def test_user_registers_deploys_returns_weeks_later(self, client, test_app):
        """
        Simulate real scenario: User registers, app gets deployed multiple times,
        user returns weeks later and tries to log in
        """
        with test_app.app_context():
            
            print("\n🔧 SCENARIO: User registers, app deploys, user returns later...")
            
            # Day 1: User registers
            print("📅 Day 1: User registration")
            registration_data = {
                'username': 'returning_user',
                'email': 'returning@example.com', 
                'password': 'RememberThisPassword123!',
                'confirm_password': 'RememberThisPassword123!'
            }
            
            response = client.post('/register', data=registration_data)
            assert response.status_code in [200, 302]
            
            original_user = User.query.filter_by(username='returning_user').first()
            assert original_user is not None
            original_hash = original_user.password_hash
            print("✅ User registered on Day 1")
            
            # Simulate multiple deployments over time
            print("\n📅 Weeks 1-4: Multiple deployments occur...")
            for week in range(1, 5):
                print(f"   Week {week}: Deployment...")
                smart_database_init(preserve_users=True)
                
                # Verify user still exists
                user = User.query.filter_by(username='returning_user').first()
                assert user is not None, f"User lost during week {week} deployment"
                print(f"   ✅ Week {week}: User still in database")
            
            # Day 30: User returns and tries to log in
            print("\n📅 Day 30: User returns and tries to log in...")
            returning_user = User.query.filter_by(username='returning_user').first()
            assert returning_user is not None, "User missing after 4 weeks of deployments"
            assert returning_user.email == 'returning@example.com', "User email corrupted"
            
            # Test login with correct password
            login_data = {
                'username': 'returning_user',
                'password': 'RememberThisPassword123!'
            }
            
            response = client.post('/login', data=login_data, follow_redirects=False)
            assert response.status_code in [200, 302], "User cannot log in after weeks of deployments"
            print("✅ User successfully logged in after weeks of deployments")
            
            # Test that password is still the same (hash integrity)
            assert returning_user.password_hash == original_hash, "Password hash changed over deployments"
            print("✅ Password hash integrity maintained")
            
            # Test wrong password still fails
            wrong_login_data = {
                'username': 'returning_user',
                'password': 'ForgotMyPassword123!'
            }
            
            wrong_response = client.post('/login', data=wrong_login_data)
            if wrong_response.status_code in [400, 401]:
                print("✅ Wrong password correctly rejected after deployments")
            elif wrong_response.status_code == 200:
                response_text = wrong_response.data.decode('utf-8').lower()
                assert any(word in response_text for word in ['invalid', 'incorrect', 'wrong', 'error'])
                print("✅ Wrong password correctly rejected (error message)")
            
            print("\n🎉 REAL-WORLD SCENARIO PASSED!")
            print("✅ User data survives weeks of deployments")
            print("✅ Login functionality remains intact")
            print("✅ Security measures still work")


if __name__ == '__main__':
    """Run tests directly if executed as script"""
    pytest.main([__file__, '-v', '--tb=short'])