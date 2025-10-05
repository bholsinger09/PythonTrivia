#!/usr/bin/env python3
"""
Simple Database Query Tool for Developer Access
Direct SQL database access for backend development and user management
"""

import sqlite3
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import requests

class SimpleDatabaseTool:
    """Direct database access for developer/owner"""
    
    def __init__(self):
        self.local_db = "instance/trivia_dev.db"
        
    def get_connection(self):
        """Get SQLite connection"""
        if not os.path.exists(self.local_db):
            print(f"❌ Database not found: {self.local_db}")
            return None
        return sqlite3.connect(self.local_db)
    
    def execute_raw_sql(self, query, params=None):
        """Execute raw SQL query"""
        
        conn = self.get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return {'columns': columns, 'rows': results}
            else:
                conn.commit()
                return {'affected_rows': cursor.rowcount}
                
        except Exception as e:
            print(f"❌ SQL Error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def show_raw_users_table(self):
        """Show complete users table with all data"""
        
        print(f"\n📊 RAW USERS TABLE DATA")
        print("=" * 100)
        
        result = self.execute_raw_sql("SELECT * FROM users ORDER BY id")
        if not result or not result['rows']:
            print("❌ No users found")
            return
        
        # Show column headers
        columns = result['columns']
        print(" | ".join(f"{col:15}" for col in columns))
        print("-" * (len(columns) * 17))
        
        # Show all user data
        for row in result['rows']:
            formatted_row = []
            for i, value in enumerate(row):
                if columns[i] == 'password_hash' and value:
                    # Show full password hash
                    formatted_row.append(f"{str(value):15}")
                else:
                    formatted_row.append(f"{str(value):15}")
            print(" | ".join(formatted_row))
        
        print(f"\nTotal users: {len(result['rows'])}")
        return result['rows']
    
    def show_user_complete(self, username):
        """Show complete user data including full password hash"""
        
        print(f"\n🔍 COMPLETE USER DATA: {username}")
        print("=" * 80)
        
        result = self.execute_raw_sql("SELECT * FROM users WHERE username = ?", (username,))
        if not result or not result['rows']:
            print(f"❌ User '{username}' not found")
            return None
        
        user_data = dict(zip(result['columns'], result['rows'][0]))
        
        # Display all fields with full values
        for field, value in user_data.items():
            if field == 'password_hash':
                print(f"{field:20}: {value}")
                print(f"{'hash_length':20}: {len(value) if value else 0} characters")
                
                # Test password verification
                if value:
                    test_passwords = ['Myspam#09', 'myspam#09', 'code_monkey', 'password']
                    print(f"{'password_tests':20}:")
                    for test_pwd in test_passwords:
                        is_valid = check_password_hash(value, test_pwd)
                        status = "✅ VALID" if is_valid else "❌ INVALID"
                        print(f"{'':20}  '{test_pwd}': {status}")
            else:
                print(f"{field:20}: {value}")
        
        return user_data
    
    def create_user_raw(self, username, email, password):
        """Create user with raw database access"""
        
        print(f"\n➕ CREATING USER WITH RAW ACCESS")
        print("=" * 50)
        
        # Generate password hash
        password_hash = generate_password_hash(password)
        
        # Insert directly into database
        query = """
        INSERT INTO users (username, email, password_hash, created_at, is_active, 
                          total_games_played, total_questions_answered, total_correct_answers,
                          best_streak, total_points)
        VALUES (?, ?, ?, ?, ?, 0, 0, 0, 0, 0)
        """
        
        created_at = datetime.now()
        params = (username, email, password_hash, created_at, True)
        
        result = self.execute_raw_sql(query, params)
        
        if result and result.get('affected_rows', 0) > 0:
            print(f"✅ User created successfully")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Password: {password}")
            print(f"Password Hash: {password_hash}")
            
            # Verify creation
            self.show_user_complete(username)
            return True
        else:
            print(f"❌ Failed to create user")
            return False
    
    def update_password_raw(self, username, new_password):
        """Update password with raw database access"""
        
        print(f"\n🔑 UPDATING PASSWORD WITH RAW ACCESS")
        print("=" * 50)
        
        new_hash = generate_password_hash(new_password)
        
        result = self.execute_raw_sql(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (new_hash, username)
        )
        
        if result and result.get('affected_rows', 0) > 0:
            print(f"✅ Password updated successfully")
            print(f"Username: {username}")
            print(f"New Password: {new_password}")
            print(f"New Hash: {new_hash}")
            
            # Verify update
            self.show_user_complete(username)
            return True
        else:
            print(f"❌ Failed to update password")
            return False
    
    def delete_user_raw(self, username):
        """Delete user with raw database access"""
        
        print(f"\n🗑️ DELETING USER WITH RAW ACCESS")
        print("=" * 50)
        
        # Show user first
        user_data = self.show_user_complete(username)
        if not user_data:
            return False
        
        confirm = input(f"\n⚠️ Delete user '{username}'? Type 'DELETE' to confirm: ")
        if confirm != 'DELETE':
            print("❌ Deletion cancelled")
            return False
        
        result = self.execute_raw_sql("DELETE FROM users WHERE username = ?", (username,))
        
        if result and result.get('affected_rows', 0) > 0:
            print(f"✅ User '{username}' deleted successfully")
            return True
        else:
            print(f"❌ Failed to delete user")
            return False
    
    def execute_custom_query(self, query):
        """Execute any custom SQL query"""
        
        print(f"\n⚡ EXECUTING CUSTOM QUERY")
        print("=" * 50)
        print(f"Query: {query}")
        
        confirm = input(f"\n⚠️ Execute this query? Type 'EXECUTE' to confirm: ")
        if confirm != 'EXECUTE':
            print("❌ Query cancelled")
            return None
        
        result = self.execute_raw_sql(query)
        
        if result:
            if 'columns' in result:
                print(f"\n📊 Results:")
                print(" | ".join(result['columns']))
                print("-" * 80)
                for row in result['rows']:
                    print(" | ".join(str(cell) for cell in row))
                print(f"\nRows returned: {len(result['rows'])}")
            else:
                print(f"✅ Query executed")
                print(f"Rows affected: {result.get('affected_rows', 0)}")
        
        return result
    
    def backup_database(self):
        """Create complete database backup"""
        
        print(f"\n💾 CREATING DATABASE BACKUP")
        print("=" * 50)
        
        # Get all users
        result = self.execute_raw_sql("SELECT * FROM users")
        if not result:
            return None
        
        # Create backup data
        backup_data = {
            'backup_date': datetime.now().isoformat(),
            'total_users': len(result['rows']),
            'columns': result['columns'],
            'users': []
        }
        
        for row in result['rows']:
            user_dict = dict(zip(result['columns'], row))
            # Convert datetime to string if needed
            for key, value in user_dict.items():
                if hasattr(value, 'isoformat'):
                    user_dict[key] = value.isoformat()
            backup_data['users'].append(user_dict)
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"database_backup_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✅ Database backed up to: {filename}")
        print(f"Users backed up: {len(backup_data['users'])}")
        
        return filename
    
    def check_production_database(self):
        """Check production database via admin endpoint"""
        
        print(f"\n🌐 CHECKING PRODUCTION DATABASE")
        print("=" * 50)
        
        try:
            response = requests.get("https://pythontrivia.onrender.com/admin/database-status", timeout=10)
            if response.status_code == 200:
                print("✅ Production database accessible")
                print(response.text)
            else:
                print(f"❌ Production database error: {response.status_code}")
        except Exception as e:
            print(f"❌ Could not access production database: {e}")

