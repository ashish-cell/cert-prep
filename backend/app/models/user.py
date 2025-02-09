from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import uuid

class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), default='user')  # 'user' or 'admin'
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    is_active = db.Column(db.Boolean, default=True)

    # Add these lines
    created_quizzes = db.relationship('Quiz', backref='creator', lazy=True,
                                    foreign_keys='Quiz.created_by')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,  # No need to convert to string anymore
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'approved': self.approved
        }

    @property
    def is_authenticated(self):
        return True

    def get_id(self):
        return self.id  # No need to convert to string anymore
