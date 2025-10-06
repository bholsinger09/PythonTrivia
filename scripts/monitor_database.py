#!/usr/bin/env python3
"""
Real-time Database Monitor
Watches for new user registrations in all databases
"""

import sqlite3
import time
import os
from datetime import datetime

def get_users_from_db(db_path):
    """Get all users from a database file"""
    if not os.path.exists(db_path):
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if not cursor.fetchone():
            conn.close()
            return []
        
        # Get all users
        cursor.execute('''SELECT id, username, email, created_at, password_hash 
                         FROM users ORDER BY created_at DESC''')
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"Error reading {db_path}: {e}")
        return []

def monitor_databases():
    """Monitor all databases for new users"""
    print("🔍 REAL-TIME DATABASE MONITOR")
    print("=" * 50)
    print("Watching for new user registrations...")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    databases = [
        ('./trivia.db', 'Main'),
        ('./instance/trivia_dev.db', 'Development'), 
        ('./instance/trivia_test.db', 'Test')
    ]
    
    # Track previous state
    previous_users = {}
    for db_path, db_name in databases:
        previous_users[db_path] = get_users_from_db(db_path)
    
    try:
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            
            for db_path, db_name in databases:
                current_users = get_users_from_db(db_path)
                prev_users = previous_users[db_path]
                
                if len(current_users) != len(prev_users):
                    print(f"🚨 [{current_time}] CHANGE DETECTED in {db_name} database!")
                    print(f"   File: {db_path}")
                    print(f"   Users: {len(prev_users)} → {len(current_users)}")
                    
                    # Show new users
                    if len(current_users) > len(prev_users):
                        new_users = current_users[:len(current_users) - len(prev_users)]
                        for user in new_users:
                            print(f"   ✅ NEW USER REGISTERED:")
                            print(f"      ID: {user[0]}")
                            print(f"      Username: {user[1]}")
                            print(f"      Email: {user[2]}")
                            print(f"      Created: {user[3]}")
                            print(f"      Password Hash: {user[4][:50]}...")
                    
                    print()
                    previous_users[db_path] = current_users
                
                # Check specifically for code_monkey
                code_monkey_users = [u for u in current_users if 'code_monkey' in u[1].lower() or 'code_monkey' in u[2].lower()]
                if code_monkey_users:
                    print(f"🐒 [{current_time}] CODE_MONKEY FOUND in {db_name} database!")
                    for user in code_monkey_users:
                        print(f"   Username: {user[1]}")
                        print(f"   Email: {user[2]}")
                        print(f"   Created: {user[3]}")
                    print()
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\n📊 FINAL STATUS:")
        for db_path, db_name in databases:
            users = get_users_from_db(db_path)
            print(f"{db_name}: {len(users)} users")
            for user in users:
                print(f"  - {user[1]} ({user[2]})")

if __name__ == "__main__":
    monitor_databases()