#!/usr/bin/env python3
"""
Quick fix for the missing route decorator in app.py
"""

# Read the file
with open('app.py', 'r') as f:
    content = f.read()

# Fix the missing route decorator
old_pattern = '''@user_rate_limit
@track_request_performance
def check_session():'''

new_pattern = '''@app.route('/api/session-check')  # Added missing route decorator
@user_rate_limit
@track_request_performance
def check_session():'''

# Only replace the first occurrence (the problematic one)
if old_pattern in content:
    content = content.replace(old_pattern, new_pattern, 1)
    
    # Write back
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed missing route decorator")
else:
    print("❌ Pattern not found")