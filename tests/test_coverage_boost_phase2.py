"""
PHASE 2: Targeted coverage tests for specific missing lines
Focus on achieving 95%+ coverage by hitting uncovered lines: 59, 61, 63, 65, 67, 69, 71, 130, 215
"""
import unittest
import sys
import os

# Add the src directory to sys.path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from models import TriviaQuestion, TriviaCard, TriviaGame, Category, Difficulty


class TestUncoveredLines:
    """Tests specifically targeting uncovered lines for 95%+ coverage"""
    
    def test_generate_wrong_answer_edge_cases(self):
        """Test all branches of _generate_wrong_answer method (lines 59-71)"""
        
        # Line 59: 'true' case
        question1 = TriviaQuestion("Is this true?", "True", Category.BASICS, Difficulty.EASY)
        wrong_answer1 = question1._generate_wrong_answer()
        assert wrong_answer1 == 'False'
        
        # Line 61: 'false' case  
        question2 = TriviaQuestion("Is this false?", "False", Category.BASICS, Difficulty.EASY)
        wrong_answer2 = question2._generate_wrong_answer()
        assert wrong_answer2 == 'True'
        
        # Line 63: 'list' case
        question3 = TriviaQuestion("What is a list?", "list data structure", Category.BASICS, Difficulty.EASY)
        wrong_answer3 = question3._generate_wrong_answer()
        assert wrong_answer3 == 'tuple'
        
        # Line 65: 'tuple' case
        question4 = TriviaQuestion("What is a tuple?", "tuple data structure", Category.BASICS, Difficulty.EASY)
        wrong_answer4 = question4._generate_wrong_answer()
        assert wrong_answer4 == 'list'
        
        # Line 67: 'dict'/'dictionary' case
        question5 = TriviaQuestion("What is a dict?", "dictionary structure", Category.BASICS, Difficulty.EASY)
        wrong_answer5 = question5._generate_wrong_answer()
        assert wrong_answer5 == 'list'
        
        # Line 69: 'def' case
        question6 = TriviaQuestion("What is def?", "def keyword", Category.BASICS, Difficulty.EASY)
        wrong_answer6 = question6._generate_wrong_answer()
        assert wrong_answer6 == 'class'
        
        # Line 71: 'class' case
        question7 = TriviaQuestion("What is class?", "class keyword", Category.BASICS, Difficulty.EASY)
        wrong_answer7 = question7._generate_wrong_answer()
        assert wrong_answer7 == 'def'
        
        # Line 74: Default 'else' case
        question8 = TriviaQuestion("What is Python?", "programming language", Category.BASICS, Difficulty.EASY)
        wrong_answer8 = question8._generate_wrong_answer()
        assert wrong_answer8 == "Not programming language"
    
    def test_trivia_card_to_dict(self):
        """Test TriviaCard.to_dict method (line 130)"""
        question = TriviaQuestion("Test question?", "Test answer", Category.BASICS, Difficulty.EASY)
        card = TriviaCard(question, card_id=1)
        
        # Line 130: to_dict method call
        card_dict = card.to_dict()
        
        expected = {
            'card_id': 1,
            'trivia_question': question.to_dict(),
            'is_flipped': False,
            'is_answered_correctly': None
        }
        assert card_dict == expected
    
    def test_trivia_game_to_dict(self):
        """Test TriviaGame.to_dict method (line 215)"""
        game = TriviaGame()
        
        # Add some test questions
        question1 = TriviaQuestion("Q1?", "A1", Category.BASICS, Difficulty.EASY)
        question2 = TriviaQuestion("Q2?", "A2", Category.BASICS, Difficulty.MEDIUM)
        game.add_question(question1)
        game.add_question(question2)
        
        # Line 215: to_dict method call
        game_dict = game.to_dict()
        
        assert 'cards' in game_dict
        assert 'current_card_index' in game_dict
        assert 'score' in game_dict
        assert 'total_questions' in game_dict
        assert len(game_dict['cards']) == 2
        assert game_dict['current_card_index'] == 0
        assert game_dict['score'] == 0
        assert game_dict['total_questions'] == 2
        
        # Verify cards are properly serialized
        for i, card_data in enumerate(game_dict['cards']):
            assert 'card_id' in card_data
            assert 'trivia_question' in card_data
            assert 'is_flipped' in card_data
            assert 'is_answered_correctly' in card_data
    
    def test_multiple_choice_constructor(self):
        """Test TriviaQuestion constructor with multiple choice (lines 46-47)"""
        # Lines 46-47: Multiple choice path
        question = TriviaQuestion(
            question="What is Python?",
            answer="A programming language", 
            category=Category.BASICS,
            difficulty=Difficulty.EASY,
            choices=["A programming language", "A snake", "A movie", "A book"],
            correct_choice_index=0
        )
        
        assert question.choices == ["A programming language", "A snake", "A movie", "A book"]
        assert question.correct_choice_index == 0
    
    def test_previous_card_at_beginning(self):
        """Test previous_card method when at beginning (line 172)"""
        game = TriviaGame()
        question = TriviaQuestion("Test?", "Answer", Category.BASICS, Difficulty.EASY)
        game.add_question(question)
        
        # Already at index 0, so previous_card should return None (line 172)
        assert game.current_card_index == 0
        result = game.previous_card()
        assert result is None


if __name__ == '__main__':
    unittest.main()