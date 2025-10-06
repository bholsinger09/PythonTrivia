"""
Enhanced Caching Strategy for Python Trivia Game
Advanced in-memory caching with compression, warming, and intelligent invalidation
"""
import time
import gzip
import pickle
import threading
from typing import Any, Dict, Optional, List, Callable
from functools import wraps
import hashlib
from collections import defaultdict, OrderedDict

# Import performance monitoring
try:
    from performance_monitoring import performance_metrics
    HAS_MONITORING = True
except ImportError:
    HAS_MONITORING = False

class CompressedCache:
    """Advanced in-memory cache with compression and LRU eviction"""
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000, compression_threshold: int = 1024):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.compression_threshold = compression_threshold
        
        # Use OrderedDict for LRU behavior
        self.cache: OrderedDict = OrderedDict()
        self._lock = threading.RLock()
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'compression_ratio': 0.0,
            'memory_saved': 0
        }
    
    def _should_compress(self, data: Any) -> bool:
        """Determine if data should be compressed"""
        try:
            serialized = pickle.dumps(data)
            return len(serialized) > self.compression_threshold
        except:
            return False
    
    def _compress_data(self, data: Any) -> bytes:
        """Compress data using gzip"""
        try:
            serialized = pickle.dumps(data)
            if len(serialized) > self.compression_threshold:
                compressed = gzip.compress(serialized)
                
                # Update compression statistics
                original_size = len(serialized)
                compressed_size = len(compressed)
                compression_ratio = compressed_size / original_size
                
                self.stats['compression_ratio'] = (
                    (self.stats['compression_ratio'] + compression_ratio) / 2
                )
                self.stats['memory_saved'] += (original_size - compressed_size)
                
                return compressed
            else:
                return serialized
        except Exception:
            # Fallback to uncompressed if compression fails
            return pickle.dumps(data)
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Decompress data"""
        try:
            # Try gzip decompression first
            try:
                decompressed = gzip.decompress(compressed_data)
                return pickle.loads(decompressed)
            except gzip.BadGzipFile:
                # Data wasn't compressed
                return pickle.loads(compressed_data)
        except Exception:
            return None
    
    def _evict_lru(self):
        """Evict least recently used items"""
        with self._lock:
            while len(self.cache) >= self.max_size:
                # Remove oldest item
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.stats['evictions'] += 1
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with LRU update"""
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if time.time() > entry['expires_at']:
                    del self.cache[key]
                    self.stats['misses'] += 1
                    return None
                
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                entry['hits'] += 1
                entry['last_accessed'] = time.time()
                self.stats['hits'] += 1
                
                # Decompress if needed
                return self._decompress_data(entry['data'])
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with compression"""
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        try:
            # Compress data
            compressed_data = self._compress_data(value)
            
            with self._lock:
                # Evict if needed
                self._evict_lru()
                
                # Store compressed data
                self.cache[key] = {
                    'data': compressed_data,
                    'expires_at': expires_at,
                    'created_at': time.time(),
                    'last_accessed': time.time(),
                    'hits': 0,
                    'size': len(compressed_data)
                }
                
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                
            return True
            
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
            # Reset stats but keep ratios
            self.stats.update({
                'hits': 0,
                'misses': 0,
                'evictions': 0
            })
    
    def get_stats(self) -> Dict:
        """Get comprehensive cache statistics"""
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_ratio = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            # Calculate memory usage
            total_memory = sum(entry['size'] for entry in self.cache.values())
            
            return {
                'total_entries': len(self.cache),
                'max_size': self.max_size,
                'hit_ratio_percent': round(hit_ratio, 2),
                'total_hits': self.stats['hits'],
                'total_misses': self.stats['misses'],
                'total_evictions': self.stats['evictions'],
                'memory_usage_bytes': total_memory,
                'memory_saved_bytes': self.stats['memory_saved'],
                'avg_compression_ratio': round(self.stats['compression_ratio'], 3),
                'cache_keys': list(self.cache.keys())
            }

class CacheWarmer:
    """Intelligent cache warming system"""
    
    def __init__(self):
        self.warming_tasks = []
        self.warming_active = False
        self._warming_thread = None
    
    def add_warming_task(self, cache_key: str, func: Callable, args: tuple = (), kwargs: dict = None, priority: int = 1):
        """Add a cache warming task"""
        kwargs = kwargs or {}
        
        task = {
            'cache_key': cache_key,
            'function': func,
            'args': args,
            'kwargs': kwargs,
            'priority': priority,
            'added_at': time.time()
        }
        
        self.warming_tasks.append(task)
        # Sort by priority (higher number = higher priority)
        self.warming_tasks.sort(key=lambda x: x['priority'], reverse=True)
    
    def start_warming(self, cache_instance):
        """Start cache warming in background"""
        if self.warming_active:
            return
        
        self.warming_active = True
        self._warming_thread = threading.Thread(
            target=self._warm_cache,
            args=(cache_instance,),
            daemon=True
        )
        self._warming_thread.start()
    
    def _warm_cache(self, cache_instance):
        """Execute cache warming tasks"""
        print(f"Starting cache warming with {len(self.warming_tasks)} tasks")
        
        for task in self.warming_tasks[:]:  # Copy list to avoid modification issues
            try:
                # Check if already cached
                if cache_instance.get(task['cache_key']) is not None:
                    continue
                
                # Execute function
                result = task['function'](*task['args'], **task['kwargs'])
                
                # Cache result
                cache_instance.set(task['cache_key'], result, ttl=600)  # 10 minutes
                
                print(f"Warmed cache for: {task['cache_key']}")
                
                # Small delay to not overwhelm the system
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Cache warming error for {task['cache_key']}: {e}")
        
        self.warming_active = False
        print("Cache warming completed")

class SmartCacheInvalidator:
    """Intelligent cache invalidation based on patterns and dependencies"""
    
    def __init__(self):
        self.invalidation_patterns = defaultdict(list)
        self.dependency_graph = defaultdict(set)
    
    def register_pattern(self, pattern: str, cache_keys: List[str]):
        """Register cache keys that should be invalidated for a pattern"""
        self.invalidation_patterns[pattern].extend(cache_keys)
    
    def register_dependency(self, parent_key: str, dependent_keys: List[str]):
        """Register cache dependencies (when parent changes, dependents should be invalidated)"""
        self.dependency_graph[parent_key].update(dependent_keys)
    
    def invalidate_pattern(self, pattern: str, cache_instances: Dict[str, CompressedCache]):
        """Invalidate all caches matching a pattern"""
        invalidated_keys = []
        
        for cache_key in self.invalidation_patterns.get(pattern, []):
            for cache_name, cache_instance in cache_instances.items():
                if cache_instance.delete(cache_key):
                    invalidated_keys.append(f"{cache_name}:{cache_key}")
        
        # Also invalidate by pattern matching
        for cache_name, cache_instance in cache_instances.items():
            keys_to_delete = []
            for key in cache_instance.cache.keys():
                if pattern in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                cache_instance.delete(key)
                invalidated_keys.append(f"{cache_name}:{key}")
        
        print(f"Invalidated {len(invalidated_keys)} cache entries for pattern: {pattern}")
        return invalidated_keys
    
    def invalidate_dependencies(self, changed_key: str, cache_instances: Dict[str, CompressedCache]):
        """Invalidate dependent cache entries"""
        invalidated_keys = []
        
        for dependent_key in self.dependency_graph.get(changed_key, []):
            for cache_name, cache_instance in cache_instances.items():
                if cache_instance.delete(dependent_key):
                    invalidated_keys.append(f"{cache_name}:{dependent_key}")
        
        return invalidated_keys

# Enhanced global cache instances
question_cache = CompressedCache(default_ttl=900, max_size=500)  # 15 minutes, 500 entries
leaderboard_cache = CompressedCache(default_ttl=120, max_size=100)  # 2 minutes, 100 entries
user_cache = CompressedCache(default_ttl=600, max_size=200)  # 10 minutes, 200 entries
query_cache = CompressedCache(default_ttl=300, max_size=1000)  # 5 minutes, 1000 entries

# Initialize cache management systems
cache_warmer = CacheWarmer()
cache_invalidator = SmartCacheInvalidator()

# Register cache dependencies
cache_invalidator.register_pattern('user_score_change', ['leaderboard_*'])
cache_invalidator.register_pattern('question_update', ['questions_*'])
cache_invalidator.register_dependency('user_answer', ['leaderboard_all', 'user_stats'])

def enhanced_cached_questions(category=None, difficulty=None, limit=20):
    """Enhanced caching decorator for questions with compression"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"questions_{category}_{difficulty}_{limit}"
            
            # Try to get from cache
            start_time = time.time()
            cached_result = question_cache.get(cache_key)
            
            if cached_result is not None:
                if HAS_MONITORING:
                    response_time = time.time() - start_time
                    performance_metrics.record_cache_hit('enhanced_questions', cache_key, response_time)
                return cached_result
            
            # Cache miss - execute function
            if HAS_MONITORING:
                performance_metrics.record_cache_miss('enhanced_questions', cache_key)
            
            result = func(*args, **kwargs)
            
            # Cache result with compression
            question_cache.set(cache_key, result, ttl=900)  # 15 minutes
            
            return result
        return wrapper
    return decorator

