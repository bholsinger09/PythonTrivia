"""
Enhanced database models for Python Trivia Game
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import enum
from typing import Dict, List, Optional
import json

db = SQLAlchemy()

class Category(enum.Enum):
    """Question categories"""
    BASICS = "basics"
    FUNCTIONS = "functions"
    DATA_STRUCTURES = "data_structures"
    OOP = "object_oriented_programming"
    LIBRARIES = "libraries"
    ADVANCED = "advanced"
    ALGORITHMS = "algorithms"
    WEB_DEVELOPMENT = "web_development"
    DATA_SCIENCE = "data_science"
    TESTING = "testing"

class Difficulty(enum.Enum):
    """Question difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class User(UserMixin, db.Model):
    """User model for authentication and score tracking"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # User preferences
    preferred_difficulty = db.Column(db.Enum(Difficulty), default=Difficulty.EASY)
    preferred_categories = db.Column(db.Text)  # JSON string of categories
    
    # Statistics
    total_games_played = db.Column(db.Integer, default=0)
    total_questions_answered = db.Column(db.Integer, default=0)
    total_correct_answers = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    total_points = db.Column(db.Integer, default=0)
    
    # Relationships
    game_sessions = db.relationship('GameSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash using bcrypt"""
        import bcrypt
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check password against hash using bcrypt"""
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def get_preferred_categories(self) -> List[Category]:
        """Get user's preferred categories"""
        if not self.preferred_categories:
            return list(Category)
        try:
            category_names = json.loads(self.preferred_categories)
            return [Category(name) for name in category_names if name in [c.value for c in Category]]
        except (json.JSONDecodeError, ValueError):
            return list(Category)
    
    def set_preferred_categories(self, categories: List[Category]):
        """Set user's preferred categories"""
        self.preferred_categories = json.dumps([cat.value for cat in categories])
    
    def get_accuracy_percentage(self) -> float:
        """Calculate user's overall accuracy"""
        if self.total_questions_answered == 0:
            return 0.0
        return (self.total_correct_answers / self.total_questions_answered) * 100
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'total_games_played': self.total_games_played,
            'total_questions_answered': self.total_questions_answered,
            'total_correct_answers': self.total_correct_answers,
            'accuracy_percentage': self.get_accuracy_percentage(),
            'best_streak': self.best_streak,
            'total_points': self.total_points,
            'preferred_difficulty': self.preferred_difficulty.value if self.preferred_difficulty else None,
            'preferred_categories': self.get_preferred_categories()
        }

