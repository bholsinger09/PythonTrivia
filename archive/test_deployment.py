#!/usr/bin/env python3
"""
Simple test to verify what's actually deployed
"""
import requests
import json

def test_endpoints():
    base_url = "https://pythontrivia.onrender.com"
    
    endpoints_to_test = [
        "/",
        "/simple-debug", 
        "/debug/routes",
        "/deployment-check",
        "/api/questions",
        "/login",
        "/auth/login",
        "/static/index-direct.html"
    ]
    
    print("🔍 Testing Render deployment endpoints...")
    print("=" * 60)
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            status = response.status_code
            content_type = response.headers.get('content-type', 'unknown')
            
            if status == 200:
                if 'application/json' in content_type:
                    try:
                        data = response.json()
                        if 'version' in data:
                            print(f"✅ {endpoint} -> {status} (Version: {data.get('version')})")
                        else:
                            print(f"✅ {endpoint} -> {status} (JSON response)")
                    except:
                        print(f"✅ {endpoint} -> {status} (JSON parse failed)")
                else:
                    print(f"✅ {endpoint} -> {status} (HTML/other)")
            elif status == 404:
                try:
                    error_data = response.json()
                    print(f"❌ {endpoint} -> {status} ({error_data.get('error', 'Not found')})")
                except:
                    print(f"❌ {endpoint} -> {status} (404 - HTML response)")
            else:
                print(f"⚠️  {endpoint} -> {status}")
                
        except Exception as e:
            print(f"💥 {endpoint} -> ERROR: {str(e)}")
    
    print("=" * 60)
    
    # Test specific debug info
    try:
        response = requests.get(f"{base_url}/api/questions")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 API working: {len(data.get('questions', []))} questions available")
        else:
            print(f"📊 API status: {response.status_code}")
    except Exception as e:
        print(f"📊 API error: {e}")

if __name__ == "__main__":
    test_endpoints()