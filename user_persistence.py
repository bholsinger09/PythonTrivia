"""
User Data Persistence System
Maintains user registrations across database rebuilds and clean builds
"""
import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from models import db, User

logger = logging.getLogger(__name__)

class UserDataManager:
    """Manages user data persistence across database rebuilds"""
    
    def __init__(self, backup_dir: str = "instance/backups"):
        """Initialize with backup directory"""
        self.backup_dir = backup_dir
        self.backup_file = os.path.join(backup_dir, "user_data_backup.json")
        
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
    
    def backup_users(self) -> bool:
        """
        Backup all user data to JSON file
        Returns True if successful, False otherwise
        """
        try:
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
            
            # Write backup file
            backup_data = {
                'backup_timestamp': datetime.now(timezone.utc).isoformat(),
                'user_count': len(user_data),
                'users': user_data
            }
            
            with open(self.backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Successfully backed up {len(user_data)} users to {self.backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup users: {e}")
            return False
    
    def restore_users(self) -> bool:
        """
        Restore users from backup file
        Returns True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.backup_file):
                logger.info("No backup file found - no users to restore")
                return True
            
            with open(self.backup_file, 'r') as f:
                backup_data = json.load(f)
            
            users_data = backup_data.get('users', [])
            if not users_data:
                logger.info("No users in backup file")
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
                from models import Difficulty  # Import here to avoid circular imports
                
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
                logger.info(f"Successfully restored {restored_count} users ({skipped_count} skipped as duplicates)")
            else:
                logger.info("No new users to restore")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore users: {e}")
            db.session.rollback()
            return False
    
    def has_backup(self) -> bool:
        """Check if a backup file exists"""
        return os.path.exists(self.backup_file)
    
    def get_backup_info(self) -> Optional[Dict]:
        """Get information about the backup file"""
        try:
            if not self.has_backup():
                return None
                
            with open(self.backup_file, 'r') as f:
                backup_data = json.load(f)
            
            return {
                'backup_timestamp': backup_data.get('backup_timestamp'),
                'user_count': backup_data.get('user_count', 0),
                'file_size': os.path.getsize(self.backup_file),
                'file_path': self.backup_file
            }
            
        except Exception as e:
            logger.error(f"Failed to get backup info: {e}")
            return None
    
    def clear_backup(self) -> bool:
        """Remove the backup file"""
        try:
            if os.path.exists(self.backup_file):
                os.remove(self.backup_file)
                logger.info("Backup file removed")
            return True
        except Exception as e:
            logger.error(f"Failed to remove backup file: {e}")
            return False


# Global instance
user_data_manager = UserDataManager()


def backup_users_before_rebuild() -> bool:
    """Convenience function to backup users before rebuild"""
    return user_data_manager.backup_users()


def restore_users_after_rebuild() -> bool:
    """Convenience function to restore users after rebuild"""
    return user_data_manager.restore_users()


def smart_database_init(preserve_users: bool = True) -> None:
    """
    Smart database initialization that preserves user data
    
    Args:
        preserve_users: If True, backup and restore user data
    """
    try:
        if preserve_users:
            # Backup existing users before any database operations
            logger.info("Backing up existing user data...")
            user_data_manager.backup_users()
        
        # Create tables (this is safe to run multiple times)
        db.create_all()
        
        if preserve_users:
            # Restore users after table creation
            logger.info("Restoring user data...")
            user_data_manager.restore_users()
        
        logger.info("Smart database initialization completed")
        
    except Exception as e:
        logger.error(f"Smart database initialization failed: {e}")
        raise


def get_user_backup_status() -> Dict:
    """Get current backup status for monitoring"""
    backup_info = user_data_manager.get_backup_info()
    current_user_count = User.query.count()
    
    return {
        'current_users': current_user_count,
        'has_backup': user_data_manager.has_backup(),
        'backup_info': backup_info,
        'backup_newer_than_db': False  # Could implement timestamp comparison
    }