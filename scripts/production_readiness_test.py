#!/usr/bin/env python3
"""
Production-Ready Test Suite for Python Trivia
Final comprehensive test report and validation
"""

import pytest
import sqlite3
import os
import requests
from datetime import datetime

# Import app and models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User
from config import TestingConfig

def run_production_readiness_tests():
    """Run comprehensive production readiness tests"""
    
    print("🚀 PRODUCTION READINESS TEST SUITE")
    print("=" * 70)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # Test 1: Database Connectivity and Schema
    print("🗄️  TEST 1: Database Schema and Connectivity")
    print("-" * 50)
    
    try:
        with app.app_context():
            db.create_all()
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['users', 'questions', 'game_sessions', 'answers', 'scores']
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if not missing_tables:
                print("✅ All required database tables exist")
                results.append(("Database Schema", "PASS"))
            else:
                print(f"⚠️  Missing tables: {missing_tables}")
                results.append(("Database Schema", "PARTIAL"))
            
            # Test user operations
            test_user = User(
                username='prod_test_user',
                email='prod@example.com',
                password_hash='test_hash'
            )
            db.session.add(test_user)
            db.session.commit()
            
            retrieved = User.query.filter_by(username='prod_test_user').first()
            if retrieved:
                print("✅ Database CRUD operations working")
                results.append(("Database CRUD", "PASS"))
                
                # Cleanup
                db.session.delete(retrieved)
                db.session.commit()
            else:
                print("❌ Database CRUD operations failed")
                results.append(("Database CRUD", "FAIL"))
    
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        results.append(("Database Schema", "FAIL"))
        results.append(("Database CRUD", "FAIL"))
    
    print()
    
    # Test 2: Critical Endpoints
    print("🌐 TEST 2: Critical Endpoint Availability")
    print("-" * 50)
    
    critical_endpoints = [
        ('/', 'Home Page'),
        ('/register', 'Registration'),
        ('/login', 'Login'),
        ('/game', 'Game Page'),
        ('/api/game-stats', 'Game Stats API')
    ]
    
    with app.test_client() as client:
        for endpoint, name in critical_endpoints:
            try:
                response = client.get(endpoint)
                if response.status_code == 200:
                    print(f"✅ {name} ({endpoint}) - OK")
                    results.append((f"Endpoint {name}", "PASS"))
                else:
                    print(f"⚠️  {name} ({endpoint}) - Status {response.status_code}")
                    results.append((f"Endpoint {name}", "PARTIAL"))
            except Exception as e:
                print(f"❌ {name} ({endpoint}) - Error: {e}")
                results.append((f"Endpoint {name}", "FAIL"))
    
    print()
    
    # Test 3: User Authentication System
    print("🔐 TEST 3: Authentication System")
    print("-" * 50)
    
    try:
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                
                # Test password hashing
                from werkzeug.security import generate_password_hash, check_password_hash
                test_password = 'secure_test_password_123'
                hashed = generate_password_hash(test_password)
                
                if check_password_hash(hashed, test_password):
                    print("✅ Password hashing/verification working")
                    results.append(("Password Security", "PASS"))
                else:
                    print("❌ Password hashing/verification failed")
                    results.append(("Password Security", "FAIL"))
                
                # Test user creation
                auth_test_user = User(
                    username='auth_test',
                    email='auth@example.com',
                    password_hash=hashed
                )
                db.session.add(auth_test_user)
                db.session.commit()
                
                # Test user retrieval
                retrieved = User.query.filter_by(username='auth_test').first()
                if retrieved and check_password_hash(retrieved.password_hash, test_password):
                    print("✅ User authentication flow working")
                    results.append(("Authentication Flow", "PASS"))
                    
                    # Cleanup
                    db.session.delete(retrieved)
                    db.session.commit()
                else:
                    print("❌ User authentication flow failed")
                    results.append(("Authentication Flow", "FAIL"))
    
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        results.append(("Password Security", "FAIL"))
        results.append(("Authentication Flow", "FAIL"))
    
    print()
    
    # Test 4: Code Monkey User Verification
    print("🐒 TEST 4: Code Monkey User Status")
    print("-" * 50)
    
    try:
        db_path = './instance/trivia_dev.db'
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT username, email, created_at FROM users WHERE username = 'code_monkey'")
            user = cursor.fetchone()
            
            if user:
                print(f"✅ code_monkey user exists: {user[1]}")
                print(f"   Created: {user[2]}")
                results.append(("Code Monkey User", "PASS"))
            else:
                print("⚠️  code_monkey user not found in development database")
                results.append(("Code Monkey User", "MISSING"))
            
            conn.close()
        else:
            print("⚠️  Development database file not found")
            results.append(("Code Monkey User", "NO_DB"))
    
    except Exception as e:
        print(f"❌ Code monkey verification failed: {e}")
        results.append(("Code Monkey User", "FAIL"))
    
    print()
    
    # Test 5: Production Environment Status
    print("🌍 TEST 5: Production Environment")
    print("-" * 50)
    
    production_url = 'https://pythontrivia-production.up.railway.app'
    
    try:
        response = requests.get(production_url, timeout=10)
        if response.status_code == 200:
            print("✅ Production environment accessible")
            results.append(("Production Access", "PASS"))
        else:
            print(f"⚠️  Production returned status {response.status_code}")
            results.append(("Production Access", "PARTIAL"))
    except requests.RequestException as e:
        print(f"❌ Production environment not accessible: {e}")
        results.append(("Production Access", "FAIL"))
    
    print()
    
    # Final Report
    print("📊 FINAL PRODUCTION READINESS REPORT")
    print("=" * 70)
    
    pass_count = sum(1 for _, status in results if status == "PASS")
    partial_count = sum(1 for _, status in results if status == "PARTIAL")
    fail_count = sum(1 for _, status in results if status in ["FAIL", "MISSING", "NO_DB"])
    
    for test_name, status in results:
        status_icon = {
            "PASS": "✅",
            "PARTIAL": "⚠️ ",
            "FAIL": "❌",
            "MISSING": "🚫",
            "NO_DB": "💾"
        }.get(status, "❓")
        
        print(f"{status_icon} {test_name:<30} | {status}")
    
    print("-" * 70)
    print(f"📈 SUMMARY:")
    print(f"   ✅ Passed: {pass_count}")
    print(f"   ⚠️  Partial: {partial_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   📊 Total: {len(results)}")
    
    success_rate = (pass_count + partial_count * 0.5) / len(results) * 100
    print(f"   🎯 Success Rate: {success_rate:.1f}%")
    
    print()
    if success_rate >= 80:
        print("🎉 APPLICATION IS PRODUCTION READY!")
        print("   Your Python Trivia app is in excellent shape for deployment.")
    elif success_rate >= 60:
        print("🚀 APPLICATION IS MOSTLY READY")
        print("   A few minor issues to address, but core functionality is solid.")
    else:
        print("🔧 APPLICATION NEEDS WORK")
        print("   Several critical issues need to be addressed before production.")
    
    print()
    print("📋 NEXT STEPS:")
    if fail_count == 0:
        print("   • Deploy to production with confidence")
        print("   • Set up monitoring and logging")
        print("   • Consider adding more advanced features")
    else:
        print("   • Fix failing tests before deployment")
        print("   • Re-run tests after fixes")
        print("   • Review error logs for additional issues")
    
    return success_rate >= 70

if __name__ == '__main__':
    success = run_production_readiness_tests()
    sys.exit(0 if success else 1)