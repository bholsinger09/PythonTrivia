#!/usr/bin/env python3
"""
Completely remove all performance monitoring decorators and imports
"""

import shutil

print("🔧 Comprehensive removal of performance monitoring...")

# Backup current app.py
shutil.copy('app.py', 'app_before_comprehensive_fix.py')
print("📋 Created backup: app_before_comprehensive_fix.py")

# Read the current app.py
with open('app.py', 'r') as f:
    lines = f.readlines()

print(f"📄 Original file has {len(lines)} lines")

# Process line by line
cleaned_lines = []
skip_next_function = False
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Skip import lines related to performance monitoring
    if ('from performance_monitoring import' in line or 
        'import performance_monitoring' in line or
        'performance_monitoring' in line and 'import' in line):
        print(f"🚫 Removing import at line {i+1}: {stripped}")
        # Skip this line and any continuation lines
        while i < len(lines) and (not lines[i].strip().endswith(')') or lines[i].strip().startswith('    ')):
            i += 1
        i += 1
        continue
    
    # Skip performance monitoring decorators
    if (stripped == '@track_request_performance' or 
        stripped == '@track_database_performance'):
        print(f"🚫 Removing decorator at line {i+1}: {stripped}")
        i += 1
        continue
    
    # Skip performance monitoring function calls
    if ('create_performance_monitoring_routes' in line or
        'performance_metrics.record_error' in line):
        print(f"🚫 Removing function call at line {i+1}: {stripped}")
        cleaned_lines.append(f"    # REMOVED: {stripped}\n")
        i += 1
        continue
    
    # Keep the line
    cleaned_lines.append(line)
    i += 1

print(f"📄 Cleaned file has {len(cleaned_lines)} lines (removed {len(lines) - len(cleaned_lines)} lines)")

# Write the cleaned version
with open('app.py', 'w') as f:
    f.writelines(cleaned_lines)

print("✅ Comprehensive cleanup complete")

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
    print(f"🔍 Has /simple-debug: {'/simple-debug' in route_paths}")
    print(f"🔑 Has /login: {'/login' in route_paths}")
    print(f"🚪 Has /logout: {'/logout' in route_paths}")
    
    # Show key routes
    key_routes = ['/login', '/logout', '/simple-debug', '/deployment-check']
    for route in key_routes:
        if route in route_paths:
            print(f"✅ {route} registered")
        else:
            print(f"❌ {route} missing")
    
except Exception as e:
    print(f"❌ Import still failed: {e}")
    # Show the specific line that's failing
    import traceback
    traceback.print_exc()