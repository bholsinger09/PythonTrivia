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
    
    # Connection pooling for development (SQLite-compatible)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 20,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'connect_args': {
            'timeout': 20,
            'check_same_thread': False  # SQLite specific
        }
    }
    
class ProductionConfig(Config):
    """Production environment configuration."""
    
    # Flask settings
    DEBUG = False
    TESTING = False
    
    # Database settings - PostgreSQL for production
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///trivia_prod.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Production-specific settings
    SQLALCHEMY_ECHO = False
    
    # Conditional connection pooling based on database type
    if DATABASE_URL and DATABASE_URL.startswith('postgresql'):
        # PostgreSQL connection pooling
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 10,          # Number of connections to maintain
            'max_overflow': 20,       # Additional connections beyond pool_size
            'pool_timeout': 30,       # Seconds to wait for connection
            'pool_recycle': 1800,     # Recycle connections after 30 minutes
            'pool_pre_ping': True,    # Validate connections before use
            'echo': False,
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'PythonTriviaApp'
            }
        }
    else:
        # SQLite connection settings
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_timeout': 20,
            'pool_recycle': 300,
            'pool_pre_ping': True,
            'connect_args': {
                'check_same_thread': False
            }
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
    
    # Fast connection settings for testing
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 5,
        'pool_recycle': 60,
        'pool_pre_ping': False,  # Skip for speed in testing
        'connect_args': {
            'timeout': 5,
            'check_same_thread': False
        }
    }

# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
