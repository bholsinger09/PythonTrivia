"""
Enhanced Database Service with Caching and Performance Optimizations

This module provides optimized database operations with:
- Redis caching for frequently accessed data
- Query optimization and performance monitoring
- Connection pooling and batch operations
- Advanced query patterns for better performance
"""

from db_service import *  # Import all existing functionality
from database_optimizations import QueryOptimizer, CacheManager, DatabaseOptimizer, PerformanceMonitor
from typing import Dict, List, Optional, Any, Union
import logging
from functools import lru_cache
import time

class OptimizedQuestionService(QuestionService):
    """Enhanced QuestionService with caching and optimization"""
    
    cache_manager = None
    
    @classmethod
    def set_cache_manager(cls, cache_manager: CacheManager):
        """Set the cache manager for this service"""
        cls.cache_manager = cache_manager
    
    @staticmethod
    @DatabaseOptimizer.query_timer
    def get_questions_by_criteria_cached(
        categories: List[Category] = None,
        difficulty: Difficulty = None,
        limit: int = None,
        exclude_ids: List[int] = None
    ) -> List[Question]:
        """Get questions with caching support"""
        
        # Try cache first
        if OptimizedQuestionService.cache_manager:
            cache_key = f"{categories}:{difficulty}:{limit}"
            cached_questions = OptimizedQuestionService.cache_manager.get_cached_questions(
                category=categories[0] if categories else None,
                difficulty=difficulty
            )
            
            if cached_questions:
                logging.info(f"Cache hit for questions: {cache_key}")
                # Filter out excluded IDs
                if exclude_ids:
                    cached_questions = [q for q in cached_questions if q['id'] not in exclude_ids]
                return cached_questions[:limit] if limit else cached_questions
        
        # Fallback to optimized database query
        questions = QueryOptimizer.get_questions_optimized(
            category=categories[0] if categories else None,
            difficulty=difficulty,
            limit=limit,
            exclude_ids=exclude_ids
        )
        
        # Cache the results
        if OptimizedQuestionService.cache_manager and questions:
            question_dicts = [q.to_dict() for q in questions]
            OptimizedQuestionService.cache_manager.cache_questions(
                question_dicts,
                category=categories[0] if categories else None,
                difficulty=difficulty
            )
            logging.info(f"Cached {len(question_dicts)} questions")
        
        return questions
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_question_stats_cached(question_id: int) -> Dict[str, Any]:
        """Get question statistics with LRU caching"""
        question = QuestionService.get_question_by_id(question_id)
        if question:
            return {
                'id': question.id,
                'times_asked': question.times_asked,
                'times_correct': question.times_correct,
                'success_rate': question.get_difficulty_percentage(),
                'difficulty': question.difficulty.value,
                'category': question.category.value
            }
        return None
    
    @staticmethod
    def get_random_questions_optimized(
        count: int = 10,
        category: Category = None,
        difficulty: Difficulty = None
    ) -> List[Question]:
        """Get random questions with optimized selection"""
        
        # Use database-level randomization for better performance
        query = Question.query.filter(Question.is_active == True)
        
        if category:
            query = query.filter(Question.category == category)
        
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        # Use ORDER BY RANDOM() for PostgreSQL or RAND() for MySQL
        # For SQLite, we'll use a different approach
        try:
            # Try PostgreSQL/MySQL approach
            questions = query.order_by(db.func.random()).limit(count).all()
        except:
            # Fallback for SQLite
            questions = query.order_by(Question.id).limit(count * 3).all()
            import random
            random.shuffle(questions)
            questions = questions[:count]
        
        return questions

