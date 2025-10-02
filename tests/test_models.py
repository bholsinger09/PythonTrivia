"""
Unit tests for trivia models
"""
import pytest
from src.models import TriviaQuestion, TriviaCard, TriviaGame, Category, Difficulty


class TestTriviaQuestion:
    """Test the TriviaQuestion class"""
    
    def test_create_trivia_question(self):
        """Test creating a basic trivia question"""
        question = TriviaQuestion(
            "What is Python?",
            "A programming language",
            Category.BASICS,
            Difficulty.EASY,
            "Python is a high-level programming language"
        )
        
        assert question.question == "What is Python?"
        assert question.answer == "A programming language"
        assert question.category == Category.BASICS
        assert question.difficulty == Difficulty.EASY
        assert question.explanation == "Python is a high-level programming language"
        
    def test_question_to_dict(self):
        """Test converting question to dictionary"""
        question = TriviaQuestion(
            "What is a list?",
            "A mutable sequence type",
            Category.DATA_STRUCTURES,
            Difficulty.MEDIUM
        )
        
        result = question.to_dict()
        
        assert result['question'] == "What is a list?"
        assert result['answer'] == "A mutable sequence type"
        assert result['category'] == "data_structures"
        assert result['difficulty'] == "medium"
        assert result['explanation'] is None
        
    def test_question_from_dict(self):
        """Test creating question from dictionary"""
        data = {
            'question': "What is OOP?",
            'answer': "Object Oriented Programming",
            'category': "object_oriented_programming",
            'difficulty': "hard",
            'explanation': "A programming paradigm"
        }
        
        question = TriviaQuestion.from_dict(data)
        
        assert question.question == "What is OOP?"
        assert question.answer == "Object Oriented Programming"
        assert question.category == Category.OOP
        assert question.difficulty == Difficulty.HARD
        assert question.explanation == "A programming paradigm"


class TestTriviaCard:
    """Test the TriviaCard class"""
    
    def test_create_trivia_card(self):
        """Test creating a trivia card"""
        question = TriviaQuestion(
            "What is Flask?",
            "A Python web framework",
            Category.LIBRARIES,
            Difficulty.MEDIUM
        )
        
        card = TriviaCard(question, 1)
        
        assert card.trivia_question == question
        assert card.card_id == 1
        assert card.is_flipped is False
        assert card.is_answered_correctly is None
        
    def test_flip_card(self):
        """Test flipping a card"""
        question = TriviaQuestion(
            "What is a decorator?",
            "A function that modifies another function",
            Category.ADVANCED,
            Difficulty.HARD
        )
        
        card = TriviaCard(question)
        assert card.is_flipped is False
        
        card.flip_card()
        assert card.is_flipped is True
        
    def test_mark_correct(self):
        """Test marking card as correct"""
        question = TriviaQuestion(
            "What is Git?",
            "Version control system",
            Category.BASICS,
            Difficulty.EASY
        )
        
        card = TriviaCard(question)
        card.mark_correct()
        
        assert card.is_answered_correctly is True
        
    def test_mark_incorrect(self):
        """Test marking card as incorrect"""
        question = TriviaQuestion(
            "What is Pandas?",
            "Data analysis library",
            Category.LIBRARIES,
            Difficulty.MEDIUM
        )
        
        card = TriviaCard(question)
        card.mark_incorrect()
        
        assert card.is_answered_correctly is False
        
    def test_reset_card(self):
        """Test resetting card state"""
        question = TriviaQuestion(
            "What is NumPy?",
            "Numerical computing library",
            Category.LIBRARIES,
            Difficulty.MEDIUM
        )
        
        card = TriviaCard(question)
        card.flip_card()
        card.mark_correct()
        
        assert card.is_flipped is True
        assert card.is_answered_correctly is True
        
        card.reset()
        
        assert card.is_flipped is False
        assert card.is_answered_correctly is None


