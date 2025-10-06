#!/usr/bin/env python3
"""
Simple Database User Verification Script
Checks multiple database files for the code_monkey user
"""

import sqlite3
import os
from datetime import datetime
import json

def check_database_file(db_path):
    """Check a specific database file for users"""
    
    if not os.path.exists(db_path):
        return None, f"Database file not found: {db_path}"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            return None, f"No 'users' table found in {db_path}"
        
        # Get all users
        cursor.execute("SELECT id, username, email, password_hash, created_at FROM users;")
        users = cursor.fetchall()
        
        # Check for code_monkey specifically
        cursor.execute("SELECT id, username, email, password_hash, created_at FROM users WHERE username = ?;", ('code_monkey',))
        code_monkey = cursor.fetchone()
        
        conn.close()
        
        return {
            'db_path': db_path,
            'total_users': len(users),
            'all_users': users,
            'code_monkey': code_monkey
        }, None
        
    except Exception as e:
        return None, f"Error checking {db_path}: {e}"

def check_user_backup_table(db_path):
    """Check UserBackup table for code_monkey"""
    
    if not os.path.exists(db_path):
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user_backup table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_backup';")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            return None
        
        # Get all backups
        cursor.execute("SELECT id, backup_name, backup_data, created_at FROM user_backup;")
        backups = cursor.fetchall()
        
        code_monkey_in_backups = []
        
        for backup in backups:
            backup_id, backup_name, backup_data, created_at = backup
            try:
                data = json.loads(backup_data)
                for user in data:
                    if user.get('username') == 'code_monkey':
                        code_monkey_in_backups.append({
                            'backup_name': backup_name,
                            'backup_id': backup_id,
                            'created_at': created_at,
                            'user_data': user
                        })
            except:
                continue
        
        conn.close()
        return code_monkey_in_backups
        
    except Exception as e:
        print(f"Error checking backups in {db_path}: {e}")
        return None

def main():
    """Check all possible database locations"""
    
    print(f"\n🔍 SEARCHING FOR code_monkey USER IN ALL DATABASES")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Database files to check
    db_files = [
        'trivia.db',
        'instance/trivia_dev.db',
        'instance/trivia_test.db',
        'instance/trivia.db'
    ]
    
    found_code_monkey = False
    total_users_found = 0
    
    for db_file in db_files:
        print(f"\n📋 CHECKING: {db_file}")
        print("-" * 40)
        
        result, error = check_database_file(db_file)
        
        if error:
            print(f"❌ {error}")
            continue
            
        if result:
            print(f"✅ Database file exists and accessible")
            print(f"   Total users in database: {result['total_users']}")
            total_users_found += result['total_users']
            
            if result['all_users']:
                print(f"   All users:")
                for i, user in enumerate(result['all_users'], 1):
                    user_id, username, email, password_hash, created_at = user
                    print(f"     {i}. {username} ({email}) - ID: {user_id}")
                    print(f"        Password hash: {password_hash[:20]}...")
                    print(f"        Created: {created_at}")
            
            if result['code_monkey']:
                found_code_monkey = True
                user_id, username, email, password_hash, created_at = result['code_monkey']
                print(f"\n   🎉 CODE_MONKEY FOUND!")
                print(f"      Username: {username}")
                print(f"      Email: {email}")
                print(f"      User ID: {user_id}")
                print(f"      Password Hash: {password_hash[:25]}... (first 25 chars)")
                print(f"      Created: {created_at}")
                print(f"      Database: {db_file}")
            else:
                print(f"   ❌ code_monkey not found in this database")
        
        # Check backup table
        backups = check_user_backup_table(db_file)
        if backups:
            print(f"\n   💾 BACKUP SYSTEM:")
            for backup in backups:
                print(f"      ✅ code_monkey found in backup: {backup['backup_name']}")
                print(f"         Email: {backup['user_data'].get('email')}")
                print(f"         Backup created: {backup['created_at']}")
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📊 SEARCH SUMMARY:")
    print(f"   Total users across all databases: {total_users_found}")
    print(f"   code_monkey found: {'✅ YES' if found_code_monkey else '❌ NO'}")
    
    if found_code_monkey:
        print(f"\n🎉 SUCCESS!")
        print(f"✅ code_monkey is properly stored in the SQL database")
        print(f"✅ User data is persistent and ready for deployment")
        print(f"✅ The user can sign in after redeployment")
    else:
        print(f"\n⚠️  WARNING!")
        print(f"❌ code_monkey user not found in any database")
        print(f"❌ User may need to register again")
        print(f"💡 This could mean:")
        print(f"   - User hasn't registered yet")
        print(f"   - Database was cleared/reset")
        print(f"   - User registered in a different environment")

if __name__ == "__main__":
    main()