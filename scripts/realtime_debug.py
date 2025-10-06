#!/usr/bin/env python3
"""
Real-time production database diagnostics
"""
import requests
import json
import time

def check_user_exists():
    """Check if user exists by trying to register again"""
    print("🔍 Checking if user exists in production...")
    
    url = "https://pythontrivia.onrender.com/register"
    data = {
        "username": "code_monkey",
        "email": "bholsinger@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"Registration attempt status: {response.status_code}")
        
        try:
            resp_json = response.json()
            print(f"Registration response: {resp_json}")
            
            if response.status_code == 400 and "already exists" in resp_json.get("message", "").lower():
                print("✅ User EXISTS in production database")
                return True
            elif response.status_code == 200:
                print("🆕 User was CREATED (didn't exist before)")
                return True
            else:
                print("❓ Unexpected registration response")
                return False
                
        except:
            print(f"Registration response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration check failed: {e}")
        return False

def test_login_multiple_times():
    """Test login multiple times to see if it's consistent"""
    print("\n🔐 Testing login multiple times...")
    
    url = "https://pythontrivia.onrender.com/login"
    data = {
        "username": "code_monkey",
        "password": "password123"
    }
    
    for i in range(3):
        print(f"\nAttempt {i+1}:")
        try:
            response = requests.post(url, json=data, timeout=30)
            print(f"  Status: {response.status_code}")
            
            try:
                resp_json = response.json()
                print(f"  Response: {resp_json}")
            except:
                print(f"  Response text: {response.text[:100]}")
                
        except Exception as e:
            print(f"  Error: {e}")
        
        time.sleep(1)  # Wait 1 second between attempts

def test_wrong_credentials():
    """Test with wrong credentials to ensure the endpoint is working"""
    print("\n❌ Testing with wrong credentials...")
    
    url = "https://pythontrivia.onrender.com/login"
    
    test_cases = [
        {"username": "wrong_user", "password": "password123"},
        {"username": "code_monkey", "password": "wrong_password"},
        {"username": "", "password": ""},
    ]
    
    for i, data in enumerate(test_cases):
        print(f"\nWrong credentials test {i+1}: {data}")
        try:
            response = requests.post(url, json=data, timeout=30)
            print(f"  Status: {response.status_code}")
            
            try:
                resp_json = response.json()
                print(f"  Response: {resp_json}")
            except:
                print(f"  Response text: {response.text[:100]}")
                
        except Exception as e:
            print(f"  Error: {e}")

def check_session_handling():
    """Test if session cookies affect login"""
    print("\n🍪 Testing session handling...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Try login with session
    url = "https://pythontrivia.onrender.com/login"
    data = {
        "username": "code_monkey",
        "password": "password123"
    }
    
    print("Login with session object:")
    try:
        response = session.post(url, json=data, timeout=30)
        print(f"  Status: {response.status_code}")
        print(f"  Cookies: {dict(response.cookies)}")
        
        try:
            resp_json = response.json()
            print(f"  Response: {resp_json}")
        except:
            print(f"  Response text: {response.text[:100]}")
            
    except Exception as e:
        print(f"  Error: {e}")

def create_user_and_test_immediately():
    """Create user and test login immediately"""
    print("\n⚡ Creating user and testing login immediately...")
    
    # Step 1: Create user
    register_url = "https://pythontrivia.onrender.com/register"
    login_url = "https://pythontrivia.onrender.com/login"
    
    data = {
        "username": "test_user_" + str(int(time.time())),  # Unique username
        "email": f"test{int(time.time())}@example.com",
        "password": "testpass123"
    }
    
    print(f"Creating user: {data['username']}")
    
    try:
        # Register
        reg_response = requests.post(register_url, json=data, timeout=30)
        print(f"  Registration status: {reg_response.status_code}")
        
        if reg_response.status_code == 200:
            print("  ✅ User created successfully")
            
            # Immediately try login
            login_data = {
                "username": data["username"],
                "password": data["password"]
            }
            
            print(f"  Testing login for: {login_data['username']}")
            login_response = requests.post(login_url, json=login_data, timeout=30)
            print(f"  Login status: {login_response.status_code}")
            
            try:
                login_resp_json = login_response.json()
                print(f"  Login response: {login_resp_json}")
                
                if login_response.status_code == 200:
                    print("  ✅ Login works immediately after registration")
                    return True
                else:
                    print("  ❌ Login failed immediately after registration")
                    return False
                    
            except:
                print(f"  Login response text: {login_response.text[:100]}")
                return False
        else:
            print(f"  ❌ User creation failed: {reg_response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 REAL-TIME PRODUCTION DIAGNOSTICS")
    print("=" * 50)
    
    # Step 1: Check if code_monkey user exists
    user_exists = check_user_exists()
    
    # Step 2: Test login multiple times
    test_login_multiple_times()
    
    # Step 3: Test wrong credentials (should consistently fail)
    test_wrong_credentials()
    
    # Step 4: Test session handling
    check_session_handling()
    
    # Step 5: Create fresh user and test immediately
    fresh_user_works = create_user_and_test_immediately()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print(f"  User exists: {user_exists}")
    print(f"  Fresh user login works: {fresh_user_works}")
    print("\n💡 DIAGNOSIS:")
    
    if fresh_user_works and not user_exists:
        print("  🔍 Database is being reset between sessions")
        print("  🔧 Need to investigate Render database persistence")
    elif user_exists and fresh_user_works:
        print("  🔍 code_monkey user might have corrupted password hash")
        print("  🔧 Try using the fresh test user instead")
    else:
        print("  🔍 There's a deeper issue with the login endpoint")
        print("  🔧 Need to check server logs and configuration")