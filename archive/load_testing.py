"""
Comprehensive Load Testing Suite for Python Trivia Game
Tests performance improvements under realistic traffic conditions.
"""
import asyncio
import time
import json
import random
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from datetime import datetime, timezone, timedelta
import logging
import sys
import argparse
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import aiohttp, use requests fallback if not available
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logger.warning("aiohttp not available, falling back to synchronous requests")

@dataclass
class LoadTestConfig:
    """Load test configuration"""
    base_url: str
    concurrent_users: int = 10
    test_duration_seconds: int = 60
    ramp_up_seconds: int = 10
    endpoints_to_test: List[str] = None
    user_credentials: List[Tuple[str, str]] = None
    think_time_seconds: float = 1.0
    
    def __post_init__(self):
        if self.endpoints_to_test is None:
            self.endpoints_to_test = [
                '/',
                '/api/questions',
                '/api/leaderboard',
                '/login',
                '/register',
                '/game',
                '/profile'
            ]
        
        if self.user_credentials is None:
            self.user_credentials = [
                ('testuser1', 'password123'),
                ('testuser2', 'password123'),
                ('code_monkey', 'banana123'),
            ]

@dataclass
class RequestResult:
    """Result of a single request"""
    endpoint: str
    status_code: int
    response_time: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    response_size: int = 0

