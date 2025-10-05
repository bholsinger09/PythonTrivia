#!/usr/bin/env python3
"""
Production database password fix script.
This script connects to the production database and fixes user password hashes.
"""

import os
import sys
import psycopg2
import bcrypt
from urllib.parse import urlparse

def get_db_connection():
    """Get database connection based on environment"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        print("This script needs to run in the production environment or with DATABASE_URL set")
        return None
    
    try:
        # Parse the database URL
        if database_url.startswith('postgres://'):
            # Railway sometimes uses postgres:// which needs to be postgresql://
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        parsed = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password,
            sslmode='require'
        )
        
        print("✅ Connected to production database")
        return conn
        
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

def fix_production_password(username, new_password):
    """Fix user password in production database"""
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User '{username}' not found in production database")
            return False
        
        user_id, old_hash = user
        print(f"Found user '{username}' (ID: {user_id}) in production database")
        
        # Generate new bcrypt hash
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update the user
        cursor.execute("UPDATE users SET password_hash = %s WHERE username = %s", (password_hash, username))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Successfully updated password for '{username}' in production")
            print(f"✅ New password: {new_password}")
            
            # Verify the update
            if bcrypt.checkpw(new_password.encode('utf-8'), password_hash.encode('utf-8')):
                print("✅ Password verification test passed")
                return True
            else:
                print("❌ Password verification test failed")
                return False
        else:
            print("❌ Failed to update password")
            return False
            
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function"""
    print("=== Production Password Fix Script ===")
    print("This script fixes password hashes in the production database")
    print()
    
    # Check if we have DATABASE_URL
    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL environment variable not found")
        print()
        print("To use this script:")
        print("1. Export your production DATABASE_URL:")
        print("   export DATABASE_URL='your_production_database_url'")
        print("2. Run this script:")
        print("   python fix_production_password.py")
        sys.exit(1)
    
    # Fix code_monkey password
    username = "code_monkey"
    password = "password123"
    
    print(f"Fixing password for user '{username}'...")
    success = fix_production_password(username, password)
    
    if success:
        print()
        print("✅ Production password fix completed successfully!")
        print(f"You can now login to production with:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
    else:
        print()
        print("❌ Production password fix failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()