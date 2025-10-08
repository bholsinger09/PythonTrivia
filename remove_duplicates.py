#!/usr/bin/env python3
"""
Remove duplicate simple_debug and deployment_check functions
"""

print("🔧 Removing duplicate debug functions...")

with open('app.py', 'r') as f:
    lines = f.readlines()

print(f"📄 File has {len(lines)} lines")

# Find the duplicate functions and remove them
# Keep the first occurrence, remove later ones
cleaned_lines = []
in_simple_debug = False
in_deployment_check = False
simple_debug_count = 0
deployment_check_count = 0
skip_lines = 0

for i, line in enumerate(lines):
    if skip_lines > 0:
        skip_lines -= 1
        continue
        
    if line.strip() == "@app.route('/simple-debug')":
        simple_debug_count += 1
        if simple_debug_count > 1:
            print(f"🚫 Removing duplicate simple_debug at line {i+1}")
            # Skip this route and its function (approximately 20 lines)
            skip_lines = 25
            continue
    
    if line.strip() == "@app.route('/deployment-check')":
        deployment_check_count += 1
        if deployment_check_count > 1:
            print(f"🚫 Removing duplicate deployment_check at line {i+1}")
            # Skip this route and its function (approximately 30 lines)
            skip_lines = 35
            continue
    
    cleaned_lines.append(line)

print(f"📄 Cleaned file has {len(cleaned_lines)} lines (removed {len(lines) - len(cleaned_lines)} lines)")

# Write back
with open('app.py', 'w') as f:
    f.writelines(cleaned_lines)

print("✅ Duplicate removal complete")

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
    key_routes = ['/simple-debug', '/deployment-check', '/login']
    for route in key_routes:
        if route in route_paths:
            print(f"✅ {route} registered")
        else:
            print(f"❌ {route} missing")
    
except Exception as e:
    print(f"❌ Import still failed: {e}")
    import traceback
    traceback.print_exc()