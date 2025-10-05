"""
Database Connection Pool Monitoring and Management
Provides utilities to monitor and manage SQLAlchemy connection pools
"""
from flask import current_app
from models import db
from typing import Dict, Optional, List
import time
from datetime import datetime

class ConnectionPoolMonitor:
    """Monitor SQLAlchemy connection pool health and performance"""
    
    @staticmethod
    def get_pool_status() -> Dict:
        """Get current connection pool status"""
        try:
            engine = db.engine
            pool = engine.pool
            
            return {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid(),
                'timestamp': datetime.utcnow().isoformat(),
                'pool_class': str(type(pool).__name__)
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def test_connection() -> Dict:
        """Test database connection and measure response time"""
        start_time = time.time()
        
        try:
            # Simple connection test
            result = db.session.execute('SELECT 1').scalar()
            response_time = (time.time() - start_time) * 1000  # ms
            
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                'status': 'error',
                'error': str(e),
                'response_time_ms': round(response_time, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def get_detailed_stats() -> Dict:
        """Get detailed connection pool statistics"""
        try:
            engine = db.engine
            pool = engine.pool
            
            # Get pool status
            pool_status = ConnectionPoolMonitor.get_pool_status()
            
            # Test connection
            connection_test = ConnectionPoolMonitor.test_connection()
            
            # Calculate utilization
            total_capacity = pool.size() + pool.overflow()
            current_usage = pool.checkedout()
            utilization = (current_usage / total_capacity * 100) if total_capacity > 0 else 0
            
            return {
                'pool_health': {
                    'status': 'healthy' if connection_test['status'] == 'healthy' else 'degraded',
                    'utilization_percent': round(utilization, 1),
                    'available_connections': pool.checkedin(),
                    'active_connections': current_usage,
                    'total_capacity': total_capacity
                },
                'pool_details': pool_status,
                'connection_test': connection_test,
                'recommendations': ConnectionPoolMonitor._get_recommendations(pool_status, utilization)
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def _get_recommendations(pool_status: Dict, utilization: float) -> List[str]:
        """Get recommendations based on pool status"""
        recommendations = []
        
        if utilization > 80:
            recommendations.append("High connection utilization - consider increasing pool_size")
        
        if pool_status.get('overflow', 0) > 0:
            recommendations.append("Using overflow connections - monitor for connection leaks")
        
        if pool_status.get('invalid', 0) > 0:
            recommendations.append("Invalid connections detected - check network stability")
        
        if not recommendations:
            recommendations.append("Connection pool operating normally")
        
        return recommendations

def create_pool_monitoring_routes(app):
    """Add connection pool monitoring routes to Flask app"""
    
    @app.route('/api/admin/pool-status')
    def pool_status():
        """Get connection pool status (admin only)"""
        from flask import jsonify
        
        # Simple admin check - in production, add proper authentication
        if not app.debug:
            return jsonify({'error': 'Access denied'}), 403
        
        status = ConnectionPoolMonitor.get_detailed_stats()
        return jsonify(status)
    
    @app.route('/api/health/database')
    def database_health():
        """Public database health check endpoint"""
        from flask import jsonify
        
        test_result = ConnectionPoolMonitor.test_connection()
        
        if test_result['status'] == 'healthy':
            return jsonify({
                'status': 'healthy',
                'response_time_ms': test_result['response_time_ms']
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'error': 'Database connection failed'
            }), 503

# Usage in app.py:
# from database_connection_monitor import create_pool_monitoring_routes
# create_pool_monitoring_routes(app)