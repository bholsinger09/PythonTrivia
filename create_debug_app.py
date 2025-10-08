#!/usr/bin/env python3
"""
Create a minimal working version of app.py to test locally
"""

import shutil

# Backup current app.py
shutil.copy('app.py', 'app_debug_backup.py')
print("📋 Created backup: app_debug_backup.py")

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Comment out problematic imports and decorators temporarily
replacements = [
    # Comment out performance monitoring imports
    ('from performance_monitoring import (', '# TEMP DISABLED: from performance_monitoring import ('),
    ('    track_request_performance, track_database_performance,', '    # track_request_performance, track_database_performance,'),
    ('    create_performance_monitoring_routes, performance_metrics', '    # create_performance_monitoring_routes, performance_metrics'),
    
    # Comment out performance monitoring decorators
    ('@track_request_performance', '# TEMP DISABLED: @track_request_performance'),
    ('@track_database_performance', '# TEMP DISABLED: @track_database_performance'),
    
    # Comment out performance monitoring calls
    ('create_performance_monitoring_routes(app)', '# TEMP DISABLED: create_performance_monitoring_routes(app)'),
    ('performance_metrics.record_error', '# TEMP DISABLED: performance_metrics.record_error'),
]

for old, new in replacements:
    content = content.replace(old, new)

# Write the temporary version
with open('app_debug.py', 'w') as f:
    f.write(content)

print("✅ Created app_debug.py with performance monitoring disabled")

# Test import
print("\n🧪 Testing app_debug.py import...")
try:
    import sys
    if 'app_debug' in sys.modules:
        del sys.modules['app_debug']
    
    import app_debug
    app = app_debug.app
    
    print("✅ Import successful!")
    
    routes = list(app.url_map.iter_rules())
    print(f"📋 Total routes: {len(routes)}")
    
    # Check for our specific routes
    route_strings = [str(rule.rule) for rule in routes]
    print(f"🔍 simple-debug: {'/simple-debug' in route_strings}")
    print(f"🔑 login: {'/login' in route_strings}")
    print(f"🚪 logout: {'/logout' in route_strings}")
    
    # List first 20 routes
    print(f"\n📍 First 20 routes:")
    for rule in sorted(routes, key=lambda x: x.rule)[:20]:
        print(f"  {rule.rule} -> {rule.endpoint}")
    
except Exception as e:
    print(f"❌ Import still failed: {e}")
    import traceback
    traceback.print_exc()