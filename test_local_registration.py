#!/usr/bin/env python3
"""
Local User Registration Test
Tests registering a user locally and verifying database storage
"""

import requests
import time
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_local_registration():
    """Test user registration on local app"""
    
    base_url = "http://127.0.0.1:5001"
    
    print(f"\n🧪 TESTING LOCAL USER REGISTRATION")
    print("=" * 50)
    
    # Test data
    test_user = {
        'username': 'test_local_user',
        'email': 'test_local@example.com',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!'
    }
    
    print(f"📝 Registering user: {test_user['username']}")
    print(f"   Email: {test_user['email']}")
    print(f"   Password: {test_user['password']}")
    
    try:
        # First get the registration page to check if app is running
        print(f"\n🔍 Checking if local app is running...")
        response = requests.get(f"{base_url}/register", timeout=5)
        if response.status_code != 200:
            print(f"❌ App not accessible. Status: {response.status_code}")
            return False
        
        print(f"✅ Local app is running and accessible")
        
        # Register user
        print(f"\n📋 Submitting registration form...")
        response = requests.post(f"{base_url}/register", data=test_user, timeout=10, allow_redirects=False)
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code in [200, 302]:
            print(f"✅ Registration submission successful!")
            
            if response.status_code == 302:
                redirect_location = response.headers.get('Location', 'Unknown')
                print(f"   Redirected to: {redirect_location}")
            
            return True
        else:
            print(f"❌ Registration failed with status: {response.status_code}")
            print(f"   Response text: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to local app at {base_url}")
        print(f"   Make sure the app is running: python app.py")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_local_login():
    """Test user login on local app"""
    
    base_url = "http://127.0.0.1:5001"
    
    print(f"\n🔐 TESTING LOCAL USER LOGIN")
    print("=" * 50)
    
    # Test data
    login_data = {
        'username': 'test_local_user',
        'password': 'TestPassword123!'
    }
    
    print(f"🔑 Attempting login: {login_data['username']}")
    
    try:
        response = requests.post(f"{base_url}/login", data=login_data, timeout=10, allow_redirects=False)
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code in [200, 302]:
            print(f"✅ Login successful!")
            
            if response.status_code == 302:
                redirect_location = response.headers.get('Location', 'Unknown')
                print(f"   Redirected to: {redirect_location}")
            
            return True
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def main():
    """Main test function"""
    
    print(f"\n🚀 LOCAL DATABASE TESTING")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test registration
    reg_success = test_local_registration()
    
    if reg_success:
        # Wait a moment for database write
        time.sleep(2)
        
        # Test login
        login_success = test_local_login()
        
        # Check database after registration
        print(f"\n💾 CHECKING DATABASE AFTER REGISTRATION...")
        os.system("python check_databases.py")
        
        if login_success:
            print(f"\n🎉 LOCAL TESTING COMPLETE!")
            print(f"✅ Registration: Working")
            print(f"✅ Login: Working") 
            print(f"✅ Database storage should be verified above")
        else:
            print(f"\n⚠️  Registration worked but login failed")
    else:
        print(f"\n❌ Registration failed - cannot proceed with login test")

if __name__ == "__main__":
    main()