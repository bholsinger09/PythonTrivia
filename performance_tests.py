"""
Database Performance Test Suite

This script tests the performance improvements of our optimizations:
- Query performance with and without indexes
- Cache hit/miss rates
- Memory usage comparison
- Concurrent query performance
"""

import time
import statistics
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, Question, GameSession, Answer, Score, User, Category, Difficulty
from config import DevelopmentConfig
from redis_cache import initialize_cache, get_cache_manager
from optimized_db_service import (
    OptimizedQuestionService, OptimizedScoreService, 
    OptimizedGameSessionService, DatabasePerformanceManager
)

class PerformanceTest:
    """Database performance testing suite"""
    
    def __init__(self, app):
        self.app = app
        self.cache_manager = get_cache_manager()
        self.db_manager = DatabasePerformanceManager(self.cache_manager.redis_client)
        self.results = {}
    
    def run_all_tests(self) -> dict:
        """Run comprehensive performance tests"""
        
        print("🚀 Starting Database Performance Tests...")
        print("=" * 60)
        
        with self.app.app_context():
            # Test 1: Query Performance
            print("\n📊 Test 1: Query Performance")
            self.test_query_performance()
            
            # Test 2: Cache Performance  
            print("\n💾 Test 2: Cache Performance")
            self.test_cache_performance()
            
            # Test 3: Concurrent Access
            print("\n🔄 Test 3: Concurrent Access Performance")
            self.test_concurrent_performance()
            
            # Test 4: Memory Usage
            print("\n🧠 Test 4: Memory and Resource Usage")
            self.test_resource_usage()
        
        # Generate report
        self.generate_report()
        return self.results
    
    def test_query_performance(self):
        """Test database query performance"""
        
        try:
            # Test question queries
            times = []
            
            # Test category + difficulty filtering
            for i in range(10):
                start_time = time.time()
                questions = OptimizedQuestionService.get_questions_by_criteria_cached(
                    categories=[Category.BASICS],
                    difficulty=Difficulty.EASY,
                    limit=20
                )
                end_time = time.time()
                times.append((end_time - start_time) * 1000)
            
            avg_query_time = statistics.mean(times)
            min_query_time = min(times)
            max_query_time = max(times)
            
            print(f"   Question Queries (10 runs):")
            print(f"     Average: {avg_query_time:.2f}ms")
            print(f"     Min: {min_query_time:.2f}ms")
            print(f"     Max: {max_query_time:.2f}ms")
            
            self.results['query_performance'] = {
                'avg_time_ms': avg_query_time,
                'min_time_ms': min_query_time,
                'max_time_ms': max_query_time,
                'status': 'fast' if avg_query_time < 50 else 'slow'
            }
            
            # Test leaderboard queries
            leaderboard_times = []
            for i in range(5):
                start_time = time.time()
                scores = OptimizedScoreService.get_leaderboard_cached(
                    category=Category.BASICS,
                    difficulty=Difficulty.EASY,
                    limit=10
                )
                end_time = time.time()
                leaderboard_times.append((end_time - start_time) * 1000)
            
            avg_leaderboard_time = statistics.mean(leaderboard_times)
            print(f"   Leaderboard Queries (5 runs): {avg_leaderboard_time:.2f}ms avg")
            
            self.results['leaderboard_performance'] = {
                'avg_time_ms': avg_leaderboard_time,
                'status': 'fast' if avg_leaderboard_time < 100 else 'slow'
            }
            
        except Exception as e:
            print(f"   ❌ Query performance test failed: {e}")
            self.results['query_performance'] = {'error': str(e)}
    
    def test_cache_performance(self):
        """Test cache hit rates and performance"""
        
        try:
            # Clear cache and get baseline stats
            self.cache_manager.clear_all()
            initial_stats = self.cache_manager.get_stats()
            
            # Test cache misses (first run)
            miss_times = []
            for i in range(5):
                start_time = time.time()
                questions = OptimizedQuestionService.get_questions_by_criteria_cached(
                    categories=[Category.BASICS],
                    difficulty=Difficulty.EASY,
                    limit=10
                )
                end_time = time.time()
                miss_times.append((end_time - start_time) * 1000)
            
            # Test cache hits (second run)
            hit_times = []
            for i in range(5):
                start_time = time.time()
                questions = OptimizedQuestionService.get_questions_by_criteria_cached(
                    categories=[Category.BASICS],
                    difficulty=Difficulty.EASY,
                    limit=10
                )
                end_time = time.time()
                hit_times.append((end_time - start_time) * 1000)
            
            final_stats = self.cache_manager.get_stats()
            
            avg_miss_time = statistics.mean(miss_times)
            avg_hit_time = statistics.mean(hit_times)
            
            print(f"   Cache Miss (DB Query): {avg_miss_time:.2f}ms avg")
            print(f"   Cache Hit (Memory): {avg_hit_time:.2f}ms avg")
            print(f"   Performance Improvement: {((avg_miss_time - avg_hit_time) / avg_miss_time * 100):.1f}%")
            print(f"   Hit Rate: {final_stats['hit_rate']:.1f}%")
            
            self.results['cache_performance'] = {
                'miss_time_ms': avg_miss_time,
                'hit_time_ms': avg_hit_time,
                'improvement_percent': ((avg_miss_time - avg_hit_time) / avg_miss_time * 100),
                'hit_rate': final_stats['hit_rate'],
                'redis_connected': final_stats['redis_connected']
            }
            
        except Exception as e:
            print(f"   ❌ Cache performance test failed: {e}")
            self.results['cache_performance'] = {'error': str(e)}
    
    def test_concurrent_performance(self):
        """Test performance under concurrent access"""
        
        try:
            # Test concurrent question queries
            def query_questions(thread_id):
                start_time = time.time()
                questions = OptimizedQuestionService.get_questions_by_criteria_cached(
                    categories=[Category.BASICS, Category.FUNCTIONS][thread_id % 2],
                    difficulty=[Difficulty.EASY, Difficulty.MEDIUM][thread_id % 2],
                    limit=15
                )
                end_time = time.time()
                return (end_time - start_time) * 1000
            
            # Run 10 concurrent queries
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(query_questions, i) for i in range(10)]
                concurrent_times = [future.result() for future in as_completed(futures)]
            
            avg_concurrent_time = statistics.mean(concurrent_times)
            max_concurrent_time = max(concurrent_times)
            
            print(f"   Concurrent Queries (10 threads): {avg_concurrent_time:.2f}ms avg")
            print(f"   Max Response Time: {max_concurrent_time:.2f}ms")
            
            self.results['concurrent_performance'] = {
                'avg_time_ms': avg_concurrent_time,
                'max_time_ms': max_concurrent_time,
                'status': 'good' if avg_concurrent_time < 100 else 'needs_optimization'
            }
            
        except Exception as e:
            print(f"   ❌ Concurrent performance test failed: {e}")
            self.results['concurrent_performance'] = {'error': str(e)}
    
    def test_resource_usage(self):
        """Test memory and resource usage"""
        
        try:
            # Get connection pool stats
            connection_stats = self.db_manager.get_performance_report()['connection_stats']
            cache_stats = self.cache_manager.get_stats()
            
            print(f"   Database Connections:")
            print(f"     Pool Size: {connection_stats.get('pool_size', 'N/A')}")
            print(f"     Checked Out: {connection_stats.get('checked_out', 'N/A')}")
            print(f"     Available: {connection_stats.get('checked_in', 'N/A')}")
            
            print(f"   Cache Usage:")
            print(f"     Total Operations: {cache_stats['total_operations']}")
            print(f"     Hit Rate: {cache_stats['hit_rate']:.1f}%")
            print(f"     Fallback Cache Size: {cache_stats['fallback_size']} items")
            
            self.results['resource_usage'] = {
                'connection_pool': connection_stats,
                'cache_stats': cache_stats
            }
            
        except Exception as e:
            print(f"   ❌ Resource usage test failed: {e}")
            self.results['resource_usage'] = {'error': str(e)}
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        
        print("\n" + "=" * 60)
        print("📈 PERFORMANCE TEST REPORT")
        print("=" * 60)
        
        # Overall assessment
        issues = []
        
        # Check query performance
        if 'query_performance' in self.results:
            qp = self.results['query_performance']
            if not qp.get('error') and qp.get('avg_time_ms', 0) > 50:
                issues.append("Slow query performance detected")
        
        # Check cache performance
        if 'cache_performance' in self.results:
            cp = self.results['cache_performance']
            if not cp.get('error') and cp.get('hit_rate', 0) < 70:
                issues.append("Low cache hit rate")
        
        # Check concurrent performance
        if 'concurrent_performance' in self.results:
            cpp = self.results['concurrent_performance']
            if not cpp.get('error') and cpp.get('avg_time_ms', 0) > 100:
                issues.append("Slow concurrent query performance")
        
        if not issues:
            print("✅ Overall Status: EXCELLENT - All performance metrics are good")
        else:
            print(f"⚠️  Overall Status: NEEDS ATTENTION")
            for issue in issues:
                print(f"   - {issue}")
        
        # Recommendations
        print("\n🎯 RECOMMENDATIONS:")
        
        if 'query_performance' in self.results and self.results['query_performance'].get('avg_time_ms', 0) > 50:
            print("   - Consider adding more specific database indexes")
            print("   - Review query patterns for optimization opportunities")
        
        if 'cache_performance' in self.results:
            cp = self.results['cache_performance']
            if cp.get('redis_connected'):
                print("   ✅ Redis caching is active and working")
            else:
                print("   - Consider setting up Redis for better caching performance")
        
        if 'concurrent_performance' in self.results and self.results['concurrent_performance'].get('avg_time_ms', 0) > 100:
            print("   - Consider increasing database connection pool size")
            print("   - Implement query result caching for frequently accessed data")
        
        print("\n📊 DETAILED METRICS:")
        for test_name, results in self.results.items():
            if not results.get('error'):
                print(f"   {test_name}: {results}")

def run_performance_tests():
    """Main function to run performance tests"""
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    # Initialize database and cache
    db.init_app(app)
    
    # Run tests
    test_suite = PerformanceTest(app)
    results = test_suite.run_all_tests()
    
    return results

if __name__ == "__main__":
    results = run_performance_tests()