#!/usr/bin/env python3
"""
Initialize production database with proper user
"""
import requests
import json

def create_permanent_user():
    """Create a user that should persist in the PostgreSQL database"""
    
    print("🔧 Creating permanent user in production PostgreSQL database...")
    
    # The production app should be using PostgreSQL based on render.yaml
    register_url = "https://pythontrivia.onrender.com/register"
    
    user_data = {
        "username": "code_monkey",
        "email": "bholsinger@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(register_url, json=user_data, timeout=30)
        print(f"Registration status: {response.status_code}")
        
        if response.status_code == 200:
            resp_json = response.json()
            print(f"✅ {resp_json['message']}")
            
            # Test login immediately
            print("\n🔐 Testing login immediately...")
            login_url = "https://pythontrivia.onrender.com/login"
            login_response = requests.post(login_url, json=user_data, timeout=30)
            
            print(f"Login status: {login_response.status_code}")
            if login_response.status_code == 200:
                login_resp = login_response.json()
                print(f"✅ {login_resp['message']}")
                print("\n🎯 POSTMAN READY!")
                print("Use these credentials in Postman:")
                print(f"  Username: {user_data['username']}")
                print(f"  Password: {user_data['password']}")
                print(f"  URL: {login_url}")
                
            else:
                print(f"❌ Login failed: {login_response.text}")
                
        elif response.status_code == 400:
            resp_json = response.json()
            if "already exists" in resp_json.get("message", ""):
                print("✅ User already exists - testing login...")
                
                # Test existing user login
                login_url = "https://pythontrivia.onrender.com/login"
                login_response = requests.post(login_url, json=user_data, timeout=30)
                
                print(f"Login status: {login_response.status_code}")
                if login_response.status_code == 200:
                    print("✅ Existing user login works!")
                else:
                    print("❌ Existing user login failed - password may be corrupted")
                    print("🔧 Try creating a new user with different username")
            else:
                print(f"❌ Registration failed: {resp_json}")
        else:
            print(f"❌ Unexpected response: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 PRODUCTION DATABASE INITIALIZER")
    print("=" * 50)
    create_permanent_user()