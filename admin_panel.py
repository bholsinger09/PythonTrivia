#!/usr/bin/env python3
"""
Admin Panel Application
Secure admin interface for user management with plain text password visibility
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
import json
import os
from datetime import datetime
from models import db, User, UserBackup
from werkzeug.security import generate_password_hash
from config import DevelopmentConfig

# Create separate admin Flask app
admin_app = Flask(__name__, template_folder='templates')
admin_app.config.from_object(DevelopmentConfig)

# Initialize database with admin app
db.init_app(admin_app)

# Simple admin authentication
ADMIN_KEY = "admin_secret_2025"  # Change this to your secure password

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key') or session.get('admin_authenticated')
        if admin_key != ADMIN_KEY:
            return render_template('admin/login.html'), 401
        return f(*args, **kwargs)
    return decorated_function

@admin_app.route('/')
def admin_login():
    """Admin login page"""
    return render_template('admin/login.html')

@admin_app.route('/auth', methods=['POST'])
def admin_authenticate():
    """Admin authentication"""
    password = request.form.get('password')
    if password == ADMIN_KEY:
        session['admin_authenticated'] = ADMIN_KEY
        return redirect('/dashboard')
    else:
        flash('Invalid admin password')
        return render_template('admin/login.html')

@admin_app.route('/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with user management"""
    with admin_app.app_context():
        users = User.query.all()
        
        # Get user data with actual passwords (for admin view only)
        users_with_passwords = []
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password_hash': user.password_hash,
                'created_at': user.created_at,
                'is_active': user.is_active,
                'total_games_played': user.total_games_played or 0,
                'total_points': user.total_points or 0,
                'last_seen': user.last_seen
            }
            users_with_passwords.append(user_data)
        
        return render_template('admin/secure_dashboard.html', 
                             users=users_with_passwords,
                             user_count=len(users_with_passwords))

@admin_app.route('/api/users')
@admin_required  
def api_get_users():
    """Get all users with full details for admin"""
    with admin_app.app_context():
        users = User.query.all()
        users_data = []
        
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password_hash': user.password_hash,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_seen': user.last_seen.isoformat() if user.last_seen else None,
                'is_active': user.is_active,
                'total_games_played': user.total_games_played or 0,
                'total_points': user.total_points or 0
            })
        
        return jsonify({'users': users_data, 'total': len(users_data)})

@admin_app.route('/api/user/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def api_reset_password(user_id):
    """Reset user password to a new plain text value"""
    with admin_app.app_context():
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        new_password = data.get('new_password')
        if not new_password:
            return jsonify({'success': False, 'error': 'Password required'}), 400
        
        # Update password hash
        user.password_hash = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'Password reset for {user.username}',
                'username': user.username,
                'new_password': new_password,  # Return the plain text password for admin
                'password_hash': user.password_hash
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_app.route('/api/user/create', methods=['POST'])
@admin_required
def api_create_user():
    """Create new user with specified password"""
    with admin_app.app_context():
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email') 
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'success': False, 'error': 'All fields required'}), 400
        
        # Check duplicates
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'error': 'Username exists'}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'Email exists'}), 400
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_active=True
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'User {username} created successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'password': password,  # Show admin the password used
                    'password_hash': user.password_hash
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_app.route('/api/user/<int:user_id>/edit', methods=['POST'])
@admin_required
def api_edit_user(user_id):
    """Edit user information"""
    with admin_app.app_context():
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        changes = []
        
        if 'username' in data and data['username'] != user.username:
            # Check if new username exists
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'success': False, 'error': 'Username already exists'}), 400
            old_username = user.username
            user.username = data['username']
            changes.append(f"Username: {old_username} → {user.username}")
        
        if 'email' in data and data['email'] != user.email:
            # Check if new email exists
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'success': False, 'error': 'Email already exists'}), 400
            old_email = user.email
            user.email = data['email']
            changes.append(f"Email: {old_email} → {user.email}")
        
        if 'is_active' in data:
            user.is_active = data['is_active']
            changes.append(f"Status: {'Active' if user.is_active else 'Inactive'}")
        
        try:
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'User {user.username} updated',
                'changes': changes
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_app.route('/api/user/<int:user_id>/delete', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    """Delete user completely"""
    with admin_app.app_context():
        user = User.query.get_or_404(user_id)
        username = user.username
        
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'User {username} deleted successfully'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_app.route('/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    return redirect('/')

if __name__ == '__main__':
    print("\n🔧 ADMIN PANEL STARTING")
    print("=" * 50)
    print(f"Admin Password: {ADMIN_KEY}")
    print(f"Admin URL: http://localhost:5002")
    print(f"⚠️  WARNING: This panel shows plain text passwords!")
    print(f"⚠️  Only use this for admin management purposes!")
    print("=" * 50)
    
    with admin_app.app_context():
        db.create_all()
    
    admin_app.run(debug=True, host='localhost', port=5002)