from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import JSON, ARRAY

class QuizAttempt(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = db.Column(db.String(36), db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    score = db.Column(db.Float)
    answers = db.Column(JSON)  # Store user's answers
    correct_questions = db.Column(ARRAY(db.String))  # Store IDs of correctly answered questions

    user = db.relationship('User', backref=db.backref('quiz_attempts', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'score': self.score
        }
