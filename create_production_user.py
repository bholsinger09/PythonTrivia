#!/usr/bin/env python3
"""
Script to create code_monkey user in production database
"""
import os
import sys
from flask import Flask
from models import db, User
from config import ProductionConfig

def create_production_user():
    """Create the code_monkey user in production database"""
    
    # Create Flask app with production config
    app = Flask(__name__)
    app.config.from_object(ProductionConfig)
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create all tables if they don't exist
            db.create_all()
            print("✅ Database tables created/verified")
            
            # Check if user already exists
            existing_user = User.query.filter_by(username='code_monkey').first()
            if existing_user:
                print(f"✅ User 'code_monkey' already exists with ID: {existing_user.id}")
                print(f"   Email: {existing_user.email}")
                print(f"   Created: {existing_user.created_at}")
                
                # Test password
                if existing_user.check_password('password123'):
                    print("✅ Password verification: PASSED")
                else:
                    print("❌ Password verification: FAILED")
                    print("🔧 Updating password...")
                    existing_user.set_password('password123')
                    db.session.commit()
                    print("✅ Password updated successfully")
                
                return existing_user
            
            # Create new user
            print("🔧 Creating new user 'code_monkey'...")
            new_user = User(
                username='code_monkey',
                email='bholsinger@gmail.com'
            )
            new_user.set_password('password123')
            
            db.session.add(new_user)
            db.session.commit()
            
            print(f"✅ User 'code_monkey' created successfully with ID: {new_user.id}")
            
            # Verify the user was created correctly
            verification_user = User.query.filter_by(username='code_monkey').first()
            if verification_user and verification_user.check_password('password123'):
                print("✅ User creation and password verification: PASSED")
            else:
                print("❌ User creation verification: FAILED")
                
            return new_user
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return None

def check_all_users():
    """Check all users in the production database"""
    
    # Create Flask app with production config
    app = Flask(__name__)
    app.config.from_object(ProductionConfig)
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            users = User.query.all()
            print(f"\n📊 Total users in production database: {len(users)}")
            
            if users:
                print("\n👥 All users:")
                for user in users:
                    print(f"   ID: {user.id}")
                    print(f"   Username: {user.username}")
                    print(f"   Email: {user.email}")
                    print(f"   Created: {user.created_at}")
                    print(f"   Active: {user.is_active}")
                    print("   ---")
            else:
                print("📭 No users found in database")
                
        except Exception as e:
            print(f"❌ Error checking users: {e}")

if __name__ == "__main__":
    print("🚀 Production User Management Script")
    print("=====================================")
    
    # Check current users
    print("\n1. Checking existing users...")
    check_all_users()
    
    # Create or verify code_monkey user
    print("\n2. Creating/verifying code_monkey user...")
    user = create_production_user()
    
    if user:
        print(f"\n✅ SUCCESS: User 'code_monkey' is ready for production login")
        print(f"   Username: code_monkey")
        print(f"   Password: password123")
        print(f"   Database: {os.getenv('DATABASE_URL', 'Not set')}")
    else:
        print(f"\n❌ FAILED: Could not create/verify user")
        sys.exit(1)