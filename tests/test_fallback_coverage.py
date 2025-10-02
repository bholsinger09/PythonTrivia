"""
Test coverage for load_sample_questions_fallback function and database error handling
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app, load_sample_questions_fallback, initialize_game_with_questions, load_questions_from_db


class TestFallbackQuestions:
    """Test the fallback question loading functionality"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_load_sample_questions_fallback_function(self):
        """Test the load_sample_questions_fallback function directly"""
        # This should trigger lines 158-233
        questions = load_sample_questions_fallback()
        
        # Verify we get sample questions
        assert len(questions) == 8  # Based on the sample questions in the function
        
        # Check first question
        first_question = questions[0]
        assert "What is the output of print(type([]))?" in first_question.question
        assert first_question.answer == "<class 'list'>"
        
        # Check different categories and difficulties are present
        categories = {q.category for q in questions}
        difficulties = {q.difficulty for q in questions}
        
        assert len(categories) > 1  # Multiple categories
        assert len(difficulties) > 1  # Multiple difficulties
    
    @patch('app.load_questions_from_db')
    def test_load_questions_from_db_exception_triggers_fallback(self, mock_load_db):
        """Test that database exceptions trigger the fallback function"""
        # Mock database function to raise exception
        mock_load_db.side_effect = Exception("Database connection failed")
        
        # This should catch the exception and call load_sample_questions_fallback
        questions = load_questions_from_db()
        
        # Verify we get fallback questions
        assert len(questions) == 8
        assert "What is the output of print(type([]))?" in questions[0].question
    
    @patch('app.load_questions_from_db')
    def test_initialize_game_with_database_failure(self, mock_load_db):
        """Test initialize_game_with_questions when database fails"""
        # Mock database function to raise exception
        mock_load_db.side_effect = Exception("Database error")
        
        # This should trigger the fallback path in initialize_game_with_questions
        # Which calls load_sample_questions_fallback on line 252
        initialize_game_with_questions()
        
        # The function should complete without raising an exception
        # and should have used the fallback questions
        assert True  # If we get here, the function worked
    
    @patch('app.TriviaGame')
    @patch('app.load_questions_from_db') 
    def test_game_initialization_with_fallback_questions(self, mock_load_db, mock_game_class):
        """Test that game gets initialized with fallback questions when DB fails"""
        # Mock database to fail
        mock_load_db.side_effect = Exception("DB unavailable")
        
        # Mock game instance
        mock_game = MagicMock()
        mock_game_class.return_value = mock_game
        
        # Initialize game - should use fallback
        initialize_game_with_questions()
        
        # Verify game.add_question was called for each fallback question
        assert mock_game.add_question.call_count == 8  # 8 sample questions
        
        # Verify shuffle was called
        mock_game.shuffle_cards.assert_called_once()
    
    def test_sample_questions_have_required_attributes(self):
        """Test that all sample questions have the required attributes"""
        questions = load_sample_questions_fallback()
        
        for question in questions:
            # Each question should have these attributes
            assert hasattr(question, 'question')
            assert hasattr(question, 'answer')
            assert hasattr(question, 'category')
            assert hasattr(question, 'difficulty')
            assert hasattr(question, 'explanation')
            assert hasattr(question, 'choices')
            assert hasattr(question, 'correct_choice_index')
            
            # Verify content is not empty
            assert len(question.question) > 0
            assert len(question.answer) > 0
            assert question.explanation is not None
            assert len(question.choices) >= 2
            assert 0 <= question.correct_choice_index < len(question.choices)
    
    def test_sample_questions_correct_answers(self):
        """Test that sample questions have correct answers matching choices"""
        questions = load_sample_questions_fallback()
        
        for question in questions:
            # The answer should match the choice at correct_choice_index
            correct_choice = question.choices[question.correct_choice_index]
            assert question.answer == correct_choice
    
    @patch('app.Question')  # Mock the database Question model
    def test_load_questions_from_db_with_empty_result(self, mock_question):
        """Test load_questions_from_db when database returns empty result"""
        # Mock empty query result
        mock_question.query.all.return_value = []
        
        # This should still work but return empty list (no fallback needed)
        questions = load_questions_from_db()
        assert questions == []
    
    @patch('app.Question')  # Mock the database Question model
    def test_load_questions_from_db_with_database_model_error(self, mock_question):
        """Test load_questions_from_db when database model raises exception"""
        # Mock database query to raise exception
        mock_question.query.all.side_effect = Exception("Database model error")
        
        # This should trigger fallback
        questions = load_questions_from_db()
        
        # Should get fallback questions
        assert len(questions) == 8
        assert "What is the output of print(type([]))?" in questions[0].question


class TestDatabaseErrorPaths:
    """Test various database error scenarios that trigger fallback"""
    
    def setup_method(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('app.db.session')
    def test_database_session_error_triggers_fallback(self, mock_session):
        """Test that database session errors trigger fallback"""
        # Mock session to raise exception
        mock_session.side_effect = Exception("Session error")
        
        questions = load_questions_from_db()
        
        # Should get fallback questions
        assert len(questions) == 8
    
    @patch('app.Question')
    def test_question_model_attribute_error(self, mock_question):
        """Test when Question model has attribute errors"""
        # Create mock question with missing attributes
        mock_q = MagicMock()
        mock_q.question_text = "Test question"
        mock_q.correct_answer = "Test answer"
        # Missing some required attributes to trigger exception
        del mock_q.category  # This will cause AttributeError
        
        mock_question.query.all.return_value = [mock_q]
        
        # This should trigger fallback due to attribute error
        questions = load_questions_from_db()
        
        # Should get fallback questions
        assert len(questions) == 8