def enhanced_cached_leaderboard(category=None, limit=10):
    """Enhanced caching decorator for leaderboard with compression"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"leaderboard_{category}_{limit}"
            
            start_time = time.time()
            cached_result = leaderboard_cache.get(cache_key)
            
            if cached_result is not None:
                if HAS_MONITORING:
                    response_time = time.time() - start_time
                    performance_metrics.record_cache_hit('enhanced_leaderboard', cache_key, response_time)
                return cached_result
            
            if HAS_MONITORING:
                performance_metrics.record_cache_miss('enhanced_leaderboard', cache_key)
            
            result = func(*args, **kwargs)
            leaderboard_cache.set(cache_key, result, ttl=120)  # 2 minutes
            
            return result
        return wrapper
    return decorator

def cache_database_query(query_type: str, ttl: int = 300):
    """Cache database query results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = f"{func.__name__}_{query_type}_{args}_{sorted(kwargs.items())}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try cache first
            cached_result = query_cache.get(cache_key)
            if cached_result is not None:
                if HAS_MONITORING:
                    performance_metrics.record_cache_hit('database_query', cache_key)
                return cached_result
            
            # Execute query
            if HAS_MONITORING:
                performance_metrics.record_cache_miss('database_query', cache_key)
            
            result = func(*args, **kwargs)
            
            # Cache result
            query_cache.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator

