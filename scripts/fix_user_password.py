#!/usr/bin/env python3
"""
Script to fix user passwords in the development database.
This converts old scrypt hashes to bcrypt format for compatibility.
"""

import sqlite3
import bcrypt
import os
import sys

def fix_user_password(username, new_password):
    """Update a user's password to use bcrypt format"""
    db_path = './instance/trivia_dev.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User '{username}' not found")
            return False
        
        user_id, old_hash = user
        print(f"Found user '{username}' (ID: {user_id})")
        
        # Check current hash format
        if old_hash and old_hash.startswith('$2b$'):
            print("✅ Password is already in bcrypt format")
            
            # Test current password
            if bcrypt.checkpw(new_password.encode('utf-8'), old_hash.encode('utf-8')):
                print("✅ Provided password matches current hash")
                return True
            else:
                print("❌ Provided password does not match current hash")
        
        # Generate new bcrypt hash
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update the user
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (password_hash, username))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Successfully updated password for '{username}'")
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
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main function"""
    if len(sys.argv) != 3:
        print("Usage: python fix_user_password.py <username> <new_password>")
        print("Example: python fix_user_password.py code_monkey password123")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print(f"=== Fixing password for user '{username}' ===")
    success = fix_user_password(username, password)
    
    if success:
        print("\n✅ Password fix completed successfully!")
        print(f"You can now login with:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
    else:
        print("\n❌ Password fix failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()