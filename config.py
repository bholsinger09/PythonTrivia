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
    
    # Connection pooling optimized for development
    SQLALCHEMY_ENGINE_OPTIONS = {
        # Smaller pools for development
        'pool_size': 3,
        'max_overflow': 5, 
        'pool_timeout': 20,
        'pool_recycle': 300,  # 5 minutes for development
        'pool_pre_ping': True,
        'echo': False,  # Set to True for SQL debugging
        
        'connect_args': {
            'timeout': 20,
            'check_same_thread': False,  # SQLite specific
            'application_name': 'PythonTriviaApp-Dev'
        }
    }
    
class ProductionConfig(Config):
    """Production environment configuration."""
    
    # Flask settings
    DEBUG = False
    TESTING = False
    
    # Database settings - MUST use PostgreSQL for production
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required for production")
        if not database_url.startswith('postgresql'):
            raise ValueError(f"Production requires PostgreSQL, got: {database_url[:30]}...")
        return database_url
    
    # Production-specific settings
    SQLALCHEMY_ECHO = False
    
    # PostgreSQL connection pooling - OPTIMIZED for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        # Core pool settings optimized for Render deployment
        'pool_size': 8,  # Base connections (2 * CPU + 1, Render has ~3 vCPU)
        'max_overflow': 16,  # Additional connections under load
        'pool_timeout': 30,  # Wait 30s for connection
        'pool_recycle': 3600,  # Recycle connections every hour
        'pool_pre_ping': True,  # Test connections before use
        
        # Performance optimizations
        'echo': False,
        'echo_pool': False,
        'pool_reset_on_return': 'commit',
        
        # PostgreSQL specific optimizations
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'PythonTriviaApp',
            'server_side_cursors': False,  # Better for short queries
            'keepalives_idle': '600',       # TCP keepalive settings
            'keepalives_interval': '30', 
            'keepalives_count': '3',
            'tcp_user_timeout': '30000',    # 30 seconds
            
            # Performance settings
            'statement_timeout': '30000',   # 30 second statement timeout
            'idle_in_transaction_session_timeout': '60000',  # 1 minute
            'options': '-c default_transaction_isolation=read_committed'
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
