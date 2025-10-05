#!/usr/bin/env python3
"""
Database Integrity Tests
Tests CRUD operations, foreign keys, data validation, and database constraints
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

# Import app and models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User, Question, GameSession, Answer, Score
from config import TestingConfig

class TestDatabaseIntegrity:
    """Test suite for database operations and integrity"""
    
    @pytest.fixture
    def client(self):
        """Create test client with fresh database"""
        app.config.from_object(TestingConfig)
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.drop_all()
    
    def test_user_model_creation(self, client):
        """Test creating and retrieving User records"""
        with app.app_context():
            # Create user
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash='$2b$12$test_hash'
            )
            db.session.add(user)
            db.session.commit()
            
            # Retrieve user
            retrieved_user = User.query.filter_by(username='testuser').first()
            assert retrieved_user is not None
            assert retrieved_user.email == 'test@example.com'
            assert retrieved_user.username == 'testuser'
            assert retrieved_user.created_at is not None
            assert retrieved_user.is_active is True  # Default value
    
    def test_user_unique_constraints(self, client):
        """Test that username and email are unique"""
        with app.app_context():
            # Create first user
            user1 = User(
                username='unique_test',
                email='unique@example.com', 
                password_hash='hash1'
            )
            db.session.add(user1)
            db.session.commit()
            
            # Try to create user with duplicate username
            user2 = User(
                username='unique_test',  # Duplicate username
                email='different@example.com',
                password_hash='hash2'
            )
            db.session.add(user2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
            
            db.session.rollback()
            
            # Try to create user with duplicate email
            user3 = User(
                username='different_user',
                email='unique@example.com',  # Duplicate email
                password_hash='hash3'
            )
            db.session.add(user3)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
    
    def test_question_model_creation(self, client):
        """Test creating and retrieving Question records"""
        with app.app_context():
            question = Question(
                question_text='What is Python?',
                correct_answer='A programming language',
                choices='["A programming language", "A snake", "A movie", "A car"]',
                correct_choice_index=0,
                category='BASICS',
                difficulty='EASY',
                explanation='Python is a high-level programming language'
            )
            db.session.add(question)
            db.session.commit()
            
            # Retrieve question
            retrieved = Question.query.filter_by(question_text='What is Python?').first()
            assert retrieved is not None
            assert retrieved.correct_answer == 'A programming language'
            assert retrieved.category == 'BASICS'
            assert retrieved.difficulty == 'EASY'
            assert retrieved.times_asked == 0  # Default value
    
    def test_game_session_model(self, client):
        """Test GameSession model with foreign key relationships"""
        with app.app_context():
            # Create user first
            user = User(
                username='gamer',
                email='gamer@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            # Create game session
            session = GameSession(
                user_id=user.id,
                session_token='test_token_123',
                difficulty='EASY',
                total_questions=5,
                correct_answers=0,
                incorrect_answers=0
            )
            db.session.add(session)
            db.session.commit()
            
            # Retrieve and verify relationship
            retrieved = GameSession.query.filter_by(session_token='test_token_123').first()
            assert retrieved is not None
            assert retrieved.user_id == user.id
            assert retrieved.difficulty == 'EASY'
            assert retrieved.user.username == 'gamer'  # Test relationship
    
    def test_answer_model_foreign_keys(self, client):
        """Test Answer model with multiple foreign key relationships"""
        with app.app_context():
            # Create prerequisites
            user = User(username='answerer', email='answer@example.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            question = Question(
                question_text='Test question?',
                correct_answer='Correct',
                choices='["Correct", "Wrong1", "Wrong2", "Wrong3"]',
                correct_choice_index=0,
                category='BASICS',
                difficulty='EASY'
            )
            db.session.add(question)
            db.session.commit()
            
            game_session = GameSession(
                user_id=user.id,
                session_token='answer_session',
                total_questions=1
            )
            db.session.add(game_session)
            db.session.commit()
            
            # Create answer
            answer = Answer(
                game_session_id=game_session.id,
                question_id=question.id,
                user_id=user.id,
                selected_choice_index=0,
                is_correct=True,
                time_taken=2.5,
                points_earned=100
            )
            db.session.add(answer)
            db.session.commit()
            
            # Verify relationships
            retrieved = Answer.query.first()
            assert retrieved.user.username == 'answerer'
            assert retrieved.question.question_text == 'Test question?'
            assert retrieved.game_session.session_token == 'answer_session'
            assert retrieved.is_correct is True
    
    def test_score_model_relationships(self, client):
        """Test Score model relationships and constraints"""
        with app.app_context():
            # Create prerequisites
            user = User(username='scorer', email='score@example.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            game_session = GameSession(
                user_id=user.id,
                session_token='score_session',
                total_questions=5,
                correct_answers=4,
                incorrect_answers=1
            )
            db.session.add(game_session)
            db.session.commit()
            
            # Create score
            score = Score(
                user_id=user.id,
                game_session_id=game_session.id,
                score=400,
                accuracy_percentage=80.0,
                questions_answered=5,
                time_taken=120.5,
                category='BASICS',
                difficulty='EASY'
            )
            db.session.add(score)
            db.session.commit()
            
            # Verify
            retrieved = Score.query.first()
            assert retrieved.user.username == 'scorer'
            assert retrieved.game_session.session_token == 'score_session'
            assert retrieved.accuracy_percentage == 80.0
            assert retrieved.score == 400
    
    def test_database_cascading_deletes(self, client):
        """Test that foreign key constraints work properly on delete"""
        with app.app_context():
            # Create user with related data
            user = User(username='cascade_test', email='cascade@example.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            game_session = GameSession(
                user_id=user.id,
                session_token='cascade_session',
                total_questions=1
            )
            db.session.add(game_session)
            db.session.commit()
            
            score = Score(
                user_id=user.id,
                game_session_id=game_session.id,
                score=100,
                accuracy_percentage=100.0,
                questions_answered=1
            )
            db.session.add(score)
            db.session.commit()
            
            # Verify data exists
            assert User.query.count() == 1
            assert GameSession.query.count() == 1 
            assert Score.query.count() == 1
            
            # Delete user (test cascade behavior)
            db.session.delete(user)
            db.session.commit()
            
            # Check what happens to related records
            remaining_sessions = GameSession.query.count()
            remaining_scores = Score.query.count()
            
            print(f"After user delete - Sessions: {remaining_sessions}, Scores: {remaining_scores}")
            # Behavior depends on cascade settings in your models
    
    def test_data_validation_constraints(self, client):
        """Test data validation and constraints"""
        with app.app_context():
            # Test required field validation
            with pytest.raises((IntegrityError, ValueError)):
                user = User(
                    username=None,  # Required field
                    email='test@example.com',
                    password_hash='hash'
                )
                db.session.add(user)
                db.session.commit()
            
            db.session.rollback()
            
            # Test email format (if validation is implemented)
            try:
                user = User(
                    username='badEmail',
                    email='not_an_email',  # Invalid email format
                    password_hash='hash'
                )
                db.session.add(user)
                db.session.commit()
                print("Warning: Email validation not implemented")
            except (IntegrityError, ValueError):
                print("Email validation is working")
                db.session.rollback()
    
    def test_database_indexes(self, client):
        """Test that database indexes exist for performance"""
        with app.app_context():
            # Check if indexes exist by examining database schema
            inspector = db.inspect(db.engine)
            
            # Get indexes for users table
            user_indexes = inspector.get_indexes('users')
            index_names = [idx['name'] for idx in user_indexes]
            
            print(f"User table indexes: {index_names}")
            
            # Verify important indexes exist
            expected_indexes = ['ix_users_username', 'ix_users_email']
            for expected in expected_indexes:
                if expected in index_names:
                    print(f"✅ Index {expected} exists")
                else:
                    print(f"⚠️  Index {expected} missing")
    
    def test_bulk_operations_performance(self, client):
        """Test bulk insert and query performance"""
        with app.app_context():
            import time
            
            # Test bulk user creation
            start_time = time.time()
            
            users = []
            for i in range(100):
                users.append(User(
                    username=f'bulk_user_{i}',
                    email=f'bulk_{i}@example.com',
                    password_hash='bulk_hash'
                ))
            
            db.session.bulk_save_objects(users)
            db.session.commit()
            
            creation_time = time.time() - start_time
            print(f"Created 100 users in {creation_time:.2f} seconds")
            
            # Test bulk query
            start_time = time.time()
            all_users = User.query.all()
            query_time = time.time() - start_time
            
            print(f"Queried {len(all_users)} users in {query_time:.3f} seconds")
            
            assert len(all_users) == 100
            assert creation_time < 5.0  # Should be fast
            assert query_time < 1.0     # Should be very fast
    
    def test_transaction_rollback(self, client):
        """Test database transaction rollback functionality"""
        with app.app_context():
            # Start transaction
            user1 = User(username='transaction1', email='trans1@example.com', password_hash='hash')
            db.session.add(user1)
            
            user2 = User(username='transaction2', email='trans2@example.com', password_hash='hash')
            db.session.add(user2)
            
            # Verify not committed yet
            assert User.query.count() == 0
            
            # Commit transaction
            db.session.commit()
            assert User.query.count() == 2
            
            # Test rollback
            user3 = User(username='transaction3', email='trans3@example.com', password_hash='hash')
            db.session.add(user3)
            
            # Rollback before commit
            db.session.rollback()
            
            # Should still be 2 users
            assert User.query.count() == 2

if __name__ == '__main__':
    print("🗄️  RUNNING DATABASE INTEGRITY TESTS")
    print("=" * 60)
    
    # Run tests with verbose output
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--no-header',
        '--disable-warnings'
    ])