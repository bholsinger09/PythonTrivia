#!/usr/bin/env python3
"""
Comprehensive cleanup script to fix all duplicate functions in app.py
"""

import re

def clean_app_py():
    print("🔧 Cleaning up app.py duplicates...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    original_length = len(content.split('\n'))
    print(f"📊 Original file: {original_length} lines")
    
    # Find and remove the second check_session function (the one without proper route)
    # Pattern: from @app.route('/api/session-check') to the end of that function
    pattern1 = r'@app\.route\(\'/api/session-check\'\)[^@]*?@user_rate_limit[^@]*?@track_request_performance[^d]*?def check_session\(\):[^@]*?(?=@app\.route|$)'
    
    matches = re.findall(pattern1, content, re.DOTALL)
    if matches:
        print(f"🗑️  Found {len(matches)} duplicate check_session to remove")
        content = re.sub(pattern1, '', content, flags=re.DOTALL)
    
    # Find and remove duplicate seed_basic_questions functions
    # Keep only the first one, remove subsequent ones
    pattern2 = r'@app\.route\(\'/api/seed-questions\'[^@]*?@user_rate_limit[^@]*?@track_request_performance[^d]*?def seed_basic_questions\(\):[^@]*?(?=@app\.route|@user_rate_limit|def |$)'
    
    matches2 = re.findall(pattern2, content, re.DOTALL)
    if len(matches2) > 1:
        print(f"🗑️  Found {len(matches2)} seed_basic_questions, keeping first, removing {len(matches2)-1}")
        # Remove all but the first occurrence
        for i in range(1, len(matches2)):
            content = content.replace(matches2[i], '', 1)
    
    # Clean up multiple blank lines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Write cleaned content
    with open('app.py', 'w') as f:
        f.write(content)
    
    new_length = len(content.split('\n'))
    print(f"📊 Cleaned file: {new_length} lines (removed {original_length - new_length} lines)")
    
    return True

if __name__ == '__main__':
    clean_app_py()
    
    # Test the import
    print("\n🧪 Testing import after cleanup...")
    try:
        import sys
        # Remove app from cache if it exists
        if 'app' in sys.modules:
            del sys.modules['app']
        
        from app import app
        print("✅ Import successful!")
        
        routes = list(app.url_map.iter_rules())
        print(f"📋 Total routes: {len(routes)}")
        
        # Check for our specific routes
        route_strings = [str(rule.rule) for rule in routes]
        print(f"🔍 simple-debug: {'/simple-debug' in route_strings}")
        print(f"🔑 login: {'/login' in route_strings}")
        
    except Exception as e:
        print(f"❌ Import still failed: {e}")
        import traceback
        traceback.print_exc()