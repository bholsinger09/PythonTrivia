"""
User Data Persistence System - Deployment Compatible
Maintains user registrations across database rebuilds using database-native storage
No dependency on local file system - works in all deployment environments
"""
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from models import db, User

logger = logging.getLogger(__name__)

class UserDataManager:
    """
    Deployment-compatible user data persistence manager
    Uses database storage instead of local files for universal compatibility
    """
    
    def __init__(self, default_backup_name: str = "auto_backup"):
        """Initialize with default backup name"""
        self.default_backup_name = default_backup_name
    
    def backup_users(self, backup_name: Optional[str] = None) -> bool:
        """
        Backup all user data to database
        Returns True if successful, False otherwise
        """
        try:
            # Import here to avoid circular imports
            from models import UserBackup
            
            users = User.query.all()
            if not users:
                logger.info("No users to backup")
                return True
            
            # Convert users to serializable format
            user_data = []
            for user in users:
                user_dict = {
                    'username': user.username,
                    'email': user.email,
                    'password_hash': user.password_hash,
                    'created_at': user.created_at.isoformat(),
                    'last_seen': user.last_seen.isoformat() if user.last_seen else None,
                    'is_active': user.is_active,
                    'preferred_difficulty': user.preferred_difficulty.value if user.preferred_difficulty else None,
                    'preferred_categories': user.preferred_categories,
                    'total_games_played': user.total_games_played,
                    'total_questions_answered': user.total_questions_answered,
                    'total_correct_answers': user.total_correct_answers,
                    'best_streak': user.best_streak,
                    'total_points': user.total_points
                }
                user_data.append(user_dict)
            
            # Save backup to database
            backup_name = backup_name or self.default_backup_name
            UserBackup.save_backup(backup_name, user_data)
            
            logger.info(f"Successfully backed up {len(user_data)} users to database (backup: {backup_name})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup users: {e}")
            return False
    
    def restore_users(self, backup_name: Optional[str] = None) -> bool:
        """
        Restore users from database backup
        Returns True if successful, False otherwise
        """
        try:
            # Import here to avoid circular imports
            from models import UserBackup, Difficulty
            
            backup_name = backup_name or self.default_backup_name
            users_data = UserBackup.load_backup(backup_name)
            
            if not users_data:
                logger.info(f"No backup found with name '{backup_name}' - no users to restore")
                return True
            
            # Check existing users to avoid duplicates
            existing_usernames = {user.username for user in User.query.all()}
            existing_emails = {user.email for user in User.query.all()}
            
            restored_count = 0
            skipped_count = 0
            
            for user_data in users_data:
                # Skip if user already exists
                if (user_data['username'] in existing_usernames or 
                    user_data['email'] in existing_emails):
                    skipped_count += 1
                    continue
                
                # Create user from backup data
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    created_at=datetime.fromisoformat(user_data['created_at'].replace('Z', '+00:00')),
                    last_seen=datetime.fromisoformat(user_data['last_seen'].replace('Z', '+00:00')) if user_data['last_seen'] else None,
                    is_active=user_data['is_active'],
                    preferred_difficulty=Difficulty(user_data['preferred_difficulty']) if user_data['preferred_difficulty'] else None,
                    preferred_categories=user_data['preferred_categories'],
                    total_games_played=user_data['total_games_played'],
                    total_questions_answered=user_data['total_questions_answered'],
                    total_correct_answers=user_data['total_correct_answers'],
                    best_streak=user_data['best_streak'],
                    total_points=user_data['total_points']
                )
                
                db.session.add(user)
                restored_count += 1
            
            if restored_count > 0:
                db.session.commit()
                logger.info(f"Successfully restored {restored_count} users from backup '{backup_name}' ({skipped_count} skipped as duplicates)")
            else:
                logger.info("No new users to restore")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore users: {e}")
            db.session.rollback()
            return False
    
    def has_backup(self, backup_name: Optional[str] = None) -> bool:
        """Check if a backup exists in database"""
        try:
            from models import UserBackup
            backup_name = backup_name or self.default_backup_name
            return UserBackup.query.filter_by(backup_name=backup_name).first() is not None
        except Exception as e:
            logger.error(f"Failed to check backup existence: {e}")
            return False
    
    def get_backup_info(self, backup_name: Optional[str] = None) -> Optional[Dict]:
        """Get information about a database backup"""
        try:
            from models import UserBackup
            backup_name = backup_name or self.default_backup_name
            backup = UserBackup.query.filter_by(backup_name=backup_name).first()
            
            if not backup:
                return None
            
            backup_dict = backup.to_dict()
            user_count = len(backup_dict['backup_data']) if backup_dict['backup_data'] else 0
            
            return {
                'backup_name': backup.backup_name,
                'backup_timestamp': backup.updated_at.isoformat(),
                'created_at': backup.created_at.isoformat(),
                'user_count': user_count,
                'storage_type': 'database'
            }
            
        except Exception as e:
            logger.error(f"Failed to get backup info: {e}")
            return None
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        try:
            from models import UserBackup
            backups = UserBackup.list_backups()
            
            backup_info = []
            for backup in backups:
                backup_dict = backup.to_dict()
                user_count = len(backup_dict['backup_data']) if backup_dict['backup_data'] else 0
                
                backup_info.append({
                    'backup_name': backup.backup_name,
                    'user_count': user_count,
                    'created_at': backup.created_at.isoformat(),
                    'updated_at': backup.updated_at.isoformat()
                })
            
            return backup_info
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def clear_backup(self, backup_name: Optional[str] = None) -> bool:
        """Remove a backup from database"""
        try:
            from models import UserBackup
            backup_name = backup_name or self.default_backup_name
            backup = UserBackup.query.filter_by(backup_name=backup_name).first()
            
            if backup:
                db.session.delete(backup)
                db.session.commit()
                logger.info(f"Backup '{backup_name}' removed from database")
            else:
                logger.info(f"No backup named '{backup_name}' found")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove backup: {e}")
            db.session.rollback()
            return False


