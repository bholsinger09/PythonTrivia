#!/usr/bin/env python3
"""
Database initialization script for Python Trivia Game
FIXED: Now uses smart_database_init to preserve user data across deployments
"""
import os
import sys
from flask import Flask
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from models import db, User, Question, GameSession, Answer, Score
from db_service import DatabaseSeeder
from user_persistence import smart_database_init, user_data_manager

def create_app(config_class=None):
    """Create Flask app with database configuration"""
    app = Flask(__name__)
    
    # Determine configuration
    if config_class is None:
        env = os.getenv('FLASK_ENV', 'development')
        if env == 'production':
            config_class = ProductionConfig
        elif env == 'testing':
            config_class = TestingConfig
        else:
            config_class = DevelopmentConfig
    
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    return app

def init_database(drop_existing=False, seed_data=True, preserve_users=True):
    """Initialize the database with user preservation"""
    app = create_app()
    
    with app.app_context():
        if drop_existing:
            print("Dropping existing tables...")
            if preserve_users:
                print("Backing up users before drop...")
                user_data_manager.backup_users()
            db.drop_all()
        
        print("Initializing database with smart preservation...")
        # Use smart initialization that preserves users
        smart_database_init(preserve_users=preserve_users)
        
        if seed_data and Question.query.count() == 0:
            print("Seeding sample questions...")
            DatabaseSeeder.seed_sample_questions()
        
        # Log user status
        user_count = User.query.count()
        if user_count > 0:
            print(f"Database initialization complete! {user_count} users preserved.")
        else:
            print("Database initialization complete! No existing users found.")

def reset_database():
    """Reset database (drop and recreate)"""
    init_database(drop_existing=True, seed_data=True)

def create_migration():
    """Create a database migration (if using Flask-Migrate)"""
    try:
        from flask_migrate import init, migrate, upgrade
        app = create_app()
        
        with app.app_context():
            # Initialize migration repository if it doesn't exist
            if not os.path.exists('migrations'):
                print("Initializing migration repository...")
                init()
            
            # Create migration
            print("Creating migration...")
            migrate(message="Auto migration")
            
            # Apply migration
            print("Applying migration...")
            upgrade()
            
    except ImportError:
        print("Flask-Migrate not installed. Using smart initialization...")
        init_database(drop_existing=False, seed_data=False)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management for Python Trivia Game")
    parser.add_argument('command', choices=['init', 'reset', 'migrate', 'seed'], 
                       help='Database command to execute')
    parser.add_argument('--drop', action='store_true', 
                       help='Drop existing tables (for init command)')
    parser.add_argument('--no-seed', action='store_true', 
                       help='Skip seeding sample data')
    parser.add_argument('--no-preserve', action='store_true',
                       help='Skip user preservation (NOT RECOMMENDED for production)')
    
    args = parser.parse_args()
    
    # Default to preserving users unless explicitly disabled
    preserve_users = not args.no_preserve
    
    if args.command == 'init':
        init_database(drop_existing=args.drop, seed_data=not args.no_seed, preserve_users=preserve_users)
    elif args.command == 'reset':
        # For reset, ask for confirmation if preserving users
        if preserve_users:
            print("WARNING: Reset will backup and restore users. Use --no-preserve to skip.")
        reset_database()
    elif args.command == 'migrate':
        create_migration()
    elif args.command == 'seed':
        app = create_app()
        with app.app_context():
            if Question.query.count() == 0:
                DatabaseSeeder.seed_sample_questions()
                print("Sample questions seeded.")
            else:
                print("Questions already exist, skipping seed.")
    
    print(f"Database {args.command} operation completed successfully!")