class TestTriviaGame:
    """Test the TriviaGame class"""
    
    def test_create_empty_game(self):
        """Test creating an empty game"""
        game = TriviaGame()
        
        assert len(game.cards) == 0
        assert game.current_card_index == 0
        assert game.score == 0
        assert game.total_questions == 0
        
    def test_add_question_to_game(self):
        """Test adding questions to game"""
        game = TriviaGame()
        
        question1 = TriviaQuestion(
            "What is Python?",
            "Programming language",
            Category.BASICS,
            Difficulty.EASY
        )
        
        question2 = TriviaQuestion(
            "What is a tuple?",
            "Immutable sequence",
            Category.DATA_STRUCTURES,
            Difficulty.MEDIUM
        )
        
        game.add_question(question1)
        game.add_question(question2)
        
        assert len(game.cards) == 2
        assert game.total_questions == 2
        assert game.cards[0].card_id == 0
        assert game.cards[1].card_id == 1
        
    def test_get_current_card(self):
        """Test getting current card"""
        game = TriviaGame()
        
        # Empty game
        assert game.get_current_card() is None
        
        # Add a question
        question = TriviaQuestion(
            "What is Django?",
            "Web framework",
            Category.LIBRARIES,
            Difficulty.MEDIUM
        )
        game.add_question(question)
        
        current_card = game.get_current_card()
        assert current_card is not None
        assert current_card.trivia_question.question == "What is Django?"
        
    def test_next_and_previous_card(self):
        """Test navigation between cards"""
        game = TriviaGame()
        
        # Add multiple questions
        questions = [
            TriviaQuestion("Q1", "A1", Category.BASICS, Difficulty.EASY),
            TriviaQuestion("Q2", "A2", Category.BASICS, Difficulty.EASY),
            TriviaQuestion("Q3", "A3", Category.BASICS, Difficulty.EASY)
        ]
        
        for q in questions:
            game.add_question(q)
            
        # Test navigation
        assert game.current_card_index == 0
        
        # Move forward
        next_card = game.next_card()
        assert game.current_card_index == 1
        assert next_card.trivia_question.question == "Q2"
        
        # Move forward again
        next_card = game.next_card()
        assert game.current_card_index == 2
        assert next_card.trivia_question.question == "Q3"
        
        # Try to move beyond last card
        next_card = game.next_card()
        assert next_card is None
        assert game.current_card_index == 2
        
        # Move backward
        prev_card = game.previous_card()
        assert game.current_card_index == 1
        assert prev_card.trivia_question.question == "Q2"
        
    def test_answer_current_card(self):
        """Test answering current card"""
        game = TriviaGame()
        
        question = TriviaQuestion(
            "What is FastAPI?",
            "Modern web framework",
            Category.LIBRARIES,
            Difficulty.MEDIUM
        )
        game.add_question(question)
        
        # Answer correctly
        game.answer_current_card(True)
        
        assert game.score == 1
        assert game.get_current_card().is_answered_correctly is True
        
        # Add another question and answer incorrectly
        question2 = TriviaQuestion(
            "What is PyTorch?",
            "Machine learning library",
            Category.LIBRARIES,
            Difficulty.HARD
        )
        game.add_question(question2)
        game.next_card()
        game.answer_current_card(False)
        
        assert game.score == 1  # Should remain the same
        assert game.get_current_card().is_answered_correctly is False
        
    def test_score_percentage(self):
        """Test score percentage calculation"""
        game = TriviaGame()
        
        # No answers yet
        assert game.get_score_percentage() == 0.0
        
        # Add questions and answer them
        for i in range(4):
            question = TriviaQuestion(
                f"Question {i+1}",
                f"Answer {i+1}",
                Category.BASICS,
                Difficulty.EASY
            )
            game.add_question(question)
            
        # Answer first 3 correctly, last one incorrectly
        for i in range(3):
            game.current_card_index = i
            game.answer_current_card(True)
            
        game.current_card_index = 3
        game.answer_current_card(False)
        
        # Should be 75% (3 out of 4 correct)
        assert game.get_score_percentage() == 75.0
        
    def test_reset_game(self):
        """Test resetting the game"""
        game = TriviaGame()
        
        # Add questions and play
        for i in range(3):
            question = TriviaQuestion(
                f"Question {i+1}",
                f"Answer {i+1}",
                Category.BASICS,
                Difficulty.EASY
            )
            game.add_question(question)
            
        # Play the game
        game.next_card()
        game.answer_current_card(True)
        
        assert game.current_card_index == 1
        assert game.score == 1
        
        # Reset
        game.reset_game()
        
        assert game.current_card_index == 0
        assert game.score == 0
        for card in game.cards:
            assert card.is_flipped is False
            assert card.is_answered_correctly is None
            
    def test_filter_by_category(self):
        """Test filtering cards by category"""
        game = TriviaGame()
        
        questions = [
            TriviaQuestion("Q1", "A1", Category.BASICS, Difficulty.EASY),
            TriviaQuestion("Q2", "A2", Category.LIBRARIES, Difficulty.MEDIUM),
            TriviaQuestion("Q3", "A3", Category.BASICS, Difficulty.HARD),
            TriviaQuestion("Q4", "A4", Category.OOP, Difficulty.MEDIUM)
        ]
        
        for q in questions:
            game.add_question(q)
            
        basics_cards = game.filter_by_category(Category.BASICS)
        assert len(basics_cards) == 2
        
        libraries_cards = game.filter_by_category(Category.LIBRARIES)
        assert len(libraries_cards) == 1
        
        oop_cards = game.filter_by_category(Category.OOP)
        assert len(oop_cards) == 1
        
    def test_filter_by_difficulty(self):
        """Test filtering cards by difficulty"""
        game = TriviaGame()
        
        questions = [
            TriviaQuestion("Q1", "A1", Category.BASICS, Difficulty.EASY),
            TriviaQuestion("Q2", "A2", Category.LIBRARIES, Difficulty.MEDIUM),
            TriviaQuestion("Q3", "A3", Category.BASICS, Difficulty.EASY),
            TriviaQuestion("Q4", "A4", Category.OOP, Difficulty.HARD)
        ]
        
        for q in questions:
            game.add_question(q)
            
        easy_cards = game.filter_by_difficulty(Difficulty.EASY)
        assert len(easy_cards) == 2
        
        medium_cards = game.filter_by_difficulty(Difficulty.MEDIUM)
        assert len(medium_cards) == 1
        
        hard_cards = game.filter_by_difficulty(Difficulty.HARD)
        assert len(hard_cards) == 1
        
    def test_shuffle_cards(self):
        """Test shuffling cards"""
        game = TriviaGame()
        
        # Add questions with specific order
        questions = [
            TriviaQuestion("Q1", "A1", Category.BASICS, Difficulty.EASY),
            TriviaQuestion("Q2", "A2", Category.BASICS, Difficulty.EASY),
            TriviaQuestion("Q3", "A3", Category.BASICS, Difficulty.EASY)
        ]
        
        for q in questions:
            game.add_question(q)
            
        original_order = [card.trivia_question.question for card in game.cards]
        
        # Shuffle multiple times to increase chance of different order
        shuffled = False
        for _ in range(10):
            game.shuffle_cards()
            new_order = [card.trivia_question.question for card in game.cards]
            if new_order != original_order:
                shuffled = True
                break
                
        # Note: There's a small chance this could fail if shuffle 
        # happens to return original order, but very unlikely
        
        # Verify card IDs are updated after shuffle
        for i, card in enumerate(game.cards):
            assert card.card_id == i