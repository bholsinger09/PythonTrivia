"""
Database Migration Script for Performance Optimizations

This script applies all database performance optimizations including:
- New indexes for frequently queried columns
- Composite indexes for multi-column queries
- Foreign key constraints verification
- Database statistics updates
"""

import sys
import os
from sqlalchemy import text, Index
from datetime import datetime

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, Question, GameSession, Answer, Score, User
from database_optimizations import DatabaseOptimizer
from config import DevelopmentConfig, ProductionConfig

def run_migrations(app):
    """Run database migrations for performance optimizations"""
    
    with app.app_context():
        try:
            print("🚀 Starting database performance optimization migrations...")
            print(f"📊 Database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
            # Step 1: Apply performance indexes
            print("\n📈 Step 1: Creating performance indexes...")
            apply_performance_indexes()
            
            # Step 2: Update database statistics
            print("\n📊 Step 2: Updating database statistics...")
            update_database_statistics()
            
            # Step 3: Verify foreign key constraints
            print("\n🔗 Step 3: Verifying foreign key constraints...")
            verify_foreign_keys()
            
            # Step 4: Analyze query performance
            print("\n🔍 Step 4: Analyzing query performance...")
            analyze_query_performance()
            
            print("\n✅ Database optimization migrations completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            db.session.rollback()
            return False

def apply_performance_indexes():
    """Apply all performance indexes"""
    
    indexes_created = 0
    
    try:
        # Create composite indexes using SQLAlchemy
        composite_indexes = [
            # Questions table - category + difficulty + active
            Index('idx_questions_category_difficulty_active', 
                  Question.category, Question.difficulty, Question.is_active),
            
            # Questions table - statistics queries
            Index('idx_questions_stats', 
                  Question.times_asked, Question.times_correct),
            
            # GameSessions table - user + time ordering  
            Index('idx_game_sessions_user_started',
                  GameSession.user_id, GameSession.started_at.desc()),
            
            # GameSessions table - completed sessions by score
            Index('idx_game_sessions_completed_score',
                  GameSession.is_completed, GameSession.total_score.desc(), GameSession.completed_at.desc()),
            
            # Answers table - session + question lookup
            Index('idx_answers_session_question_correct',
                  Answer.game_session_id, Answer.question_id, Answer.is_correct),
            
            # Answers table - user answer history
            Index('idx_answers_user_answered_at',
                  Answer.user_id, Answer.answered_at.desc()),
            
            # Scores table - leaderboard queries
            Index('idx_scores_category_difficulty_score',
                  Score.category, Score.difficulty, Score.score.desc(), Score.achieved_at.desc()),
            
            # Scores table - user score history
            Index('idx_scores_user_achieved',
                  Score.user_id, Score.achieved_at.desc()),
            
            # Users table - active users by activity
            Index('idx_users_active_last_seen',
                  User.is_active, User.last_seen.desc()),
            
            # Users table - user statistics
            Index('idx_users_stats',
                  User.total_games_played, User.total_points.desc())
        ]
        
        for index in composite_indexes:
            try:
                # Check if index exists first
                inspector = db.inspect(db.engine)
                existing_indexes = inspector.get_indexes(index.table.name)
                index_names = [idx['name'] for idx in existing_indexes]
                
                if index.name not in index_names:
                    index.create(db.engine)
                    indexes_created += 1
                    print(f"   ✅ Created index: {index.name}")
                else:
                    print(f"   ℹ️  Index already exists: {index.name}")
                    
            except Exception as e:
                print(f"   ⚠️  Failed to create index {index.name}: {e}")
        
        print(f"   📈 Created {indexes_created} new indexes")
        
    except Exception as e:
        print(f"   ❌ Error applying indexes: {e}")
        raise

def update_database_statistics():
    """Update database statistics for query optimizer"""
    
    try:
        # Get database type
        db_url = str(db.engine.url)
        
        if 'postgresql' in db_url:
            # PostgreSQL - update statistics
            tables = ['questions', 'game_sessions', 'answers', 'scores', 'users']
            for table in tables:
                try:
                    db.engine.execute(text(f"ANALYZE {table}"))
                    print(f"   ✅ Updated statistics for: {table}")
                except Exception as e:
                    print(f"   ⚠️  Failed to analyze {table}: {e}")
                    
        elif 'mysql' in db_url:
            # MySQL - update statistics
            tables = ['questions', 'game_sessions', 'answers', 'scores', 'users'] 
            for table in tables:
                try:
                    db.engine.execute(text(f"ANALYZE TABLE {table}"))
                    print(f"   ✅ Updated statistics for: {table}")
                except Exception as e:
                    print(f"   ⚠️  Failed to analyze {table}: {e}")
                    
        else:
            # SQLite - no statistics update needed
            print("   ℹ️  SQLite detected - statistics update not required")
            
    except Exception as e:
        print(f"   ❌ Error updating statistics: {e}")

def verify_foreign_keys():
    """Verify all foreign key constraints are properly set"""
    
    try:
        inspector = db.inspect(db.engine)
        
        # Check foreign keys for each table
        tables_to_check = {
            'questions': ['created_by'],
            'game_sessions': ['user_id'],
            'answers': ['user_id', 'question_id', 'game_session_id'],
            'scores': ['user_id', 'game_session_id']
        }
        
        for table_name, fk_columns in tables_to_check.items():
            try:
                foreign_keys = inspector.get_foreign_keys(table_name)
                existing_fks = [fk['constrained_columns'][0] for fk in foreign_keys]
                
                for column in fk_columns:
                    if column in existing_fks:
                        print(f"   ✅ Foreign key exists: {table_name}.{column}")
                    else:
                        print(f"   ⚠️  Missing foreign key: {table_name}.{column}")
                        
            except Exception as e:
                print(f"   ⚠️  Error checking {table_name}: {e}")
                
    except Exception as e:
        print(f"   ❌ Error verifying foreign keys: {e}")

def analyze_query_performance():
    """Analyze common query patterns for performance"""
    
    try:
        # Common query patterns to test
        test_queries = [
            {
                'name': 'Question filtering by category and difficulty',
                'query': 'SELECT COUNT(*) FROM questions WHERE category = :cat AND difficulty = :diff AND is_active = true',
                'params': {'cat': 'basics', 'diff': 'easy'}
            },
            {
                'name': 'User game sessions by date',
                'query': 'SELECT COUNT(*) FROM game_sessions WHERE user_id = :user_id ORDER BY started_at DESC LIMIT 10',
                'params': {'user_id': 1}
            },
            {
                'name': 'Leaderboard query',
                'query': 'SELECT COUNT(*) FROM scores WHERE category = :cat ORDER BY score DESC LIMIT 10',
                'params': {'cat': 'basics'}
            },
            {
                'name': 'Answer history lookup',
                'query': 'SELECT COUNT(*) FROM answers WHERE game_session_id = :session_id ORDER BY answered_at',
                'params': {'session_id': 1}
            }
        ]
        
        for query_info in test_queries:
            try:
                start_time = datetime.now()
                result = db.engine.execute(text(query_info['query']), query_info['params'])
                end_time = datetime.now()
                
                duration_ms = (end_time - start_time).total_seconds() * 1000
                
                if duration_ms > 50:  # Flag slow queries (>50ms)
                    status = "⚠️  SLOW"
                else:
                    status = "✅ FAST"
                    
                print(f"   {status} {query_info['name']}: {duration_ms:.2f}ms")
                
            except Exception as e:
                print(f"   ❌ Query failed - {query_info['name']}: {e}")
                
    except Exception as e:
        print(f"   ❌ Error analyzing queries: {e}")

def rollback_migrations(app):
    """Rollback performance optimizations if needed"""
    
    with app.app_context():
        try:
            print("🔄 Rolling back database optimizations...")
            
            # Drop custom indexes (keep original table indexes)
            custom_indexes = [
                'idx_questions_category_difficulty_active',
                'idx_questions_stats', 
                'idx_game_sessions_user_started',
                'idx_game_sessions_completed_score',
                'idx_answers_session_question_correct',
                'idx_answers_user_answered_at',
                'idx_scores_category_difficulty_score',
                'idx_scores_user_achieved',
                'idx_users_active_last_seen',
                'idx_users_stats'
            ]
            
            dropped_count = 0
            for index_name in custom_indexes:
                try:
                    db.engine.execute(text(f"DROP INDEX IF EXISTS {index_name}"))
                    dropped_count += 1
                    print(f"   ✅ Dropped index: {index_name}")
                except Exception as e:
                    print(f"   ⚠️  Error dropping {index_name}: {e}")
            
            print(f"   📉 Dropped {dropped_count} performance indexes")
            print("✅ Rollback completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

if __name__ == "__main__":
    """Run migrations from command line"""
    
    from flask import Flask
    
    # Create app with appropriate config
    app = Flask(__name__)
    
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    
    # Initialize database
    db.init_app(app)
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        success = rollback_migrations(app)
    else:
        success = run_migrations(app)
    
    sys.exit(0 if success else 1)