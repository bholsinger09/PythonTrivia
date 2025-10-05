"""
Simple in-memory caching layer for Python Trivia Game
Provides performance improvements for frequently accessed data
"""
import time
from typing import Any, Dict, Optional, List
from functools import wraps
import json
import hashlib

class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict] = {}
        self.default_ttl = default_ttl
    
    def _is_expired(self, cache_entry: Dict) -> bool:
        """Check if cache entry is expired"""
        return time.time() > cache_entry['expires_at']
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            if not self._is_expired(entry):
                entry['hits'] += 1
                return entry['value']
            else:
                # Remove expired entry
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL"""
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        self.cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time(),
            'hits': 0
        }
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_entries = len(self.cache)
        total_hits = sum(entry['hits'] for entry in self.cache.values())
        
        return {
            'total_entries': total_entries,
            'total_hits': total_hits,
            'cache_keys': list(self.cache.keys())
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)

# Global cache instances
question_cache = SimpleCache(default_ttl=600)  # 10 minutes for questions
leaderboard_cache = SimpleCache(default_ttl=60)  # 1 minute for leaderboards
user_cache = SimpleCache(default_ttl=300)  # 5 minutes for user data

def cache_key_from_args(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = f"{args}_{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()

def cached_questions(category=None, difficulty=None, limit=20):
    """Decorator for caching question queries"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"questions_{category}_{difficulty}_{limit}"
            
            # Try to get from cache
            cached_result = question_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            question_cache.set(cache_key, result, ttl=600)  # 10 minutes
            
            return result
        return wrapper
    return decorator

def cached_leaderboard(category=None, limit=10):
    """Decorator for caching leaderboard queries"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"leaderboard_{category}_{limit}"
            
            cached_result = leaderboard_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            leaderboard_cache.set(cache_key, result, ttl=60)  # 1 minute
            
            return result
        return wrapper
    return decorator

def invalidate_leaderboard_cache():
    """Invalidate all leaderboard cache entries"""
    leaderboard_cache.clear()

def invalidate_question_cache():
    """Invalidate all question cache entries"""
    question_cache.clear()

def get_cache_stats():
    """Get overall cache statistics"""
    return {
        'questions': question_cache.get_stats(),
        'leaderboard': leaderboard_cache.get_stats(),
        'users': user_cache.get_stats()
    }