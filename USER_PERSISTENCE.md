# User Data Persistence System

The Python Trivia Game now includes a comprehensive user data persistence system that ensures registered users are preserved across database rebuilds and clean builds.

## 🎯 **Features**

### **Automatic User Preservation**
- ✅ **Smart Database Initialization** - Automatically backs up and restores users during database operations
- ✅ **Clean Build Support** - Users persist through complete application rebuilds
- ✅ **Migration Safe** - User data is preserved during database schema changes
- ✅ **Backup & Restore** - JSON-based backup system for portability

### **Management Tools**
- ✅ **Interactive CLI** - Easy-to-use command-line interface
- ✅ **Status Monitoring** - Check backup status and user counts
- ✅ **Manual Operations** - Backup, restore, and manage users manually

## 🚀 **How It Works**

### **Automatic Persistence**
The system automatically:
1. **Backs up user data** before any database rebuild
2. **Preserves passwords** (hashed) and user preferences
3. **Restores users** after database initialization
4. **Skips duplicates** to prevent conflicts

### **Smart Database Initialization**
```python
# Old way (users lost on rebuild):
db.create_all()

# New way (users preserved):
smart_database_init(preserve_users=True)
```

## 📋 **Usage**

### **Command Line Management**
```bash
# Show current status
python manage_users.py status

# List all users
python manage_users.py list

# Manual backup
python manage_users.py backup

# Manual restore
python manage_users.py restore

# Interactive mode
python manage_users.py interactive
```

### **Programmatic Usage**
```python
from user_persistence import user_data_manager

# Backup users
user_data_manager.backup_users()

# Restore users
user_data_manager.restore_users()

# Check backup status
if user_data_manager.has_backup():
    info = user_data_manager.get_backup_info()
    print(f"Backup contains {info['user_count']} users")
```

## 🗂️ **File Structure**

```
PythonTrivia/
├── user_persistence.py       # Core persistence system
├── manage_users.py           # CLI management tool
├── instance/
│   └── backups/
│       └── user_data_backup.json  # User backup file
└── app.py                    # Updated with smart initialization
```

## 🔧 **Configuration**

### **Backup Location**
By default, user backups are stored in `instance/backups/user_data_backup.json`. You can customize this:

```python
from user_persistence import UserDataManager

# Custom backup location
manager = UserDataManager(backup_dir="custom/backup/path")
```

### **Database Initialization**
The system is automatically enabled in `app.py`:

```python
# Automatic user preservation
smart_database_init(preserve_users=True)

# Disable user preservation (old behavior)
smart_database_init(preserve_users=False)
```

## 📊 **Backup Format**

User data is stored in JSON format:
```json
{
  "backup_timestamp": "2025-10-04T18:39:09.109983+00:00",
  "user_count": 2,
  "users": [
    {
      "username": "john_doe",
      "email": "john@example.com",
      "password_hash": "hashed_password",
      "created_at": "2025-10-01T10:00:00+00:00",
      "total_games_played": 15,
      "total_points": 3750,
      "preferred_difficulty": "medium",
      ...
    }
  ]
}
```

## 🛡️ **Security**

- ✅ **Password hashes** are preserved (not plain text passwords)
- ✅ **Duplicate prevention** - users won't be duplicated on restore
- ✅ **Error handling** - graceful fallback if backup/restore fails
- ✅ **Validation** - data integrity checks during restore

## 🎮 **User Experience**

### **For Players**
- ✅ **Seamless experience** - accounts persist through updates
- ✅ **Game history preserved** - scores and stats maintained
- ✅ **Preferences retained** - difficulty and category preferences saved

### **For Developers**
- ✅ **No manual work** - automatic during development
- ✅ **Clean rebuilds** - database can be rebuilt without user loss
- ✅ **Testing friendly** - easy to backup/restore test users

## 🔄 **Common Workflows**

### **Development Rebuild**
```bash
# Users are automatically preserved
python init_db.py reset

# Or manually:
python manage_users.py backup
python init_db.py reset
python manage_users.py restore
```

### **Production Deployment**
```bash
# Before deployment
python manage_users.py backup

# After deployment
python manage_users.py restore
```

### **User Management**
```bash
# Check current status
python manage_users.py status

# View all users
python manage_users.py list

# Interactive management
python manage_users.py interactive
```

## 🚨 **Troubleshooting**

### **Backup Not Found**
If no backup exists on first run:
```bash
python manage_users.py status
# Shows: "Backup file exists: ❌ No"
```
This is normal - backups are created when users exist.

### **Restore Conflicts**
Users with duplicate usernames/emails are automatically skipped:
```
Successfully restored 2 users (1 skipped as duplicates)
```

### **Permission Issues**
Ensure the backup directory is writable:
```bash
mkdir -p instance/backups
chmod 755 instance/backups
```

## ✨ **Benefits**

1. **👥 User Retention** - No more lost accounts during development
2. **🚀 Faster Development** - Clean rebuilds without user recreation
3. **🔒 Data Safety** - Automatic backups prevent accidental loss
4. **📱 Better UX** - Seamless experience for returning users
5. **🛠️ Easy Management** - Simple tools for user data operations

The user persistence system makes the Python Trivia Game production-ready while maintaining ease of development!