def warm_essential_caches():
    """Warm up essential caches with popular data"""
    from models import Question, Category, Difficulty
    
    # Add common question queries to warming tasks
    cache_warmer.add_warming_task(
        'questions_all_easy_20',
        lambda: Question.query.filter_by(difficulty=Difficulty.EASY, is_active=True).limit(20).all(),
        priority=3
    )
    
    cache_warmer.add_warming_task(
        'questions_all_medium_20',
        lambda: Question.query.filter_by(difficulty=Difficulty.MEDIUM, is_active=True).limit(20).all(),
        priority=2
    )
    
    # Start warming
    cache_warmer.start_warming(question_cache)

def invalidate_user_related_caches(user_id: int = None):
    """Invalidate caches when user data changes"""
    cache_instances = {
        'leaderboard': leaderboard_cache,
        'user': user_cache
    }
    
    if user_id:
        cache_invalidator.invalidate_pattern(f'user_{user_id}', cache_instances)
    
    cache_invalidator.invalidate_pattern('leaderboard', cache_instances)

def get_enhanced_cache_stats() -> Dict:
    """Get comprehensive cache statistics for all cache instances"""
    return {
        'question_cache': question_cache.get_stats(),
        'leaderboard_cache': leaderboard_cache.get_stats(),
        'user_cache': user_cache.get_stats(),
        'query_cache': query_cache.get_stats(),
        'cache_warmer': {
            'active': cache_warmer.warming_active,
            'pending_tasks': len(cache_warmer.warming_tasks)
        },
        'total_memory_usage': sum([
            question_cache.get_stats()['memory_usage_bytes'],
            leaderboard_cache.get_stats()['memory_usage_bytes'],
            user_cache.get_stats()['memory_usage_bytes'],
            query_cache.get_stats()['memory_usage_bytes']
        ]),
        'total_memory_saved': sum([
            question_cache.get_stats()['memory_saved_bytes'],
            leaderboard_cache.get_stats()['memory_saved_bytes'],
            user_cache.get_stats()['memory_saved_bytes'],
            query_cache.get_stats()['memory_saved_bytes']
        ])
    }