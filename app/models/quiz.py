from app import db
from datetime import datetime
import uuid

class Quiz(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    duration_minutes = db.Column(db.Integer, default=30)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    # Define all relationships in Quiz model
    questions = db.relationship('Question', backref=db.backref('quiz', lazy=True), lazy=True)
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'question_count': len(self.questions)
        }
