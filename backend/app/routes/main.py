from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.models import Quiz, Question, QuizAttempt, User
from app import db
from datetime import datetime
import json
from urllib.parse import unquote
from flask_wtf import FlaskForm

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    if not current_user.approved:
        flash('Your account is pending approval.')
        return render_template('dashboard/home.html')
    
    if current_user.role == 'admin':
        return redirect(url_for('admin.index'))
    
    # For students, show the welcome page
    completed_attempts = QuizAttempt.query.filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed_at.isnot(None)
    ).all()
    
    completed_count = len(completed_attempts)
    average_score = 0
    if completed_count > 0:
        average_score = sum(attempt.score for attempt in completed_attempts) / completed_count
    
    recent_attempts = QuizAttempt.query.filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed_at.isnot(None)
    ).order_by(QuizAttempt.completed_at.desc()).limit(5).all()
    
    return render_template('dashboard/home.html',
                         completed_count=completed_count,
                         average_score=round(average_score),
                         recent_attempts=recent_attempts)

@main.route('/dashboard')
@login_required
def dashboard():
    if not current_user.approved:
        flash('Your account is pending approval.')
        return redirect(url_for('main.index'))
    
    if current_user.role == 'admin':
        return redirect(url_for('admin.index'))
    
    # For students, show quiz list
    available_quizzes = Quiz.query.filter_by(is_active=True).all()
    completed_attempts = QuizAttempt.query.filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed_at.isnot(None)
    ).all()
    
    completed_quiz_titles = {attempt.quiz.title for attempt in completed_attempts}
    new_quizzes = [quiz for quiz in available_quizzes if quiz.title not in completed_quiz_titles]
    completed_quizzes = [quiz for quiz in available_quizzes if quiz.title in completed_quiz_titles]
    
    return render_template('dashboard/quizzes.html',
                         new_quizzes=new_quizzes,
                         completed_quizzes=completed_quizzes)

@main.route('/quiz/<quiz_title>/start')
@login_required
def start_quiz(quiz_title):
    print(f"\n=== Starting Quiz: {quiz_title} ===")
    quiz = Quiz.query.filter_by(title=quiz_title).first_or_404()
    
    # Check for existing incomplete attempt
    existing_attempt = QuizAttempt.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz.id,
        completed_at=None
    ).first()
    
    if not existing_attempt:
        # Create new attempt
        existing_attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz.id,
            started_at=datetime.utcnow()
        )
        db.session.add(existing_attempt)
        db.session.commit()
        print(f"Created new attempt ID: {existing_attempt.id}")
    else:
        print(f"Found existing attempt ID: {existing_attempt.id}")
    
    return render_template('main/take_quiz.html', quiz=quiz, attempt=existing_attempt)

@main.route('/quiz/<quiz_title>/result')
@login_required
def view_result(quiz_title):
    if not current_user.approved:
        flash('Your account is pending approval.')
        return redirect(url_for('main.index'))
    
    quiz = Quiz.query.filter_by(title=quiz_title).first_or_404()
    
    # Get the latest attempt for this quiz
    attempt = QuizAttempt.query.filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.quiz_id == quiz.id,
        QuizAttempt.completed_at.isnot(None)
    ).order_by(QuizAttempt.completed_at.desc()).first_or_404()
    
    # Add debug prints
    print("\n=== Quiz Result Debug ===")
    for question in quiz.questions:
        print(f"Question: {question.text}")
        print(f"Has explanation: {hasattr(question, 'explanation')}")
        print(f"Explanation: {question.explanation}")
        print(f"Has option_explanations: {hasattr(question, 'option_explanations')}")
        print(f"Option explanations: {question.option_explanations}")
    
    return render_template('main/quiz_result.html', quiz=quiz, attempt=attempt)

@main.route('/quiz/<quiz_title>/take')
@login_required
def take_quiz(quiz_title):
    if not current_user.approved:
        flash('Your account is pending approval.')
        return redirect(url_for('main.index'))
    
    quiz = Quiz.query.filter_by(title=quiz_title).first_or_404()
    if not quiz.is_active:
        flash('This quiz is not currently available.')
        return redirect(url_for('main.index'))
    
    # Get the active attempt for this quiz
    attempt = QuizAttempt.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz.id,
        completed_at=None
    ).first()
    
    # If no active attempt exists, redirect to start_quiz
    if not attempt:
        return redirect(url_for('main.start_quiz', quiz_title=quiz_title))
    
    return render_template('main/take_quiz.html', quiz=quiz, attempt=attempt)

# Admin specific routes
@main.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('main.index'))
    
    # Get all quizzes
    all_quizzes = Quiz.query.all()
    
    # Get all users except admin
    all_users = User.query.filter(User.role != 'admin').all()
    
    print(f"Debug - Number of quizzes found: {len(all_quizzes)}")  # Add debug print
    for quiz in all_quizzes:
        print(f"Quiz: {quiz.title}")  # Add debug print
    
    return render_template('admin/quizzes.html', 
                         quizzes=all_quizzes,
                         all_users=all_users)

@main.route('/quiz/<quiz_title>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_title):
    print("\n=== Quiz Submission Debug ===")
    print(f"1. Quiz Title: {quiz_title}")
    print(f"2. Request Method: {request.method}")
    print(f"3. Form Data: {request.form}")
    
    try:
        # Find the quiz
        quiz = Quiz.query.filter_by(title=quiz_title).first()
        if not quiz:
            print(f"ERROR: Quiz not found with title: {quiz_title}")
            return "Quiz not found", 404
            
        print(f"4. Found quiz: {quiz.title} (ID: {quiz.id})")
        
        # Find the attempt
        attempt = QuizAttempt.query.filter_by(
            user_id=current_user.id,
            quiz_id=quiz.id,
            completed_at=None
        ).first()
        
        if not attempt:
            print(f"ERROR: No active attempt found for user {current_user.id} on quiz {quiz.id}")
            return "No active attempt found", 404
            
        print(f"5. Found attempt ID: {attempt.id}")
        
        # Process answers
        answers = {}
        for key, value in request.form.items():
            if key.startswith('question_'):
                question_id = key.split('_')[1]  # Keep as string
                if isinstance(value, list):
                    answers[question_id] = [int(v) for v in value if v.isdigit()]
                else:
                    answers[question_id] = [int(value)] if value.isdigit() else []
        
        print(f"6. Processed answers: {answers}")
        
        # Calculate correct answers
        correct_questions = []
        for question in quiz.questions:
            question_id = str(question.id)  # Convert to string for comparison
            if question_id in answers:
                if set(answers[question_id]) == set(question.correct_answers):
                    correct_questions.append(question.id)
        
        print(f"7. Correct questions: {correct_questions}")
        
        # Update attempt
        attempt.answers = answers
        attempt.correct_questions = correct_questions
        attempt.completed_at = datetime.utcnow()
        attempt.score = (len(correct_questions) / len(quiz.questions)) * 100 if quiz.questions else 0
        
        db.session.commit()
        print("8. Successfully saved attempt")
        
        return redirect(url_for('main.view_result', quiz_title=quiz.title))
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())
        db.session.rollback()
        return f"Error: {str(e)}", 500
