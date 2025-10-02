"""
Database service layer for Python Trivia Game
"""
from typing import List, Optional, Dict
from sqlalchemy import func
from models import db, User, Question, GameSession, Answer, Score, Category, Difficulty
import uuid
from datetime import datetime, timezone

class QuestionService:
    """Service for managing questions"""
    
    @staticmethod
    def get_questions_by_criteria(
        categories: List[Category] = None,
        difficulty: Difficulty = None,
        limit: int = None,
        exclude_ids: List[int] = None
    ) -> List[Question]:
        """Get questions matching criteria"""
        query = Question.query.filter(Question.is_active == True)
        
        if categories:
            query = query.filter(Question.category.in_(categories))
        
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        if exclude_ids:
            query = query.filter(~Question.id.in_(exclude_ids))
        
        query = query.order_by(func.random())  # PostgreSQL: func.random(), SQLite: func.random()
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_question_by_id(question_id: int) -> Optional[Question]:
        """Get question by ID"""
        return Question.query.filter_by(id=question_id, is_active=True).first()
    
    @staticmethod
    def create_question(
        question_text: str,
        correct_answer: str,
        choices: List[str],
        correct_choice_index: int,
        category: Category,
        difficulty: Difficulty,
        explanation: str = None,
        created_by: int = None
    ) -> Question:
        """Create a new question"""
        question = Question(
            question_text=question_text,
            correct_answer=correct_answer,
            correct_choice_index=correct_choice_index,
            category=category,
            difficulty=difficulty,
            explanation=explanation,
            created_by=created_by
        )
        question.set_choices(choices)
        
        db.session.add(question)
        db.session.commit()
        return question
    
    @staticmethod
    def update_question_stats(question_id: int, is_correct: bool):
        """Update question statistics"""
        question = Question.query.get(question_id)
        if question:
            question.times_asked += 1
            if is_correct:
                question.times_correct += 1
            else:
                question.times_incorrect += 1
            db.session.commit()
    
    @staticmethod
    def get_question_stats() -> Dict:
        """Get overall question statistics"""
        total_questions = Question.query.filter_by(is_active=True).count()
        by_category = db.session.query(
            Question.category, func.count(Question.id)
        ).filter_by(is_active=True).group_by(Question.category).all()
        
        by_difficulty = db.session.query(
            Question.difficulty, func.count(Question.id)
        ).filter_by(is_active=True).group_by(Question.difficulty).all()
        
        return {
            'total_questions': total_questions,
            'by_category': {str(cat): count for cat, count in by_category},
            'by_difficulty': {str(diff): count for diff, count in by_difficulty}
        }

class GameSessionService:
    """Service for managing game sessions"""
    
    @staticmethod
    def create_session(
        user_id: int = None,
        categories: List[Category] = None,
        difficulty: Difficulty = None,
        time_limit: int = 30
    ) -> GameSession:
        """Create a new game session"""
        session = GameSession(
            user_id=user_id,
            session_token=str(uuid.uuid4()),
            difficulty=difficulty,
            time_limit=time_limit
        )
        
        if categories:
            session.set_categories(categories)
        
        db.session.add(session)
        db.session.commit()
        return session
    
    @staticmethod
    def get_session_by_token(session_token: str) -> Optional[GameSession]:
        """Get session by token"""
        return GameSession.query.filter_by(session_token=session_token).first()
    
    @staticmethod
    def update_session_progress(
        session_id: int,
        current_question_index: int,
        correct_answers: int = None,
        incorrect_answers: int = None,
        current_streak: int = None,
        total_score: int = None
    ):
        """Update session progress"""
        session = GameSession.query.get(session_id)
        if session:
            session.current_question_index = current_question_index
            
            if correct_answers is not None:
                session.correct_answers = correct_answers
            if incorrect_answers is not None:
                session.incorrect_answers = incorrect_answers
            if current_streak is not None:
                session.current_streak = current_streak
                if current_streak > session.best_streak:
                    session.best_streak = current_streak
            if total_score is not None:
                session.total_score = total_score
            
            db.session.commit()
    
    @staticmethod
    def complete_session(session_id: int) -> GameSession:
        """Mark session as completed"""
        session = GameSession.query.get(session_id)
        if session:
            session.is_completed = True
            session.completed_at = datetime.now(timezone.utc)
            db.session.commit()
        return session
    
    @staticmethod
    def get_user_sessions(user_id: int, limit: int = 10) -> List[GameSession]:
        """Get recent sessions for a user"""
        return GameSession.query.filter_by(user_id=user_id)\
            .order_by(GameSession.started_at.desc())\
            .limit(limit).all()

