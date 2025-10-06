"""
Enhanced Caching Strategy Test and Demonstration
Tests the advanced caching features including compression, LRU eviction, and cache warming
"""
import sys
import os
import time
import random
from typing import List, Dict

# Add the project root to the path
sys.path.append('/Users/benh/Documents/PythonTrivia')

from enhanced_caching import (
    CompressedCache, CacheWarmer, SmartCacheInvalidator,
    enhanced_cached_questions, enhanced_cached_leaderboard,
    cache_database_query, get_enhanced_cache_stats
)

def test_compressed_cache():
    """Test the compressed cache functionality"""
    print("🧪 Testing Compressed Cache...")
    
    cache = CompressedCache(default_ttl=60, max_size=5, compression_threshold=100)
    
    # Test basic operations
    cache.set('small_data', 'hello', ttl=30)
    cache.set('large_data', 'x' * 2000, ttl=30)  # Should be compressed
    
    # Test retrieval
    small = cache.get('small_data')
    large = cache.get('large_data')
    
    print(f"✅ Small data retrieved: {small[:10]}...")
    print(f"✅ Large data retrieved: {large[:10]}... (length: {len(large)})")
    
    # Test LRU eviction by adding more than max_size
    for i in range(10):
        cache.set(f'item_{i}', f'data_{i}' * 100)
    
    stats = cache.get_stats()
    print(f"✅ Cache stats after LRU test:")
    print(f"   - Entries: {stats['total_entries']}/{stats['max_size']}")
    print(f"   - Hit ratio: {stats['hit_ratio_percent']}%")
    print(f"   - Memory saved: {stats['memory_saved_bytes']} bytes")
    print(f"   - Compression ratio: {stats['avg_compression_ratio']}")
    print(f"   - Evictions: {stats['total_evictions']}")

def test_cache_warming():
    """Test cache warming functionality"""
    print("\n🔥 Testing Cache Warming...")
    
    cache = CompressedCache(default_ttl=60, max_size=100)
    warmer = CacheWarmer()
    
    # Simulate expensive data generation functions
    def generate_questions(category: str, count: int) -> List[Dict]:
        time.sleep(0.1)  # Simulate database query
        return [
            {
                'id': i,
                'question': f'Question {i} about {category}',
                'category': category
            }
            for i in range(count)
        ]
    
    def generate_leaderboard(limit: int) -> List[Dict]:
        time.sleep(0.05)  # Simulate database query
        return [
            {
                'username': f'user_{i}',
                'score': random.randint(100, 1000)
            }
            for i in range(limit)
        ]
    
    # Add warming tasks
    warmer.add_warming_task('questions_python', generate_questions, ('Python', 20), priority=3)
    warmer.add_warming_task('questions_javascript', generate_questions, ('JavaScript', 20), priority=2)
    warmer.add_warming_task('leaderboard_top10', generate_leaderboard, (10,), priority=1)
    
    print(f"Added {len(warmer.warming_tasks)} warming tasks")
    
    # Start warming
    warmer.start_warming(cache)
    
    # Wait a bit for warming to complete
    time.sleep(1)
    
    # Test that data was warmed
    python_qs = cache.get('questions_python')
    js_qs = cache.get('questions_javascript')
    leaderboard = cache.get('leaderboard_top10')
    
    print(f"✅ Python questions warmed: {len(python_qs) if python_qs else 0} items")
    print(f"✅ JavaScript questions warmed: {len(js_qs) if js_qs else 0} items")
    print(f"✅ Leaderboard warmed: {len(leaderboard) if leaderboard else 0} items")
    
    print(f"✅ Cache stats after warming: {cache.get_stats()['total_entries']} entries")

def test_smart_invalidation():
    """Test smart cache invalidation"""
    print("\n🧹 Testing Smart Cache Invalidation...")
    
    question_cache = CompressedCache(default_ttl=60, max_size=100)
    leaderboard_cache = CompressedCache(default_ttl=60, max_size=100)
    
    invalidator = SmartCacheInvalidator()
    
    # Set up some test data
    question_cache.set('questions_python_easy', ['q1', 'q2', 'q3'])
    question_cache.set('questions_python_hard', ['q4', 'q5', 'q6'])
    question_cache.set('questions_javascript_easy', ['q7', 'q8', 'q9'])
    
    leaderboard_cache.set('leaderboard_all', ['user1', 'user2', 'user3'])
    leaderboard_cache.set('leaderboard_python', ['user4', 'user5'])
    
    # Register patterns
    invalidator.register_pattern('python', ['questions_python_easy', 'questions_python_hard'])
    invalidator.register_pattern('leaderboard', ['leaderboard_all', 'leaderboard_python'])
    
    caches = {
        'questions': question_cache,
        'leaderboard': leaderboard_cache
    }
    
    print(f"Before invalidation:")
    print(f"  - Question cache: {question_cache.get_stats()['total_entries']} entries")
    print(f"  - Leaderboard cache: {leaderboard_cache.get_stats()['total_entries']} entries")
    
    # Test pattern invalidation
    invalidated = invalidator.invalidate_pattern('python', caches)
    print(f"✅ Invalidated {len(invalidated)} Python-related entries")
    
    invalidated = invalidator.invalidate_pattern('leaderboard', caches)
    print(f"✅ Invalidated {len(invalidated)} leaderboard entries")
    
    print(f"After invalidation:")
    print(f"  - Question cache: {question_cache.get_stats()['total_entries']} entries")
    print(f"  - Leaderboard cache: {leaderboard_cache.get_stats()['total_entries']} entries")