@dataclass
class LoadTestResults:
    """Comprehensive load test results"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_duration: float
    requests_per_second: float
    average_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    endpoint_stats: Dict[str, Dict[str, Any]]
    error_summary: Dict[str, int]
    throughput_over_time: List[Dict[str, Any]]

class LoadTester:
    """Advanced load testing framework"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results: List[RequestResult] = []
        self.session_tokens: Dict[str, str] = {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
    async def run_load_test(self) -> LoadTestResults:
        """Run comprehensive load test"""
        logger.info(f"Starting load test with {self.config.concurrent_users} concurrent users")
        logger.info(f"Test duration: {self.config.test_duration_seconds}s")
        logger.info(f"Target URL: {self.config.base_url}")
        
        self.start_time = datetime.now(timezone.utc)
        
        # Setup user sessions
        self._setup_user_sessions_sync()
        
        if AIOHTTP_AVAILABLE:
            # Use async implementation
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=100)
            ) as session:
                
                tasks = []
                for user_id in range(self.config.concurrent_users):
                    task = asyncio.create_task(
                        self._simulate_user_behavior(session, user_id)
                    )
                    tasks.append(task)
                    
                    if self.config.ramp_up_seconds > 0:
                        await asyncio.sleep(
                            self.config.ramp_up_seconds / self.config.concurrent_users
                        )
                
                await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Use synchronous implementation with threading
            self._run_sync_load_test()
        
        self.end_time = datetime.now(timezone.utc)
        return self._generate_results()
    
    def _setup_user_sessions_sync(self):
        """Set up authenticated user sessions synchronously"""
        for username, password in self.config.user_credentials:
            try:
                # Register user if needed
                register_data = {
                    'username': username,
                    'email': f"{username}@test.com",
                    'password': password
                }
                
                register_url = urljoin(self.config.base_url, '/register')
                requests.post(register_url, json=register_data, timeout=10)
                
                # Login and get session token
                login_data = {'username': username, 'password': password}
                login_url = urljoin(self.config.base_url, '/login')
                
                response = requests.post(login_url, json=login_data, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'session_token' in data:
                        self.session_tokens[username] = data['session_token']
                    logger.info(f"User {username} logged in successfully")
                else:
                    logger.warning(f"Failed to login user {username}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error setting up user {username}: {e}")
    
    def _run_sync_load_test(self):
        """Run load test using synchronous requests and threading"""
        with ThreadPoolExecutor(max_workers=self.config.concurrent_users) as executor:
            futures = []
            
            for user_id in range(self.config.concurrent_users):
                future = executor.submit(self._simulate_user_behavior_sync, user_id)
                futures.append(future)
                
                # Ramp up delay
                if self.config.ramp_up_seconds > 0:
                    time.sleep(self.config.ramp_up_seconds / self.config.concurrent_users)
            
            # Wait for all to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"User simulation error: {e}")
    
    def _simulate_user_behavior_sync(self, user_id: int):
        """Simulate user behavior synchronously"""
        end_time = self.start_time + timedelta(seconds=self.config.test_duration_seconds)
        user_session_token = None
        
        if self.config.user_credentials:
            username = self.config.user_credentials[user_id % len(self.config.user_credentials)][0]
            user_session_token = self.session_tokens.get(username)
        
        while datetime.now(timezone.utc) < end_time:
            self._simulate_user_journey_sync(user_id, user_session_token)
            time.sleep(self.config.think_time_seconds)
    
    def _simulate_user_journey_sync(self, user_id: int, session_token: Optional[str]):
        """Simulate user journey synchronously"""
        journeys = [
            ['/', '/api/questions', '/api/leaderboard'],
            ['/', '/game', '/api/questions', '/api/questions', '/api/leaderboard'],
            ['/', '/profile', '/api/leaderboard'],
            ['/', '/api/questions', '/game', '/profile', '/api/leaderboard']
        ]
        
        journey = random.choice(journeys)
        
        for endpoint in journey:
            self._make_request_sync(endpoint, user_id, session_token)
            time.sleep(random.uniform(0.1, 0.5))
    
    def _make_request_sync(self, endpoint: str, user_id: int, session_token: Optional[str]):
        """Make HTTP request synchronously"""
        url = urljoin(self.config.base_url, endpoint)
        headers = {}
        
        if session_token:
            headers['Authorization'] = f'Bearer {session_token}'
        
        start_time = time.time()
        timestamp = datetime.now(timezone.utc)
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response_time = time.time() - start_time
            
            result = RequestResult(
                endpoint=endpoint,
                status_code=response.status_code,
                response_time=response_time,
                timestamp=timestamp,
                success=200 <= response.status_code < 400,
                response_size=len(response.content)
            )
            
            self.results.append(result)
            
        except Exception as e:
            response_time = time.time() - start_time
            result = RequestResult(
                endpoint=endpoint,
                status_code=0,
                response_time=response_time,
                timestamp=timestamp,
                success=False,
                error_message=str(e)
            )
            
            self.results.append(result)

    async def _setup_user_sessions(self):
        """Set up authenticated user sessions"""
        async with aiohttp.ClientSession() as session:
            for username, password in self.config.user_credentials:
                try:
                    # Register user if needed
                    register_data = {
                        'username': username,
                        'email': f"{username}@test.com",
                        'password': password
                    }
                    
                    register_url = urljoin(self.config.base_url, '/register')
                    async with session.post(register_url, json=register_data) as resp:
                        # Registration may fail if user exists - that's OK
                        pass
                    
                    # Login and get session token
                    login_data = {'username': username, 'password': password}
                    login_url = urljoin(self.config.base_url, '/login')
                    
                    async with session.post(login_url, json=login_data) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if 'session_token' in data:
                                self.session_tokens[username] = data['session_token']
                            logger.info(f"User {username} logged in successfully")
                        else:
                            logger.warning(f"Failed to login user {username}: {resp.status}")
                            
                except Exception as e:
                    logger.error(f"Error setting up user {username}: {e}")
    
    async def _simulate_user_behavior(self, session: aiohttp.ClientSession, user_id: int):
        """Simulate realistic user behavior patterns"""
        end_time = self.start_time + timedelta(seconds=self.config.test_duration_seconds)
        user_session_token = None
        
        # Get session token for this user
        if self.config.user_credentials:
            username = self.config.user_credentials[user_id % len(self.config.user_credentials)][0]
            user_session_token = self.session_tokens.get(username)
        
        while datetime.now(timezone.utc) < end_time:
            # Simulate user journey
            await self._simulate_user_journey(session, user_id, user_session_token)
            
            # Think time between actions
            await asyncio.sleep(self.config.think_time_seconds)
    
    async def _simulate_user_journey(self, session: aiohttp.ClientSession, user_id: int, session_token: Optional[str]):
        """Simulate a realistic user journey"""
        # Common user journey patterns
        journeys = [
            # Quick browse
            ['/', '/api/questions', '/api/leaderboard'],
            # Game session
            ['/', '/game', '/api/questions', '/api/questions', '/api/leaderboard'],
            # Profile check
            ['/', '/profile', '/api/leaderboard'],
            # Full journey
            ['/', '/api/questions', '/game', '/profile', '/api/leaderboard']
        ]
        
        # Select random journey
        journey = random.choice(journeys)
        
        for endpoint in journey:
            await self._make_request(session, endpoint, user_id, session_token)
            
            # Small delay between requests in journey
            await asyncio.sleep(random.uniform(0.1, 0.5))
    
    async def _make_request(self, session: aiohttp.ClientSession, endpoint: str, user_id: int, session_token: Optional[str]):
        """Make HTTP request and record results"""
        url = urljoin(self.config.base_url, endpoint)
        headers = {}
        
        if session_token:
            headers['Authorization'] = f'Bearer {session_token}'
        
        start_time = time.time()
        timestamp = datetime.now(timezone.utc)
        
        try:
            async with session.get(url, headers=headers) as response:
                response_time = time.time() - start_time
                content = await response.read()
                
                result = RequestResult(
                    endpoint=endpoint,
                    status_code=response.status,
                    response_time=response_time,
                    timestamp=timestamp,
                    success=200 <= response.status < 400,
                    response_size=len(content)
                )
                
                self.results.append(result)
                
        except Exception as e:
            response_time = time.time() - start_time
            result = RequestResult(
                endpoint=endpoint,
                status_code=0,
                response_time=response_time,
                timestamp=timestamp,
                success=False,
                error_message=str(e)
            )
            
            self.results.append(result)
    
    def _generate_results(self) -> LoadTestResults:
        """Generate comprehensive test results"""
        if not self.results:
            logger.error("No results to analyze")
            return None
        
        # Basic metrics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests
        
        total_duration = (self.end_time - self.start_time).total_seconds()
        requests_per_second = total_requests / total_duration if total_duration > 0 else 0
        
        # Response time statistics
        response_times = [r.response_time for r in self.results]
        response_times.sort()
        
        average_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Percentiles
        p95_index = int(0.95 * len(response_times))
        p99_index = int(0.99 * len(response_times))
        p95_response_time = response_times[p95_index] if p95_index < len(response_times) else max_response_time
        p99_response_time = response_times[p99_index] if p99_index < len(response_times) else max_response_time
        
        # Endpoint-specific statistics
        endpoint_stats = self._calculate_endpoint_stats()
        
        # Error summary
        error_summary = {}
        for result in self.results:
            if not result.success:
                error_key = f"{result.status_code}: {result.error_message or 'HTTP Error'}"
                error_summary[error_key] = error_summary.get(error_key, 0) + 1
        
        # Throughput over time
        throughput_over_time = self._calculate_throughput_over_time()
        
        return LoadTestResults(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_duration=total_duration,
            requests_per_second=requests_per_second,
            average_response_time=average_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            endpoint_stats=endpoint_stats,
            error_summary=error_summary,
            throughput_over_time=throughput_over_time
        )
    
    def _calculate_endpoint_stats(self) -> Dict[str, Dict[str, Any]]:
        """Calculate per-endpoint statistics"""
        endpoint_stats = {}
        
        # Group results by endpoint
        endpoint_results = {}
        for result in self.results:
            if result.endpoint not in endpoint_results:
                endpoint_results[result.endpoint] = []
            endpoint_results[result.endpoint].append(result)
        
        # Calculate stats for each endpoint
        for endpoint, results in endpoint_results.items():
            response_times = [r.response_time for r in results]
            successful = sum(1 for r in results if r.success)
            
            endpoint_stats[endpoint] = {
                'total_requests': len(results),
                'successful_requests': successful,
                'success_rate': (successful / len(results)) * 100,
                'average_response_time': statistics.mean(response_times),
                'median_response_time': statistics.median(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'total_bytes': sum(r.response_size for r in results)
            }
        
        return endpoint_stats
    
    def _calculate_throughput_over_time(self) -> List[Dict[str, Any]]:
        """Calculate throughput over time in 5-second intervals"""
        if not self.results:
            return []
        
        # Group requests by 5-second intervals
        interval_seconds = 5
        intervals = {}
        
        for result in self.results:
            interval_start = int((result.timestamp - self.start_time).total_seconds() // interval_seconds) * interval_seconds
            
            if interval_start not in intervals:
                intervals[interval_start] = {
                    'timestamp': interval_start,
                    'requests': 0,
                    'successful_requests': 0,
                    'total_response_time': 0.0
                }
            
            intervals[interval_start]['requests'] += 1
            if result.success:
                intervals[interval_start]['successful_requests'] += 1
            intervals[interval_start]['total_response_time'] += result.response_time
        
        # Convert to list and calculate averages
        throughput_data = []
        for interval_start in sorted(intervals.keys()):
            interval_data = intervals[interval_start]
            avg_response_time = interval_data['total_response_time'] / interval_data['requests']
            
            throughput_data.append({
                'timestamp': interval_start,
                'requests_per_second': interval_data['requests'] / interval_seconds,
                'success_rate': (interval_data['successful_requests'] / interval_data['requests']) * 100,
                'average_response_time': avg_response_time
            })
        
        return throughput_data

class LoadTestReporter:
    """Generate comprehensive load test reports"""
    
    @staticmethod
    def print_console_report(results: LoadTestResults, config: LoadTestConfig):
        """Print detailed console report"""
        print("\n" + "="*80)
        print("LOAD TEST RESULTS")
        print("="*80)
        
        print(f"\nTest Configuration:")
        print(f"  Target URL: {config.base_url}")
        print(f"  Concurrent Users: {config.concurrent_users}")
        print(f"  Test Duration: {config.test_duration_seconds}s")
        print(f"  Ramp-up Time: {config.ramp_up_seconds}s")
        
        print(f"\nOverall Performance:")
        print(f"  Total Requests: {results.total_requests:,}")
        print(f"  Successful Requests: {results.successful_requests:,}")
        print(f"  Failed Requests: {results.failed_requests:,}")
        print(f"  Success Rate: {(results.successful_requests/results.total_requests)*100:.1f}%")
        print(f"  Requests/Second: {results.requests_per_second:.2f}")
        
        print(f"\nResponse Time Statistics:")
        print(f"  Average: {results.average_response_time*1000:.1f}ms")
        print(f"  Median: {results.median_response_time*1000:.1f}ms")
        print(f"  95th Percentile: {results.p95_response_time*1000:.1f}ms")
        print(f"  99th Percentile: {results.p99_response_time*1000:.1f}ms")
        print(f"  Min: {results.min_response_time*1000:.1f}ms")
        print(f"  Max: {results.max_response_time*1000:.1f}ms")
        
        print(f"\nEndpoint Performance:")
        for endpoint, stats in results.endpoint_stats.items():
            print(f"  {endpoint}:")
            print(f"    Requests: {stats['total_requests']:,}")
            print(f"    Success Rate: {stats['success_rate']:.1f}%")
            print(f"    Avg Response Time: {stats['average_response_time']*1000:.1f}ms")
            print(f"    Total Bytes: {stats['total_bytes']:,}")
        
        if results.error_summary:
            print(f"\nError Summary:")
            for error, count in results.error_summary.items():
                print(f"  {error}: {count} occurrences")
        
        print("\n" + "="*80)
    
    @staticmethod
    def generate_json_report(results: LoadTestResults, config: LoadTestConfig, filename: str = None):
        """Generate detailed JSON report"""
        if filename is None:
            filename = f"load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            'test_config': {
                'base_url': config.base_url,
                'concurrent_users': config.concurrent_users,
                'test_duration_seconds': config.test_duration_seconds,
                'ramp_up_seconds': config.ramp_up_seconds,
                'endpoints_tested': config.endpoints_to_test
            },
            'test_results': {
                'total_requests': results.total_requests,
                'successful_requests': results.successful_requests,
                'failed_requests': results.failed_requests,
                'success_rate': (results.successful_requests / results.total_requests) * 100,
                'requests_per_second': results.requests_per_second,
                'response_time_stats': {
                    'average_ms': results.average_response_time * 1000,
                    'median_ms': results.median_response_time * 1000,
                    'p95_ms': results.p95_response_time * 1000,
                    'p99_ms': results.p99_response_time * 1000,
                    'min_ms': results.min_response_time * 1000,
                    'max_ms': results.max_response_time * 1000
                },
                'endpoint_stats': results.endpoint_stats,
                'error_summary': results.error_summary,
                'throughput_over_time': results.throughput_over_time
            },
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"JSON report saved to: {filename}")
        return filename

async def run_performance_test(
    base_url: str = "http://localhost:5000",
    concurrent_users: int = 10,
    duration: int = 60,
    output_file: str = None
):
    """Run comprehensive performance test"""
    
    config = LoadTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration_seconds=duration,
        ramp_up_seconds=min(10, duration // 6)  # 10s or 1/6 of duration
    )
    
    tester = LoadTester(config)
    results = await tester.run_load_test()
    
    if results:
        # Print console report
        LoadTestReporter.print_console_report(results, config)
        
        # Generate JSON report
        if output_file:
            LoadTestReporter.generate_json_report(results, config, output_file)
        else:
            LoadTestReporter.generate_json_report(results, config)
        
        return results
    else:
        logger.error("Load test failed to generate results")
        return None

def run_quick_smoke_test(base_url: str = "http://localhost:5000"):
    """Run quick smoke test to verify basic functionality"""
    logger.info("Running quick smoke test...")
    
    endpoints = ['/', '/api/questions', '/api/leaderboard']
    results = []
    
    for endpoint in endpoints:
        url = urljoin(base_url, endpoint)
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            
            results.append({
                'endpoint': endpoint,
                'status_code': response.status_code,
                'response_time_ms': response_time * 1000,
                'success': 200 <= response.status_code < 400
            })
            
            logger.info(f"{endpoint}: {response.status_code} ({response_time*1000:.1f}ms)")
            
        except Exception as e:
            results.append({
                'endpoint': endpoint,
                'status_code': 0,
                'response_time_ms': 0,
                'success': False,
                'error': str(e)
            })
            logger.error(f"{endpoint}: ERROR - {e}")
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\nSmoke Test Results: {successful}/{total} endpoints passed")
    
    if successful == total:
        logger.info("✅ All smoke tests passed - system is ready for load testing")
        return True
    else:
        logger.warning(f"⚠️  Only {successful}/{total} smoke tests passed")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python Trivia Load Testing Suite")
    parser.add_argument("--url", default="http://localhost:5000", help="Base URL to test")
    parser.add_argument("--users", type=int, default=10, help="Concurrent users")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--smoke-test", action="store_true", help="Run smoke test only")
    
    args = parser.parse_args()
    
    if args.smoke_test:
        run_quick_smoke_test(args.url)
    else:
        # Run smoke test first
        if run_quick_smoke_test(args.url):
            # Run full load test
            asyncio.run(run_performance_test(
                base_url=args.url,
                concurrent_users=args.users,
                duration=args.duration,
                output_file=args.output
            ))
        else:
            logger.error("Smoke test failed - skipping load test")
            sys.exit(1)