class AnswerService:
    """Service for managing answers"""
    
    @staticmethod
    def record_answer(
        game_session_id: int,
        question_id: int,
        selected_choice_index: int,
        is_correct: bool,
        time_taken: float = None,
        user_id: int = None
    ) -> Answer:
        """Record a user's answer"""
        answer = Answer(
            game_session_id=game_session_id,
            question_id=question_id,
            user_id=user_id,
            selected_choice_index=selected_choice_index,
            is_correct=is_correct,
            time_taken=time_taken
        )
        
        # Calculate points (basic implementation)
        base_points = 10
        answer.points_earned = base_points if is_correct else 0
        
        db.session.add(answer)
        
        # Update question statistics
        QuestionService.update_question_stats(question_id, is_correct)
        
        db.session.commit()
        return answer
    
    @staticmethod
    def get_session_answers(session_id: int) -> List[Answer]:
        """Get all answers for a session"""
        return Answer.query.filter_by(game_session_id=session_id)\
            .order_by(Answer.answered_at).all()

class ScoreService:
    """Service for managing scores and leaderboards"""
    
    @staticmethod
    def save_score(
        game_session_id: int,
        score: int,
        accuracy_percentage: float,
        questions_answered: int,
        time_taken: float = None,
        streak: int = 0,
        category: Category = None,
        difficulty: Difficulty = None,
        user_id: int = None,
        anonymous_name: str = None
    ) -> Score:
        """Save a game score"""
        score_record = Score(
            user_id=user_id,
            game_session_id=game_session_id,
            score=score,
            accuracy_percentage=accuracy_percentage,
            questions_answered=questions_answered,
            time_taken=time_taken,
            streak=streak,
            category=category,
            difficulty=difficulty,
            anonymous_name=anonymous_name
        )
        
        db.session.add(score_record)
        db.session.commit()
        return score_record
    
    @staticmethod
    def get_leaderboard(
        category: Category = None,
        difficulty: Difficulty = None,
        limit: int = 10
    ) -> List[Score]:
        """Get leaderboard scores"""
        query = Score.query
        
        if category:
            query = query.filter_by(category=category)
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        
        return query.order_by(Score.score.desc(), Score.accuracy_percentage.desc())\
            .limit(limit).all()
    
    @staticmethod
    def get_user_best_scores(user_id: int, limit: int = 5) -> List[Score]:
        """Get user's best scores"""
        return Score.query.filter_by(user_id=user_id)\
            .order_by(Score.score.desc())\
            .limit(limit).all()

class UserService:
    """Service for managing users"""
    
    @staticmethod
    def create_user(username: str, email: str, password: str) -> User:
        """Create a new user"""
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def update_user_stats(user_id: int, game_session: GameSession):
        """Update user statistics after a game"""
        user = User.query.get(user_id)
        if user:
            user.total_games_played += 1
            user.total_questions_answered += (game_session.correct_answers + game_session.incorrect_answers)
            user.total_correct_answers += game_session.correct_answers
            user.total_points += game_session.total_score
            
            if game_session.best_streak > user.best_streak:
                user.best_streak = game_session.best_streak
            
            user.last_seen = datetime.now(timezone.utc)
            db.session.commit()