# Global instance
user_data_manager = UserDataManager()


def backup_users_before_rebuild(backup_name: Optional[str] = None) -> bool:
    """Convenience function to backup users before rebuild"""
    return user_data_manager.backup_users(backup_name)


def restore_users_after_rebuild(backup_name: Optional[str] = None) -> bool:
    """Convenience function to restore users after rebuild"""
    return user_data_manager.restore_users(backup_name)


def smart_database_init(preserve_users: bool = True) -> None:
    """
    Smart database initialization that preserves user data using database storage
    
    Args:
        preserve_users: If True, backup and restore user data
    """
    try:
        if preserve_users:
            # Backup existing users before any database operations
            logger.info("Backing up existing user data to database...")
            user_data_manager.backup_users()
        
        # Create tables (this is safe to run multiple times)
        db.create_all()
        
        if preserve_users:
            # Restore users after table creation
            logger.info("Restoring user data from database backup...")
            user_data_manager.restore_users()
        
        # Ensure code_monkey user exists with standard password
        create_default_users()
        
        logger.info("Smart database initialization completed with deployment-compatible persistence")
        
    except Exception as e:
        logger.error(f"Smart database initialization failed: {e}")
        raise


def create_default_users() -> None:
    """Create default users like code_monkey if they don't exist"""
    try:
        # Check if code_monkey user exists
        code_monkey = User.query.filter_by(username='code_monkey').first()
        
        if not code_monkey:
            # Create code_monkey user with standard password
            code_monkey = User(
                username='code_monkey',
                email='code_monkey@example.com'
            )
            code_monkey.set_password('password123')
            db.session.add(code_monkey)
            db.session.commit()
            logger.info("Created default user: code_monkey")
        else:
            # Ensure code_monkey has the correct password
            if not code_monkey.check_password('password123'):
                code_monkey.set_password('password123')
                db.session.commit()
                logger.info("Reset password for existing user: code_monkey")
            else:
                logger.info("Default user code_monkey already exists with correct password")
                
    except Exception as e:
        logger.error(f"Failed to create default users: {e}")
        # Don't raise - this shouldn't break the initialization


def get_user_backup_status() -> Dict:
    """Get current backup status for monitoring"""
    backup_info = user_data_manager.get_backup_info()
    current_user_count = User.query.count()
    all_backups = user_data_manager.list_backups()
    
    return {
        'current_users': current_user_count,
        'has_backup': user_data_manager.has_backup(),
        'backup_info': backup_info,
        'total_backups': len(all_backups),
        'all_backups': all_backups,
        'storage_type': 'database',
        'deployment_compatible': True
    }