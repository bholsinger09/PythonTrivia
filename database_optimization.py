"""
Advanced Database Connection Pool Optimization for PostgreSQL
Provides optimized connection pool configurations and monitoring
"""
import os
import time
from typing import Dict, Any, Optional
from sqlalchemy import event, pool
from sqlalchemy.engine import Engine
from models import db
from datetime import datetime

class DatabaseConnectionOptimizer:
    """Advanced PostgreSQL connection pool optimization"""
    
    @staticmethod
    def get_optimized_production_config() -> Dict[str, Any]:
        """Get optimized production database configuration"""
        
        # Determine optimal pool size based on deployment environment
        # Render typically gives 1 vCPU, so we optimize for that
        cpu_count = int(os.environ.get('WEB_CONCURRENCY', 1))
        
        # Calculate optimal pool sizes
        # Formula: (2 * cpu_count) + effective_spindle_count
        # For cloud deployments, effective_spindle_count ≈ 1
        base_pool_size = max(5, (2 * cpu_count) + 1)
        max_overflow = base_pool_size * 2
        
        return {
            # Core pool settings
            'pool_size': base_pool_size,
            'max_overflow': max_overflow,
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
                'keepalives_idle': '600',
                'keepalives_interval': '30', 
                'keepalives_count': '3',
                'tcp_user_timeout': '30000',  # 30 seconds
                
                # Performance settings
                'statement_timeout': '30000',  # 30 second statement timeout
                'idle_in_transaction_session_timeout': '60000',  # 1 minute
                'options': '-c default_transaction_isolation=read_committed'
            }
        }
    
    @staticmethod
    def get_optimized_development_config() -> Dict[str, Any]:
        """Get optimized development database configuration"""
        
        # For development, we use smaller pools and faster recycling
        return {
            'pool_size': 3,
            'max_overflow': 5,
            'pool_timeout': 20,
            'pool_recycle': 300,  # 5 minutes for development
            'pool_pre_ping': True,
            'echo': False,
            
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'PythonTriviaApp-Dev',
                'check_same_thread': False,  # For SQLite compatibility
                'timeout': 20
            }
        }
    
    @staticmethod
    def setup_connection_monitoring(app):
        """Set up advanced connection pool monitoring"""
        
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Optimize SQLite connections for development"""
            if 'sqlite' in str(dbapi_connection):
                cursor = dbapi_connection.cursor()
                # Performance optimizations for SQLite
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
        
        @event.listens_for(Engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Track connection checkouts"""
            connection_record.info['checkout_time'] = time.time()
            
            # Record checkout in performance metrics
            try:
                from performance_monitoring import performance_metrics
                performance_metrics.record_db_query_time(0, 'connection_checkout')
            except ImportError:
                pass
        
        @event.listens_for(Engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Track connection checkins and usage time"""
            if 'checkout_time' in connection_record.info:
                usage_time = time.time() - connection_record.info['checkout_time']
                
                # Log long-running connections
                if usage_time > 30:  # 30 seconds
                    app.logger.warning(f"Long-running connection: {usage_time:.2f}s")
                
                # Record usage in performance metrics
                try:
                    from performance_monitoring import performance_metrics
                    performance_metrics.record_db_query_time(usage_time, 'connection_usage')
                except ImportError:
                    pass
        
        @event.listens_for(pool.Pool, "connect")
        def set_postgresql_search_path(dbapi_connection, connection_record):
            """Optimize PostgreSQL connections"""
            if hasattr(dbapi_connection, 'autocommit'):
                # This is a PostgreSQL connection
                with dbapi_connection.cursor() as cursor:
                    # Set optimizations
                    cursor.execute("SET application_name = 'PythonTriviaApp'")
                    cursor.execute("SET statement_timeout = '30s'")
                    cursor.execute("SET idle_in_transaction_session_timeout = '60s'")

class ConnectionPoolHealthChecker:
    """Monitor connection pool health and provide recommendations"""
    
    def __init__(self):
        self.connection_errors = 0
        self.last_health_check = None
        self.health_status = 'unknown'
    
    def check_pool_health(self) -> Dict[str, Any]:
        """Comprehensive connection pool health check"""
        try:
            from database_connection_monitor import ConnectionPoolMonitor
            
            # Get current pool status
            pool_status = ConnectionPoolMonitor.get_detailed_stats()
            
            # Test connection performance
            start_time = time.time()
            test_result = ConnectionPoolMonitor.test_connection()
            response_time = time.time() - start_time
            
            # Analyze health
            health_issues = []
            health_score = 100
            
            # Check utilization
            if 'pool_health' in pool_status:
                utilization = pool_status['pool_health'].get('utilization_percent', 0)
                if utilization > 90:
                    health_issues.append('Very high pool utilization')
                    health_score -= 30
                elif utilization > 75:
                    health_issues.append('High pool utilization')
                    health_score -= 15
            
            # Check response time
            if response_time > 1.0:
                health_issues.append('Slow database response')
                health_score -= 25
            elif response_time > 0.5:
                health_issues.append('Moderate database latency')
                health_score -= 10
            
            # Check for overflow usage
            if pool_status.get('pool_details', {}).get('overflow', 0) > 0:
                health_issues.append('Using overflow connections')
                health_score -= 20
            
            # Determine overall health
            if health_score >= 90:
                self.health_status = 'excellent'
            elif health_score >= 75:
                self.health_status = 'good'
            elif health_score >= 50:
                self.health_status = 'fair'
            else:
                self.health_status = 'poor'
            
            self.last_health_check = datetime.utcnow()
            
            return {
                'health_status': self.health_status,
                'health_score': health_score,
                'response_time': round(response_time, 3),
                'issues': health_issues,
                'recommendations': self._get_recommendations(pool_status, response_time),
                'last_check': self.last_health_check.isoformat(),
                'pool_details': pool_status
            }
            
        except Exception as e:
            self.connection_errors += 1
            return {
                'health_status': 'error',
                'error': str(e),
                'connection_errors': self.connection_errors
            }
    
    def _get_recommendations(self, pool_status: Dict, response_time: float) -> list:
        """Generate optimization recommendations"""
        recommendations = []
        
        if 'pool_health' in pool_status:
            utilization = pool_status['pool_health'].get('utilization_percent', 0)
            
            if utilization > 90:
                recommendations.append("Increase pool_size and max_overflow")
                recommendations.append("Consider connection pooling at application level")
            elif utilization > 75:
                recommendations.append("Monitor for potential pool size increase")
            
        if response_time > 1.0:
            recommendations.append("Check database performance and query optimization")
            recommendations.append("Consider connection keep-alive settings")
        
        overflow = pool_status.get('pool_details', {}).get('overflow', 0)
        if overflow > 0:
            recommendations.append("Monitor for connection leaks")
            recommendations.append("Consider increasing base pool_size")
        
        if not recommendations:
            recommendations.append("Connection pool operating optimally")
        
        return recommendations

def create_optimized_database_config(app):
    """Apply optimized database configuration to Flask app"""
    
    env = os.getenv('FLASK_ENV', 'development')
    optimizer = DatabaseConnectionOptimizer()
    
    if env == 'production':
        config = optimizer.get_optimized_production_config()
        app.logger.info("Applied optimized production database configuration")
    else:
        config = optimizer.get_optimized_development_config()
        app.logger.info("Applied optimized development database configuration")
    
    # Update SQLAlchemy engine options
    if hasattr(app.config, 'SQLALCHEMY_ENGINE_OPTIONS'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'].update(config)
    else:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = config
    
    # Set up monitoring
    optimizer.setup_connection_monitoring(app)
    
    return config

# Global health checker instance
pool_health_checker = ConnectionPoolHealthChecker()

def create_database_optimization_routes(app):
    """Add database optimization monitoring routes"""
    
    @app.route('/api/admin/database-optimization')
    def database_optimization_status():
        """Get database optimization status and recommendations"""
        from flask import jsonify
        
        if not app.debug:
            return jsonify({'error': 'Access denied'}), 403
        
        health_check = pool_health_checker.check_pool_health()
        return jsonify(health_check)
    
    @app.route('/api/admin/connection-pool-tune')
    def connection_pool_tuning():
        """Get connection pool tuning recommendations"""
        from flask import jsonify
        
        if not app.debug:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get current configuration
        current_config = app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
        
        # Analyze and recommend optimizations
        optimizer = DatabaseConnectionOptimizer()
        
        if os.getenv('FLASK_ENV') == 'production':
            recommended_config = optimizer.get_optimized_production_config()
        else:
            recommended_config = optimizer.get_optimized_development_config()
        
        # Compare configurations
        differences = {}
        for key, recommended_value in recommended_config.items():
            current_value = current_config.get(key)
            if current_value != recommended_value:
                differences[key] = {
                    'current': current_value,
                    'recommended': recommended_value
                }
        
        return jsonify({
            'current_config': current_config,
            'recommended_config': recommended_config,
            'differences': differences,
            'environment': os.getenv('FLASK_ENV', 'development')
        })