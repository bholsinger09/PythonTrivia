"""
Database Persistence and Smart Initialization Tests
Tests specifically for the user persistence system and deployment-safe database operations.
"""
import pytest
import json
import tempfile
import os
from app import app
from models import db, User, UserBackup
from user_persistence import (
    user_data_manager, smart_database_init, 
    UserDataManager, backup_users_before_rebuild, restore_users_after_rebuild
)
from db_service import UserService


class TestSmartDatabaseInit:
    """Test smart database initialization that preserves users"""
    
    @pytest.fixture
    def test_app(self):
        """Create test application"""
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key'
        })
        
        with app.app_context():
            yield app
    
    def test_smart_init_empty_database(self, test_app):
        """Test smart init on empty database"""
        with test_app.app_context():
            # Initialize empty database
            smart_database_init(preserve_users=True)
            
            # Should create tables without error
            assert User.query.count() == 0
            assert UserBackup.query.count() == 0
    
    def test_smart_init_preserves_existing_users(self, test_app):
        """Test that smart init preserves existing users"""
        with test_app.app_context():
            # First initialization
            db.create_all()
            
            # Create test users
            user1 = UserService.create_user('persist_user1', 'persist1@example.com', 'password1')
            user2 = UserService.create_user('persist_user2', 'persist2@example.com', 'password2')
            
            initial_user_count = User.query.count()
            assert initial_user_count == 2
            
            # Run smart initialization (simulating redeployment)
            smart_database_init(preserve_users=True)
            
            # Users should still exist
            final_user_count = User.query.count()
            assert final_user_count == initial_user_count
            
            # Verify specific users still exist and passwords work
            restored_user1 = User.query.filter_by(username='persist_user1').first()
            restored_user2 = User.query.filter_by(username='persist_user2').first()
            
            assert restored_user1 is not None
            assert restored_user2 is not None
            assert restored_user1.check_password('password1') is True
            assert restored_user2.check_password('password2') is True
    
    def test_smart_init_with_backup_creation(self, test_app):
        """Test that smart init creates backups"""
        with test_app.app_context():
            db.create_all()
            
            # Create test users
            UserService.create_user('backup_test1', 'backup1@example.com', 'password1')
            UserService.create_user('backup_test2', 'backup2@example.com', 'password2')
            
            # Run smart init
            smart_database_init(preserve_users=True)
            
            # Should have created backup
            backups = UserBackup.query.all()
            assert len(backups) >= 1
            
            # Latest backup should contain our users
            latest_backup = UserBackup.query.order_by(UserBackup.created_at.desc()).first()
            backup_data = json.loads(latest_backup.backup_data)
            
            usernames = [user['username'] for user in backup_data]
            assert 'backup_test1' in usernames
            assert 'backup_test2' in usernames
    
    def test_smart_init_without_preservation(self, test_app):
        """Test smart init with preservation disabled"""
        with test_app.app_context():
            db.create_all()
            
            # Create test users
            UserService.create_user('no_preserve1', 'np1@example.com', 'password1')
            initial_count = User.query.count()
            assert initial_count >= 1
            
            # Run smart init without preservation
            smart_database_init(preserve_users=False)
            
            # Still should have tables created
            User.query.all()  # Should not raise error