class OptimizedGameSessionService(GameSessionService):
    """Enhanced GameSessionService with performance optimizations"""
    
    @staticmethod
    @DatabaseOptimizer.query_timer
    def get_user_sessions_optimized(user_id: int, limit: int = 10) -> List[GameSession]:
        """Get user sessions with optimized query"""
        return QueryOptimizer.get_user_game_history_optimized(user_id, limit)
    
    @staticmethod
    def bulk_update_session_progress(session_updates: List[Dict]) -> bool:
        """Bulk update multiple sessions for better performance"""
        try:
            # Batch update for better performance
            for update_data in session_updates:
                session = GameSession.query.get(update_data['session_id'])
                if session:
                    for key, value in update_data.items():
                        if key != 'session_id' and hasattr(session, key):
                            setattr(session, key, value)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Bulk session update failed: {e}")
            return False
    
    @staticmethod
    @lru_cache(maxsize=64)
    def get_session_summary_cached(session_token: str) -> Optional[Dict]:
        """Get session summary with caching"""
        session = GameSessionService.get_session_by_token(session_token)
        if session:
            return {
                'id': session.id,
                'total_questions': session.total_questions,
                'correct_answers': session.correct_answers,
                'accuracy': session.get_accuracy_percentage(),
                'current_streak': session.current_streak,
                'best_streak': session.best_streak,
                'total_score': session.total_score,
                'is_completed': session.is_completed
            }
        return None

class OptimizedScoreService(ScoreService):
    """Enhanced ScoreService with caching and optimization"""
    
    cache_manager = None
    
    @classmethod
    def set_cache_manager(cls, cache_manager: CacheManager):
        """Set the cache manager for this service"""
        cls.cache_manager = cache_manager
    
    @staticmethod
    @DatabaseOptimizer.query_timer
    def get_leaderboard_cached(
        category: Category = None,
        difficulty: Difficulty = None,
        limit: int = 10
    ) -> List[Score]:
        """Get leaderboard with caching"""
        
        # Try cache first
        if OptimizedScoreService.cache_manager:
            cached_scores = OptimizedScoreService.cache_manager.get_cached_leaderboard(
                category=category,
                difficulty=difficulty
            )
            
            if cached_scores:
                logging.info(f"Cache hit for leaderboard: {category}:{difficulty}")
                return cached_scores[:limit]
        
        # Fallback to optimized database query
        scores = QueryOptimizer.get_leaderboard_optimized(category, difficulty, limit)
        
        # Cache the results
        if OptimizedScoreService.cache_manager and scores:
            score_dicts = [score.to_dict() for score in scores]
            OptimizedScoreService.cache_manager.cache_leaderboard(
                score_dicts,
                category=category,
                difficulty=difficulty
            )
            logging.info(f"Cached {len(score_dicts)} leaderboard entries")
        
        return scores
    
    @staticmethod
    def invalidate_leaderboard_cache(category: Category = None, difficulty: Difficulty = None):
        """Invalidate leaderboard cache when new scores are added"""
        if OptimizedScoreService.cache_manager:
            pattern = f"leaderboard:{category or '*'}:{difficulty or '*'}"
            OptimizedScoreService.cache_manager.invalidate_cache(pattern)
    
    @staticmethod
    def save_score_optimized(
        game_session_id: int,
        user_id: int = None,
        anonymous_name: str = None,
        score: int = 0,
        accuracy_percentage: float = 0.0,
        questions_answered: int = 0,
        category: Category = None,
        difficulty: Difficulty = None
    ) -> Score:
        """Save score with cache invalidation"""
        
        # Save score using original method
        new_score = ScoreService.save_score(
            game_session_id=game_session_id,
            user_id=user_id,
            anonymous_name=anonymous_name,
            score=score,
            accuracy_percentage=accuracy_percentage,
            questions_answered=questions_answered,
            category=category,
            difficulty=difficulty
        )
        
        # Invalidate relevant caches
        OptimizedScoreService.invalidate_leaderboard_cache(category, difficulty)
        OptimizedScoreService.invalidate_leaderboard_cache()  # Also invalidate overall leaderboard
        
        return new_score
    
    @staticmethod
    @lru_cache(maxsize=32)
    def get_score_statistics_cached() -> Dict[str, Any]:
        """Get overall score statistics with caching"""
        
        total_scores = Score.query.count()
        if total_scores == 0:
            return {
                'total_scores': 0,
                'average_score': 0,
                'highest_score': 0,
                'average_accuracy': 0
            }
        
        # Use database aggregation for better performance
        stats = db.session.query(
            db.func.count(Score.id).label('total'),
            db.func.avg(Score.score).label('avg_score'),
            db.func.max(Score.score).label('max_score'),
            db.func.avg(Score.accuracy_percentage).label('avg_accuracy')
        ).first()
        
        return {
            'total_scores': stats.total,
            'average_score': round(stats.avg_score, 1) if stats.avg_score else 0,
            'highest_score': stats.max_score or 0,
            'average_accuracy': round(stats.avg_accuracy, 1) if stats.avg_accuracy else 0
        }

