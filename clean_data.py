#!/usr/bin/env python
from app import create_app, db
from app.models.user import User
from app.models import Quiz, Question, QuizAttempt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_database():
    """Delete all records from all tables but keep the admin user"""
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("Starting database cleanup...")
            
            # Save admin user(s) to restore later
            admin_users = User.query.filter_by(role='admin').all()
            admin_data = []
            for admin in admin_users:
                admin_data.append({
                    'username': admin.username,
                    'email': admin.email,
                    'password_hash': admin.password_hash,
                    'role': admin.role,
                    'approved': admin.approved,
                    'created_at': admin.created_at
                })
            
            # Delete all records from tables in the correct order to avoid foreign key constraints
            logger.info("Deleting quiz attempts...")
            QuizAttempt.query.delete()
            
            logger.info("Deleting questions...")
            Question.query.delete()
            
            logger.info("Deleting quizzes...")
            Quiz.query.delete()
            
            logger.info("Deleting users...")
            User.query.delete()
            
            # Commit the deletions
            db.session.commit()
            
            # Restore admin users
            logger.info("Restoring admin users...")
            for admin_info in admin_data:
                admin = User(
                    username=admin_info['username'],
                    email=admin_info['email'],
                    role=admin_info['role'],
                    approved=admin_info['approved'],
                    created_at=admin_info['created_at']
                )
                admin.password_hash = admin_info['password_hash']
                db.session.add(admin)
            
            db.session.commit()
            logger.info("Database cleanup completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during database cleanup: {str(e)}")
            raise

if __name__ == "__main__":
    confirm = input("⚠ WARNING: This will DELETE ALL DATA except admin users! Type 'yes' to continue: ")
    if confirm.lower() == 'yes':
        clean_database()
    else:
        print("Operation canceled.") 