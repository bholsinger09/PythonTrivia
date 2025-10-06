#!/usr/bin/env python3
"""
Production database initialization and user setup
This script should be run after each deployment to ensure users persist
"""
import os
import sys
from flask import Flask
from models import db, User

def init_production_database():
    """Initialize production database and create essential users"""
    
    print("🚀 PRODUCTION DATABASE INITIALIZATION")
    print("=" * 50)
    
    # Check environment
    database_url = os.environ.get('DATABASE_URL')
    print(f"DATABASE_URL: {database_url[:50] if database_url else 'NOT SET'}...")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not set!")
        print("This script requires a DATABASE_URL environment variable")
        return False
    
    if not database_url.startswith('postgresql'):
        print(f"❌ ERROR: Expected PostgreSQL, got: {database_url[:30]}...")
        print("Production must use PostgreSQL for data persistence")
        return False
    
    print("✅ Using PostgreSQL database")
    
    # Create Flask app
    app = Flask(__name__)
    
    # Simple production config
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'temp-key')
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create all tables
            print("📋 Creating database tables...")
            db.create_all()
            print("✅ Tables created successfully")
            
            # Create essential users
            essential_users = [
                {
                    'username': 'code_monkey',
                    'email': 'bholsinger@gmail.com',
                    'password': 'password123'
                },
                {
                    'username': 'admin',
                    'email': 'admin@pythontrivia.com',
                    'password': 'admin123'
                }
            ]
            
            for user_data in essential_users:
                create_or_update_user(user_data)
            
            # Verify users exist and can login
            print("\n🔐 Verifying user authentication...")
            for user_data in essential_users:
                verify_user_login(user_data)
            
            print("\n✅ Production database initialization complete!")
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False

def create_or_update_user(user_data):
    """Create or update a user with proper password"""
    username = user_data['username']
    
    # Check if user exists
    existing_user = User.query.filter_by(username=username).first()
    
    if existing_user:
        print(f"👤 User '{username}' exists - updating password...")
        existing_user.set_password(user_data['password'])
        db.session.commit()
        print(f"   ✅ Password updated for '{username}'")
    else:
        print(f"👤 Creating user '{username}'...")
        new_user = User(
            username=username,
            email=user_data['email']
        )
        new_user.set_password(user_data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        print(f"   ✅ User '{username}' created successfully")

def verify_user_login(user_data):
    """Verify that a user can login with their password"""
    username = user_data['username']
    password = user_data['password']
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        print(f"   ✅ '{username}' login verification: PASSED")
        return True
    else:
        print(f"   ❌ '{username}' login verification: FAILED")
        return False

if __name__ == "__main__":
    success = init_production_database()
    if success:
        print("\n🎯 READY FOR TESTING!")
        print("Use these credentials in Postman:")
        print("  Username: code_monkey")
        print("  Password: password123")
        print("  URL: https://pythontrivia.onrender.com/login")
        sys.exit(0)
    else:
        print("\n❌ Initialization failed!")
        sys.exit(1)