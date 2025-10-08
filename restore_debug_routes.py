#!/usr/bin/env python3
"""
Restore missing debug routes to app.py
"""

print("🔧 Restoring missing debug routes...")

# Read current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Define the debug routes to add
simple_debug_route = '''
@app.route('/simple-debug')
def simple_debug():
    """Simple debug endpoint to check deployment and route registration"""
    from datetime import datetime
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(str(rule.rule))
    
    return jsonify({
        'message': 'Simple debug working on Render',
        'timestamp': datetime.now().isoformat(),
        'total_routes': len(routes),
        'has_login_route': '/login' in routes,
        'sample_routes': sorted(routes)[:15],
        'login_routes': [r for r in routes if 'login' in r.lower()],
        'debug_routes': [r for r in routes if 'debug' in r.lower()],
        'deployment_info': {
            'version': 'simple-debug-v1',
            'flask_debug': app.debug,
            'flask_env': app.config.get('ENV', 'not-set')
        }
    })

'''

deployment_check_route = '''
@app.route('/deployment-check')
def deployment_check():
    """Comprehensive deployment debugging endpoint"""
    from datetime import datetime
    import os
    
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'rule': str(rule.rule),
            'endpoint': rule.endpoint,
            'methods': list(rule.methods)
        })
    
    return jsonify({
        'status': 'deployment-check-working',
        'timestamp': datetime.now().isoformat(),
        'environment': {
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'not-set'),
            'FLASK_DEBUG': os.environ.get('FLASK_DEBUG', 'not-set'),
            'PORT': os.environ.get('PORT', 'not-set'),
            'RENDER': os.environ.get('RENDER', 'not-set')
        },
        'flask_config': {
            'DEBUG': app.debug,
            'ENV': app.config.get('ENV', 'not-set'),
            'SECRET_KEY_SET': bool(app.config.get('SECRET_KEY'))
        },
        'route_analysis': {
            'total_routes': len(routes),
            'routes': routes
        }
    })

'''

# Find a good place to insert - right before if __name__ == '__main__':
if "if __name__ == '__main__':" in content:
    # Insert before the main block
    content = content.replace(
        "if __name__ == '__main__':",
        simple_debug_route + deployment_check_route + "if __name__ == '__main__':"
    )
    print("✅ Added debug routes before main block")
else:
    # Just append at the end
    content += simple_debug_route + deployment_check_route
    print("✅ Added debug routes at end of file")

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Routes restored")

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
    
    if '/simple-debug' in route_paths:
        print("🎉 /simple-debug route is now working!")
    
except Exception as e:
    print(f"❌ Import still failed: {e}")
    import traceback
    traceback.print_exc()