class OptimizedUserService(UserService):
    """Enhanced UserService with performance optimizations"""
    
    @staticmethod
    @DatabaseOptimizer.query_timer
    def get_user_profile_optimized(user_id: int) -> Optional[Dict]:
        """Get complete user profile with optimized queries"""
        
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None
        
        # Single query for recent sessions
        recent_sessions = db.session.query(GameSession).filter(
            GameSession.user_id == user_id,
            GameSession.is_completed == True
        ).order_by(GameSession.completed_at.desc()).limit(5).all()
        
        # Single query for best scores
        best_scores = db.session.query(Score).filter(
            Score.user_id == user_id
        ).order_by(Score.score.desc()).limit(5).all()
        
        return {
            'user': user.to_dict(),
            'recent_sessions': [session.to_dict() for session in recent_sessions],
            'best_scores': [score.to_dict() for score in best_scores]
        }
    
    @staticmethod
    def bulk_update_user_stats(user_stats_updates: List[Dict]) -> bool:
        """Bulk update user statistics for better performance"""
        try:
            for update_data in user_stats_updates:
                user = User.query.get(update_data['user_id'])
                if user:
                    for key, value in update_data.items():
                        if key != 'user_id' and hasattr(user, key):
                            setattr(user, key, value)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Bulk user stats update failed: {e}")
            return False
    
    @staticmethod
    @lru_cache(maxsize=16)
    def get_active_users_count() -> int:
        """Get count of active users with caching"""
        return User.query.filter(User.is_active == True).count()

class DatabasePerformanceManager:
    """Centralized database performance management"""
    
    def __init__(self, redis_client=None):
        self.cache_manager = CacheManager(redis_client) if redis_client else None
        self.setup_optimizations()
    
    def setup_optimizations(self):
        """Initialize all performance optimizations"""
        
        # Apply database indexes
        DatabaseOptimizer.apply_indexes()
        
        # Setup cache managers
        if self.cache_manager:
            OptimizedQuestionService.set_cache_manager(self.cache_manager)
            OptimizedScoreService.set_cache_manager(self.cache_manager)
            logging.info("✅ Cache managers configured")
        
        logging.info("✅ Database optimizations applied")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        return {
            'connection_stats': PerformanceMonitor.get_connection_stats(),
            'query_recommendations': DatabaseOptimizer.analyze_query_performance(),
            'cache_status': 'enabled' if self.cache_manager else 'disabled',
            'optimization_status': 'applied'
        }
    
    def clear_all_caches(self):
        """Clear all application caches"""
        if self.cache_manager:
            self.cache_manager.invalidate_cache('*')
        
        # Clear LRU caches
        OptimizedQuestionService.get_question_stats_cached.cache_clear()
        OptimizedGameSessionService.get_session_summary_cached.cache_clear()
        OptimizedScoreService.get_score_statistics_cached.cache_clear()
        OptimizedUserService.get_active_users_count.cache_clear()
        
        logging.info("✅ All caches cleared")

# Export optimized services for easy replacement
__all__ = [
    'OptimizedQuestionService',
    'OptimizedGameSessionService', 
    'OptimizedScoreService',
    'OptimizedUserService',
    'DatabasePerformanceManager',
    'QueryOptimizer',
    'CacheManager',
    'DatabaseOptimizer',
    'PerformanceMonitor'
]