class DatabaseSeeder:
    """Seed database with initial data"""
    
    @staticmethod
    def seed_sample_questions():
        """Seed database with sample questions"""
        sample_questions = [
            {
                'question_text': "What is the output of print(type([]))?",
                'correct_answer': "<class 'list'>",
                'choices': ["<class 'list'>", "<class 'array'>"],
                'correct_choice_index': 0,
                'category': Category.BASICS,
                'difficulty': Difficulty.EASY,
                'explanation': "The type() function returns the type of an object. An empty list [] is of type 'list'."
            },
            {
                'question_text': "Which Python keyword is used to define a function?",
                'correct_answer': "def",
                'choices': ["def", "function"],
                'correct_choice_index': 0,
                'category': Category.FUNCTIONS,
                'difficulty': Difficulty.EASY,
                'explanation': "The 'def' keyword is used to define functions in Python."
            },
            {
                'question_text': "What does PEP stand for in Python?",
                'correct_answer': "Python Enhancement Proposal",
                'choices': ["Python Enhancement Proposal", "Python Executable Package"],
                'correct_choice_index': 0,
                'category': Category.BASICS,
                'difficulty': Difficulty.MEDIUM,
                'explanation': "PEP stands for Python Enhancement Proposal, which are design documents for Python."
            },
            {
                'question_text': "What is the difference between a list and a tuple in Python?",
                'correct_answer': "Lists are mutable, tuples are immutable",
                'choices': ["Lists are mutable, tuples are immutable", "Lists are immutable, tuples are mutable"],
                'correct_choice_index': 0,
                'category': Category.DATA_STRUCTURES,
                'difficulty': Difficulty.MEDIUM,
                'explanation': "Lists can be modified after creation (mutable), while tuples cannot be changed (immutable)."
            },
            {
                'question_text': "What is a decorator in Python?",
                'correct_answer': "A function that modifies another function",
                'choices': ["A function that modifies another function", "A special type of class"],
                'correct_choice_index': 0,
                'category': Category.ADVANCED,
                'difficulty': Difficulty.HARD,
                'explanation': "Decorators are a way to modify or enhance functions without permanently modifying their code."
            },
            {
                'question_text': "What does the __init__ method do in a Python class?",
                'correct_answer': "Initializes a new instance of the class",
                'choices': ["Initializes a new instance of the class", "Destroys an instance of the class"],
                'correct_choice_index': 0,
                'category': Category.OOP,
                'difficulty': Difficulty.MEDIUM,
                'explanation': "The __init__ method is the constructor that initializes new objects when they are created."
            },
            {
                'question_text': "Which library is commonly used for data analysis in Python?",
                'correct_answer': "pandas",
                'choices': ["pandas", "numpy"],
                'correct_choice_index': 0,
                'category': Category.LIBRARIES,
                'difficulty': Difficulty.EASY,
                'explanation': "Pandas is the most popular library for data manipulation and analysis in Python."
            },
            {
                'question_text': "What is the Global Interpreter Lock (GIL) in Python?",
                'correct_answer': "A mutex that prevents multiple threads from executing Python code simultaneously",
                'choices': [
                    "A mutex that prevents multiple threads from executing Python code simultaneously", 
                    "A feature that speeds up multi-threaded programs"
                ],
                'correct_choice_index': 0,
                'category': Category.ADVANCED,
                'difficulty': Difficulty.HARD,
                'explanation': "The GIL ensures that only one thread executes Python bytecode at a time, affecting multi-threading performance."
            }
        ]
        
        for q_data in sample_questions:
            question = QuestionService.create_question(**q_data)
            print(f"Created question: {question.question_text[:50]}...")
        
        print(f"Seeded {len(sample_questions)} sample questions")
    
    @staticmethod
    def create_admin_user():
        """Create an admin user for testing"""
        import os
        # Use environment variable or default for demo purposes
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin = UserService.create_user(
            username="admin",
            email="admin@pythontrivia.com",
            password=admin_password
        )
        print(f"Created admin user: {admin.username}")