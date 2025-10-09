#!/usr/bin/env python3
"""
Comprehensive production database and login debugging
"""
import os
import sys
import requests
import json
from flask import Flask
from models import db, User
from config import ProductionConfig, DevelopmentConfig

def check_environment():
    """Check environment variables and configuration"""
    print("🔍 ENVIRONMENT CHECK")
    print("=" * 50)
    
    print(f"FLASK_ENV: {os.getenv('FLASK_ENV', 'not set')}")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'not set')}")
    
    # Check which config would be used
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        config = ProductionConfig
    else:
        config = DevelopmentConfig
    
    print(f"Config class: {config.__name__}")
    print(f"Database URI: {config.SQLALCHEMY_DATABASE_URI}")
    print()

def check_production_database():
    """Check users in production database"""
    print("🗄️ PRODUCTION DATABASE CHECK")
    print("=" * 50)
    
    # Force production config
    app = Flask(__name__)
    app.config.from_object(ProductionConfig)
    
    print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables in database: {tables}")
            
            if 'users' not in tables:
                print("❌ Users table does not exist!")
                print("Creating tables...")
                db.create_all()
                print("✅ Tables created")
            
            # Get all users
            users = User.query.all()
            print(f"Total users: {len(users)}")
            
            for user in users:
                print(f"  User ID: {user.id}")
                print(f"  Username: {user.username}")
                print(f"  Email: {user.email}")
                print(f"  Password hash: {user.password_hash[:50]}...")
                print(f"  Created: {user.created_at}")
                print(f"  Active: {user.is_active}")
                
                # Test password verification
                try:
                    is_valid = user.check_password('password123')
                    print(f"  Password check result: {is_valid}")
                except Exception as e:
                    print(f"  Password check error: {e}")
                print("  ---")
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    
    return True

def test_direct_login_logic():
    """Test the login logic directly"""
    print("🔐 DIRECT LOGIN LOGIC TEST")
    print("=" * 50)
    
    app = Flask(__name__)
    app.config.from_object(ProductionConfig)
    
    db.init_app(app)
    
    with app.app_context():
        try:
            from db_service import UserService
            
            # Test UserService
            print("Testing UserService.get_user_by_username...")
            user = UserService.get_user_by_username('code_monkey')
            
            if user:
                print(f"✅ UserService found user: {user.username}")
                
                # Test password check
                print("Testing password verification...")
                is_valid = user.check_password('password123')
                print(f"Password verification result: {is_valid}")
                
                if is_valid:
                    print("✅ Password verification PASSED")
                else:
                    print("❌ Password verification FAILED")
                    
                    # Test with raw bcrypt
                    try:
                        import bcrypt
                        is_bcrypt_valid = bcrypt.checkpw(
                            'password123'.encode('utf-8'), 
                            user.password_hash.encode('utf-8')
                        )
                        print(f"Raw bcrypt check: {is_bcrypt_valid}")
                    except Exception as e:
                        print(f"Raw bcrypt error: {e}")
            else:
                print("❌ UserService did NOT find user")
                
        except Exception as e:
            print(f"❌ Login logic error: {e}")

def create_test_user():
    """Create a fresh test user"""
    print("👤 CREATING FRESH TEST USER")
    print("=" * 50)
    
    app = Flask(__name__)
    app.config.from_object(ProductionConfig)
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # Delete existing user if exists
            existing = User.query.filter_by(username='code_monkey').first()
            if existing:
                print(f"Deleting existing user: {existing.username}")
                db.session.delete(existing)
                db.session.commit()
            
            # Create fresh user
            print("Creating new user...")
            new_user = User(
                username='code_monkey',
                email='bholsinger@gmail.com'
            )
            new_user.set_password('password123')
            
            db.session.add(new_user)
            db.session.commit()
            
            print(f"✅ Created user with ID: {new_user.id}")
            
            # Verify immediately
            verification = User.query.filter_by(username='code_monkey').first()
            if verification and verification.check_password('password123'):
                print("✅ Immediate verification PASSED")
                return True
            else:
                print("❌ Immediate verification FAILED")
                return False
                
        except Exception as e:
            print(f"❌ User creation error: {e}")
            return False

def test_production_endpoint():
    """Test the actual production endpoint"""
    print("🌐 PRODUCTION ENDPOINT TEST")
    print("=" * 50)
    
    url = "https://pythontrivia.onrender.com/login"
    
    # Test multiple scenarios
    test_cases = [
        {
            "name": "Correct credentials (JSON)",
            "data": {"username": "code_monkey", "password": "password123"},
            "headers": {"Content-Type": "application/json"},
            "method": "json"
        },
        {
            "name": "Correct credentials (Form)",
            "data": {"username": "code_monkey", "password": "password123"},
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "method": "form"
        },
        {
            "name": "Wrong password",
            "data": {"username": "code_monkey", "password": "wrongpassword"},
            "headers": {"Content-Type": "application/json"},
            "method": "json"
        },
        {
            "name": "Wrong username",
            "data": {"username": "wrong_user", "password": "password123"},
            "headers": {"Content-Type": "application/json"},
            "method": "json"
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        try:
            if test['method'] == 'json':
                response = requests.post(url, json=test['data'], headers=test['headers'], timeout=30)
            else:
                response = requests.post(url, data=test['data'], headers=test['headers'], timeout=30)
            
            print(f"  Status: {response.status_code}")
            
            try:
                resp_json = response.json()
                print(f"  Response: {resp_json}")
            except:
                print(f"  Response text: {response.text[:100]}")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    print("🚀 PRODUCTION LOGIN DEBUGGER")
    print("=" * 60)
    
    # Step 1: Check environment
    check_environment()
    
    # Step 2: Check production database
    if check_production_database():
        
        # Step 3: Test login logic directly
        test_direct_login_logic()
        
        # Step 4: Create fresh user and test
        if create_test_user():
            
            # Step 5: Test production endpoint
            test_production_endpoint()
        else:
            print("❌ Could not create test user, skipping endpoint test")
    else:
        print("❌ Database check failed, cannot continue")