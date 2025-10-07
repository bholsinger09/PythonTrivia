#!/usr/bin/env python3
"""
Simple database initialization that runs as part of app startup
This ensures users are created every time the app starts
"""
import os
import logging
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_essential_users():
    """Ensure essential users exist in the database"""
    try:
        from models import db, User
        
        logger.info("🔧 Checking for essential users...")
        
        # Essential users to maintain
        essential_users = [
            {
                'username': 'code_monkey',
                'email': 'bholsinger@gmail.com',
                'password': 'password123'
            }
        ]
        
        for user_data in essential_users:
            username = user_data['username']
            
            # Check if user exists
            existing_user = User.query.filter_by(username=username).first()
            
            if existing_user:
                logger.info(f"✅ User '{username}' exists")
                # Verify password works
                if existing_user.check_password(user_data['password']):
                    logger.info(f"✅ User '{username}' password verified")
                else:
                    logger.info(f"🔧 Updating password for '{username}'")
                    existing_user.set_password(user_data['password'])
                    db.session.commit()
                    logger.info(f"✅ Password updated for '{username}'")
            else:
                logger.info(f"🔧 Creating user '{username}'...")
                new_user = User(
                    username=username,
                    email=user_data['email']
                )
                new_user.set_password(user_data['password'])
                
                db.session.add(new_user)
                db.session.commit()
                logger.info(f"✅ User '{username}' created successfully")
        
        logger.info("✅ Essential users check complete")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error ensuring essential users: {e}")
        return False

def init_app_with_users(app):
    """Initialize app and ensure users exist"""
    try:
        from models import db
        
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            logger.info("✅ Database tables verified")
            
            # Ensure essential users exist
            ensure_essential_users()
            
        return True
        
    except Exception as e:
        logger.error(f"❌ App initialization error: {e}")
        return False

if __name__ == "__main__":
    # This runs when called directly
    from app import app
    init_app_with_users(app)
    logger.info("🎯 Initialization complete - users should be available")