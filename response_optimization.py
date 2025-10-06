"""
API Response Time Optimization
Implements response compression, ETag support, JSON optimization, and other performance enhancements
"""
import gzip
import json
import hashlib
import time
import io
from typing import Any, Dict, Optional, Tuple, Union
from functools import wraps
from flask import request, Response, jsonify, current_app, g

# Try to import orjson for faster JSON serialization
try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False

# Import performance monitoring
try:
    from performance_monitoring import performance_metrics
    HAS_MONITORING = True
except ImportError:
    HAS_MONITORING = False

class ResponseOptimizer:
    """Advanced response optimization utilities"""
    
    @staticmethod
    def compress_response(response_data: bytes, min_size: int = 1024) -> Tuple[bytes, bool]:
        """Compress response data if it's large enough"""
        if len(response_data) < min_size:
            return response_data, False
        
        try:
            # Compress using gzip
            compressed = gzip.compress(response_data, compresslevel=6)
            
            # Only use compressed version if it's actually smaller
            if len(compressed) < len(response_data):
                return compressed, True
            else:
                return response_data, False
                
        except Exception:
            return response_data, False
    
    @staticmethod
    def generate_etag(data: Union[str, bytes, dict]) -> str:
        """Generate ETag for response data"""
        if isinstance(data, dict):
            # Sort dict keys for consistent hashing
            data_str = json.dumps(data, sort_keys=True)
        elif isinstance(data, str):
            data_str = data
        else:
            data_str = str(data)
        
        return hashlib.md5(data_str.encode()).hexdigest()
    
    @staticmethod
    def optimize_json_response(data: Any) -> bytes:
        """Optimize JSON serialization"""
        if HAS_ORJSON:
            # Use orjson for faster serialization
            return orjson.dumps(data)
        else:
            # Fallback to standard json with optimizations
            return json.dumps(
                data, 
                separators=(',', ':'),  # No spaces for smaller size
                ensure_ascii=False
            ).encode('utf-8')
    
    @staticmethod
    def should_compress(accept_encoding: str) -> bool:
        """Check if client accepts gzip compression"""
        return 'gzip' in accept_encoding.lower()

def compress_response(min_size: int = 1024, cache_etag: bool = True):
    """Decorator to add response compression and ETag support"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # Check if client supports compression
            accept_encoding = request.headers.get('Accept-Encoding', '')
            supports_compression = ResponseOptimizer.should_compress(accept_encoding)
            
            # Check for conditional requests (ETag)
            if_none_match = request.headers.get('If-None-Match')
            
            # Execute the original function
            result = f(*args, **kwargs)
            
            # Handle different response types
            if isinstance(result, Response):
                response = result
                response_data = response.get_data()
            elif isinstance(result, tuple):
                # Handle (data, status_code) tuples
                data, status_code = result
                if isinstance(data, dict):
                    response_data = ResponseOptimizer.optimize_json_response(data)
                    response = Response(
                        response_data,
                        status=status_code,
                        mimetype='application/json'
                    )
                else:
                    response = Response(data, status=status_code)
                    response_data = response.get_data()
            else:
                # Handle direct dict/object responses
                if isinstance(result, dict):
                    response_data = ResponseOptimizer.optimize_json_response(result)
                    response = Response(
                        response_data,
                        mimetype='application/json'
                    )
                else:
                    response = Response(str(result))
                    response_data = response.get_data()
            
            # Generate ETag if caching is enabled
            if cache_etag:
                etag = ResponseOptimizer.generate_etag(response_data)
                response.headers['ETag'] = f'"{etag}"'
                
                # Check if client has current version
                if if_none_match and etag in if_none_match:
                    # Client has current version, return 304 Not Modified
                    response = Response(status=304)
                    response.headers['ETag'] = f'"{etag}"'
                    
                    if HAS_MONITORING:
                        performance_metrics.record_cache_hit('etag', request.endpoint)
                    
                    return response
                
                if HAS_MONITORING and if_none_match:
                    performance_metrics.record_cache_miss('etag', request.endpoint)
            
            # Apply compression if supported and beneficial
            if supports_compression and len(response_data) >= min_size:
                compressed_data, was_compressed = ResponseOptimizer.compress_response(
                    response_data, min_size
                )
                
                if was_compressed:
                    response.set_data(compressed_data)
                    response.headers['Content-Encoding'] = 'gzip'
                    response.headers['Content-Length'] = len(compressed_data)
                    
                    # Track compression savings
                    compression_ratio = len(compressed_data) / len(response_data)
                    if HAS_MONITORING:
                        savings = len(response_data) - len(compressed_data)
                        performance_metrics.record_cache_hit('compression', f'saved_{savings}_bytes')
            
            # Add performance headers
            processing_time = time.time() - start_time
            response.headers['X-Response-Time'] = f'{processing_time:.3f}s'
            response.headers['X-Optimized'] = 'true'
            
            # Add cache headers for static-like content
            if cache_etag:
                response.headers['Cache-Control'] = 'public, max-age=60'  # 1 minute cache
            
            return response
        
        return decorated_function
    return decorator

def json_response_optimized(data: Any, status: int = 200, cache_ttl: int = 60) -> Response:
    """Create optimized JSON response with compression and caching headers"""
    
    # Optimize JSON serialization
    json_data = ResponseOptimizer.optimize_json_response(data)
    
    # Create response
    response = Response(
        json_data,
        status=status,
        mimetype='application/json'
    )
    
    # Add ETag
    etag = ResponseOptimizer.generate_etag(json_data)
    response.headers['ETag'] = f'"{etag}"'
    
    # Add compression if client supports it
    accept_encoding = request.headers.get('Accept-Encoding', '')
    if ResponseOptimizer.should_compress(accept_encoding) and len(json_data) > 1024:
        compressed_data, was_compressed = ResponseOptimizer.compress_response(json_data)
        
        if was_compressed:
            response.set_data(compressed_data)
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(compressed_data)
    
    # Add cache headers
    response.headers['Cache-Control'] = f'public, max-age={cache_ttl}'
    response.headers['X-Optimized-JSON'] = 'true'
    
    return response

def api_cache_headers(max_age: int = 300, stale_while_revalidate: int = 60):
    """Add intelligent caching headers to API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            
            if isinstance(response, Response):
                # Add advanced cache headers
                cache_control = f'public, max-age={max_age}, stale-while-revalidate={stale_while_revalidate}'
                response.headers['Cache-Control'] = cache_control
                
                # Add Vary header for compression
                response.headers['Vary'] = 'Accept-Encoding'
                
                # Add performance hints
                response.headers['X-Cache-Strategy'] = 'optimized'
            
            return response
        
        return decorated_function
    return decorator

