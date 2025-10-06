"""
API Rate Limiting for Python Trivia Game
Simple in-memory rate limiting with sliding window algorithm
"""
import time
from collections import defaultdict, deque
from typing import Dict, Tuple, Optional
from functools import wraps
from flask import request, jsonify, g

# Import performance monitoring for rate limit analytics
try:
    from performance_monitoring import performance_metrics
    HAS_MONITORING = True
except ImportError:
    HAS_MONITORING = False

class RateLimiter:
    """Simple in-memory rate limiter using sliding window"""
    
    def __init__(self):
        # Store: {key: deque of timestamps}
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.last_cleanup = time.time()
    
    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """
        Check if request is allowed
        
        Args:
            key: Unique identifier (IP + endpoint)
            limit: Max requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, requests_remaining)
        """
        now = time.time()
        
        # Clean up old entries periodically
        if now - self.last_cleanup > 60:  # Cleanup every minute
            self._cleanup_old_entries(now - 3600)  # Remove entries older than 1 hour
            self.last_cleanup = now
        
        # Get request history for this key
        request_times = self.requests[key]
        
        # Remove requests outside the window
        while request_times and request_times[0] <= now - window:
            request_times.popleft()
        
        # Check if limit exceeded
        current_requests = len(request_times)
        
        if current_requests >= limit:
            # Record rate limit block
            if HAS_MONITORING:
                endpoint = key.split(':')[-1] if ':' in key else 'unknown'
                performance_metrics.record_rate_limit_event(endpoint, 'block')
            
            return False, 0
        
        # Add current request
        request_times.append(now)
        
        # Record successful request
        if HAS_MONITORING:
            endpoint = key.split(':')[-1] if ':' in key else 'unknown'
            performance_metrics.record_rate_limit_event(endpoint, 'hit')
        
        return True, limit - current_requests - 1
    
    def _cleanup_old_entries(self, cutoff_time: float):
        """Remove old entries to prevent memory leaks"""
        keys_to_remove = []
        
        for key, request_times in self.requests.items():
            # Remove old requests
            while request_times and request_times[0] <= cutoff_time:
                request_times.popleft()
            
            # Remove empty entries
            if not request_times:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.requests[key]
    
    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        active_keys = len(self.requests)
        total_requests = sum(len(times) for times in self.requests.values())
        
        return {
            'active_keys': active_keys,
            'total_tracked_requests': total_requests,
            'memory_usage_estimate': f"{active_keys * 50}B"  # Rough estimate
        }

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(max_requests: int = 60, window: int = 60, per: str = 'ip'):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum requests allowed
        window: Time window in seconds
        per: Rate limit per 'ip' or 'user'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate rate limit key
            if per == 'ip':
                key = f"ip:{request.remote_addr}:{request.endpoint}"
            elif per == 'user':
                user_id = getattr(g, 'user_id', None) or 'anonymous'
                key = f"user:{user_id}:{request.endpoint}"
            else:
                key = f"global:{request.endpoint}"
            
            # Check rate limit
            allowed, remaining = rate_limiter.is_allowed(key, max_requests, window)
            
            if not allowed:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Limit: {max_requests} per {window} seconds',
                    'retry_after': window
                }), 429
            
            # Add rate limit headers
            response = f(*args, **kwargs)
            
            # Add headers if response is a Flask response
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(max_requests)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Window'] = str(window)
            
            return response
        
        return decorated_function
    return decorator

# Preset decorators for common scenarios
def api_rate_limit(f):
    """Standard API rate limit: 100 requests per minute"""
    return rate_limit(max_requests=100, window=60, per='ip')(f)

def strict_rate_limit(f):
    """Strict rate limit for sensitive endpoints: 10 requests per minute"""
    return rate_limit(max_requests=10, window=60, per='ip')(f)

def user_rate_limit(f):
    """User-based rate limit: 200 requests per minute"""
    return rate_limit(max_requests=200, window=60, per='user')(f)

def game_rate_limit(f):
    """Game action rate limit: 30 requests per minute"""
    return rate_limit(max_requests=30, window=60, per='ip')(f)

# Rate limiting status endpoint
def create_rate_limit_routes(app):
    """Add rate limiting status routes"""
    
    @app.route('/api/admin/rate-limit-stats')
    @strict_rate_limit
    def rate_limit_stats():
        """Get rate limiting statistics (admin only)"""
        if not app.debug:
            return jsonify({'error': 'Access denied'}), 403
        
        stats = rate_limiter.get_stats()
        return jsonify(stats)
    
    @app.route('/api/health/rate-limit')
    def rate_limit_health():
        """Check rate limiting system health"""
        try:
            # Test the rate limiter
            test_key = f"health_check:{time.time()}"
            allowed, remaining = rate_limiter.is_allowed(test_key, 1, 60)
            
            return jsonify({
                'status': 'healthy',
                'rate_limiter_working': allowed
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500