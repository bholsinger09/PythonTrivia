#!/usr/bin/env python3
"""
Debug production login issues
"""
import requests
import json

def test_production_login():
    """Test the production login endpoint"""
    
    # Production URL
    base_url = "https://pythontrivia.onrender.com"
    login_url = f"{base_url}/login"
    
    # Test data
    test_credentials = {
        "username": "code_monkey",
        "password": "password123"
    }
    
    print("🔍 Testing Production Login")
    print("=" * 40)
    print(f"URL: {login_url}")
    print(f"Credentials: {test_credentials}")
    print()
    
    try:
        # Test with JSON payload
        print("1. Testing with JSON payload...")
        response = requests.post(
            login_url,
            json=test_credentials,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Response Text: {response.text}")
        
        print()
        
        # Test with form data
        print("2. Testing with form data...")
        response = requests.post(
            login_url,
            data=test_credentials,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
            allow_redirects=False  # Don't follow redirects to see the response
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Response Text: {response.text[:200]}...")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def print_postman_instructions():
    """Print detailed Postman testing instructions"""
    
    print("\n" + "=" * 60)
    print("📮 POSTMAN TESTING INSTRUCTIONS")
    print("=" * 60)
    
    print("\n🔧 SETUP:")
    print("1. Open Postman")
    print("2. Create a new request")
    print("3. Set method to POST")
    
    print("\n📍 ENDPOINT:")
    print("URL: https://pythontrivia.onrender.com/login")
    
    print("\n📝 TEST 1 - JSON Login:")
    print("Headers:")
    print("  Content-Type: application/json")
    print("\nBody (raw JSON):")
    print(json.dumps({
        "username": "code_monkey",
        "password": "password123"
    }, indent=2))
    
    print("\n📝 TEST 2 - Form Data Login:")
    print("Headers:")
    print("  Content-Type: application/x-www-form-urlencoded")
    print("\nBody (x-www-form-urlencoded):")
    print("  username: code_monkey")
    print("  password: password123")
    
    print("\n✅ EXPECTED SUCCESS RESPONSES:")
    print("JSON Test:")
    print('  Status: 200 OK')
    print('  Body: {"success": true, "message": "Login successful"}')
    print("\nForm Test:")
    print('  Status: 302 Found')
    print('  Location: /game')
    
    print("\n❌ CURRENT ISSUE:")
    print('  Status: 400 Bad Request')
    print('  Body: {"success": false, "message": "Invalid username or password"}')
    
    print("\n🔍 DEBUGGING STEPS:")
    print("1. First, test if user exists by trying to register with same username")
    print("2. If registration fails with 'user exists', then login issue is password")
    print("3. If registration succeeds, then user didn't exist in production DB")

def test_user_registration():
    """Test if we can register the user (to see if they exist)"""
    
    print("\n🔍 Testing User Registration (to check if user exists)")
    print("=" * 60)
    
    register_url = "https://pythontrivia.onrender.com/register"
    
    test_data = {
        "username": "code_monkey",
        "email": "bholsinger@gmail.com", 
        "password": "password123"
    }
    
    try:
        response = requests.post(
            register_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
            
        if response.status_code == 400:
            response_data = response.json()
            if "already exists" in response_data.get("message", "").lower():
                print("✅ User EXISTS in production database")
                print("🔍 Login issue is likely a PASSWORD problem")
            else:
                print("❓ User registration failed for other reason")
        elif response.status_code == 200 or response.status_code == 201:
            print("✅ User CREATED successfully in production database")
            print("🔍 Now try login again")
        else:
            print(f"❓ Unexpected registration response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Registration test failed: {e}")

if __name__ == "__main__":
    print("🚀 Production Login Debugger")
    
    # Test registration first to see if user exists
    test_user_registration()
    
    # Test login
    test_production_login()
    
    # Print Postman instructions
    print_postman_instructions()