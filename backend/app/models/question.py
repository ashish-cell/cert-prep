from app import db
import uuid
from sqlalchemy.dialects.postgresql import ARRAY, JSON

class Question(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = db.Column(db.String(36), db.ForeignKey('quiz.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)  # List of options
    correct_answers = db.Column(db.JSON, nullable=False)  # List of correct answer indices
    explanations = db.Column(db.JSON)  # Dictionary of explanations for each option
    domain = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, default=1)
    order = db.Column(db.Integer, nullable=False)
    
    @property
    def explanation(self):
        """General explanation is stored in the correct answer's explanation"""
        if self.explanations and str(self.correct_answers[0]) in self.explanations:
            return self.explanations[str(self.correct_answers[0])]
        return None

    @property
    def option_explanations(self):
        """Return a list of explanations for each option"""
        if not self.explanations:
            return None
        return [self.explanations.get(str(i), "") for i in range(len(self.options))]

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'domain': self.domain,
            'options': self.options,
            'points': self.points,
            'order': self.order
        }

    def check_answer(self, selected_answers):
        return sorted(selected_answers) == sorted(self.correct_answers)
