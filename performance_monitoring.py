"""
Performance Monitoring and Metrics System
Provides comprehensive performance tracking and analytics for the trivia application
"""
import time
import functools
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from flask import request, g
import threading
import json

class PerformanceMetrics:
    """Centralized performance metrics collection and analysis"""
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Request timing data
        self.request_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.slow_requests: List[Dict] = []
        
        # Cache performance
        self.cache_hits: Dict[str, int] = defaultdict(int)
        self.cache_misses: Dict[str, int] = defaultdict(int)
        self.cache_response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Database performance
        self.db_query_times: deque = deque(maxlen=1000)
        self.slow_queries: List[Dict] = []
        
        # Rate limiting data
        self.rate_limit_hits: Dict[str, int] = defaultdict(int)
        self.rate_limit_blocks: Dict[str, int] = defaultdict(int)
        
        # Error tracking
        self.error_counts: Dict[str, int] = defaultdict(int)
        
        # Performance thresholds
        self.slow_request_threshold = 1.0  # seconds
        self.slow_query_threshold = 0.5    # seconds
        
    def record_request_time(self, endpoint: str, duration: float, status_code: int = 200):
        """Record request timing data"""
        with self._lock:
            self.request_times[endpoint].append({
                'duration': duration,
                'timestamp': time.time(),
                'status_code': status_code
            })
            
            # Track slow requests
            if duration > self.slow_request_threshold:
                self.slow_requests.append({
                    'endpoint': endpoint,
                    'duration': duration,
                    'timestamp': datetime.utcnow().isoformat(),
                    'status_code': status_code
                })
                
                # Keep only last 100 slow requests
                if len(self.slow_requests) > 100:
                    self.slow_requests.pop(0)
    
    def record_cache_hit(self, cache_type: str, key: str, response_time: float = 0):
        """Record cache hit"""
        with self._lock:
            self.cache_hits[cache_type] += 1
            if response_time > 0:
                self.cache_response_times[cache_type].append(response_time)
    
    def record_cache_miss(self, cache_type: str, key: str):
        """Record cache miss"""
        with self._lock:
            self.cache_misses[cache_type] += 1
    
    def record_db_query_time(self, duration: float, query_type: str = 'unknown'):
        """Record database query timing"""
        with self._lock:
            self.db_query_times.append({
                'duration': duration,
                'timestamp': time.time(),
                'type': query_type
            })
            
            # Track slow queries
            if duration > self.slow_query_threshold:
                self.slow_queries.append({
                    'duration': duration,
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': query_type
                })
                
                # Keep only last 50 slow queries
                if len(self.slow_queries) > 50:
                    self.slow_queries.pop(0)
    
    def record_rate_limit_event(self, endpoint: str, event_type: str):
        """Record rate limiting events"""
        with self._lock:
            if event_type == 'hit':
                self.rate_limit_hits[endpoint] += 1
            elif event_type == 'block':
                self.rate_limit_blocks[endpoint] += 1
    
    def record_error(self, error_type: str, endpoint: str = ''):
        """Record application errors"""
        with self._lock:
            key = f"{error_type}:{endpoint}" if endpoint else error_type
            self.error_counts[key] += 1
    
    def get_cache_performance(self) -> Dict:
        """Get cache performance statistics"""
        with self._lock:
            cache_stats = {}
            
            for cache_type in set(list(self.cache_hits.keys()) + list(self.cache_misses.keys())):
                hits = self.cache_hits[cache_type]
                misses = self.cache_misses[cache_type]
                total = hits + misses
                
                hit_ratio = (hits / total * 100) if total > 0 else 0
                
                # Calculate average response time
                avg_response_time = 0
                if cache_type in self.cache_response_times:
                    times = list(self.cache_response_times[cache_type])
                    avg_response_time = sum(times) / len(times) if times else 0
                
                cache_stats[cache_type] = {
                    'hits': hits,
                    'misses': misses,
                    'total_requests': total,
                    'hit_ratio_percent': round(hit_ratio, 2),
                    'avg_response_time_ms': round(avg_response_time * 1000, 2)
                }
            
            return cache_stats
    
    def get_request_performance(self, minutes: int = 15) -> Dict:
        """Get request performance for the last N minutes"""
        cutoff_time = time.time() - (minutes * 60)
        
        with self._lock:
            stats = {}
            
            for endpoint, times in self.request_times.items():
                recent_times = [
                    t for t in times 
                    if t['timestamp'] > cutoff_time
                ]
                
                if not recent_times:
                    continue
                
                durations = [t['duration'] for t in recent_times]
                status_codes = [t['status_code'] for t in recent_times]
                
                stats[endpoint] = {
                    'request_count': len(recent_times),
                    'avg_response_time': round(sum(durations) / len(durations), 3),
                    'min_response_time': round(min(durations), 3),
                    'max_response_time': round(max(durations), 3),
                    'p95_response_time': round(self._percentile(durations, 95), 3),
                    'error_rate_percent': round(
                        len([s for s in status_codes if s >= 400]) / len(status_codes) * 100, 2
                    ),
                    'requests_per_minute': round(len(recent_times) / minutes, 1)
                }
            
            return stats
    
    def get_database_performance(self) -> Dict:
        """Get database performance statistics"""
        with self._lock:
            if not self.db_query_times:
                return {'message': 'No database metrics collected yet'}
            
            durations = [q['duration'] for q in self.db_query_times]
            
            return {
                'total_queries': len(self.db_query_times),
                'avg_query_time': round(sum(durations) / len(durations), 4),
                'min_query_time': round(min(durations), 4),
                'max_query_time': round(max(durations), 4),
                'p95_query_time': round(self._percentile(durations, 95), 4),
                'slow_queries_count': len(self.slow_queries),
                'recent_slow_queries': self.slow_queries[-5:] if self.slow_queries else []
            }
    
    def get_rate_limit_stats(self) -> Dict:
        """Get rate limiting statistics"""
        with self._lock:
            stats = {}
            
            all_endpoints = set(list(self.rate_limit_hits.keys()) + list(self.rate_limit_blocks.keys()))
            
            for endpoint in all_endpoints:
                hits = self.rate_limit_hits[endpoint]
                blocks = self.rate_limit_blocks[endpoint]
                total = hits + blocks
                
                block_rate = (blocks / total * 100) if total > 0 else 0
                
                stats[endpoint] = {
                    'total_requests': hits,
                    'blocked_requests': blocks,
                    'block_rate_percent': round(block_rate, 2)
                }
            
            return stats
    
    def get_error_summary(self) -> Dict:
        """Get error statistics"""
        with self._lock:
            return dict(self.error_counts)
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        return {
            'cache_performance': self.get_cache_performance(),
            'request_performance': self.get_request_performance(),
            'database_performance': self.get_database_performance(),
            'rate_limit_stats': self.get_rate_limit_stats(),
            'error_summary': self.get_error_summary(),
            'slow_requests': self.slow_requests[-10:] if self.slow_requests else [],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile of a dataset"""
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        index = min(index, len(sorted_data) - 1)
        return sorted_data[index]

# Global metrics instance
performance_metrics = PerformanceMetrics()

def track_request_performance(f: Callable) -> Callable:
    """Decorator to track request performance"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            status_code = 200
            
            # Try to extract status code from response
            if hasattr(result, 'status_code'):
                status_code = result.status_code
            elif isinstance(result, tuple) and len(result) > 1:
                status_code = result[1]
            
            return result
            
        except Exception as e:
            status_code = 500
            performance_metrics.record_error('exception', request.endpoint)
            raise
            
        finally:
            duration = time.time() - start_time
            performance_metrics.record_request_time(
                request.endpoint or 'unknown',
                duration,
                status_code
            )
    
    return decorated_function

def track_cache_performance(cache_type: str):
    """Decorator to track cache performance"""
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # Check if this is a cache hit or miss
            # This is a simplified approach - in reality, you'd integrate with your cache
            cache_key = f"{f.__name__}_{hash(str(args) + str(kwargs))}"
            
            result = f(*args, **kwargs)
            
            response_time = time.time() - start_time
            
            # For now, assume cache miss since we're calling the function
            performance_metrics.record_cache_miss(cache_type, cache_key)
            
            return result
        
        return decorated_function
    return decorator

def track_database_performance(query_type: str = 'unknown'):
    """Decorator to track database query performance"""
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                performance_metrics.record_db_query_time(duration, query_type)
        
        return decorated_function
    return decorator

def create_performance_monitoring_routes(app):
    """Add performance monitoring routes to Flask app"""
    
    @app.route('/api/admin/performance-metrics')
    def get_performance_metrics():
        """Get comprehensive performance metrics (admin only)"""
        from flask import jsonify
        
        if not app.debug:
            return jsonify({'error': 'Access denied'}), 403
        
        metrics = performance_metrics.get_performance_summary()
        return jsonify(metrics)
    
    @app.route('/api/admin/cache-metrics')
    def get_cache_metrics():
        """Get detailed cache performance metrics"""
        from flask import jsonify
        
        if not app.debug:
            return jsonify({'error': 'Access denied'}), 403
        
        cache_stats = performance_metrics.get_cache_performance()
        return jsonify(cache_stats)
    
    @app.route('/api/health/performance')
    def performance_health():
        """Public performance health check"""
        from flask import jsonify
        
        # Get basic performance indicators
        request_stats = performance_metrics.get_request_performance(minutes=5)
        db_stats = performance_metrics.get_database_performance()
        
        # Simple health assessment
        health_status = 'healthy'
        issues = []
        
        # Check if any endpoints have high response times
        for endpoint, stats in request_stats.items():
            if stats['avg_response_time'] > 2.0:
                health_status = 'degraded'
                issues.append(f"High response time on {endpoint}: {stats['avg_response_time']}s")
        
        # Check database performance
        if isinstance(db_stats, dict) and 'avg_query_time' in db_stats:
            if db_stats['avg_query_time'] > 0.1:
                health_status = 'degraded'
                issues.append(f"High database query time: {db_stats['avg_query_time']}s")
        
        return jsonify({
            'status': health_status,
            'issues': issues,
            'timestamp': datetime.utcnow().isoformat()
        })