"""
Database Performance Optimization
Add composite indexes for frequently used query patterns
"""
from flask import current_app
from models import db

def add_performance_indexes():
    """Add composite indexes for better query performance"""
    
    print("Adding performance optimization indexes...")
    
    try:
        from sqlalchemy import text
        
        # User table composite indexes
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_active_created 
            ON users (is_active, created_at);
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_active_lastseen 
            ON users (is_active, last_seen);
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_stats_lookup 
            ON users (total_points DESC, total_games_played DESC);
        """))
        
        # Question table performance indexes
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_question_category_difficulty 
            ON questions (category, difficulty, times_asked);
        """))
        
        # Score table performance indexes for leaderboards
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_score_leaderboard 
            ON scores (score DESC, achieved_at DESC);
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_score_user_category 
            ON scores (user_id, category, score DESC);
        """))
        
        # Game session performance indexes
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_session_user_date 
            ON game_sessions (user_id, started_at DESC);
        """))
        
        # Answer performance indexes for analytics
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_answer_correctness 
            ON answers (is_correct, answered_at DESC);
        """))
        
        db.session.commit()
        print("✅ Performance indexes added successfully!")
        
    except Exception as e:
        print(f"Error adding indexes: {e}")
        db.session.rollback()

def remove_performance_indexes():
    """Remove the performance indexes (for rollback)"""
    
    print("Removing performance optimization indexes...")
    
    indexes_to_remove = [
        'idx_user_active_created',
        'idx_user_active_lastseen', 
        'idx_user_stats_lookup',
        'idx_question_category_difficulty',
        'idx_score_leaderboard',
        'idx_score_user_category',
        'idx_session_user_date',
        'idx_answer_correctness'
    ]
    
    try:
        for index_name in indexes_to_remove:
            db.engine.execute(f"DROP INDEX IF EXISTS {index_name};")
        
        print("✅ Performance indexes removed successfully!")
        
    except Exception as e:
        print(f"Error removing indexes: {e}")

if __name__ == "__main__":
    from app import app
    
    with app.app_context():
        import sys
        
        if len(sys.argv) > 1 and sys.argv[1] == 'remove':
            remove_performance_indexes()
        else:
            add_performance_indexes()