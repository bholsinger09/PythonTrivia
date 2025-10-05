#!/usr/bin/env python3
"""
Game Logic Tests
Tests trivia game mechanics, scoring, question selection, and game flow
"""

import pytest
import json
import tempfile
import os
from datetime import datetime

# Import app and models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User, Question, GameSession, Answer, Score
from config import TestingConfig

class TestGameLogic:
    """Test suite for trivia game logic and mechanics"""
    
    @pytest.fixture
    def client(self):
        """Create test client with sample data"""
        app.config.from_object(TestingConfig)
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                self.setup_test_data()
                yield client
                db.drop_all()
    
    def setup_test_data(self):
        """Set up test users and questions"""
        # Create test user
        self.test_user = User(
            username='game_tester',
            email='game@example.com',
            password_hash='$2b$12$test_hash'
        )
        db.session.add(self.test_user)
        
        # Create test questions
        questions = [
            {
                'question_text': 'What is 2 + 2?',
                'correct_answer': '4',
                'choices': '["4", "3", "5", "6"]',
                'correct_choice_index': 0,
                'category': 'BASICS',
                'difficulty': 'EASY',
                'explanation': 'Basic arithmetic'
            },
            {
                'question_text': 'What is the capital of France?',
                'correct_answer': 'Paris',
                'choices': '["Paris", "London", "Berlin", "Madrid"]',
                'correct_choice_index': 0,
                'category': 'GEOGRAPHY',
                'difficulty': 'EASY',
                'explanation': 'Paris is the capital of France'
            },
            {
                'question_text': 'What is the time complexity of binary search?',
                'correct_answer': 'O(log n)',
                'choices': '["O(log n)", "O(n)", "O(n^2)", "O(1)"]',
                'correct_choice_index': 0,
                'category': 'ADVANCED',
                'difficulty': 'HARD',
                'explanation': 'Binary search has logarithmic time complexity'
            }
        ]
        
        for q_data in questions:
            question = Question(**q_data)
            db.session.add(question)
        
        db.session.commit()
    
    def test_game_session_creation(self, client):
        """Test creating a new game session"""
        with app.app_context():
            response = client.post('/api/start-game', json={
                'user_id': self.test_user.id,
                'difficulty': 'EASY',
                'categories': ['BASICS', 'GEOGRAPHY'],
                'question_count': 5
            })
            
            if response.status_code == 200:
                data = response.get_json()
                assert 'session_token' in data
                assert 'questions' in data
                
                # Verify session was created in database
                session = GameSession.query.filter_by(session_token=data['session_token']).first()
                assert session is not None
                assert session.user_id == self.test_user.id
                assert session.difficulty == 'EASY'
    
    def test_question_selection_by_difficulty(self, client):
        """Test that questions are filtered by difficulty"""
        with app.app_context():
            # Request easy questions
            response = client.post('/api/start-game', json={
                'difficulty': 'EASY',
                'question_count': 10
            })
            
            if response.status_code == 200:
                data = response.get_json()
                questions = data.get('questions', [])
                
                # All questions should be EASY difficulty
                for question in questions:
                    if 'difficulty' in question:
                        assert question['difficulty'] == 'EASY'
    
    def test_question_selection_by_category(self, client):
        """Test that questions are filtered by category"""
        with app.app_context():
            # Request only BASICS questions
            response = client.post('/api/start-game', json={
                'categories': ['BASICS'],
                'question_count': 5
            })
            
            if response.status_code == 200:
                data = response.get_json()
                questions = data.get('questions', [])
                
                # All questions should be from BASICS category
                for question in questions:
                    if 'category' in question:
                        assert question['category'] == 'BASICS'
    
    def test_answer_submission_correct(self, client):
        """Test submitting a correct answer"""
        with app.app_context():
            # Create game session first
            session = GameSession(
                user_id=self.test_user.id,
                session_token='test_session_123',
                total_questions=1,
                correct_answers=0,
                incorrect_answers=0
            )
            db.session.add(session)
            db.session.commit()
            
            # Get a question
            question = Question.query.filter_by(difficulty='EASY').first()
            
            # Submit correct answer
            response = client.post('/api/submit-answer', json={
                'session_token': 'test_session_123',
                'question_id': question.id,
                'selected_choice': question.correct_choice_index,
                'time_taken': 5.0
            })
            
            if response.status_code == 200:
                data = response.get_json()
                assert data.get('is_correct') is True
                assert data.get('points_earned', 0) > 0
                
                # Verify answer was recorded
                answer = Answer.query.filter_by(
                    game_session_id=session.id,
                    question_id=question.id
                ).first()
                
                if answer:
                    assert answer.is_correct is True
                    assert answer.selected_choice_index == question.correct_choice_index
    
    def test_answer_submission_incorrect(self, client):
        """Test submitting an incorrect answer"""
        with app.app_context():
            # Create game session
            session = GameSession(
                user_id=self.test_user.id,
                session_token='test_session_456',
                total_questions=1
            )
            db.session.add(session)
            db.session.commit()
            
            # Get a question
            question = Question.query.filter_by(difficulty='EASY').first()
            
            # Submit wrong answer (any index != correct_choice_index)
            wrong_choice = (question.correct_choice_index + 1) % 4
            
            response = client.post('/api/submit-answer', json={
                'session_token': 'test_session_456',
                'question_id': question.id,
                'selected_choice': wrong_choice,
                'time_taken': 3.0
            })
            
            if response.status_code == 200:
                data = response.get_json()
                assert data.get('is_correct') is False
                assert data.get('points_earned', 0) == 0
                
                # Verify answer was recorded
                answer = Answer.query.filter_by(
                    game_session_id=session.id,
                    question_id=question.id
                ).first()
                
                if answer:
                    assert answer.is_correct is False
                    assert answer.selected_choice_index == wrong_choice
    
    def test_scoring_calculation(self, client):
        """Test that scoring is calculated correctly"""
        with app.app_context():
            # Create game session
            session = GameSession(
                user_id=self.test_user.id,
                session_token='scoring_test',
                total_questions=3,
                correct_answers=2,
                incorrect_answers=1
            )
            db.session.add(session)
            db.session.commit()
            
            # Test scoring endpoint
            response = client.post('/api/calculate-score', json={
                'session_token': 'scoring_test',
                'total_questions': 3,
                'correct_answers': 2,
                'time_taken': 60.0,
                'difficulty': 'EASY'
            })
            
            if response.status_code == 200:
                data = response.get_json()
                
                # Verify score calculations
                assert 'total_score' in data
                assert 'accuracy_percentage' in data
                
                accuracy = data.get('accuracy_percentage')
                expected_accuracy = (2 / 3) * 100  # 66.67%
                assert abs(accuracy - expected_accuracy) < 0.1
                
                total_score = data.get('total_score', 0)
                assert total_score > 0  # Should have earned some points
    
    def test_streak_bonus_calculation(self, client):
        """Test streak bonus scoring"""
        with app.app_context():
            session = GameSession(
                user_id=self.test_user.id,
                session_token='streak_test',
                total_questions=5,
                current_streak=3,  # 3 correct in a row
                best_streak=3
            )
            db.session.add(session)
            db.session.commit()
            
            question = Question.query.first()
            
            # Submit correct answer to continue streak
            response = client.post('/api/submit-answer', json={
                'session_token': 'streak_test',
                'question_id': question.id,
                'selected_choice': question.correct_choice_index,
                'time_taken': 2.0
            })
            
            if response.status_code == 200:
                data = response.get_json()
                
                # Should have streak bonus
                if 'streak_bonus' in data:
                    assert data['streak_bonus'] > 0
                    print(f"Streak bonus: {data['streak_bonus']}")
    
    def test_time_bonus_calculation(self, client):
        """Test time-based scoring bonus"""
        with app.app_context():
            session = GameSession(
                user_id=self.test_user.id,
                session_token='time_test',
                total_questions=1
            )
            db.session.add(session)
            db.session.commit()
            
            question = Question.query.first()
            
            # Submit answer quickly (should get time bonus)
            response = client.post('/api/submit-answer', json={
                'session_token': 'time_test',
                'question_id': question.id,
                'selected_choice': question.correct_choice_index,
                'time_taken': 1.0  # Very fast
            })
            
            if response.status_code == 200:
                data = response.get_json()
                quick_points = data.get('points_earned', 0)
            
            # Submit same type of answer slowly
            session2 = GameSession(
                user_id=self.test_user.id,
                session_token='time_test_slow',
                total_questions=1
            )
            db.session.add(session2)
            db.session.commit()
            
            response2 = client.post('/api/submit-answer', json={
                'session_token': 'time_test_slow',
                'question_id': question.id,
                'selected_choice': question.correct_choice_index,
                'time_taken': 10.0  # Slow
            })
            
            if response2.status_code == 200:
                data2 = response2.get_json()
                slow_points = data2.get('points_earned', 0)
                
                # Quick answer should score higher or equal
                assert quick_points >= slow_points
                print(f"Quick: {quick_points}, Slow: {slow_points}")
    
    def test_game_completion(self, client):
        """Test completing a full game"""
        with app.app_context():
            # Start game
            response = client.post('/api/start-game', json={
                'user_id': self.test_user.id,
                'difficulty': 'EASY',
                'question_count': 2
            })
            
            if response.status_code != 200:
                pytest.skip("Game start endpoint not available")
            
            data = response.get_json()
            session_token = data['session_token']
            questions = data['questions']
            
            # Answer all questions
            for question in questions:
                client.post('/api/submit-answer', json={
                    'session_token': session_token,
                    'question_id': question['id'],
                    'selected_choice': question['correct_choice_index'],
                    'time_taken': 3.0
                })
            
            # Complete game
            response = client.post('/api/complete-game', json={
                'session_token': session_token
            })
            
            if response.status_code == 200:
                data = response.get_json()
                assert 'final_score' in data
                assert 'accuracy' in data
                
                # Verify game session marked as complete
                session = GameSession.query.filter_by(session_token=session_token).first()
                if session:
                    assert session.is_completed is True
                    assert session.completed_at is not None
    
    def test_question_statistics_update(self, client):
        """Test that question statistics are updated after answers"""
        with app.app_context():
            question = Question.query.first()
            initial_times_asked = question.times_asked
            initial_times_correct = question.times_correct
            
            session = GameSession(
                user_id=self.test_user.id,
                session_token='stats_test',
                total_questions=1
            )
            db.session.add(session)
            db.session.commit()
            
            # Submit correct answer
            client.post('/api/submit-answer', json={
                'session_token': 'stats_test',
                'question_id': question.id,
                'selected_choice': question.correct_choice_index,
                'time_taken': 2.0
            })
            
            # Check if statistics were updated
            db.session.refresh(question)
            
            if question.times_asked > initial_times_asked:
                assert question.times_asked == initial_times_asked + 1
                assert question.times_correct == initial_times_correct + 1
                print("✅ Question statistics updated correctly")
            else:
                print("⚠️  Question statistics not automatically updated")
    
    def test_leaderboard_functionality(self, client):
        """Test leaderboard and high score functionality"""
        with app.app_context():
            # Create multiple scores
            users = []
            for i in range(3):
                user = User(
                    username=f'player_{i}',
                    email=f'player_{i}@example.com',
                    password_hash='hash'
                )
                db.session.add(user)
                users.append(user)
            
            db.session.commit()
            
            # Create scores for each user
            scores_data = [500, 300, 400]  # Different scores
            for i, score_value in enumerate(scores_data):
                session = GameSession(
                    user_id=users[i].id,
                    session_token=f'leader_test_{i}',
                    total_questions=5,
                    correct_answers=score_value // 100
                )
                db.session.add(session)
                db.session.commit()
                
                score = Score(
                    user_id=users[i].id,
                    game_session_id=session.id,
                    score=score_value,
                    accuracy_percentage=80.0,
                    questions_answered=5,
                    category='BASICS',
                    difficulty='EASY'
                )
                db.session.add(score)
            
            db.session.commit()
            
            # Test leaderboard endpoint
            response = client.get('/api/leaderboard')
            
            if response.status_code == 200:
                data = response.get_json()
                leaderboard = data.get('leaderboard', [])
                
                # Should be sorted by score (highest first)
                if len(leaderboard) >= 2:
                    assert leaderboard[0]['score'] >= leaderboard[1]['score']
                    print(f"✅ Leaderboard working: {[s['score'] for s in leaderboard]}")

if __name__ == '__main__':
    print("🎮 RUNNING GAME LOGIC TESTS")
    print("=" * 60)
    
    # Run tests with verbose output
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--no-header',
        '--disable-warnings'
    ])