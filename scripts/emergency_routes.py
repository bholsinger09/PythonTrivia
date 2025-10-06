from flask import Blueprint
from models import User, db

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route("/emergency-create-user")
def emergency_create_user():
    """Emergency route to create code_monkey user"""
    try:
        existing = User.query.filter_by(username="code_monkey").first()
        if existing:
            return "User code_monkey already exists in database"
        
        user = User(username="code_monkey", email="code_monkey@test.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        
        return "SUCCESS: User code_monkey created with password: password123"
    except Exception as e:
        return f"ERROR creating user: {str(e)}"

@emergency_bp.route("/test-db-connection")
def test_db_connection():
    """Test if database connection is working"""
    try:
        from models import User
        count = User.query.count()
        return f"Database connection OK. Total users: {count}"
    except Exception as e:
        return f"Database connection ERROR: {str(e)}"