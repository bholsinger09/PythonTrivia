#!/usr/bin/env python3
"""
Database User Verification Script
Checks if specific users exist in the SQL database and shows their details
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User, UserBackup
from sqlalchemy import text
import json

def verify_user_in_database(username):
    """Verify if a specific user exists in the database"""
    
    with app.app_context():
        print(f"\n🔍 VERIFYING USER: '{username}' IN SQL DATABASE")
        print("=" * 50)
        
        # Check if user exists in User table
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"✅ USER FOUND IN DATABASE!")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   User ID: {user.id}")
            print(f"   Password Hash: {user.password_hash[:20]}... (truncated for security)")
            print(f"   Created: {user.created_at if hasattr(user, 'created_at') else 'N/A'}")
            
            # Test password verification with common passwords
            print(f"\n🔑 PASSWORD VERIFICATION TEST:")
            test_passwords = ['Myspam#09', 'myspam#09', 'password', 'code_monkey']
            
            for test_pwd in test_passwords:
                try:
                    is_valid = user.check_password(test_pwd)
                    status = "✅ VALID" if is_valid else "❌ INVALID"
                    print(f"   Password '{test_pwd}': {status}")
                    if is_valid:
                        print(f"   🎉 CORRECT PASSWORD FOUND: '{test_pwd}'")
                        break
                except Exception as e:
                    print(f"   Password '{test_pwd}': ❌ ERROR - {e}")
            
            return True
        else:
            print(f"❌ USER NOT FOUND IN DATABASE!")
            return False

def show_all_users():
    """Show all users in the database"""
    
    with app.app_context():
        print(f"\n📊 ALL USERS IN DATABASE:")
        print("=" * 50)
        
        users = User.query.all()
        
        if users:
            print(f"Total users found: {len(users)}")
            print()
            
            for i, user in enumerate(users, 1):
                print(f"{i}. Username: {user.username}")
                print(f"   Email: {user.email}")
                print(f"   ID: {user.id}")
                print(f"   Password Hash: {user.password_hash[:15]}...")
                print()
        else:
            print("❌ NO USERS FOUND IN DATABASE!")
        
        return len(users)

def check_database_tables():
    """Check what tables exist in the database"""
    
    with app.app_context():
        print(f"\n📋 DATABASE TABLES:")
        print("=" * 50)
        
        try:
            # Get all table names
            result = db.engine.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result]
            
            print(f"Tables found: {len(tables)}")
            for table in tables:
                print(f"   - {table}")
                
                # Count rows in each table
                try:
                    count_result = db.engine.execute(text(f"SELECT COUNT(*) FROM {table};"))
                    count = count_result.fetchone()[0]
                    print(f"     Rows: {count}")
                except Exception as e:
                    print(f"     Rows: Error - {e}")
            
            return tables
            
        except Exception as e:
            print(f"❌ Error checking tables: {e}")
            return []

def check_user_backups():
    """Check if user is in backup system"""
    
    with app.app_context():
        print(f"\n💾 USER BACKUP SYSTEM:")
        print("=" * 50)
        
        backups = UserBackup.query.all()
        
        if backups:
            print(f"Backup records found: {len(backups)}")
            print()
            
            for backup in backups:
                print(f"Backup: {backup.backup_name}")
                print(f"Created: {backup.created_at}")
                
                try:
                    backup_data = json.loads(backup.backup_data)
                    print(f"Users in backup: {len(backup_data)}")
                    
                    for user_data in backup_data:
                        if user_data.get('username') == 'code_monkey':
                            print(f"   ✅ code_monkey found in backup!")
                            print(f"   Email: {user_data.get('email')}")
                            break
                    else:
                        print(f"   ❌ code_monkey not found in this backup")
                        
                except Exception as e:
                    print(f"   Error reading backup data: {e}")
                print()
        else:
            print("❌ NO BACKUP RECORDS FOUND!")

def main():
    """Main verification function"""
    
    print(f"\n🚀 DATABASE VERIFICATION SCRIPT")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown')}")
    
    # Check database tables
    tables = check_database_tables()
    
    # Show all users
    user_count = show_all_users()
    
    # Verify specific user
    user_exists = verify_user_in_database('code_monkey')
    
    # Check backup system
    check_user_backups()
    
    # Summary
    print(f"\n📋 VERIFICATION SUMMARY:")
    print("=" * 50)
    print(f"Database tables: {len(tables)}")
    print(f"Total users: {user_count}")
    print(f"code_monkey user: {'✅ FOUND' if user_exists else '❌ NOT FOUND'}")
    
    if user_exists:
        print(f"\n🎉 SUCCESS: code_monkey is properly stored in the SQL database!")
        print(f"✅ Ready for deployment - user data will persist!")
    else:
        print(f"\n⚠️  WARNING: code_monkey not found in database!")
        print(f"❌ User may need to re-register!")

if __name__ == "__main__":
    main()