# Admin Panel Documentation

## ⚠️ IMPORTANT SECURITY NOTICE

**This admin panel is designed to give you complete control over user accounts, including the ability to see and manage passwords. While this provides the functionality you requested, please understand the security implications:**

1. **Passwords are still stored securely** - The database still uses bcrypt hashing
2. **Admin panel shows hashes** - You can see the full password hashes
3. **Password management** - You can reset passwords to any value you choose
4. **Complete user control** - Create, edit, and delete users

## 🚀 How to Use the Admin Panel

### Starting the Admin Panel

1. **Run the admin panel server:**
   ```bash
   cd /Users/benh/Documents/PythonTrivia
   python admin_panel.py
   ```

2. **Access the admin interface:**
   - Open your browser to: `http://localhost:5002`
   - Admin password: `admin_secret_2025`

### Admin Panel Features

#### 🔍 **View All Users**
- See complete user database
- View usernames, emails, password hashes
- Check user status (active/inactive)
- See registration dates and activity
- View game statistics

#### ➕ **Create New Users**
1. Click "Create New User" button
2. Enter username, email, and password
3. Choose active/inactive status
4. Password will be stored exactly as you enter it (then hashed)

#### ✏️ **Edit Existing Users**
1. Click "Edit" button next to any user
2. Modify username, email, or status
3. Leave password blank to keep current password
4. Or enter new password to change it

#### 🔑 **Reset Passwords**
1. Click "Password" button next to any user
2. Enter the new password you want them to use
3. System will show you the exact password set
4. User can immediately log in with this new password

#### 🗑️ **Delete Users**
1. Click "Delete" button next to any user
2. Confirm deletion (this is permanent!)
3. All user data is completely removed

#### 🔍 **Search Users**
- Use the search box to find users by:
  - Username
  - Email address
  - User ID

## 📋 **What You Can See and Control**

### User Information Displayed:
- **User ID** - Unique database identifier
- **Username** - Login username
- **Email** - User's email address
- **Password Hash** - Full bcrypt hash (60+ characters)
- **Status** - Active or Inactive
- **Created Date** - When user registered
- **Last Seen** - Last login time
- **Games Played** - Total trivia games
- **Points** - Total points earned

### Admin Actions Available:
- **Create users** with specific passwords
- **Edit** usernames and emails
- **Reset passwords** to any value you choose
- **Activate/deactivate** user accounts
- **Delete users** permanently
- **Search and filter** users

## 🔒 **Password Management Explained**

### How It Works:
1. **You enter plain text password** in admin panel
2. **System hashes it with bcrypt** before storing
3. **Database stores only the hash** (secure)
4. **Admin panel shows you the hash** (full visibility)
5. **User logs in with the plain text password** you set

### Example:
- You set password: `MyNewPassword123!`
- Database stores: `$2b$12$abc123def456...` (bcrypt hash)
- User logs in with: `MyNewPassword123!`
- You can see the hash in admin panel for verification

## 🛡️ **Security Best Practices**

1. **Keep admin panel secure** - Only access from trusted locations
2. **Use strong admin password** - Change `admin_secret_2025` to something secure
3. **Don't share admin access** - Only for authorized administrators
4. **Log admin actions** - Keep track of who makes changes
5. **Regular security review** - Periodically audit user accounts

## 🚀 **Production Deployment**

If you want to deploy this admin panel to production:

1. **Change the admin password** in `admin_panel.py`:
   ```python
   ADMIN_KEY = "your_secure_admin_password_here"
   ```

2. **Use HTTPS only** for admin access

3. **Restrict IP access** to admin panel

4. **Consider two-factor authentication** for admin access

## 📞 **Support**

This admin panel gives you complete control over your user database while maintaining the security of password hashing. You can now:

- ✅ See all user information clearly
- ✅ Create users with specific passwords  
- ✅ Edit any user details
- ✅ Reset passwords to any value
- ✅ Delete users permanently
- ✅ Search and manage users easily

The system balances your need for complete admin control with security best practices by using bcrypt hashing while giving you full visibility and management capabilities.