class JSONStreamOptimizer:
    """Optimize large JSON responses by streaming"""
    
    @staticmethod
    def stream_json_array(items, chunk_size: int = 100):
        """Stream large JSON arrays in chunks"""
        def generate():
            yield '['
            
            for i, item in enumerate(items):
                if i > 0:
                    yield ','
                
                if HAS_ORJSON:
                    yield orjson.dumps(item).decode('utf-8')
                else:
                    yield json.dumps(item, separators=(',', ':'))
                
                # Yield control periodically for large datasets
                if i % chunk_size == 0:
                    time.sleep(0.001)  # Small delay to prevent blocking
            
            yield ']'
        
        return Response(
            generate(),
            mimetype='application/json',
            headers={'X-Streaming': 'true'}
        )

def benchmark_json_serialization():
    """Benchmark different JSON serialization methods"""
    test_data = {
        'questions': [
            {
                'id': i,
                'question': f'Sample question {i}?',
                'options': [f'Option A {i}', f'Option B {i}', f'Option C {i}', f'Option D {i}'],
                'category': 'Python',
                'difficulty': 'medium',
                'explanation': f'This is a detailed explanation for question {i}. ' * 3
            }
            for i in range(100)
        ],
        'metadata': {
            'total': 100,
            'generated_at': time.time(),
            'version': '1.0'
        }
    }
    
    # Benchmark standard json
    start_time = time.time()
    for _ in range(10):
        json.dumps(test_data)
    standard_time = time.time() - start_time
    
    # Benchmark optimized json
    start_time = time.time()
    for _ in range(10):
        json.dumps(test_data, separators=(',', ':'), ensure_ascii=False)
    optimized_time = time.time() - start_time
    
    # Benchmark orjson if available
    orjson_time = None
    if HAS_ORJSON:
        start_time = time.time()
        for _ in range(10):
            orjson.dumps(test_data)
        orjson_time = time.time() - start_time
    
    return {
        'standard_json_time': round(standard_time, 4),
        'optimized_json_time': round(optimized_time, 4),
        'orjson_time': round(orjson_time, 4) if orjson_time else None,
        'optimization_ratio': round(standard_time / optimized_time, 2),
        'orjson_ratio': round(standard_time / orjson_time, 2) if orjson_time else None
    }

def create_response_optimization_routes(app):
    """Add response optimization monitoring routes"""
    
    @app.route('/api/admin/response-optimization-stats')
    def response_optimization_stats():
        """Get response optimization statistics"""
        from flask import jsonify
        
        if not app.debug:
            return jsonify({'error': 'Access denied'}), 403
        
        # Run JSON serialization benchmark
        benchmark_results = benchmark_json_serialization()
        
        # Get compression stats from performance metrics if available
        compression_stats = {}
        if HAS_MONITORING:
            try:
                cache_stats = performance_metrics.get_cache_performance()
                compression_stats = cache_stats.get('compression', {})
            except:
                pass
        
        return jsonify({
            'json_serialization': benchmark_results,
            'compression_stats': compression_stats,
            'optimizations_available': {
                'orjson': HAS_ORJSON,
                'gzip_compression': True,
                'etag_support': True,
                'cache_headers': True
            },
            'timestamp': time.time()
        })
    
    @app.route('/api/test/large-response')
    @compress_response(min_size=1024, cache_etag=True)
    def test_large_response():
        """Test endpoint for large response optimization"""
        # Generate a large test response
        test_data = {
            'large_dataset': [
                {
                    'id': i,
                    'data': f'Sample data entry {i} with some content to make it larger. ' * 10,
                    'metadata': {'index': i, 'processed': True}
                }
                for i in range(500)
            ],
            'summary': {
                'total_items': 500,
                'generated_at': time.time(),
                'optimization_test': True
            }
        }
        
        return json_response_optimized(test_data, cache_ttl=300)
    
    @app.route('/api/test/streaming-response')
    def test_streaming_response():
        """Test endpoint for streaming large responses"""
        # Generate large dataset
        large_items = [
            {'id': i, 'value': f'Item {i}', 'data': 'x' * 100}
            for i in range(1000)
        ]
        
        return JSONStreamOptimizer.stream_json_array(large_items, chunk_size=50)