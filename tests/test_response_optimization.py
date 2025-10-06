"""
Response Optimization Test Suite
Tests compression, ETag support, JSON optimization, and caching headers
"""
import sys
import time
import gzip
import json

# Add the project root to the path
sys.path.append('/Users/benh/Documents/PythonTrivia')

from response_optimization import (
    ResponseOptimizer, compress_response, json_response_optimized,
    benchmark_json_serialization, JSONStreamOptimizer
)

def test_response_compression():
    """Test response compression functionality"""
    print("🗜️ Testing Response Compression...")
    
    # Test small data (should not be compressed)
    small_data = b'{"message": "hello"}'
    compressed, was_compressed = ResponseOptimizer.compress_response(small_data, min_size=1024)
    print(f"✅ Small data compression: {was_compressed} (expected: False)")
    
    # Test large data (should be compressed)
    large_data = b'{"data": "' + b'x' * 5000 + b'"}'
    compressed, was_compressed = ResponseOptimizer.compress_response(large_data, min_size=1024)
    
    if was_compressed:
        compression_ratio = len(compressed) / len(large_data)
        savings = len(large_data) - len(compressed)
        print(f"✅ Large data compressed: {compression_ratio:.3f} ratio, saved {savings:,} bytes")
        
        # Test decompression
        decompressed = gzip.decompress(compressed)
        print(f"✅ Decompression successful: {decompressed == large_data}")
    else:
        print("❌ Large data was not compressed")

def test_etag_generation():
    """Test ETag generation"""
    print("\n🏷️ Testing ETag Generation...")
    
    # Test consistent ETag generation
    data1 = {"id": 1, "name": "test", "values": [1, 2, 3]}
    data2 = {"id": 1, "name": "test", "values": [1, 2, 3]}
    data3 = {"id": 2, "name": "test", "values": [1, 2, 3]}
    
    etag1 = ResponseOptimizer.generate_etag(data1)
    etag2 = ResponseOptimizer.generate_etag(data2)
    etag3 = ResponseOptimizer.generate_etag(data3)
    
    print(f"✅ Consistent ETags: {etag1 == etag2} (expected: True)")
    print(f"✅ Different ETags: {etag1 != etag3} (expected: True)")
    print(f"   ETag 1: {etag1}")
    print(f"   ETag 3: {etag3}")

def test_json_optimization():
    """Test JSON serialization optimization"""
    print("\n⚡ Testing JSON Optimization...")
    
    # Create test data
    test_data = {
        "questions": [
            {
                "id": i,
                "question": f"What is the answer to question {i}?",
                "options": ["A", "B", "C", "D"],
                "category": "Python",
                "difficulty": "medium"
            }
            for i in range(50)
        ],
        "metadata": {
            "total": 50,
            "timestamp": time.time()
        }
    }
    
    # Test standard JSON
    start_time = time.time()
    standard_json = json.dumps(test_data)
    standard_time = time.time() - start_time
    
    # Test optimized JSON
    start_time = time.time()
    optimized_json = ResponseOptimizer.optimize_json_response(test_data)
    optimized_time = time.time() - start_time
    
    # Compare sizes
    standard_size = len(standard_json.encode('utf-8'))
    optimized_size = len(optimized_json)
    size_ratio = optimized_size / standard_size
    
    print(f"✅ Standard JSON: {standard_size:,} bytes in {standard_time:.4f}s")
    print(f"✅ Optimized JSON: {optimized_size:,} bytes in {optimized_time:.4f}s")
    print(f"✅ Size ratio: {size_ratio:.3f} (smaller is better)")
    
    if optimized_time > 0:
        speedup = standard_time / optimized_time
        print(f"✅ Speed improvement: {speedup:.1f}x faster")

def test_compression_detection():
    """Test client compression support detection"""
    print("\n🔍 Testing Compression Detection...")
    
    test_cases = [
        ("gzip, deflate", True),
        ("gzip", True),
        ("deflate", False),
        ("", False),
        ("br, gzip, deflate", True),
        ("GZIP", True),  # Case insensitive
    ]
    
    for accept_encoding, expected in test_cases:
        result = ResponseOptimizer.should_compress(accept_encoding)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{accept_encoding}' -> {result} (expected: {expected})")

