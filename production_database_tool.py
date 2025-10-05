#!/usr/bin/env python3
"""
Production Database Access Tool
Direct access to production PostgreSQL database for developer/owner
"""

import os
import requests
import json
from datetime import datetime

class ProductionDatabaseAccess:
    """Access production database through admin endpoints"""
    
    def __init__(self):
        self.base_url = "https://pythontrivia.onrender.com"
        self.admin_key = "admin_secret_key_2025"  # Use your admin key
        
    def get_all_production_users(self):
        """Get all users from production database"""
        
        print(f"\n🌐 PRODUCTION DATABASE - ALL USERS")
        print("=" * 80)
        
        try:
            response = requests.get(f"{self.base_url}/admin/database-status", timeout=15)
            
            if response.status_code == 200:
                print("✅ Production database accessible")
                content = response.text
                print(content)
                
                # Parse user information from response
                lines = content.split('\n')
                users = []
                for line in lines:
                    if '•' in line and '(' in line and ')' in line:
                        # Parse user line: • username (email) - timestamp
                        parts = line.strip().split('•')[1].strip()
                        username_part = parts.split('(')[0].strip()
                        email_part = parts.split('(')[1].split(')')[0]
                        timestamp_part = parts.split('-')[1].strip() if '-' in parts else 'Unknown'
                        
                        users.append({
                            'username': username_part,
                            'email': email_part,
                            'created_at': timestamp_part
                        })
                
                return users
            else:
                print(f"❌ Could not access production database: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error accessing production database: {e}")
            return None
    
    def create_production_user_via_registration(self, username, email, password):
        """Create user in production by simulating registration"""
        
        print(f"\n➕ CREATING PRODUCTION USER: {username}")
        print("=" * 50)
        
        # Use the registration endpoint
        registration_data = {
            'username': username,
            'email': email,
            'password': password,
            'confirm_password': password
        }
        
        try:
            response = requests.post(f"{self.base_url}/register", 
                                   data=registration_data, 
                                   timeout=15,
                                   allow_redirects=False)
            
            print(f"Registration response: {response.status_code}")
            
            if response.status_code in [200, 302]:
                print(f"✅ User '{username}' created in production")
                print(f"Username: {username}")
                print(f"Email: {email}")
                print(f"Password: {password}")
                
                # Verify by checking database
                print(f"\n🔍 Verifying user creation...")
                self.get_all_production_users()
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                if response.content:
                    print(f"Response: {response.content.decode()[:200]}...")
                return False
                
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return False
    
    def test_production_login(self, username, password):
        """Test login with production database"""
        
        print(f"\n🔐 TESTING PRODUCTION LOGIN: {username}")
        print("=" * 50)
        
        login_data = {
            'username': username,
            'password': password
        }
        
        try:
            response = requests.post(f"{self.base_url}/login",
                                   data=login_data,
                                   timeout=15,
                                   allow_redirects=False)
            
            print(f"Login response: {response.status_code}")
            
            if response.status_code == 302:
                print(f"✅ Login successful for '{username}'")
                redirect_location = response.headers.get('Location', 'Unknown')
                print(f"Redirected to: {redirect_location}")
                return True
            elif response.status_code == 200:
                # Check for error messages in response
                response_text = response.text.lower()
                if any(error in response_text for error in ['invalid', 'incorrect', 'error']):
                    print(f"❌ Login failed - Invalid credentials")
                    return False
                else:
                    print(f"✅ Login successful (200 response)")
                    return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing login: {e}")
            return False
    
    def get_production_database_status(self):
        """Get detailed production database status"""
        
        print(f"\n📊 PRODUCTION DATABASE STATUS")
        print("=" * 50)
        
        endpoints_to_check = [
            '/admin/database-status',
            '/debug/routes',
            '/health'
        ]
        
        for endpoint in endpoints_to_check:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"\n🔍 Checking: {url}")
                
                response = requests.get(url, timeout=10)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text
                    if len(content) > 500:
                        print(f"Content: {content[:500]}...")
                    else:
                        print(f"Content: {content}")
                else:
                    print(f"Error response: {response.content.decode()[:200]}...")
                    
            except Exception as e:
                print(f"❌ Error checking {endpoint}: {e}")
    
    def backup_production_users(self):
        """Backup production users data"""
        
        print(f"\n💾 BACKING UP PRODUCTION USERS")
        print("=" * 50)
        
        users = self.get_all_production_users()
        if not users:
            print("❌ No users found to backup")
            return None
        
        backup_data = {
            'backup_date': datetime.now().isoformat(),
            'source': 'production',
            'total_users': len(users),
            'users': users
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"production_backup_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✅ Production users backed up to: {filename}")
        print(f"Users backed up: {len(users)}")
        
        return filename

def main():
    """Interactive production database tool"""
    
    print(f"\n🌐 PRODUCTION DATABASE ACCESS TOOL")
    print(f"Developer/Owner Backend Management")
    print(f"Production PostgreSQL Database Access")
    print("=" * 60)
    
    db = ProductionDatabaseAccess()
    
    while True:
        print(f"\n📋 PRODUCTION DATABASE COMMANDS:")
        print(f"1. Show all production users")
        print(f"2. Create user in production")
        print(f"3. Test user login")
        print(f"4. Get database status")
        print(f"5. Backup production users")
        print(f"6. Exit")
        
        choice = input(f"\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            db.get_all_production_users()
            
        elif choice == '2':
            username = input("Enter username: ").strip()
            email = input("Enter email: ").strip()
            password = input("Enter password: ").strip()
            db.create_production_user_via_registration(username, email, password)
            
        elif choice == '3':
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            db.test_production_login(username, password)
            
        elif choice == '4':
            db.get_production_database_status()
            
        elif choice == '5':
            db.backup_production_users()
            
        elif choice == '6':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice")

if __name__ == '__main__':
    main()