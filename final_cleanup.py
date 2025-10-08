#!/usr/bin/env python3
"""
Final cleanup to remove ALL performance monitoring decorators
"""

print("🔧 Final cleanup of performance monitoring decorators...")

# Read the entire file
with open('app.py', 'r') as f:
    content = f.read()

# Remove all performance monitoring decorators with any amount of whitespace
import re

# Remove decorators with any whitespace before them
content = re.sub(r'^\s*@track_request_performance\s*$', '', content, flags=re.MULTILINE)
content = re.sub(r'^\s*@track_database_performance\s*$', '', content, flags=re.MULTILINE)

# Remove any blank lines that were left behind
content = re.sub(r'\n\n\n+', '\n\n', content)

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Regex cleanup complete")

# Test import
print("\n🧪 Testing app.py import...")
try:
    import sys
    if 'app' in sys.modules:
        del sys.modules['app']
    
    import app
    flask_app = app.app
    
    print("✅ Import successful!")
    
    routes = list(flask_app.url_map.iter_rules())
    route_paths = [str(rule.rule) for rule in routes]
    
    print(f"📋 Total routes: {len(routes)}")
    
    # Check for our key debugging routes
    key_routes = ['/simple-debug', '/deployment-check', '/login', '/logout']
    for route in key_routes:
        if route in route_paths:
            print(f"✅ {route} registered")
        else:
            print(f"❌ {route} missing")
    
    if '/simple-debug' in route_paths:
        print("🎉 /simple-debug route is now working!")
    
except Exception as e:
    print(f"❌ Import still failed: {e}")
    import traceback
    traceback.print_exc()