def main():
    """Interactive database tool"""
    
    print(f"\n🛠️ DIRECT DATABASE ACCESS TOOL")
    print(f"Developer/Owner Backend Management")
    print(f"Direct SQL Database Access")
    print("=" * 60)
    
    db = SimpleDatabaseTool()
    
    while True:
        print(f"\n📋 DEVELOPER DATABASE COMMANDS:")
        print(f"1. Show complete users table")
        print(f"2. Show complete user details")
        print(f"3. Create user (raw)")
        print(f"4. Update password (raw)")
        print(f"5. Delete user (raw)")
        print(f"6. Execute custom SQL")
        print(f"7. Backup database")
        print(f"8. Check production database")
        print(f"9. Exit")
        
        choice = input(f"\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            db.show_raw_users_table()
            
        elif choice == '2':
            username = input("Enter username: ").strip()
            db.show_user_complete(username)
            
        elif choice == '3':
            username = input("Enter username: ").strip()
            email = input("Enter email: ").strip()
            password = input("Enter password: ").strip()
            db.create_user_raw(username, email, password)
            
        elif choice == '4':
            username = input("Enter username: ").strip()
            password = input("Enter new password: ").strip()
            db.update_password_raw(username, password)
            
        elif choice == '5':
            username = input("Enter username: ").strip()
            db.delete_user_raw(username)
            
        elif choice == '6':
            query = input("Enter SQL query: ").strip()
            db.execute_custom_query(query)
            
        elif choice == '7':
            db.backup_database()
            
        elif choice == '8':
            db.check_production_database()
            
        elif choice == '9':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice")

if __name__ == '__main__':
    main()