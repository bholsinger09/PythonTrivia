#!/usr/bin/env python3
"""
User Data Management Script - Deployment Compatible
Provides easy commands for backing up, restoring, and managing user data persistence
Now using database-native storage for deployment compatibility
"""
import sys
import argparse
from flask import Flask
from app import app
from user_persistence import user_data_manager, get_user_backup_status
from models import db, User, UserBackup

def create_app_context():
    """Create app context for operations"""
    return app.app_context()

def backup_users(backup_name=None):
    """Backup user data to database"""
    with create_app_context():
        backup_name = backup_name or 'cli_backup'
        if user_data_manager.backup_users(backup_name):
            user_count = User.query.count()
            print(f"✅ Successfully backed up {user_count} users to database (backup: {backup_name})")
            print(f"📦 Storage: Database-native (deployment compatible)")
            return True
        else:
            print("❌ Failed to backup users")
            return False

def restore_users(backup_name=None):
    """Restore user data from database backup"""
    with create_app_context():
        backup_name = backup_name or 'cli_backup'
        
        if not user_data_manager.has_backup(backup_name):
            print(f"❌ No backup found with name '{backup_name}'")
            # Show available backups
            available = user_data_manager.list_backups()
            if available:
                print("Available backups:")
                for backup in available:
                    print(f"  • {backup['backup_name']} ({backup['user_count']} users)")
            return False
        
        if user_data_manager.restore_users(backup_name):
            user_count = User.query.count()
            print(f"✅ Successfully restored users from backup '{backup_name}'")
            print(f"👥 Total users now: {user_count}")
            return True
        else:
            print("❌ Failed to restore users")
            return False

def show_status():
    """Show current backup and user status"""
    with create_app_context():
        status = get_user_backup_status()
        
        print("\n📊 User Data Status (Deployment Compatible):")
        print("=" * 50)
        print(f"Current users in database: {status['current_users']}")
        print(f"Storage type: {status.get('storage_type', 'database')} ✅")
        print(f"Deployment compatible: {status.get('deployment_compatible', True)} ✅")
        print(f"Total backups available: {status.get('total_backups', 0)}")
        
        if status['backup_info']:
            backup_info = status['backup_info']
            print(f"\nDefault backup info:")
            print(f"  • Backup name: {backup_info['backup_name']}")
            print(f"  • Last updated: {backup_info['backup_timestamp']}")
            print(f"  • Users in backup: {backup_info['user_count']}")
            print(f"  • Created: {backup_info['created_at']}")
        
        print()

def list_users():
    """List current users in database"""
    with create_app_context():
        users = User.query.all()
        
        if not users:
            print("No users found in database")
            return
        
        print(f"\n👥 Current Users ({len(users)}):")
        print("-" * 50)
        for user in users:
            print(f"• {user.username} ({user.email})")
            print(f"  Created: {user.created_at}")
            print(f"  Games: {user.total_games_played}, Points: {user.total_points}")
            print()

def list_backups():
    """List all available backups in database"""
    with create_app_context():
        backups = user_data_manager.list_backups()
        
        if not backups:
            print("No backups found in database")
            return
        
        print(f"\n💾 Available Backups ({len(backups)}):")
        print("-" * 50)
        for backup in backups:
            print(f"• {backup['backup_name']}")
            print(f"  Users: {backup['user_count']}")
            print(f"  Created: {backup['created_at']}")
            print(f"  Updated: {backup['updated_at']}")
            print()

def clear_backup(backup_name=None):
    """Remove backup from database"""
    with create_app_context():
        backup_name = backup_name or 'cli_backup'
        
        if not user_data_manager.has_backup(backup_name):
            print(f"❌ No backup named '{backup_name}' found")
            return False
        
        if user_data_manager.clear_backup(backup_name):
            print(f"✅ Backup '{backup_name}' removed from database")
            return True
        else:
            print(f"❌ Failed to remove backup '{backup_name}'")
            return False

def test_deployment_scenario():
    """Test complete deployment rebuild scenario"""
    with create_app_context():
        print("\n🧪 Testing Deployment Rebuild Scenario")
        print("=" * 45)
        
        # 1. Show current state
        users_before = User.query.count()
        print(f"1. Current users: {users_before}")
        
        # 2. Create backup
        print("2. Creating deployment backup...")
        backup_name = 'deployment_test'
        if not user_data_manager.backup_users(backup_name):
            print("❌ Failed to create backup")
            return
        
        # 3. Simulate deployment (drop users)
        print("3. Simulating deployment rebuild (dropping user data)...")
        User.query.delete()
        db.session.commit()
        users_after_drop = User.query.count()
        print(f"   Users after drop: {users_after_drop}")
        
        # 4. Restore from backup
        print("4. Restoring from database backup...")
        if user_data_manager.restore_users(backup_name):
            users_restored = User.query.count()
            print(f"   Users restored: {users_restored}")
            
            if users_restored == users_before:
                print("✅ SUCCESS: All users preserved through deployment! 🎉")
            else:
                print(f"⚠️  WARNING: User count mismatch ({users_before} -> {users_restored})")
        else:
            print("❌ Failed to restore users")
        
        # 5. Cleanup test backup
        user_data_manager.clear_backup(backup_name)
        print("5. Test backup cleaned up")

def interactive_mode():
    """Interactive mode for user data management"""
    print("\n🔧 Interactive User Data Management (Deployment Compatible)")
    print("=" * 60)
    
    while True:
        print("\nAvailable commands:")
        print("1. Show status")
        print("2. List users")
        print("3. List backups")
        print("4. Backup users")
        print("5. Restore users")
        print("6. Clear backup")
        print("7. Test deployment scenario")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == '1':
            show_status()
        elif choice == '2':
            list_users()
        elif choice == '3':
            list_backups()
        elif choice == '4':
            backup_name = input("Backup name (or press Enter for 'cli_backup'): ").strip()
            backup_users(backup_name if backup_name else None)
        elif choice == '5':
            backup_name = input("Backup name to restore (or press Enter for 'cli_backup'): ").strip()
            restore_users(backup_name if backup_name else None)
        elif choice == '6':
            backup_name = input("Backup name to clear (or press Enter for 'cli_backup'): ").strip()
            clear_backup(backup_name if backup_name else None)
        elif choice == '7':
            test_deployment_scenario()
        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="User Data Management for Python Trivia (Deployment Compatible)")
    parser.add_argument('command', nargs='?', 
                       choices=['backup', 'restore', 'status', 'list', 'backups', 'clear', 'test', 'interactive'],
                       help='Command to execute')
    parser.add_argument('--name', '-n', type=str, 
                       help='Backup name for backup/restore/clear operations')
    
    args = parser.parse_args()
    
    if not args.command:
        # Default to interactive mode if no command specified
        interactive_mode()
        return
    
    if args.command == 'backup':
        backup_users(args.name)
    elif args.command == 'restore':
        restore_users(args.name)
    elif args.command == 'status':
        show_status()
    elif args.command == 'list':
        list_users()
    elif args.command == 'backups':
        list_backups()
    elif args.command == 'clear':
        clear_backup(args.name)
    elif args.command == 'test':
        test_deployment_scenario()
    elif args.command == 'interactive':
        interactive_mode()

if __name__ == "__main__":
    main()