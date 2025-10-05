#!/usr/bin/env python3
"""
Direct Database Access Tool for Developer/Owner
Provides raw SQL database access and user management for backend development
"""

import sqlite3
import psycopg2
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sys

class DatabaseManager:
    """Direct database access for owner/developer"""
    
    def __init__(self):
        self.local_db = "instance/trivia_dev.db"
        self.production_db_url = os.getenv('DATABASE_URL')
        
    def get_local_connection(self):
        """Get SQLite connection for local development"""
        if not os.path.exists(self.local_db):
            print(f"❌ Local database not found: {self.local_db}")
            return None
        return sqlite3.connect(self.local_db)
    
    def get_production_connection(self):
        """Get PostgreSQL connection for production"""
        if not self.production_db_url:
            print("❌ No DATABASE_URL environment variable found")
            return None
        try:
            return psycopg2.connect(self.production_db_url)
        except Exception as e:
            print(f"❌ Could not connect to production database: {e}")
            return None
    
    def execute_query(self, query, params=None, use_production=False):
        """Execute SQL query directly on database"""
        
        conn = self.get_production_connection() if use_production else self.get_local_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # For SELECT queries, fetch results
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return {'columns': columns, 'rows': results}
            else:
                # For INSERT/UPDATE/DELETE, commit and return affected rows
                conn.commit()
                return {'affected_rows': cursor.rowcount}
                
        except Exception as e:
            print(f"❌ Query error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def show_all_users(self, use_production=False):
        """Show all users in raw database format"""
        
        print(f"\n📊 ALL USERS IN {'PRODUCTION' if use_production else 'LOCAL'} DATABASE")
        print("=" * 80)
        
        query = """
        SELECT id, username, email, password_hash, created_at, last_seen, 
               is_active, total_games_played, total_points 
        FROM users 
        ORDER BY id
        """
        
        result = self.execute_query(query, use_production=use_production)
        if not result:
            return
            
        if not result['rows']:
            print("❌ No users found in database")
            return
            
        # Print table header
        print(f"{'ID':<4} {'Username':<15} {'Email':<25} {'Password Hash':<20} {'Created':<20} {'Active':<8} {'Games':<6} {'Points':<8}")
        print("-" * 110)
        
        for row in result['rows']:
            user_id, username, email, password_hash, created_at, last_seen, is_active, games, points = row
            
            # Truncate long fields for display
            email_short = email[:22] + "..." if len(email) > 25 else email
            hash_short = password_hash[:17] + "..." if password_hash and len(password_hash) > 20 else (password_hash or "None")
            created_short = str(created_at)[:19] if created_at else "N/A"
            
            print(f"{user_id:<4} {username:<15} {email_short:<25} {hash_short:<20} {created_short:<20} {is_active:<8} {games or 0:<6} {points or 0:<8}")
        
        print(f"\nTotal users: {len(result['rows'])}")
        
        return result['rows']
    
    def get_user_details(self, username, use_production=False):
        """Get complete user details including password hash"""
        
        print(f"\n🔍 USER DETAILS: {username}")
        print("=" * 60)
        
        query = """
        SELECT id, username, email, password_hash, created_at, last_seen,
               is_active, preferred_difficulty, preferred_categories,
               total_games_played, total_questions_answered, total_correct_answers,
               best_streak, total_points
        FROM users 
        WHERE username = ?
        """
        
        params = (username,) if not use_production else (username,)
        if use_production:
            query = query.replace('?', '%s')
            
        result = self.execute_query(query, params, use_production=use_production)
        if not result or not result['rows']:
            print(f"❌ User '{username}' not found")
            return None
            
        user = result['rows'][0]
        columns = result['columns']
        
        # Display all user data
        for i, column in enumerate(columns):
            value = user[i]
            if column == 'password_hash' and value:
                print(f"{column:25}: {value}")
                print(f"{'password_hash_length':25}: {len(value)} characters")
            else:
                print(f"{column:25}: {value}")
        
        return dict(zip(columns, user))
    
    def create_user_direct(self, username, email, password, use_production=False):
        """Create user directly in database"""
        
        print(f"\n➕ CREATING USER: {username}")
        print("=" * 50)
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        query = """
        INSERT INTO users (username, email, password_hash, created_at, is_active)
        VALUES (?, ?, ?, ?, ?)
        """
        
        created_at = datetime.now().isoformat()
        params = (username, email, password_hash, created_at, True)
        
        if use_production:
            query = query.replace('?', '%s')
            
        result = self.execute_query(query, params, use_production=use_production)
        
        if result and result.get('affected_rows', 0) > 0:
            print(f"✅ User created successfully")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print(f"   Password Hash: {password_hash}")
            print(f"   Created: {created_at}")
            return True
        else:
            print(f"❌ Failed to create user")
            return False
    
    def update_user_password(self, username, new_password, use_production=False):
        """Update user password directly"""
        
        print(f"\n🔑 UPDATING PASSWORD: {username}")
        print("=" * 50)
        
        password_hash = generate_password_hash(new_password)
        
        query = """
        UPDATE users 
        SET password_hash = ?
        WHERE username = ?
        """
        
        params = (password_hash, username)
        
        if use_production:
            query = query.replace('?', '%s')
            
        result = self.execute_query(query, params, use_production=use_production)
        
        if result and result.get('affected_rows', 0) > 0:
            print(f"✅ Password updated successfully")
            print(f"   Username: {username}")
            print(f"   New Password: {new_password}")
            print(f"   New Hash: {password_hash}")
            return True
        else:
            print(f"❌ Failed to update password (user may not exist)")
            return False
    
    def delete_user_direct(self, username, use_production=False):
        """Delete user directly from database"""
        
        print(f"\n🗑️ DELETING USER: {username}")
        print("=" * 50)
        
        # First show user details
        user_details = self.get_user_details(username, use_production)
        if not user_details:
            return False
            
        confirm = input(f"\n⚠️ Are you sure you want to delete user '{username}'? (type 'DELETE' to confirm): ")
        if confirm != 'DELETE':
            print("❌ Deletion cancelled")
            return False
        
        query = "DELETE FROM users WHERE username = ?"
        params = (username,)
        
        if use_production:
            query = query.replace('?', '%s')
            
        result = self.execute_query(query, params, use_production=use_production)
        
        if result and result.get('affected_rows', 0) > 0:
            print(f"✅ User '{username}' deleted successfully")
            return True
        else:
            print(f"❌ Failed to delete user")
            return False
    
    def execute_custom_sql(self, sql_query, use_production=False):
        """Execute custom SQL query"""
        
        print(f"\n⚡ EXECUTING CUSTOM SQL")
        print("=" * 50)
        print(f"Query: {sql_query}")
        print(f"Database: {'Production' if use_production else 'Local'}")
        
        confirm = input(f"\n⚠️ Execute this query? (type 'EXECUTE' to confirm): ")
        if confirm != 'EXECUTE':
            print("❌ Query cancelled")
            return None
            
        result = self.execute_query(sql_query, use_production=use_production)
        
        if result:
            if 'columns' in result:
                # SELECT query results
                print(f"\n📊 Query Results:")
                print(" | ".join(result['columns']))
                print("-" * 80)
                for row in result['rows']:
                    print(" | ".join(str(cell) for cell in row))
                print(f"\nTotal rows: {len(result['rows'])}")
            else:
                # INSERT/UPDATE/DELETE results
                print(f"✅ Query executed successfully")
                print(f"Affected rows: {result.get('affected_rows', 0)}")
        
        return result
    
    def backup_users_table(self, use_production=False):
        """Backup entire users table to JSON"""
        
        print(f"\n💾 BACKING UP USERS TABLE")
        print("=" * 50)
        
        query = "SELECT * FROM users"
        result = self.execute_query(query, use_production=use_production)
        
        if not result:
            return None
            
        # Convert to JSON format
        users_backup = []
        for row in result['rows']:
            user_dict = dict(zip(result['columns'], row))
            # Convert datetime objects to strings
            for key, value in user_dict.items():
                if hasattr(value, 'isoformat'):
                    user_dict[key] = value.isoformat()
            users_backup.append(user_dict)
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"users_backup_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(users_backup, f, indent=2)
        
        print(f"✅ Users table backed up to: {filename}")
        print(f"Total users backed up: {len(users_backup)}")
        
        return filename

def main():
    """Interactive database management tool"""
    
    print(f"\n🛠️ DIRECT DATABASE ACCESS TOOL")
    print(f"Developer/Owner Backend Management")
    print("=" * 60)
    
    db = DatabaseManager()
    
    while True:
        print(f"\n📋 AVAILABLE COMMANDS:")
        print(f"1. Show all users (local)")
        print(f"2. Show all users (production)")
        print(f"3. Get user details")
        print(f"4. Create new user")
        print(f"5. Update user password")
        print(f"6. Delete user")
        print(f"7. Execute custom SQL")
        print(f"8. Backup users table")
        print(f"9. Exit")
        
        choice = input(f"\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            db.show_all_users(use_production=False)
            
        elif choice == '2':
            db.show_all_users(use_production=True)
            
        elif choice == '3':
            username = input("Enter username: ").strip()
            use_prod = input("Use production database? (y/n): ").strip().lower() == 'y'
            db.get_user_details(username, use_production=use_prod)
            
        elif choice == '4':
            username = input("Enter username: ").strip()
            email = input("Enter email: ").strip()
            password = input("Enter password: ").strip()
            use_prod = input("Use production database? (y/n): ").strip().lower() == 'y'
            db.create_user_direct(username, email, password, use_production=use_prod)
            
        elif choice == '5':
            username = input("Enter username: ").strip()
            password = input("Enter new password: ").strip()
            use_prod = input("Use production database? (y/n): ").strip().lower() == 'y'
            db.update_user_password(username, password, use_production=use_prod)
            
        elif choice == '6':
            username = input("Enter username to delete: ").strip()
            use_prod = input("Use production database? (y/n): ").strip().lower() == 'y'
            db.delete_user_direct(username, use_production=use_prod)
            
        elif choice == '7':
            sql = input("Enter SQL query: ").strip()
            use_prod = input("Use production database? (y/n): ").strip().lower() == 'y'
            db.execute_custom_sql(sql, use_production=use_prod)
            
        elif choice == '8':
            use_prod = input("Backup production database? (y/n): ").strip().lower() == 'y'
            db.backup_users_table(use_production=use_prod)
            
        elif choice == '9':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice")

if __name__ == '__main__':
    main()