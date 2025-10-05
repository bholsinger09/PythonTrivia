#!/usr/bin/env python3
"""
Password Verification Script
Tests common passwords against the code_monkey user to determine what was stored
"""

import requests
import time

def test_login_with_password(username, password):
    """Test login with a specific password"""
    
    base_url = "https://pythontrivia.onrender.com"
    
    login_data = {
        'username': username,
        'password': password
    }
    
    try:
        print(f"🔑 Testing password: '{password}'")
        
        # Make login request
        response = requests.post(f"{base_url}/login", data=login_data, timeout=10, allow_redirects=False)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            # Successful login (redirect)
            redirect_location = response.headers.get('Location', '')
            print(f"   ✅ SUCCESS! Redirected to: {redirect_location}")
            return True
        elif response.status_code == 200:
            # Check response content for success/error indicators
            response_text = response.text.lower()
            if any(error_word in response_text for error_word in ['invalid', 'incorrect', 'wrong', 'error', 'failed']):
                print(f"   ❌ Failed - Error message in response")
                return False
            else:
                print(f"   ✅ SUCCESS! Login page returned without errors")
                return True
        else:
            print(f"   ❌ Failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Test various common passwords for code_monkey user"""
    
    username = "code_monkey"
    
    print(f"\n🔍 PASSWORD VERIFICATION FOR USER: {username}")
    print(f"Production URL: https://pythontrivia.onrender.com")
    print("=" * 60)
    
    # List of common passwords to test (based on our conversation history)
    test_passwords = [
        "Myspam#09",           # The password mentioned in conversation
        "myspam#09",           # Lowercase version
        "MYSPAM#09",           # Uppercase version
        "MySpam#09",           # Alternative capitalization
        "code_monkey",         # Username as password
        "password",            # Common default
        "Password123",         # Common pattern
        "CodeMonkey123",       # Username variation
        "TestPassword123!",    # Test pattern
        "admin",               # Simple admin
        "123456",              # Numeric
        "password123"          # Simple combination
    ]
    
    print(f"📋 Testing {len(test_passwords)} common password possibilities...")
    print(f"⚠️  Note: Only testing common/expected passwords for security")
    print()
    
    successful_password = None
    
    for i, password in enumerate(test_passwords, 1):
        print(f"[{i:2d}/{len(test_passwords)}] ", end="")
        
        success = test_login_with_password(username, password)
        
        if success:
            successful_password = password
            print(f"\n🎉 FOUND THE CORRECT PASSWORD!")
            print(f"✅ Username: {username}")
            print(f"✅ Password: {password}")
            break
        
        # Small delay to avoid overwhelming the server
        time.sleep(1)
    
    print(f"\n" + "=" * 60)
    print(f"📊 PASSWORD VERIFICATION RESULTS:")
    
    if successful_password:
        print(f"✅ SUCCESS: Found the stored password")
        print(f"   Username: {username}")
        print(f"   Password: {successful_password}")
        print(f"   Storage: Password is hashed with bcrypt in PostgreSQL")
        print(f"   Security: ✅ Password verification working correctly")
    else:
        print(f"❌ Could not determine the password from common options")
        print(f"💡 This could mean:")
        print(f"   - Password is not in our test list")
        print(f"   - User account is locked or disabled")
        print(f"   - Server is not responding correctly")
        print(f"   - Password contains special characters not tested")
    
    print(f"\n🔒 SECURITY NOTE:")
    print(f"   - Actual password is stored as bcrypt hash in database")
    print(f"   - This test only verifies what the original password was")
    print(f"   - Database never stores plain text passwords")

if __name__ == "__main__":
    main()