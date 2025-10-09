# Simple script to add minimal debugging to app.py without complex changes

import re

def add_simple_debug_route():
    """Add a simple debug route to app.py right after existing routes"""
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Look for a safe place to insert a debug route - after the logout route
    logout_route_pattern = r"(@app\.route\('/logout'\)\ndef logout_page\(\):[^@]+)"
    
    debug_route = '''
@app.route('/simple-debug')
def simple_debug():
    """Simple debug endpoint to check deployment"""
    from datetime import datetime
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(str(rule.rule))
    
    return jsonify({
        'message': 'Simple debug working',
        'timestamp': datetime.now().isoformat(),
        'total_routes': len(routes),
        'has_login_route': '/login' in routes,
        'sample_routes': routes[:10]
    })

'''
    
    # Insert the debug route after logout
    new_content = re.sub(
        logout_route_pattern,
        r'\1' + debug_route,
        content,
        count=1
    )
    
    if new_content != content:
        with open('app.py', 'w') as f:
            f.write(new_content)
        print("✅ Added simple debug route after logout")
        return True
    else:
        print("❌ Could not find logout route to insert after")
        return False

if __name__ == '__main__':
    add_simple_debug_route()