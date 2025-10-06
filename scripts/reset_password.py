#!/usr/bin/env python3
"""
Script to reset password for a user in the Python Trivia application
"""
import sys
from app import app
from models import db, User

def reset_password(username: str, new_password: str):
    """Reset password for a user"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ User '{username}' not found")
            return False
        
        print(f"📋 Found user: {user.username} ({user.email})")
        
        # Set new password
        user.set_password(new_password)
        db.session.commit()
        
        print(f"✅ Password updated for user '{username}'")
        
        # Verify the new password works
        if user.check_password(new_password):
            print(f"✅ Password verification successful")
            return True
        else:
            print(f"❌ Password verification failed")
            return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python reset_password.py <username> <new_password>")
        print("Example: python reset_password.py code_monkey mypassword123")
        sys.exit(1)
    
    username = sys.argv[1]
    new_password = sys.argv[2]
    
    print(f"🔄 Resetting password for user: {username}")
    success = reset_password(username, new_password)
    
    if success:
        print(f"\n🎉 SUCCESS! You can now login with:")
        print(f"   Username: {username}")
        print(f"   Password: {new_password}")
    else:
        print(f"\n❌ Failed to reset password")
        sys.exit(1)