#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner
Runs all automated tests for the Python Trivia application
"""

import pytest
import os
import sys
import subprocess
import time
from datetime import datetime

def run_test_suite():
    """Run the complete automated test suite"""
    
    print("🧪 PYTHON TRIVIA - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test categories to run
    test_files = [
        ('🔐 Authentication & Security Tests', 'tests/test_authentication_security.py'),
        ('🗄️  Database Integrity Tests', 'tests/test_database_integrity.py'),
        ('🎮 Game Logic Tests', 'tests/test_game_logic.py'),
    ]
    
    results = []
    total_start_time = time.time()
    
    for test_name, test_file in test_files:
        print(f"Running {test_name}...")
        print("-" * 50)
        
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            results.append((test_name, 'MISSING', 0, 0, 0))
            continue
        
        start_time = time.time()
        
        try:
            # Run pytest on the specific test file
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                test_file,
                '-v',
                '--tb=short',
                '--no-header',
                '--disable-warnings',
                '--quiet'
            ], capture_output=True, text=True, timeout=300)
            
            duration = time.time() - start_time
            
            # Parse results
            if result.returncode == 0:
                status = 'PASSED'
                print(f"✅ {test_name} - All tests passed")
            else:
                status = 'FAILED'
                print(f"❌ {test_name} - Some tests failed")
            
            # Try to extract test counts from output
            output = result.stdout
            failed_count = output.count('FAILED')
            passed_count = output.count('PASSED')
            
            print(f"   Duration: {duration:.2f}s")
            if passed_count > 0:
                print(f"   Passed: {passed_count}")
            if failed_count > 0:
                print(f"   Failed: {failed_count}")
                print("   Error details:")
                print(result.stdout[-500:])  # Show last 500 chars of output
            
            results.append((test_name, status, passed_count, failed_count, duration))
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} - Test timed out (>5 minutes)")
            results.append((test_name, 'TIMEOUT', 0, 0, 300))
        except Exception as e:
            print(f"💥 {test_name} - Test crashed: {e}")
            results.append((test_name, 'ERROR', 0, 0, 0))
        
        print()
    
    # Print summary
    total_duration = time.time() - total_start_time
    
    print("📊 TEST SUITE SUMMARY")
    print("=" * 70)
    
    total_passed = sum(r[2] for r in results)
    total_failed = sum(r[3] for r in results)
    
    for test_name, status, passed, failed, duration in results:
        status_icon = {
            'PASSED': '✅',
            'FAILED': '❌', 
            'MISSING': '🚫',
            'TIMEOUT': '⏰',
            'ERROR': '💥'
        }.get(status, '❓')
        
        print(f"{status_icon} {test_name:<35} | {status:<8} | {duration:>6.1f}s")
    
    print("-" * 70)
    print(f"📈 OVERALL RESULTS:")
    print(f"   Total Tests Passed: {total_passed}")
    print(f"   Total Tests Failed: {total_failed}")
    print(f"   Total Duration: {total_duration:.1f}s")
    
    if total_failed == 0:
        print("🎉 ALL TESTS PASSED! Your application is in great shape!")
    else:
        print(f"⚠️  {total_failed} tests failed. Review the details above.")
    
    print(f"   Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return total_failed == 0

def run_quick_tests():
    """Run a quick subset of critical tests"""
    print("⚡ QUICK TEST SUITE")
    print("=" * 40)
    
    # Critical tests only
    critical_tests = [
        'tests/test_authentication_security.py::TestAuthentication::test_user_registration_success',
        'tests/test_authentication_security.py::TestAuthentication::test_password_hashing_security',
        'tests/test_database_integrity.py::TestDatabaseIntegrity::test_user_model_creation',
        'tests/test_database_integrity.py::TestDatabaseIntegrity::test_user_unique_constraints',
    ]
    
    for test in critical_tests:
        if os.path.exists(test.split('::')[0]):
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                test,
                '-v',
                '--tb=line',
                '--disable-warnings'
            ], capture_output=True, text=True)
            
            status = "✅ PASS" if result.returncode == 0 else "❌ FAIL"
            test_name = test.split('::')[-1]
            print(f"{status} {test_name}")

def check_test_dependencies():
    """Check if all test dependencies are available"""
    print("🔍 CHECKING TEST DEPENDENCIES")
    print("-" * 40)
    
    required_packages = [
        'pytest',
        'flask',
        'sqlalchemy',
        'werkzeug'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("✅ All dependencies available")
    return True

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Python Trivia test suite')
    parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    parser.add_argument('--check-deps', action='store_true', help='Check test dependencies')
    
    args = parser.parse_args()
    
    if args.check_deps:
        check_test_dependencies()
    elif args.quick:
        run_quick_tests()
    else:
        if check_test_dependencies():
            success = run_test_suite()
            sys.exit(0 if success else 1)
        else:
            print("Cannot run tests - missing dependencies")
            sys.exit(1)