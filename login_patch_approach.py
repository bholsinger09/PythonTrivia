#!/usr/bin/env python3
"""
Create a simple hook that ensures code_monkey user exists on first login attempt
"""

# This approach modifies the login function to automatically create the user if it doesn't exist
# This is more reliable than trying to create users during app startup

LOGIN_PATCH = '''
# AUTOMATIC USER CREATION ON LOGIN ATTEMPT
# This code should be inserted into the login route

# After the line: user = UserService.get_user_by_username(username)
# And before the line: if user and user.check_password(password):

# Add this code:
if not user and username == "code_monkey" and password == "password123":
    # Auto-create the essential code_monkey user if it doesn't exist
    try:
        app.logger.info("Creating essential user: code_monkey")
        user = UserService.create_user(username, "bholsinger@gmail.com", password)
        app.logger.info("Essential user created successfully")
    except Exception as e:
        app.logger.error(f"Failed to create essential user: {e}")
'''

print("🔧 LOGIN PATCH APPROACH")
print("="*50)
print("Instead of startup initialization, we can modify the login route")
print("to automatically create the code_monkey user if it doesn't exist.")
print("This ensures the user is created exactly when needed.")
print()
print("Patch to add to login route:")
print(LOGIN_PATCH)