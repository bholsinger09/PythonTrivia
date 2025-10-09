"""
Advanced Database Query Optimization for Python Trivia Game
Implements sophisticated indexing, query optimization, and performance monitoring.
"""
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import text, func, and_, or_, Index, event
from sqlalchemy.orm import joinedload, selectinload, contains_eager
from sqlalchemy.sql import select
from models import db, User, Question, GameSession, Answer, Score, Category, Difficulty
from datetime import datetime, timezone, timedelta
import logging
from performance_monitoring import performance_monitor
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Advanced query optimization service"""
    
    def __init__(self):
        self.query_cache = {}
        self.query_stats = {}
        
    def create_performance_indexes(self):
        """Create strategic database indexes for performance"""
        try:
            # Core performance indexes
            indexes_to_create = [
                # User table indexes
                Index('idx_user_username_active', 'users.username', 'users.is_active'),
                Index('idx_user_email_active', 'users.email', 'users.is_active'),
                Index('idx_user_last_seen', 'users.last_seen'),
                Index('idx_user_total_points', 'users.total_points'),
                Index('idx_user_created_at', 'users.created_at'),
                
                # Question table indexes
                Index('idx_question_category_difficulty', 'questions.category', 'questions.difficulty'),
                Index('idx_question_active_times_asked', 'questions.is_active', 'questions.times_asked'),
                Index('idx_question_created_updated', 'questions.created_at', 'questions.updated_at'),
                Index('idx_question_success_rate', 'questions.times_correct', 'questions.times_asked'),
                
                # Game session indexes
                Index('idx_session_user_completed', 'game_sessions.user_id', 'game_sessions.is_completed'),
                Index('idx_session_started_completed', 'game_sessions.started_at', 'game_sessions.completed_at'),
                Index('idx_session_token', 'game_sessions.session_token'),
                
                # Answer table indexes
                Index('idx_answer_session_question', 'answers.game_session_id', 'answers.question_id'),
                Index('idx_answer_user_correct', 'answers.user_id', 'answers.is_correct'),
                Index('idx_answer_answered_at', 'answers.answered_at'),
                
                # Score table indexes
                Index('idx_score_user_achieved', 'scores.user_id', 'scores.achieved_at'),
                Index('idx_score_category_difficulty', 'scores.category', 'scores.difficulty'),
                Index('idx_score_leaderboard', 'scores.score', 'scores.achieved_at'),
            ]
            
            # Create indexes
            with db.engine.begin() as conn:
                for index in indexes_to_create:
                    try:
                        index.create(conn, checkfirst=True)
                        logger.info(f"Created index: {index.name}")
                    except Exception as e:
                        logger.warning(f"Index {index.name} may already exist: {e}")
                        
            logger.info("Performance indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            return False
    
    def optimize_leaderboard_query(self, limit: int = 10, category: Optional[Category] = None) -> List[Dict]:
        """Optimized leaderboard query with strategic joins"""
        start_time = time.time()
        
        try:
            # Base query with optimized joins
            query = db.session.query(
                User.id,
                User.username,
                User.total_points,
                User.total_games_played,
                User.total_correct_answers,
                User.total_questions_answered,
                func.max(Score.score).label('best_score'),
                func.count(Score.id).label('total_scores')
            ).join(Score, User.id == Score.user_id, isouter=True)
            
            # Category filter if specified
            if category:
                query = query.filter(Score.category == category)
            
            # Active users only
            query = query.filter(User.is_active == True)
            
            # Group and order optimally
            query = query.group_by(
                User.id, User.username, User.total_points,
                User.total_games_played, User.total_correct_answers,
                User.total_questions_answered
            ).order_by(
                User.total_points.desc(),
                func.max(Score.score).desc(),
                User.total_correct_answers.desc()
            ).limit(limit)
            
            # Execute with result transformation
            results = []
            for row in query.all():
                accuracy = 0.0
                if row.total_questions_answered > 0:
                    accuracy = (row.total_correct_answers / row.total_questions_answered) * 100
                
                results.append({
                    'id': row.id,
                    'username': row.username,
                    'total_points': row.total_points,
                    'total_games': row.total_games_played,
                    'accuracy': round(accuracy, 1),
                    'best_score': row.best_score or 0,
                    'total_scores': row.total_scores
                })
            
            # Record performance
            duration = time.time() - start_time
            self._record_query_performance('optimized_leaderboard', duration, len(results))
            
            return results
            
        except Exception as e:
            logger.error(f"Leaderboard query optimization failed: {e}")
            return []
    
    def optimize_user_stats_query(self, user_id: int) -> Optional[Dict]:
        """Optimized user statistics with single query"""
        start_time = time.time()
        
        try:
            # Single query with all user stats
            result = db.session.query(
                User.id,
                User.username,
                User.email,
                User.total_points,
                User.total_games_played,
                User.total_correct_answers,
                User.total_questions_answered,
                User.best_streak,
                User.created_at,
                User.last_seen,
                func.count(GameSession.id).label('completed_sessions'),
                func.avg(GameSession.total_score).label('avg_score'),
                func.max(Score.score).label('best_overall_score'),
                func.count(Score.id).label('total_scores')
            ).outerjoin(GameSession, and_(
                User.id == GameSession.user_id,
                GameSession.is_completed == True
            )).outerjoin(Score, User.id == Score.user_id).filter(
                User.id == user_id,
                User.is_active == True
            ).group_by(
                User.id, User.username, User.email, User.total_points,
                User.total_games_played, User.total_correct_answers,
                User.total_questions_answered, User.best_streak,
                User.created_at, User.last_seen
            ).first()
            
            if not result:
                return None
            
            # Calculate derived metrics
            accuracy = 0.0
            if result.total_questions_answered > 0:
                accuracy = (result.total_correct_answers / result.total_questions_answered) * 100
            
            user_stats = {
                'id': result.id,
                'username': result.username,
                'email': result.email,
                'total_points': result.total_points,
                'total_games': result.total_games_played,
                'total_correct': result.total_correct_answers,
                'total_questions': result.total_questions_answered,
                'accuracy': round(accuracy, 1),
                'best_streak': result.best_streak,
                'completed_sessions': result.completed_sessions,
                'avg_score': round(float(result.avg_score or 0), 1),
                'best_score': result.best_overall_score or 0,
                'total_scores': result.total_scores,
                'member_since': result.created_at.isoformat(),
                'last_seen': result.last_seen.isoformat() if result.last_seen else None
            }
            
            # Record performance
            duration = time.time() - start_time
            self._record_query_performance('optimized_user_stats', duration, 1)
            
            return user_stats
            
        except Exception as e:
            logger.error(f"User stats query optimization failed: {e}")
            return None
    
    def optimize_question_selection_query(
        self,
        categories: List[Category] = None,
        difficulty: Difficulty = None,
        limit: int = 10,
        user_id: Optional[int] = None
    ) -> List[Question]:
        """Optimized question selection with smart filtering"""
        start_time = time.time()
        
        try:
            # Base query with strategic filtering
            query = db.session.query(Question).filter(Question.is_active == True)
            
            # Category filtering
            if categories:
                query = query.filter(Question.category.in_(categories))
            
            # Difficulty filtering
            if difficulty:
                query = query.filter(Question.difficulty == difficulty)
            
            # Avoid recently answered questions for user
            if user_id:
                # Subquery for recently answered questions
                recent_answers = db.session.query(Answer.question_id).filter(
                    Answer.user_id == user_id,
                    Answer.answered_at >= datetime.now(timezone.utc) - timedelta(hours=24)
                ).subquery()
                
                query = query.filter(~Question.id.in_(recent_answers))
            
            # Optimize ordering for variety and difficulty
            query = query.order_by(
                Question.times_asked.asc(),  # Prefer less asked questions
                func.random()  # Add randomness
            ).limit(limit * 2)  # Get more for filtering
            
            # Execute and apply intelligent selection
            candidate_questions = query.all()
            
            # Smart selection algorithm
            selected_questions = self._smart_question_selection(
                candidate_questions, limit, user_id
            )
            
            # Record performance
            duration = time.time() - start_time
            self._record_query_performance('optimized_question_selection', duration, len(selected_questions))
            
            return selected_questions
            
        except Exception as e:
            logger.error(f"Question selection optimization failed: {e}")
            return []
    
    def optimize_session_analysis_query(self, session_id: int) -> Optional[Dict]:
        """Optimized session analysis with comprehensive metrics"""
        start_time = time.time()
        
        try:
            # Single query for session analysis
            session_query = db.session.query(
                GameSession.id,
                GameSession.user_id,
                GameSession.started_at,
                GameSession.completed_at,
                GameSession.total_questions,
                GameSession.correct_answers,
                GameSession.incorrect_answers,
                GameSession.current_streak,
                GameSession.best_streak,
                GameSession.total_score,
                User.username
            ).join(User, GameSession.user_id == User.id).filter(
                GameSession.id == session_id
            ).first()
            
            if not session_query:
                return None
            
            # Answer analysis query
            answer_stats = db.session.query(
                func.count(Answer.id).label('total_answers'),
                func.avg(Answer.time_taken).label('avg_time'),
                func.sum(Answer.points_earned).label('total_points'),
                func.avg(Answer.points_earned).label('avg_points')
            ).filter(Answer.game_session_id == session_id).first()
            
            # Category performance query
            category_performance = db.session.query(
                Question.category,
                func.count(Answer.id).label('questions_answered'),
                func.sum(func.case([(Answer.is_correct == True, 1)], else_=0)).label('correct_answers'),
                func.avg(Answer.time_taken).label('avg_time')
            ).join(Answer, Question.id == Answer.question_id).filter(
                Answer.game_session_id == session_id
            ).group_by(Question.category).all()
            
            # Compile comprehensive analysis
            session_analysis = {
                'session_id': session_query.id,
                'user_id': session_query.user_id,
                'username': session_query.username,
                'started_at': session_query.started_at.isoformat(),
                'completed_at': session_query.completed_at.isoformat() if session_query.completed_at else None,
                'duration_minutes': self._calculate_session_duration(session_query.started_at, session_query.completed_at),
                'total_questions': session_query.total_questions,
                'correct_answers': session_query.correct_answers,
                'incorrect_answers': session_query.incorrect_answers,
                'accuracy': round((session_query.correct_answers / max(session_query.total_questions, 1)) * 100, 1),
                'current_streak': session_query.current_streak,
                'best_streak': session_query.best_streak,
                'total_score': session_query.total_score,
                'avg_time_per_question': round(float(answer_stats.avg_time or 0), 2),
                'avg_points_per_question': round(float(answer_stats.avg_points or 0), 1),
                'category_performance': [
                    {
                        'category': cp.category.value,
                        'questions_answered': cp.questions_answered,
                        'correct_answers': cp.correct_answers,
                        'accuracy': round((cp.correct_answers / cp.questions_answered) * 100, 1),
                        'avg_time': round(float(cp.avg_time or 0), 2)
                    }
                    for cp in category_performance
                ]
            }
            
            # Record performance
            duration = time.time() - start_time
            self._record_query_performance('optimized_session_analysis', duration, 1)
            
            return session_analysis
            
        except Exception as e:
            logger.error(f"Session analysis optimization failed: {e}")
            return None
    
    def _smart_question_selection(self, candidates: List[Question], limit: int, user_id: Optional[int]) -> List[Question]:
        """Intelligent question selection algorithm"""
        if len(candidates) <= limit:
            return candidates
        
        # Score questions based on multiple factors
        scored_questions = []
        for question in candidates:
            score = 0
            
            # Prefer less frequently asked questions
            if question.times_asked < 5:
                score += 3
            elif question.times_asked < 10:
                score += 2
            else:
                score += 1
            
            # Prefer questions with good difficulty balance
            if question.times_asked > 0:
                success_rate = question.times_correct / question.times_asked
                if 0.4 <= success_rate <= 0.7:  # Sweet spot
                    score += 2
                elif 0.3 <= success_rate <= 0.8:
                    score += 1
            
            # Add some randomness
            import random
            score += random.uniform(0, 1)
            
            scored_questions.append((question, score))
        
        # Sort by score and take top questions
        scored_questions.sort(key=lambda x: x[1], reverse=True)
        return [q[0] for q in scored_questions[:limit]]
    
    def _calculate_session_duration(self, started_at: datetime, completed_at: Optional[datetime]) -> float:
        """Calculate session duration in minutes"""
        if not completed_at:
            return 0.0
        return (completed_at - started_at).total_seconds() / 60.0
    
    def _record_query_performance(self, query_type: str, duration: float, result_count: int):
        """Record query performance metrics"""
        if query_type not in self.query_stats:
            self.query_stats[query_type] = {
                'total_executions': 0,
                'total_duration': 0.0,
                'avg_duration': 0.0,
                'min_duration': float('inf'),
                'max_duration': 0.0,
                'total_results': 0
            }
        
        stats = self.query_stats[query_type]
        stats['total_executions'] += 1
        stats['total_duration'] += duration
        stats['avg_duration'] = stats['total_duration'] / stats['total_executions']
        stats['min_duration'] = min(stats['min_duration'], duration)
        stats['max_duration'] = max(stats['max_duration'], duration)
        stats['total_results'] += result_count
        
        # Log slow queries
        if duration > 1.0:  # More than 1 second
            logger.warning(f"Slow query detected: {query_type} took {duration:.2f}s")
    
    def get_query_performance_stats(self) -> Dict:
        """Get comprehensive query performance statistics"""
        return {
            'query_stats': self.query_stats,
            'total_queries': sum(stats['total_executions'] for stats in self.query_stats.values()),
            'total_duration': sum(stats['total_duration'] for stats in self.query_stats.values()),
            'slow_queries': [
                {
                    'query_type': qtype,
                    'max_duration': stats['max_duration'],
                    'avg_duration': stats['avg_duration']
                }
                for qtype, stats in self.query_stats.items()
                if stats['max_duration'] > 1.0
            ]
        }

# Global optimizer instance
query_optimizer = QueryOptimizer()

def create_query_optimization_routes(app):
    """Create routes for query optimization monitoring"""
    
    @app.route('/admin/query-performance')
    @performance_monitor.track_performance
    def query_performance_dashboard():
        """Query performance monitoring dashboard"""
        try:
            stats = query_optimizer.get_query_performance_stats()
            return {
                'status': 'success',
                'query_performance': stats,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Query performance dashboard error: {e}")
            return {'status': 'error', 'message': str(e)}, 500
    
    @app.route('/admin/create-indexes', methods=['POST'])
    @performance_monitor.track_performance
    def create_performance_indexes():
        """Create performance indexes endpoint"""
        try:
            success = query_optimizer.create_performance_indexes()
            return {
                'status': 'success' if success else 'error',
                'message': 'Performance indexes created' if success else 'Failed to create indexes',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Index creation error: {e}")
            return {'status': 'error', 'message': str(e)}, 500

def initialize_query_optimization(app):
    """Initialize query optimization system"""
    try:
        # Create routes
        create_query_optimization_routes(app)
        
        # Create indexes
        query_optimizer.create_performance_indexes()
        
        logger.info("Query optimization system initialized successfully")
        
    except Exception as e:
        logger.error(f"Query optimization initialization failed: {e}")

# Query optimization event handlers
@event.listens_for(db.engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query execution start time"""
    context._query_start_time = time.time()

@event.listens_for(db.engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query execution duration"""
    total = time.time() - context._query_start_time
    
    # Log slow queries
    if total > 0.5:  # Queries taking more than 500ms
        logger.warning(f"Slow query executed in {total:.2f}s: {statement[:200]}...")