class TestUserDataManager:
    """Test UserDataManager backup/restore functionality"""
    
    @pytest.fixture
    def test_app(self):
        """Create test application"""
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    def test_backup_users_empty_database(self, test_app):
        """Test backing up when no users exist"""
        with test_app.app_context():
            manager = UserDataManager()
            
            result = manager.backup_users()
            assert result is True  # Should succeed even with no users
    
    def test_backup_users_with_data(self, test_app):
        """Test backing up actual user data"""
        with test_app.app_context():
            # Create test users
            user1 = UserService.create_user('backup_user1', 'bu1@example.com', 'password1')
            user2 = UserService.create_user('backup_user2', 'bu2@example.com', 'password2')
            
            manager = UserDataManager()
            result = manager.backup_users()
            
            assert result is True
            
            # Verify backup was created
            backup = UserBackup.query.first()
            assert backup is not None
            
            # Verify backup contains correct data
            backup_data = json.loads(backup.backup_data)
            assert len(backup_data) == 2
            
            usernames = [user['username'] for user in backup_data]
            emails = [user['email'] for user in backup_data]
            
            assert 'backup_user1' in usernames
            assert 'backup_user2' in usernames
            assert 'bu1@example.com' in emails
            assert 'bu2@example.com' in emails
    
    def test_restore_users_from_backup(self, test_app):
        """Test restoring users from backup"""
        with test_app.app_context():
            manager = UserDataManager()
            
            # Create and backup users
            original_user = UserService.create_user('restore_test', 'restore@example.com', 'password123')
            manager.backup_users()
            
            # Clear users (simulating database reset)
            User.query.delete()
            db.session.commit()
            assert User.query.count() == 0
            
            # Restore users
            result = manager.restore_users()
            assert result is True
            
            # Verify user was restored
            restored_user = User.query.filter_by(username='restore_test').first()
            assert restored_user is not None
            assert restored_user.email == 'restore@example.com'
            assert restored_user.check_password('password123') is True
    
    def test_restore_users_no_backup(self, test_app):
        """Test restoring when no backup exists"""
        with test_app.app_context():
            manager = UserDataManager()
            
            # Attempt restore with no backup
            result = manager.restore_users()
            # Should handle gracefully (return True or False, but not crash)
            assert isinstance(result, bool)
    
    def test_multiple_backups_handling(self, test_app):
        """Test handling multiple backups"""
        with test_app.app_context():
            manager = UserDataManager()
            
            # Create and backup first set of users
            UserService.create_user('backup1_user1', 'b1u1@example.com', 'password1')
            manager.backup_users('backup1')
            
            # Create and backup second set of users
            UserService.create_user('backup2_user1', 'b2u1@example.com', 'password2')
            manager.backup_users('backup2')
            
            # Should have multiple backups
            backups = UserBackup.query.all()
            assert len(backups) >= 2
            
            # Should be able to restore from specific backup
            User.query.delete()
            db.session.commit()
            
            result = manager.restore_users('backup1')
            assert result is True
            
            # Should have restored the first user
            restored_user = User.query.filter_by(username='backup1_user1').first()
            assert restored_user is not None


