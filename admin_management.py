"""
Admin User Management System
Provides full admin control over users while maintaining password security
"""

from flask import render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
import json
from datetime import datetime
from models import db, User, UserBackup
from werkzeug.security import generate_password_hash

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Simple admin check - in production, use proper authentication
        admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key') or session.get('admin_authenticated')
        if admin_key != 'admin_secret_key_2025':  # Change this to your secure key
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def init_admin_routes(app):
    """Initialize admin routes"""
    
    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        """Admin dashboard with full user management"""
        
        users = User.query.all()
        user_count = len(users)
        
        # Get backup information
        backups = UserBackup.query.all()
        
        return render_template('admin/dashboard.html', 
                             users=users, 
                             user_count=user_count,
                             backups=backups)
    
    @app.route('/admin/users')
    @admin_required
    def admin_users():
        """Get all users in JSON format for admin"""
        
        users = User.query.all()
        users_data = []
        
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_seen': user.last_seen.isoformat() if user.last_seen else None,
                'is_active': user.is_active,
                'total_games_played': user.total_games_played,
                'total_points': user.total_points,
                'password_hash_preview': user.password_hash[:20] + '...' if user.password_hash else None
            })
        
        return jsonify({
            'total_users': len(users_data),
            'users': users_data
        })
    
    @app.route('/admin/user/<int:user_id>')
    @admin_required
    def admin_get_user(user_id):
        """Get specific user details"""
        
        user = User.query.get_or_404(user_id)
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_seen': user.last_seen.isoformat() if user.last_seen else None,
            'is_active': user.is_active,
            'preferred_difficulty': user.preferred_difficulty,
            'preferred_categories': user.preferred_categories,
            'total_games_played': user.total_games_played,
            'total_questions_answered': user.total_questions_answered,
            'total_correct_answers': user.total_correct_answers,
            'best_streak': user.best_streak,
            'total_points': user.total_points,
            'password_hash': user.password_hash  # Full hash for admin
        })
    
    @app.route('/admin/user/<int:user_id>/edit', methods=['POST'])
    @admin_required
    def admin_edit_user(user_id):
        """Edit user information (admin only)"""
        
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Track changes
        changes = []
        
        if 'username' in data and data['username'] != user.username:
            old_username = user.username
            user.username = data['username']
            changes.append(f"Username: {old_username} → {user.username}")
        
        if 'email' in data and data['email'] != user.email:
            old_email = user.email
            user.email = data['email']
            changes.append(f"Email: {old_email} → {user.email}")
        
        if 'is_active' in data:
            old_active = user.is_active
            user.is_active = data['is_active']
            changes.append(f"Active: {old_active} → {user.is_active}")
        
        # Reset password if requested
        if 'new_password' in data and data['new_password']:
            user.password_hash = generate_password_hash(data['new_password'])
            changes.append(f"Password reset to: {data['new_password']}")
        
        try:
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'User {user.username} updated successfully',
                'changes': changes,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_active': user.is_active
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/admin/user/<int:user_id>/delete', methods=['DELETE'])
    @admin_required
    def admin_delete_user(user_id):
        """Delete user (admin only)"""
        
        user = User.query.get_or_404(user_id)
        username = user.username
        email = user.email
        
        try:
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'User {username} ({email}) deleted successfully'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/admin/user/create', methods=['POST'])
    @admin_required
    def admin_create_user():
        """Create new user (admin only)"""
        
        data = request.get_json()
        
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'error': 'Email already exists'}), 400
        
        try:
            user = User(
                username=data['username'],
                email=data['email'],
                password_hash=generate_password_hash(data['password']),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'User {user.username} created successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'password_used': data['password'],  # Show admin what password was set
                    'is_active': user.is_active
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/admin/password-reset/<int:user_id>', methods=['POST'])
    @admin_required
    def admin_reset_password(user_id):
        """Reset user password to a new value (admin only)"""
        
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'new_password' not in data or not data['new_password']:
            return jsonify({'success': False, 'error': 'New password required'}), 400
        
        new_password = data['new_password']
        user.password_hash = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Password reset for user {user.username}',
                'username': user.username,
                'new_password': new_password,  # Show admin the new password
                'password_hash': user.password_hash
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/admin/search')
    @admin_required
    def admin_search_users():
        """Search users by username or email"""
        
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'users': []})
        
        users = User.query.filter(
            db.or_(
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        ).all()
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return jsonify({
            'query': query,
            'count': len(users_data),
            'users': users_data
        })
    
    @app.route('/admin/auth', methods=['POST'])
    def admin_authenticate():
        """Simple admin authentication"""
        
        data = request.get_json()
        admin_key = data.get('admin_key')
        
        if admin_key == 'admin_secret_key_2025':  # Change this to your secure key
            session['admin_authenticated'] = True
            return jsonify({'success': True, 'message': 'Admin authenticated'})
        else:
            return jsonify({'success': False, 'error': 'Invalid admin key'}), 401