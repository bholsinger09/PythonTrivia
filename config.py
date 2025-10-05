"""
Configuration settings for the Python Trivia application.

This module defines configuration classes for different environments:
- DevelopmentConfig: Local development settings
- ProductionConfig: Deployed production settings  
- TestingConfig: Testing environment settings
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class with common settings."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Security settings
    WTF_CSRF_ENABLED = True
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    # Flask settings
    DEBUG = True
    TESTING = False
    
    # Database settings - SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///trivia_dev.db'
    
    # Development-specific settings
    SQLALCHEMY_ECHO = False  # Set to True to see SQL queries
    
class ProductionConfig(Config):
    """Production environment configuration."""
    
    # Flask settings
    DEBUG = False
    TESTING = False
    
    # Database settings - PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///trivia_prod.db'
    
    # Production-specific settings
    SQLALCHEMY_ECHO = False
    
    # Security settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

class TestingConfig(Config):
    """Testing environment configuration."""
    
    # Flask settings
    DEBUG = True
    TESTING = True
    
    # Database settings - In-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Testing-specific settings
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_ECHO = False

# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
