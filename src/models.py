"""
Trivia Question and Card Models for Python Trivia Game
"""
from enum import Enum
from typing import List, Dict, Optional
import random
import json


class Difficulty(Enum):
    """Difficulty levels for trivia questions"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Category(Enum):
    """Categories for Python trivia questions"""
    BASICS = "basics"
    DATA_STRUCTURES = "data_structures"
    FUNCTIONS = "functions"
    OOP = "object_oriented_programming"
    LIBRARIES = "libraries"
    ADVANCED = "advanced"


class TriviaQuestion:
    """Represents a single trivia question with multiple choice answers"""
    
    def __init__(self, 
                 question: str, 
                 answer: str, 
                 category: Category, 
                 difficulty: Difficulty,
                 explanation: Optional[str] = None,
                 choices: Optional[List[str]] = None,
                 correct_choice_index: Optional[int] = None):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty
        self.explanation = explanation
        
        # Multiple choice support
        if choices and correct_choice_index is not None:
            self.choices = choices
            self.correct_choice_index = correct_choice_index
        else:
            # Generate simple True/False choices if none provided
            self.choices = [answer, self._generate_wrong_answer()]
            self.correct_choice_index = 0
            
    def _generate_wrong_answer(self) -> str:
        """Generate a plausible wrong answer based on the correct answer"""
        answer_lower = self.answer.lower()
        
        # Common wrong answers for different types
        if answer_lower in ['true', 'yes', 'correct']:
            return 'False'
        elif answer_lower in ['false', 'no', 'incorrect']:
            return 'True'
        elif 'list' in answer_lower:
            return 'tuple'
        elif 'tuple' in answer_lower:
            return 'list'
        elif 'dict' in answer_lower or 'dictionary' in answer_lower:
            return 'list'
        elif 'def' in answer_lower:
            return 'class'
        elif 'class' in answer_lower:
            return 'def'
        else:
            # Generic wrong answer
            return f"Not {self.answer}"
        
    def to_dict(self) -> Dict:
        """Convert question to dictionary for JSON serialization"""
        return {
            'question': self.question,
            'answer': self.answer,
            'category': self.category.value,
            'difficulty': self.difficulty.value,
            'explanation': self.explanation,
            'choices': self.choices,
            'correct_choice_index': self.correct_choice_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TriviaQuestion':
        """Create TriviaQuestion from dictionary"""
        return cls(
            question=data['question'],
            answer=data['answer'],
            category=Category(data['category']),
            difficulty=Difficulty(data['difficulty']),
            explanation=data.get('explanation'),
            choices=data.get('choices'),
            correct_choice_index=data.get('correct_choice_index')
        )


class TriviaCard:
    """Represents a flip card containing a trivia question"""
    
    def __init__(self, trivia_question: TriviaQuestion, card_id: Optional[int] = None):
        self.trivia_question = trivia_question
        self.card_id = card_id
        self.is_flipped = False
        self.is_answered_correctly = None
        
    def flip_card(self):
        """Flip the card to show the answer"""
        self.is_flipped = True
        
    def mark_correct(self):
        """Mark the card as answered correctly"""
        self.is_answered_correctly = True
        
    def mark_incorrect(self):
        """Mark the card as answered incorrectly"""
        self.is_answered_correctly = False
        
    def reset(self):
        """Reset the card to its initial state"""
        self.is_flipped = False
        self.is_answered_correctly = None
        
    def to_dict(self) -> Dict:
        """Convert card to dictionary for JSON serialization"""
        return {
            'card_id': self.card_id,
            'trivia_question': self.trivia_question.to_dict(),
            'is_flipped': self.is_flipped,
            'is_answered_correctly': self.is_answered_correctly
        }


class TriviaGame:
    """Manages the trivia game state and deck of cards"""
    
    def __init__(self):
        self.cards: List[TriviaCard] = []
        self.current_card_index = 0
        self.score = 0
        self.total_questions = 0
        
    def add_question(self, trivia_question: TriviaQuestion):
        """Add a question to the game deck"""
        card_id = len(self.cards)
        card = TriviaCard(trivia_question, card_id)
        self.cards.append(card)
        self.total_questions += 1
        
    def get_current_card(self) -> Optional[TriviaCard]:
        """Get the current card being displayed"""
        if 0 <= self.current_card_index < len(self.cards):
            return self.cards[self.current_card_index]
        return None
        
    def next_card(self) -> Optional[TriviaCard]:
        """Move to the next card"""
        if self.current_card_index < len(self.cards) - 1:
            self.current_card_index += 1
            return self.get_current_card()
        return None
        
    def previous_card(self) -> Optional[TriviaCard]:
        """Move to the previous card"""
        if self.current_card_index > 0:
            self.current_card_index -= 1
            return self.get_current_card()
        return None
        
    def shuffle_cards(self):
        """Shuffle the deck of cards"""
        random.shuffle(self.cards)
        # Reset card IDs after shuffling
        for i, card in enumerate(self.cards):
            card.card_id = i
            
    def answer_current_card(self, is_correct: bool):
        """Mark the current card as answered correctly or incorrectly"""
        current_card = self.get_current_card()
        if current_card:
            if is_correct:
                current_card.mark_correct()
                self.score += 1
            else:
                current_card.mark_incorrect()
                
    def get_score_percentage(self) -> float:
        """Get the current score as a percentage"""
        answered_cards = sum(1 for card in self.cards if card.is_answered_correctly is not None)
        if answered_cards == 0:
            return 0.0
        return (self.score / answered_cards) * 100
        
    def reset_game(self):
        """Reset the game to initial state"""
        self.current_card_index = 0
        self.score = 0
        for card in self.cards:
            card.reset()
            
    def filter_by_category(self, category: Category) -> List[TriviaCard]:
        """Get all cards from a specific category"""
        return [card for card in self.cards if card.trivia_question.category == category]
        
    def filter_by_difficulty(self, difficulty: Difficulty) -> List[TriviaCard]:
        """Get all cards of a specific difficulty"""
        return [card for card in self.cards if card.trivia_question.difficulty == difficulty]
        
    def to_dict(self) -> Dict:
        """Convert game state to dictionary for JSON serialization"""
        return {
            'cards': [card.to_dict() for card in self.cards],
            'current_card_index': self.current_card_index,
            'score': self.score,
            'total_questions': self.total_questions
        }