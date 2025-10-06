#!/usr/bin/env python3
"""
Flask-based production password fix script.
This script uses the Flask app's database connection to fix user passwords.
"""

import os
import sys
import bcrypt

def fix_user_password_flask():
    """Fix user password using Flask app context"""
    
    # Import Flask app components
    from app import app, db
    from models import User
    
    with app.app_context():
        try:
            # Find the code_monkey user
            user = User.query.filter_by(username='code_monkey').first()
            
            if not user:
                print("❌ User 'code_monkey' not found in database")
                return False
            
            print(f"✅ Found user 'code_monkey' (ID: {user.id})")
            
            # Check current password hash format
            if user.password_hash and user.password_hash.startswith('$2b$'):
                print("ℹ️  Password is already in bcrypt format")
                # Test if password123 already works
                if user.check_password('password123'):
                    print("✅ Password 'password123' already works!")
                    return True
                else:
                    print("❌ Current bcrypt hash doesn't match 'password123'")
            else:
                print("ℹ️  Password needs to be converted to bcrypt format")
            
            # Set new password using the User model's method
            user.set_password('password123')
            db.session.commit()
            
            print("✅ Successfully updated password to bcrypt format")
            print("✅ New password: password123")
            
            # Verify the password works
            if user.check_password('password123'):
                print("✅ Password verification test passed")
                return True
            else:
                print("❌ Password verification test failed")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return False

def main():
    """Main function"""
    print("=== Flask App Password Fix Script ===")
    print("Fixing code_monkey user password...")
    print()
    
    # Set environment to production if not set
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'production'
    
    success = fix_user_password_flask()
    
    if success:
        print()
        print("✅ Password fix completed successfully!")
        print("You can now login with:")
        print("  Username: code_monkey")
        print("  Password: password123")
    else:
        print()
        print("❌ Password fix failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()