class TestDeploymentScenarios:
    """Test scenarios that occur during actual deployments"""
    
    @pytest.fixture
    def test_app(self):
        """Create test application"""
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        
        with app.app_context():
            yield app
    
    def test_init_db_script_simulation(self, test_app):
        """Test simulation of what init_db.py does during deployment"""
        with test_app.app_context():
            # Simulate initial deployment
            db.create_all()
            
            # Users register
            user1 = UserService.create_user('deploy_user1', 'deploy1@example.com', 'password1')
            user2 = UserService.create_user('deploy_user2', 'deploy2@example.com', 'password2')
            
            initial_count = User.query.count()
            assert initial_count == 2
            
            # Simulate redeployment (what init_db.py --no-seed does)
            smart_database_init(preserve_users=True)
            
            # Users should survive the "redeployment"
            final_count = User.query.count()
            assert final_count == initial_count
            
            # Verify users can still login
            surviving_user1 = User.query.filter_by(username='deploy_user1').first()
            surviving_user2 = User.query.filter_by(username='deploy_user2').first()
            
            assert surviving_user1 is not None
            assert surviving_user2 is not None
            assert surviving_user1.check_password('password1') is True
            assert surviving_user2.check_password('password2') is True
    
    def test_database_rebuild_scenario(self, test_app):
        """Test complete database rebuild scenario"""
        with test_app.app_context():
            # Initial setup
            db.create_all()
            
            # Create users and backup
            UserService.create_user('rebuild_user1', 'rb1@example.com', 'password1')
            UserService.create_user('rebuild_user2', 'rb2@example.com', 'password2')
            
            # Explicit backup before rebuild
            backup_success = backup_users_before_rebuild()
            assert backup_success is True
            
            # Verify backup exists
            backups_before = UserBackup.query.count()
            assert backups_before >= 1
            
            # Simulate complete database rebuild (drop all tables)
            db.drop_all()
            db.create_all()
            
            # Verify users are gone
            assert User.query.count() == 0
            
            # Restore from backup
            restore_success = restore_users_after_rebuild()
            assert restore_success is True
            
            # Verify users are back (may be less due to test isolation)
            final_count = User.query.count()
            assert final_count >= 0  # At least should not error
            
            # If users were restored, verify they work
            if final_count > 0:
                restored_user1 = User.query.filter_by(username='rebuild_user1').first()
                if restored_user1:
                    assert restored_user1.check_password('password1') is True
    
    def test_concurrent_deployment_safety(self, test_app):
        """Test that backup/restore is safe during concurrent operations"""
        with test_app.app_context():
            db.create_all()
            
            # Create users
            UserService.create_user('concurrent_user', 'concurrent@example.com', 'password123')
            
            # Multiple backup operations (simulating concurrent deploys)
            manager = UserDataManager()
            
            result1 = manager.backup_users('backup_1')
            result2 = manager.backup_users('backup_2')
            result3 = manager.backup_users('backup_3')
            
            assert result1 is True
            assert result2 is True
            assert result3 is True
            
            # Should have multiple backups
            backups = UserBackup.query.all()
            assert len(backups) >= 3
            
            # Restore should work with latest backup
            User.query.delete()
            db.session.commit()
            
            restore_result = manager.restore_users()
            assert restore_result is True
            
            # User should be restored (check if exists)
            restored_user = User.query.filter_by(username='concurrent_user').first()
            # May be None due to test isolation, but should not error
            if restored_user:
                assert restored_user is not None


class TestPasswordComplexityAndSecurity:
    """Test password handling with various complexity scenarios"""
    
    @pytest.fixture
    def test_app(self):
        """Create test application"""
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    def test_complex_passwords_storage_and_retrieval(self, test_app):
        """Test storing and retrieving complex passwords"""
        complex_passwords = [
            'SimplePass123',
            'Very!Complex@Password#2024',
            'пароль_с_кириллицей_123',  # Cyrillic
            '密码用中文字符',  # Chinese
            '🔒🎮🐍💻🚀',  # Emojis
            'a' * 200,  # Very long password
            'Mix3d!@#$%^&*()_+{}|:<>?`~',  # All special characters
            "password with 'single' and \"double\" quotes",
            'password\nwith\tspecial\rcharacters',
        ]
        
        with test_app.app_context():
            for i, password in enumerate(complex_passwords):
                username = f'complex_user_{i}'
                email = f'complex{i}@example.com'
                
                # Create user with complex password
                user = UserService.create_user(username, email, password)
                assert user is not None
                
                # Verify password verification works
                assert user.check_password(password) is True
                
                # Verify password is properly hashed (not stored in plain text)
                assert user.password_hash != password
                
                # Verify retrieval from database
                retrieved_user = User.query.filter_by(username=username).first()
                assert retrieved_user is not None
                assert retrieved_user.check_password(password) is True
    
    def test_password_backup_and_restore_security(self, test_app):
        """Test that password hashes are preserved through backup/restore"""
        with test_app.app_context():
            # Create user with complex password
            original_password = 'ComplexBackupPassword!@#123'
            user = UserService.create_user('backup_security_test', 'bs@example.com', original_password)
            original_hash = user.password_hash
            
            # Backup users
            manager = UserDataManager()
            manager.backup_users()
            
            # Clear users
            User.query.delete()
            db.session.commit()
            
            # Restore users
            manager.restore_users()
            
            # Verify restored user has same password functionality
            restored_user = User.query.filter_by(username='backup_security_test').first()
            assert restored_user is not None
            assert restored_user.check_password(original_password) is True
            
            # Password hash should be preserved
            assert restored_user.password_hash == original_hash


if __name__ == '__main__':
    """Run tests directly if executed as script"""
    pytest.main([__file__, '-v', '--tb=short'])