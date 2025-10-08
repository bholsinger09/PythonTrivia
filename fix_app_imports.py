#!/usr/bin/env python3
"""
Fix the import issues in app.py by properly handling performance monitoring
"""

import shutil
import re

print("🔧 Fixing app.py import issues...")

# Backup current app.py
shutil.copy('app.py', 'app_before_import_fix.py')
print("📋 Created backup: app_before_import_fix.py")

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Check if performance_monitoring.py exists
import os
performance_file_exists = os.path.exists('performance_monitoring.py')
print(f"🔍 performance_monitoring.py exists: {performance_file_exists}")

if not performance_file_exists:
    print("🚫 performance_monitoring.py not found - removing all references")
    
    # Remove the import block
    import_pattern = r'from performance_monitoring import \(\s*[^)]*\)'
    content = re.sub(import_pattern, '# REMOVED: performance_monitoring imports (file not found)', content, flags=re.MULTILINE | re.DOTALL)
    
    # Remove individual decorators
    content = re.sub(r'@track_request_performance\s*\n', '', content)
    content = re.sub(r'@track_database_performance\s*\n', '', content)
    
    # Remove function calls
    content = re.sub(r'create_performance_monitoring_routes\(app\)', '# REMOVED: create_performance_monitoring_routes(app)', content)
    content = re.sub(r'performance_metrics\.record_error\([^)]*\)', '# REMOVED: performance_metrics.record_error(...)', content)
    
    # Remove any standalone lines with just decorators
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped == '@track_request_performance' or stripped == '@track_database_performance':
            continue  # Skip the decorator line entirely
        cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)

# Write the fixed version
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Fixed app.py - removed performance monitoring references")

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
    
    # Check for debug routes
    debug_routes = [r for r in route_paths if 'debug' in r.lower()]
    print(f"🐛 Debug routes: {debug_routes}")
    
except Exception as e:
    print(f"❌ Import still failed: {e}")
    import traceback
    traceback.print_exc()