def test_caching_decorators():
    """Test caching decorators"""
    print("\n🎭 Testing Caching Decorators...")
    
    @enhanced_cached_questions(category='Python', difficulty='easy', limit=10)
    def get_python_questions():
        time.sleep(0.1)  # Simulate database query
        return [f'Python question {i}' for i in range(10)]
    
    @enhanced_cached_leaderboard(category='Python', limit=5)
    def get_python_leaderboard():
        time.sleep(0.05)  # Simulate database query
        return [f'Python user {i}' for i in range(5)]
    
    @cache_database_query('user_stats', ttl=30)
    def get_user_stats(user_id: int):
        time.sleep(0.02)  # Simulate database query
        return {'user_id': user_id, 'score': random.randint(100, 1000)}
    
    # Test question caching
    start_time = time.time()
    questions1 = get_python_questions()
    first_call_time = time.time() - start_time
    
    start_time = time.time()
    questions2 = get_python_questions()  # Should be cached
    second_call_time = time.time() - start_time
    
    print(f"✅ Questions - First call: {first_call_time:.3f}s, Second call: {second_call_time:.3f}s")
    print(f"   Speedup: {first_call_time / second_call_time:.1f}x")
    
    # Test leaderboard caching
    start_time = time.time()
    leaderboard1 = get_python_leaderboard()
    first_call_time = time.time() - start_time
    
    start_time = time.time()
    leaderboard2 = get_python_leaderboard()  # Should be cached
    second_call_time = time.time() - start_time
    
    print(f"✅ Leaderboard - First call: {first_call_time:.3f}s, Second call: {second_call_time:.3f}s")
    print(f"   Speedup: {first_call_time / second_call_time:.1f}x")
    
    # Test database query caching
    start_time = time.time()
    stats1 = get_user_stats(123)
    first_call_time = time.time() - start_time
    
    start_time = time.time()
    stats2 = get_user_stats(123)  # Should be cached
    second_call_time = time.time() - start_time
    
    print(f"✅ User stats - First call: {first_call_time:.3f}s, Second call: {second_call_time:.3f}s")
    print(f"   Speedup: {first_call_time / second_call_time:.1f}x")

def test_performance_impact():
    """Test performance impact of caching"""
    print("\n📊 Testing Performance Impact...")
    
    cache = CompressedCache(default_ttl=60, max_size=1000)
    
    # Generate test data of various sizes
    test_data = {
        'small': 'x' * 50,
        'medium': 'x' * 500,
        'large': 'x' * 5000,
        'huge': 'x' * 50000
    }
    
    for size_name, data in test_data.items():
        # Test write performance
        start_time = time.time()
        cache.set(f'test_{size_name}', data)
        write_time = time.time() - start_time
        
        # Test read performance
        start_time = time.time()
        retrieved = cache.get(f'test_{size_name}')
        read_time = time.time() - start_time
        
        print(f"✅ {size_name.capitalize()} data ({len(data)} chars):")
        print(f"   Write: {write_time:.4f}s, Read: {read_time:.4f}s")
    
    # Show final cache statistics
    final_stats = cache.get_stats()
    print(f"\n📈 Final Cache Statistics:")
    print(f"   - Total entries: {final_stats['total_entries']}")
    print(f"   - Memory usage: {final_stats['memory_usage_bytes']:,} bytes")
    print(f"   - Memory saved: {final_stats['memory_saved_bytes']:,} bytes")
    print(f"   - Average compression ratio: {final_stats['avg_compression_ratio']:.3f}")
    print(f"   - Hit ratio: {final_stats['hit_ratio_percent']:.1f}%")

def main():
    """Run all caching tests"""
    print("🚀 Enhanced Caching Strategy Test Suite")
    print("=" * 50)
    
    try:
        test_compressed_cache()
        test_cache_warming()
        test_smart_invalidation()
        test_caching_decorators()
        test_performance_impact()
        
        print("\n🎉 All caching tests completed successfully!")
        
        # Show comprehensive stats
        print("\n📊 Comprehensive Cache Statistics:")
        stats = get_enhanced_cache_stats()
        print(f"Total memory usage: {stats['total_memory_usage']:,} bytes")
        print(f"Total memory saved: {stats['total_memory_saved']:,} bytes")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()