class Question(db.Model):
    """Enhanced question model with database persistence"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(500), nullable=False)
    choices = db.Column(db.Text, nullable=False)  # JSON string of choices
    correct_choice_index = db.Column(db.Integer, nullable=False)
    explanation = db.Column(db.Text)
    category = db.Column(db.Enum(Category), nullable=False, index=True)
    difficulty = db.Column(db.Enum(Difficulty), nullable=False, index=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_active = db.Column(db.Boolean, default=True)
    
    # Statistics
    times_asked = db.Column(db.Integer, default=0, index=True)
    times_correct = db.Column(db.Integer, default=0)
    times_incorrect = db.Column(db.Integer, default=0)
    
    # Relationships
    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_choices(self) -> List[str]:
        """Get question choices as list"""
        try:
            return json.loads(self.choices)
        except json.JSONDecodeError:
            return []
    
    def set_choices(self, choices: List[str]):
        """Set question choices from list"""
        self.choices = json.dumps(choices)
    
    def get_difficulty_percentage(self) -> float:
        """Calculate how difficult this question is based on success rate"""
        if self.times_asked == 0:
            return 0.0
        return (self.times_correct / self.times_asked) * 100
    
    def get_accuracy_percentage(self) -> float:
        """Get accuracy percentage for this question (alias for compatibility)"""
        return self.get_difficulty_percentage()
    
    def to_dict(self) -> Dict:
        """Convert question to dictionary"""
        return {
            'id': self.id,
            'question': self.question_text,
            'answer': self.correct_answer,
            'choices': self.get_choices(),
            'correct_choice_index': self.correct_choice_index,
            'explanation': self.explanation,
            'category': self.category.value,
            'difficulty': self.difficulty.value,
            'times_asked': self.times_asked,
            'times_correct': self.times_correct,
            'success_rate': self.get_difficulty_percentage()
        }

class GameSession(db.Model):
    """Track individual game sessions"""
    __tablename__ = 'game_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for anonymous users
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)  # For anonymous tracking
    
    # Game settings
    categories = db.Column(db.Text)  # JSON string of selected categories
    difficulty = db.Column(db.Enum(Difficulty))
    time_limit = db.Column(db.Integer)  # seconds per question
    
    # Game state
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)
    current_question_index = db.Column(db.Integer, default=0)
    
    # Statistics
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    incorrect_answers = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)
    
    # Relationships
    answers = db.relationship('Answer', backref='game_session', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_categories(self) -> List[Category]:
        """Get session categories"""
        if not self.categories:
            return list(Category)
        try:
            category_names = json.loads(self.categories)
            return [Category(name) for name in category_names]
        except (json.JSONDecodeError, ValueError):
            return list(Category)
    
    def set_categories(self, categories: List[Category]):
        """Set session categories"""
        self.categories = json.dumps([cat.value for cat in categories])
    
    def get_accuracy_percentage(self) -> float:
        """Calculate session accuracy"""
        total_answered = self.correct_answers + self.incorrect_answers
        if total_answered == 0:
            return 0.0
        return (self.correct_answers / total_answered) * 100
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'session_token': self.session_token,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_completed': self.is_completed,
            'current_question_index': self.current_question_index,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'incorrect_answers': self.incorrect_answers,
            'accuracy_percentage': self.get_accuracy_percentage(),
            'current_streak': self.current_streak,
            'best_streak': self.best_streak,
            'total_score': self.total_score,
            'categories': [cat.value for cat in self.get_categories()],
            'difficulty': self.difficulty.value if self.difficulty else None
        }

class Answer(db.Model):
    """Track individual question answers"""
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    game_session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # Answer details
    selected_choice_index = db.Column(db.Integer, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, index=True)
    time_taken = db.Column(db.Float)  # seconds
    answered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Points earned for this answer
    points_earned = db.Column(db.Integer, default=0)
    streak_bonus = db.Column(db.Integer, default=0)
    
    def to_dict(self) -> Dict:
        """Convert answer to dictionary"""
        return {
            'id': self.id,
            'question_id': self.question_id,
            'selected_choice_index': self.selected_choice_index,
            'is_correct': self.is_correct,
            'time_taken': self.time_taken,
            'answered_at': self.answered_at.isoformat(),
            'points_earned': self.points_earned,
            'streak_bonus': self.streak_bonus
        }

class Score(db.Model):
    """High scores and leaderboard"""
    __tablename__ = 'scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    game_session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False, index=True)
    
    # Score details  
    score = db.Column(db.Integer, nullable=False, index=True)
    accuracy_percentage = db.Column(db.Float, nullable=False)
    questions_answered = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Float)  # total time in seconds
    streak = db.Column(db.Integer, default=0)
    
    # Metadata
    category = db.Column(db.Enum(Category), index=True)
    difficulty = db.Column(db.Enum(Difficulty), index=True)
    achieved_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # For anonymous users
    anonymous_name = db.Column(db.String(50))
    
    def to_dict(self) -> Dict:
        """Convert score to dictionary"""
        return {
            'id': self.id,
            'score': self.score,
            'accuracy_percentage': self.accuracy_percentage,
            'questions_answered': self.questions_answered,
            'time_taken': self.time_taken,
            'streak': self.streak,
            'category': self.category.value if self.category else None,
            'difficulty': self.difficulty.value if self.difficulty else None,
            'achieved_at': self.achieved_at.isoformat(),
            'username': self.user.username if self.user else self.anonymous_name,
            'user_id': self.user_id
        }

class UserBackup(db.Model):
    """
    Deployment-compatible user backup storage
    Stores user data as JSON in database instead of local files
    """
    __tablename__ = 'user_backups'
    
    id = db.Column(db.Integer, primary_key=True)
    backup_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    backup_data = db.Column(db.Text, nullable=False)  # JSON string of user data
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict:
        """Convert backup to dictionary"""
        return {
            'id': self.id,
            'backup_name': self.backup_name,
            'backup_data': json.loads(self.backup_data),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def save_backup(cls, name: str, user_data: List[Dict]) -> 'UserBackup':
        """Save user data backup to database"""
        existing = cls.query.filter_by(backup_name=name).first()
        if existing:
            existing.backup_data = json.dumps(user_data)
            existing.updated_at = datetime.now(timezone.utc)
            backup = existing
        else:
            backup = cls(
                backup_name=name,
                backup_data=json.dumps(user_data)
            )
            db.session.add(backup)
        
        db.session.commit()
        return backup
    
    @classmethod
    def load_backup(cls, name: str) -> Optional[List[Dict]]:
        """Load user data backup from database"""
        backup = cls.query.filter_by(backup_name=name).first()
        if backup:
            return json.loads(backup.backup_data)
        return None
    
    @classmethod
    def list_backups(cls) -> List['UserBackup']:
        """List all available backups"""
        return cls.query.order_by(cls.created_at.desc()).all()
