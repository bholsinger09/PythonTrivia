"""
Redis Cache Configuration and Setup

This module provides Redis caching integration for the Python Trivia app:
- Cache configuration with fallback to in-memory caching
- Cache warming strategies
- Cache invalidation patterns
- Performance monitoring
"""

import redis
import json
import logging
from typing import Optional, Dict, List, Any, Union
from functools import wraps
import os
import time
from datetime import datetime, timedelta

class CacheConfig:
    """Redis cache configuration"""
    
    # Redis connection settings
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_URL = os.getenv('REDIS_URL', None)
    
    # Cache settings
    DEFAULT_TTL = 300  # 5 minutes
    LEADERBOARD_TTL = 600  # 10 minutes  
    QUESTIONS_TTL = 1800  # 30 minutes
    USER_STATS_TTL = 300  # 5 minutes
    
    # Performance settings
    CONNECTION_POOL_SIZE = 20
    SOCKET_TIMEOUT = 5
    SOCKET_CONNECT_TIMEOUT = 5
    
    # Feature flags
    ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'
    CACHE_DEBUG = os.getenv('CACHE_DEBUG', 'false').lower() == 'true'

class EnhancedCacheManager:
    """Enhanced cache manager with Redis and fallback support"""
    
    def __init__(self, redis_client=None, enable_fallback=True):
        self.redis_client = redis_client
        self.enable_fallback = enable_fallback
        self.fallback_cache = {}  # In-memory fallback
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        
        if not self.redis_client:
            self.redis_client = self._create_redis_client()
    
    def _create_redis_client(self) -> Optional[redis.Redis]:
        """Create Redis client with proper configuration"""
        try:
            if CacheConfig.REDIS_URL:
                # Use Redis URL (for production deployments)
                client = redis.from_url(
                    CacheConfig.REDIS_URL,
                    socket_timeout=CacheConfig.SOCKET_TIMEOUT,
                    socket_connect_timeout=CacheConfig.SOCKET_CONNECT_TIMEOUT,
                    decode_responses=True
                )
            else:
                # Use individual connection parameters
                pool = redis.ConnectionPool(
                    host=CacheConfig.REDIS_HOST,
                    port=CacheConfig.REDIS_PORT,
                    db=CacheConfig.REDIS_DB,
                    password=CacheConfig.REDIS_PASSWORD,
                    max_connections=CacheConfig.CONNECTION_POOL_SIZE,
                    socket_timeout=CacheConfig.SOCKET_TIMEOUT,
                    socket_connect_timeout=CacheConfig.SOCKET_CONNECT_TIMEOUT,
                    decode_responses=True
                )
                client = redis.Redis(connection_pool=pool)
            
            # Test connection
            client.ping()
            logging.info("✅ Redis connection established successfully")
            return client
            
        except Exception as e:
            logging.warning(f"⚠️ Redis connection failed: {e}")
            if self.enable_fallback:
                logging.info("📝 Using in-memory fallback cache")
            return None
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data for caching"""
        try:
            return json.dumps(data, default=str, separators=(',', ':'))
        except Exception as e:
            logging.error(f"Cache serialization error: {e}")
            return None
    
    def _deserialize_data(self, data: str) -> Any:
        """Deserialize cached data"""
        try:
            return json.loads(data)
        except Exception as e:
            logging.error(f"Cache deserialization error: {e}")
            return None
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached data with fallback support"""
        try:
            # Try Redis first
            if self.redis_client and CacheConfig.ENABLE_CACHE:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    self.cache_stats['hits'] += 1
                    if CacheConfig.CACHE_DEBUG:
                        logging.debug(f"Cache HIT: {key}")
                    return self._deserialize_data(cached_data)
            
            # Try fallback cache
            if self.enable_fallback and key in self.fallback_cache:
                cache_entry = self.fallback_cache[key]
                if cache_entry['expires'] > datetime.now():
                    self.cache_stats['hits'] += 1
                    if CacheConfig.CACHE_DEBUG:
                        logging.debug(f"Fallback cache HIT: {key}")
                    return cache_entry['data']
                else:
                    # Expired entry
                    del self.fallback_cache[key]
            
            self.cache_stats['misses'] += 1
            if CacheConfig.CACHE_DEBUG:
                logging.debug(f"Cache MISS: {key}")
            return None
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            logging.error(f"Cache get error for key '{key}': {e}")
            return None
    
    def set(self, key: str, data: Any, ttl: int = None) -> bool:
        """Set cached data with fallback support"""
        try:
            ttl = ttl or CacheConfig.DEFAULT_TTL
            serialized_data = self._serialize_data(data)
            
            if not serialized_data:
                return False
            
            # Set in Redis
            if self.redis_client and CacheConfig.ENABLE_CACHE:
                success = self.redis_client.setex(key, ttl, serialized_data)
                if success:
                    self.cache_stats['sets'] += 1
                    if CacheConfig.CACHE_DEBUG:
                        logging.debug(f"Cache SET: {key} (TTL: {ttl}s)")
                    return True
            
            # Set in fallback cache
            if self.enable_fallback:
                self.fallback_cache[key] = {
                    'data': data,
                    'expires': datetime.now() + timedelta(seconds=ttl)
                }
                self.cache_stats['sets'] += 1
                if CacheConfig.CACHE_DEBUG:
                    logging.debug(f"Fallback cache SET: {key}")
                return True
            
            return False
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            logging.error(f"Cache set error for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached data"""
        try:
            deleted = False
            
            # Delete from Redis
            if self.redis_client and CacheConfig.ENABLE_CACHE:
                result = self.redis_client.delete(key)
                deleted = deleted or (result > 0)
            
            # Delete from fallback cache
            if self.enable_fallback and key in self.fallback_cache:
                del self.fallback_cache[key]
                deleted = True
            
            if deleted:
                self.cache_stats['deletes'] += 1
                if CacheConfig.CACHE_DEBUG:
                    logging.debug(f"Cache DELETE: {key}")
            
            return deleted
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            logging.error(f"Cache delete error for key '{key}': {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        try:
            deleted_count = 0
            
            # Redis pattern deletion
            if self.redis_client and CacheConfig.ENABLE_CACHE:
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted_count += self.redis_client.delete(*keys)
            
            # Fallback cache pattern deletion
            if self.enable_fallback:
                keys_to_delete = [key for key in self.fallback_cache.keys() if self._match_pattern(key, pattern)]
                for key in keys_to_delete:
                    del self.fallback_cache[key]
                    deleted_count += 1
            
            self.cache_stats['deletes'] += deleted_count
            if CacheConfig.CACHE_DEBUG:
                logging.debug(f"Cache INVALIDATE pattern '{pattern}': {deleted_count} keys")
            
            return deleted_count
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            logging.error(f"Cache pattern invalidation error for '{pattern}': {e}")
            return 0
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching for fallback cache"""
        if '*' in pattern:
            pattern_parts = pattern.split('*')
            if len(pattern_parts) == 2:
                prefix, suffix = pattern_parts
                return key.startswith(prefix) and key.endswith(suffix)
        return key == pattern
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_ops = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_ops * 100) if total_ops > 0 else 0
        
        stats = {
            **self.cache_stats,
            'hit_rate': round(hit_rate, 2),
            'total_operations': total_ops,
            'redis_connected': self.redis_client is not None,
            'fallback_enabled': self.enable_fallback,
            'fallback_size': len(self.fallback_cache) if self.enable_fallback else 0
        }
        
        # Add Redis-specific stats if available
        if self.redis_client:
            try:
                redis_info = self.redis_client.info()
                stats.update({
                    'redis_memory_used': redis_info.get('used_memory_human', 'N/A'),
                    'redis_connected_clients': redis_info.get('connected_clients', 'N/A'),
                    'redis_keyspace_hits': redis_info.get('keyspace_hits', 0),
                    'redis_keyspace_misses': redis_info.get('keyspace_misses', 0)
                })
            except Exception as e:
                logging.debug(f"Could not get Redis info: {e}")
        
        return stats
    
    def clear_all(self) -> bool:
        """Clear all cached data"""
        try:
            # Clear Redis
            if self.redis_client and CacheConfig.ENABLE_CACHE:
                self.redis_client.flushdb()
            
            # Clear fallback cache
            if self.enable_fallback:
                self.fallback_cache.clear()
            
            logging.info("🗑️ All cache data cleared")
            return True
            
        except Exception as e:
            logging.error(f"Cache clear error: {e}")
            return False
    
    def warm_cache(self):
        """Warm up cache with frequently accessed data"""
        try:
            from models import Category, Difficulty
            from optimized_db_service import OptimizedQuestionService, OptimizedScoreService
            
            logging.info("🔥 Starting cache warm-up...")
            
            # Warm up questions by category and difficulty
            categories = list(Category)
            difficulties = list(Difficulty)
            
            for category in categories:
                for difficulty in difficulties:
                    try:
                        questions = OptimizedQuestionService.get_questions_by_criteria_cached(
                            categories=[category],
                            difficulty=difficulty,
                            limit=20
                        )
                        logging.debug(f"   Warmed: {category.value}/{difficulty.value} - {len(questions)} questions")
                    except Exception as e:
                        logging.debug(f"   Failed to warm {category.value}/{difficulty.value}: {e}")
            
            # Warm up leaderboards
            for category in categories:
                for difficulty in difficulties:
                    try:
                        scores = OptimizedScoreService.get_leaderboard_cached(
                            category=category,
                            difficulty=difficulty,
                            limit=10
                        )
                        logging.debug(f"   Warmed leaderboard: {category.value}/{difficulty.value} - {len(scores)} scores")
                    except Exception as e:
                        logging.debug(f"   Failed to warm leaderboard {category.value}/{difficulty.value}: {e}")
            
            # Warm up overall leaderboard
            try:
                overall_scores = OptimizedScoreService.get_leaderboard_cached(limit=50)
                logging.debug(f"   Warmed overall leaderboard: {len(overall_scores)} scores")
            except Exception as e:
                logging.debug(f"   Failed to warm overall leaderboard: {e}")
            
            logging.info("✅ Cache warm-up completed")
            
        except Exception as e:
            logging.error(f"Cache warm-up failed: {e}")

def cached(key_func=None, ttl=None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cache_manager = getattr(func, '_cache_manager', None)
            if cache_manager:
                cached_result = cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            if cache_manager and result is not None:
                cache_ttl = ttl or CacheConfig.DEFAULT_TTL
                cache_manager.set(cache_key, result, cache_ttl)
            
            return result
        return wrapper
    return decorator

# Global cache manager instance
cache_manager = None

def initialize_cache() -> EnhancedCacheManager:
    """Initialize global cache manager"""
    global cache_manager
    
    if not cache_manager:
        cache_manager = EnhancedCacheManager()
        
        # Warm up cache in production
        if os.getenv('FLASK_ENV') == 'production':
            cache_manager.warm_cache()
    
    return cache_manager

def get_cache_manager() -> EnhancedCacheManager:
    """Get the global cache manager instance"""
    global cache_manager
    
    if not cache_manager:
        cache_manager = initialize_cache()
    
    return cache_manager

# Export for easy imports
__all__ = [
    'CacheConfig',
    'EnhancedCacheManager', 
    'initialize_cache',
    'get_cache_manager',
    'cached'
]