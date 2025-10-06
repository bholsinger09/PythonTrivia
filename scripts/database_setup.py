"""
Database setup utilities for loading sample data.
"""
from models import db, User, Question, GameSession, Answer, Score, Category, Difficulty
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def load_sample_data():
    """Load sample data for testing performance optimizations."""
    try:
        # Check if data already exists
        if Question.query.count() > 0:
            logger.info("Sample data already exists")
            return
            
        # Create sample categories and difficulties
        categories = ['BASICS', 'ADVANCED', 'EXPERT']
        difficulties = ['EASY', 'MEDIUM', 'HARD']
        
        # Create sample questions
        sample_questions = []
        for i in range(100):  # Create 100 sample questions
            category = categories[i % 3]
            difficulty = difficulties[i % 3]
            
            question = Question(
                question_text=f"Sample question {i+1}",
                correct_answer=f"Answer {i+1}",
                choices='["Choice 1", "Choice 2", "Choice 3", "Choice 4"]',  # JSON string
                correct_choice_index=0,
                explanation=f"Explanation for question {i+1}",
                category=category,
                difficulty=difficulty,
                is_active=True,
                times_asked=i,  # Vary times_asked for testing
                times_correct=i // 2,
                times_incorrect=i - (i // 2),
                created_at=datetime.now(timezone.utc)
            )
            sample_questions.append(question)
        
        # Add to database
        db.session.bulk_save_objects(sample_questions)
        
        # Create sample user
        sample_user = User(
            username="test_user",
            email="test@example.com",
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(sample_user)
        
        db.session.commit()
        logger.info(f"✅ Loaded {len(sample_questions)} sample questions and 1 test user")
        
    except Exception as e:
        logger.error(f"❌ Error loading sample data: {e}")
        db.session.rollback()
        raise

if __name__ == "__main__":
    from app import app
    with app.app_context():
        load_sample_data()