"""
Advanced Question Randomization System
Provides intelligent question selection with duplicate avoidance and balanced distribution
"""
import random
from typing import List, Set, Dict, Optional, Tuple
from models import Question, Category, Difficulty, User, Answer
from datetime import datetime, timedelta

class SmartQuestionSelector:
    """Intelligent question selection with memory and balancing"""
    
    def __init__(self, user_id: Optional[int] = None, session_length: int = 20):
        self.user_id = user_id
        self.session_length = session_length
        self.recent_questions: Set[int] = set()
        self.user_history: Set[int] = set()
        self.category_weights: Dict[Category, float] = {}
        self.difficulty_weights: Dict[Difficulty, float] = {}
        
        # Load user history if available
        if user_id:
            self._load_user_history()
    
    def _load_user_history(self, days_back: int = 7):
        """Load user's recent question history to avoid immediate repeats"""
        if not self.user_id:
            return
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get questions answered by user in last week
        recent_answers = Answer.query.filter(
            Answer.user_id == self.user_id,
            Answer.answered_at >= cutoff_date
        ).all()
        
        self.user_history = set(answer.question_id for answer in recent_answers)
        print(f"Loaded {len(self.user_history)} recent questions for user {self.user_id}")
    
    def _calculate_category_weights(self, available_questions: List[Question]) -> Dict[Category, float]:
        """Calculate weights for categories based on user performance and preferences"""
        weights = {}
        
        if not self.user_id:
            # Equal weights for anonymous users
            categories = set(q.category for q in available_questions)
            return {cat: 1.0 for cat in categories}
        
        # For authenticated users, analyze performance
        for category in Category:
            # Get user's accuracy in this category
            user_answers = Answer.query.filter(
                Answer.user_id == self.user_id,
                Answer.question.has(category=category)
            ).all()
            
            if not user_answers:
                weights[category] = 1.0  # Default weight
                continue
            
            accuracy = sum(1 for a in user_answers if a.is_correct) / len(user_answers)
            
            # Weight inversely to accuracy (focus on weaker areas)
            # But not too extreme - keep it between 0.5 and 2.0
            if accuracy < 0.4:
                weights[category] = 2.0  # More questions from weak areas
            elif accuracy < 0.7:
                weights[category] = 1.5
            elif accuracy > 0.9:
                weights[category] = 0.5  # Fewer from mastered areas
            else:
                weights[category] = 1.0
        
        return weights
    
    def _calculate_difficulty_weights(self, available_questions: List[Question]) -> Dict[Difficulty, float]:
        """Calculate weights for difficulty based on user level"""
        weights = {}
        
        if not self.user_id:
            # Balanced for anonymous users
            return {diff: 1.0 for diff in Difficulty}
        
        # Get user's overall accuracy
        user_answers = Answer.query.filter_by(user_id=self.user_id).all()
        
        if not user_answers:
            # New user - start with easier questions
            return {
                Difficulty.EASY: 2.0,
                Difficulty.MEDIUM: 1.0,
                Difficulty.HARD: 0.5,
                Difficulty.EXPERT: 0.2
            }
        
        overall_accuracy = sum(1 for a in user_answers if a.is_correct) / len(user_answers)
        
        # Adjust difficulty based on performance
        if overall_accuracy < 0.5:
            # Struggling user - more easy questions
            weights = {
                Difficulty.EASY: 2.5,
                Difficulty.MEDIUM: 1.0,
                Difficulty.HARD: 0.3,
                Difficulty.EXPERT: 0.1
            }
        elif overall_accuracy < 0.7:
            # Average user - balanced with slight easy bias
            weights = {
                Difficulty.EASY: 1.5,
                Difficulty.MEDIUM: 2.0,
                Difficulty.HARD: 1.0,
                Difficulty.EXPERT: 0.5
            }
        elif overall_accuracy < 0.85:
            # Good user - more challenging
            weights = {
                Difficulty.EASY: 0.8,
                Difficulty.MEDIUM: 1.5,
                Difficulty.HARD: 2.0,
                Difficulty.EXPERT: 1.0
            }
        else:
            # Expert user - focus on hard questions
            weights = {
                Difficulty.EASY: 0.3,
                Difficulty.MEDIUM: 1.0,
                Difficulty.HARD: 2.0,
                Difficulty.EXPERT: 2.5
            }
        
        return weights
    
    def select_questions(
        self, 
        available_questions: List[Question],
        count: int = None
    ) -> List[Question]:
        """Select questions using intelligent algorithm"""
        
        if count is None:
            count = self.session_length
        
        if not available_questions:
            return []
        
        # Remove recently answered questions
        filtered_questions = [
            q for q in available_questions 
            if q.id not in self.user_history and q.id not in self.recent_questions
        ]
        
        # If we filtered too many, add some back (but prefer not recent)
        if len(filtered_questions) < count:
            print(f"Not enough unique questions ({len(filtered_questions)}), adding some recent ones")
            remaining_needed = count - len(filtered_questions)
            recent_but_not_session = [
                q for q in available_questions 
                if q.id in self.user_history and q.id not in self.recent_questions
            ]
            filtered_questions.extend(random.sample(
                recent_but_not_session, 
                min(remaining_needed, len(recent_but_not_session))
            ))
        
        # Calculate weights
        self.category_weights = self._calculate_category_weights(filtered_questions)
        self.difficulty_weights = self._calculate_difficulty_weights(filtered_questions)
        
        # Weighted selection
        selected = []
        remaining_questions = filtered_questions.copy()
        
        for _ in range(min(count, len(remaining_questions))):
            if not remaining_questions:
                break
            
            # Calculate weights for remaining questions
            weights = []
            for question in remaining_questions:
                category_weight = self.category_weights.get(question.category, 1.0)
                difficulty_weight = self.difficulty_weights.get(question.difficulty, 1.0)
                
                # Boost weight for less frequently asked questions
                frequency_weight = 1.0 / max(1, question.times_asked / 10)
                
                total_weight = category_weight * difficulty_weight * frequency_weight
                weights.append(total_weight)
            
            # Weighted random selection
            selected_question = random.choices(remaining_questions, weights=weights, k=1)[0]
            selected.append(selected_question)
            remaining_questions.remove(selected_question)
            
            # Track this question
            self.recent_questions.add(selected_question.id)
        
        # Shuffle final list to avoid predictable patterns
        random.shuffle(selected)
        
        print(f"Selected {len(selected)} questions with smart algorithm")
        return selected
    
    def get_selection_stats(self) -> Dict:
        """Get statistics about current selection weights"""
        return {
            'category_weights': {cat.value: weight for cat, weight in self.category_weights.items()},
            'difficulty_weights': {diff.value: weight for diff, weight in self.difficulty_weights.items()},
            'recent_questions_count': len(self.recent_questions),
            'user_history_count': len(self.user_history)
        }

def get_smart_questions(
    user_id: Optional[int] = None,
    categories: List[Category] = None,
    difficulty: Difficulty = None,
    count: int = 20
) -> List[Question]:
    """Get intelligently selected questions"""
    
    # Get base question pool
    query = Question.query.filter_by(is_active=True)
    
    if categories:
        query = query.filter(Question.category.in_(categories))
    
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    available_questions = query.all()
    
    if not available_questions:
        print("No questions found matching criteria")
        return []
    
    # Use smart selector
    selector = SmartQuestionSelector(user_id=user_id, session_length=count)
    selected = selector.select_questions(available_questions, count)
    
    # Update question statistics
    for question in selected:
        question.times_asked = (question.times_asked or 0) + 1
    
    # Commit the updates
    from models import db
    db.session.commit()
    
    return selected