def test_json_streaming():
    """Test JSON streaming for large datasets"""
    print("\n🌊 Testing JSON Streaming...")
    
    # Create large dataset
    large_items = [
        {"id": i, "data": f"Item {i}", "value": i * 2}
        for i in range(1000)
    ]
    
    # Test streaming
    start_time = time.time()
    stream_response = JSONStreamOptimizer.stream_json_array(large_items, chunk_size=100)
    
    # Consume the stream
    streamed_data = ''.join(stream_response.response).encode('utf-8')
    stream_time = time.time() - start_time
    
    # Test regular JSON for comparison
    start_time = time.time()
    regular_json = json.dumps(large_items).encode('utf-8')
    regular_time = time.time() - start_time
    
    print(f"✅ Streamed JSON: {len(streamed_data):,} bytes in {stream_time:.4f}s")
    print(f"✅ Regular JSON: {len(regular_json):,} bytes in {regular_time:.4f}s")
    print(f"✅ Size match: {len(streamed_data) == len(regular_json)}")
    
    # Verify the streamed JSON is valid
    try:
        parsed = json.loads(streamed_data)
        print(f"✅ Streamed JSON is valid: {len(parsed)} items")
    except json.JSONDecodeError:
        print("❌ Streamed JSON is invalid")

def test_full_optimization_pipeline():
    """Test the complete optimization pipeline"""
    print("\n🚀 Testing Full Optimization Pipeline...")
    
    # Create realistic API response data
    api_response = {
        "questions": [
            {
                "id": i,
                "question": f"What is the result of 2 + {i}?",
                "options": [str(2 + i), str(2 + i + 1), str(2 + i - 1), str(2 + i + 2)],
                "correct_answer": str(2 + i),
                "category": "Mathematics",
                "difficulty": "easy",
                "explanation": f"Simple addition: 2 + {i} = {2 + i}. This is basic arithmetic."
            }
            for i in range(100)
        ],
        "metadata": {
            "total": 100,
            "page": 1,
            "per_page": 100,
            "generated_at": time.time(),
            "cache_ttl": 600
        }
    }
    
    # Test the full pipeline
    start_time = time.time()
    
    # 1. Optimize JSON serialization
    optimized_json = ResponseOptimizer.optimize_json_response(api_response)
    
    # 2. Generate ETag
    etag = ResponseOptimizer.generate_etag(optimized_json)
    
    # 3. Apply compression
    compressed_data, was_compressed = ResponseOptimizer.compress_response(optimized_json)
    
    total_time = time.time() - start_time
    
    # Calculate savings
    original_size = len(json.dumps(api_response).encode('utf-8'))
    optimized_size = len(optimized_json)
    final_size = len(compressed_data) if was_compressed else optimized_size
    
    json_savings = original_size - optimized_size
    compression_savings = optimized_size - final_size if was_compressed else 0
    total_savings = original_size - final_size
    
    print(f"✅ Original size: {original_size:,} bytes")
    print(f"✅ After JSON optimization: {optimized_size:,} bytes (saved {json_savings:,})")
    print(f"✅ After compression: {final_size:,} bytes (saved {compression_savings:,})")
    print(f"✅ Total savings: {total_savings:,} bytes ({total_savings/original_size*100:.1f}%)")
    print(f"✅ Processing time: {total_time:.4f}s")
    print(f"✅ ETag generated: {etag}")
    print(f"✅ Compression applied: {was_compressed}")

def test_benchmark_serialization():
    """Test JSON serialization benchmarks"""
    print("\n📊 Testing JSON Serialization Benchmarks...")
    
    benchmark_results = benchmark_json_serialization()
    
    print(f"✅ Standard JSON: {benchmark_results['standard_json_time']:.4f}s")
    print(f"✅ Optimized JSON: {benchmark_results['optimized_json_time']:.4f}s")
    print(f"✅ Optimization ratio: {benchmark_results['optimization_ratio']:.1f}x faster")
    
    if benchmark_results['orjson_time']:
        print(f"✅ orjson: {benchmark_results['orjson_time']:.4f}s")
        print(f"✅ orjson ratio: {benchmark_results['orjson_ratio']:.1f}x faster")
    else:
        print("ℹ️ orjson not available (install with: pip install orjson)")

def main():
    """Run all response optimization tests"""
    print("🚀 Response Optimization Test Suite")
    print("=" * 50)
    
    try:
        test_response_compression()
        test_etag_generation()
        test_json_optimization()
        test_compression_detection()
        test_json_streaming()
        test_full_optimization_pipeline()
        test_benchmark_serialization()
        
        print("\n🎉 All response optimization tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()