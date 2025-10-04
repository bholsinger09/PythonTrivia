#!/bin/bash
# Script to update the init_db function in app.py

# Create the new init_db function
cat > /tmp/new_init_db.py << 'EOF'
def init_db() -> None:
    """
    Initialize database tables with user persistence support.
    
    PEP 20: "Simple is better than complex" - focused initialization with user preservation
    """
    try:
        with app.app_context():
            # Use smart initialization that preserves user data
            smart_database_init(preserve_users=True)
            
            # Check if we need to seed data (only questions, not users)
            if Question.query.count() == 0:
                print("Seeding database with initial data...")
                DatabaseSeeder.seed_sample_questions()
                
            # Log user persistence status
            user_count = User.query.count()
            if user_count > 0:
                print(f"Database initialized with {user_count} existing users preserved")
            else:
                print("Database initialized - no existing users found")
                
    except Exception as e:
        print(f"Database initialization error: {e}")


def backup_user_data() -> bool:
    """Manually backup user data"""
    with app.app_context():
        return user_data_manager.backup_users()


def restore_user_data() -> bool:
    """Manually restore user data"""
    with app.app_context():
        return user_data_manager.restore_users()
EOF

# Find the line numbers for the init_db function
start_line=$(grep -n "def init_db" app.py | cut -d: -f1)
end_line=$(awk -v start="$start_line" 'NR >= start && /^def / && NR > start {print NR-1; exit} END {if (NR >= start) print NR}' app.py)

# Replace the function
if [ -n "$start_line" ] && [ -n "$end_line" ]; then
    echo "Replacing init_db function (lines $start_line-$end_line)"
    
    # Create backup
    cp app.py app.py.backup
    
    # Replace the function
    {
        head -n $((start_line-1)) app.py
        cat /tmp/new_init_db.py
        tail -n +$((end_line+1)) app.py
    } > app.py.new && mv app.py.new app.py
    
    echo "Function replaced successfully"
else
    echo "Could not find init_db function"
fi

# Clean up
rm -f /tmp/new_init_db.py