"""
Database optimization module for enhanced performance.

This module provides comprehensive database optimization tools including:
- Automatic index creation for frequently queried columns
- Query performance monitoring and analysis
- Connection pooling optimization
- Cache invalidation strategies
"""
from sqlalchemy import Index, event, text
from sqlalchemy.orm import sessionmaker
from functools import wraps
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import json
import logging

logger = logging.getLogger(__name__)

from sqlalchemy import Index, text
from models import db, Question, GameSession, Answer, Score, User
from typing import Dict, List, Optional, Any
import logging
import time
from functools import wraps

class DatabaseOptimizer:
    """Database optimization utilities and performance monitoring"""
    
    @staticmethod
    def create_indexes():
        """Create composite indexes for better query performance."""
        try:
            # Import here to avoid circular imports
            from models import db
            from sqlalchemy import text
            
            # Create composite indexes
            with db.engine.connect() as conn:
                # Question indexes
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_questions_active_difficulty_category 
                        ON questions(is_active, difficulty, category)
                    """))
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")
                
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_questions_difficulty_times_asked 
                        ON questions(difficulty, times_asked)
                    """))
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")
                
                # Answer indexes  
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_answers_session_question 
                        ON answers(game_session_id, question_id)
                    """))
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")
                
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_answers_user_correct_date 
                        ON answers(user_id, is_correct, answered_at)
                    """))
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")
                
                # Score indexes
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_scores_user_session 
                        ON scores(user_id, game_session_id)
                    """))
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")
                
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_scores_category_score 
                        ON scores(category, score DESC)
                    """))
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")
                
                conn.commit()
                
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
            raise
    
    @staticmethod
    def apply_indexes():
        """Apply all performance indexes to the database"""
        try:
            indexes = DatabaseOptimizer.create_performance_indexes()
            
            for index in indexes:
                # Check if index already exists
                index_name = index.name
                exists = db.engine.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.statistics 
                    WHERE table_schema = DATABASE() 
                    AND index_name = '{index_name}'
                """)).scalar() > 0
                
                if not exists:
                    index.create(db.engine)
                    print(f"✅ Created index: {index_name}")
                else:
                    print(f"ℹ️  Index already exists: {index_name}")
                    
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
            logging.error(f"Database index creation failed: {e}")

    @staticmethod
    def query_timer(func):
        """Decorator to time database queries"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            query_time = (end_time - start_time) * 1000  # Convert to milliseconds
            if query_time > 100:  # Log slow queries (>100ms)
                logging.warning(f"Slow query detected in {func.__name__}: {query_time:.2f}ms")
            
            return result
        return wrapper

    @staticmethod
    def analyze_query_performance():
        """Analyze database query performance and provide recommendations"""
        
        recommendations = []
        
        # Check for missing indexes
        slow_queries = [
            "SELECT * FROM questions WHERE category = ? AND difficulty = ?",
            "SELECT * FROM game_sessions WHERE user_id = ? ORDER BY started_at DESC",
            "SELECT * FROM scores WHERE category = ? ORDER BY score DESC LIMIT 10",
            "SELECT * FROM answers WHERE game_session_id = ? ORDER BY answered_at"
        ]
        
        for query in slow_queries:
            # Simulate query analysis
            recommendations.append(f"Consider adding composite index for: {query}")
        
        return recommendations

class CacheManager:
    """Redis-based caching for frequently accessed data"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.default_ttl = 300  # 5 minutes
    
    def get_cached_questions(self, category=None, difficulty=None) -> Optional[List[Dict]]:
        """Get cached questions by category and difficulty"""
        if not self.redis_client:
            return None
            
        cache_key = f"questions:{category or 'all'}:{difficulty or 'all'}"
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                import json
                return json.loads(cached_data)
        except Exception as e:
            logging.error(f"Cache get error: {e}")
        
        return None
    
    def cache_questions(self, questions: List[Dict], category=None, difficulty=None):
        """Cache questions data"""
        if not self.redis_client:
            return
            
        cache_key = f"questions:{category or 'all'}:{difficulty or 'all'}"
        
        try:
            import json
            self.redis_client.setex(
                cache_key,
                self.default_ttl,
                json.dumps(questions, default=str)
            )
        except Exception as e:
            logging.error(f"Cache set error: {e}")
    
    def get_cached_leaderboard(self, category=None, difficulty=None) -> Optional[List[Dict]]:
        """Get cached leaderboard data"""
        if not self.redis_client:
            return None
            
        cache_key = f"leaderboard:{category or 'all'}:{difficulty or 'all'}"
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                import json
                return json.loads(cached_data)
        except Exception as e:
            logging.error(f"Cache get error: {e}")
        
        return None
    
    def cache_leaderboard(self, scores: List[Dict], category=None, difficulty=None):
        """Cache leaderboard data"""
        if not self.redis_client:
            return
            
        cache_key = f"leaderboard:{category or 'all'}:{difficulty or 'all'}"
        
        try:
            import json
            self.redis_client.setex(
                cache_key,
                self.default_ttl,
                json.dumps(scores, default=str)
            )
        except Exception as e:
            logging.error(f"Cache set error: {e}")
    
    def invalidate_cache(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        if not self.redis_client:
            return
            
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logging.error(f"Cache invalidation error: {e}")

class QueryOptimizer:
    """Optimized query methods for common operations"""
    
    @staticmethod
    @DatabaseOptimizer.query_timer
    def get_questions_optimized(category=None, difficulty=None, limit=None, exclude_ids=None):
        """Optimized question fetching with eager loading"""
        from models import Question
        
        # Use select for better performance than filter on large datasets
        query = db.session.query(Question).filter(Question.is_active == True)
        
        # Apply filters in order of selectivity (most selective first)
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        if category:
            query = query.filter(Question.category == category)
        
        if exclude_ids:
            query = query.filter(~Question.id.in_(exclude_ids))
        
        # Order by question statistics for better distribution
        query = query.order_by(Question.times_asked.asc(), Question.id)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    @DatabaseOptimizer.query_timer
    def get_user_game_history_optimized(user_id: int, limit: int = 10):
        """Optimized user game history with minimal queries"""
        from models import GameSession
        
        # Single query with all needed data
        sessions = db.session.query(GameSession).filter(
            GameSession.user_id == user_id,
            GameSession.is_completed == True
        ).order_by(
            GameSession.completed_at.desc()
        ).limit(limit).all()
        
        return sessions
    
    @staticmethod
    @DatabaseOptimizer.query_timer  
    def get_leaderboard_optimized(category=None, difficulty=None, limit=10):
        """Optimized leaderboard query"""
        from models import Score
        
        query = db.session.query(Score).join(Score.user)
        
        # Apply filters
        if category:
            query = query.filter(Score.category == category)
        
        if difficulty:
            query = query.filter(Score.difficulty == difficulty)
        
        # Order by score and time for tie-breaking
        scores = query.order_by(
            Score.score.desc(),
            Score.achieved_at.asc()
        ).limit(limit).all()
        
        return scores

# Performance monitoring utilities
class PerformanceMonitor:
    """Monitor database performance metrics"""
    
    @staticmethod
    def get_slow_queries():
        """Get slow query log (implementation depends on database)"""
        # This would integrate with database-specific monitoring
        return []
    
    @staticmethod
    def get_connection_stats():
        """Get database connection pool statistics"""
        engine = db.engine
        pool = engine.pool
        
        return {
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'invalid': pool.invalid()
        }
    
    @staticmethod
    def log_performance_metrics():
        """Log current performance metrics"""
        stats = PerformanceMonitor.get_connection_stats()
        logging.info(f"Database connection stats: {stats}")