#!/usr/bin/env python3
"""
User Data Management Script
Provides easy commands for backing up, restoring, and managing user data persistence
"""
import sys
import argparse
from flask import Flask
from app import app, backup_user_data, restore_user_data
from user_persistence import user_data_manager, get_user_backup_status
from models import db, User

def create_app_context():
    """Create app context for operations"""
    return app.app_context()

def backup_users():
    """Backup user data to JSON file"""
    with create_app_context():
        if user_data_manager.backup_users():
            user_count = User.query.count()
            print(f"✅ Successfully backed up {user_count} users")
            return True
        else:
            print("❌ Failed to backup users")
            return False

def restore_users():
    """Restore user data from JSON file"""
    with create_app_context():
        if not user_data_manager.has_backup():
            print("❌ No backup file found")
            return False
        
        if user_data_manager.restore_users():
            user_count = User.query.count()
            print(f"✅ Successfully restored users. Total users: {user_count}")
            return True
        else:
            print("❌ Failed to restore users")
            return False

def show_status():
    """Show current backup and user status"""
    with create_app_context():
        status = get_user_backup_status()
        
        print("\n📊 User Data Status:")
        print(f"Current users in database: {status['current_users']}")
        print(f"Backup file exists: {'✅ Yes' if status['has_backup'] else '❌ No'}")
        
        if status['backup_info']:
            backup_info = status['backup_info']
            print(f"Backup timestamp: {backup_info['backup_timestamp']}")
            print(f"Users in backup: {backup_info['user_count']}")
            print(f"Backup file size: {backup_info['file_size']} bytes")
        
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

def clear_backup():
    """Remove backup file"""
    if user_data_manager.clear_backup():
        print("✅ Backup file removed")
    else:
        print("❌ Failed to remove backup file")

def interactive_mode():
    """Interactive mode for user data management"""
    print("\n🔧 Interactive User Data Management")
    print("=" * 40)
    
    while True:
        print("\nAvailable commands:")
        print("1. Show status")
        print("2. List users")
        print("3. Backup users")
        print("4. Restore users")
        print("5. Clear backup")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            show_status()
        elif choice == '2':
            list_users()
        elif choice == '3':
            backup_users()
        elif choice == '4':
            restore_users()
        elif choice == '5':
            clear_backup()
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="User Data Management for Python Trivia")
    parser.add_argument('command', nargs='?', 
                       choices=['backup', 'restore', 'status', 'list', 'clear', 'interactive'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    if not args.command:
        # Default to interactive mode if no command specified
        interactive_mode()
        return
    
    if args.command == 'backup':
        backup_users()
    elif args.command == 'restore':
        restore_users()
    elif args.command == 'status':
        show_status()
    elif args.command == 'list':
        list_users()
    elif args.command == 'clear':
        clear_backup()
    elif args.command == 'interactive':
        interactive_mode()

if __name__ == "__main__":
    main()