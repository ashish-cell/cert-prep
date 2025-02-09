from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.models import User, Quiz, Question, QuizAttempt
from app import db
from functools import wraps
import json
from werkzeug.utils import secure_filename
import os
from collections import defaultdict
from flask_wtf import FlaskForm

# Create the admin blueprint with a url_prefix
admin = Blueprint('admin', __name__, url_prefix='/admin')

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def index():
    # Get all users and their performance data
    users = User.query.all()
    for user in users:
        user.completed_attempts = [a for a in user.quiz_attempts if a.completed_at]
        if user.completed_attempts:
            scores = [a.score for a in user.completed_attempts if a.score is not None]
            user.average_score = sum(scores) / len(scores) if scores else None
        else:
            user.average_score = None
        user.last_activity = max([a.started_at for a in user.quiz_attempts] + [user.created_at]) if user.quiz_attempts else user.created_at

    # Get recent quiz attempts
    recent_attempts = QuizAttempt.query.order_by(QuizAttempt.started_at.desc()).limit(10).all()

    return render_template('admin/dashboard.html',
                         users=users,
                         total_users=User.query.count(),
                         pending_users=User.query.filter_by(approved=False).count(),
                         total_quizzes=Quiz.query.count(),
                         active_quizzes=Quiz.query.filter_by(is_active=True).count(),
                         recent_attempts=recent_attempts)

@admin.route('/users')
@login_required
@admin_required
def users():
    users = User.query.filter(User.email != current_user.email).all()
    return render_template('admin/users.html', users=users)

@admin.route('/users/<user_id>/approve')
@login_required
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.approved = True
    db.session.commit()
    flash(f'User {user.username} has been approved!')
    return redirect(url_for('admin.users'))

@admin.route('/users/<user_id>/disapprove')
@login_required
@admin_required
def disapprove_user(user_id):
    user = User.query.get_or_404(user_id)
    user.approved = False
    db.session.commit()
    flash(f'User {user.username} has been disapproved!')
    return redirect(url_for('admin.users'))

@admin.route('/quizzes')
@login_required
@admin_required
def quizzes():
    all_quizzes = Quiz.query.all()
    return render_template('admin/quizzes.html', quizzes=all_quizzes)

@admin.route('/quizzes/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_quiz():
    if request.method == 'POST':
        quiz = Quiz(
            title=request.form['title'],
            description=request.form['description'],
            duration_minutes=int(request.form['duration']),
            created_by=current_user.id
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully!')
        return redirect(url_for('admin.edit_quiz', quiz_id=quiz.id))
    return render_template('admin/quiz_form.html')

@admin.route('/quizzes/<quiz_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        quiz.title = request.form['title']
        quiz.description = request.form['description']
        quiz.duration_minutes = int(request.form['duration'])
        db.session.commit()
        flash('Quiz updated successfully!')
        return redirect(url_for('admin.quizzes'))
    return render_template('admin/quiz_form.html', quiz=quiz)

@admin.route('/quizzes/<quiz_id>/toggle')
@login_required
@admin_required
def toggle_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    quiz.is_active = not quiz.is_active
    db.session.commit()
    flash(f'Quiz {"activated" if quiz.is_active else "deactivated"} successfully!')
    return redirect(url_for('admin.quizzes'))

@admin.route('/quiz/<quiz_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_quiz_status(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    quiz.is_active = not quiz.is_active
    db.session.commit()
    return jsonify({'success': True})

@admin.route('/quiz/<quiz_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return jsonify({'success': True})

def validate_quiz_json(content):
    """Validates the quiz JSON structure"""
    required_fields = {
        'question_id': int,
        'question_text': str,
        'domain': str,
        'options': list,
        'correct_answers': list,
        'explanations': dict
    }
    
    errors = []
    
    if not isinstance(content, list):
        return False, ["JSON must be an array of questions"]
    
    for idx, question in enumerate(content):
        # Check for required fields and their types
        for field, field_type in required_fields.items():
            if field not in question:
                errors.append(f"Question {idx + 1}: Missing required field '{field}'")
            elif not isinstance(question[field], field_type):
                errors.append(f"Question {idx + 1}: Field '{field}' must be of type {field_type.__name__}")
        
        # Validate options and correct_answers
        if 'options' in question and 'correct_answers' in question:
            if not question['options']:
                errors.append(f"Question {idx + 1}: Must have at least one option")
            if not question['correct_answers']:
                errors.append(f"Question {idx + 1}: Must have at least one correct answer")
            if max(question.get('correct_answers', [0])) >= len(question['options']):
                errors.append(f"Question {idx + 1}: Correct answer index out of range")
        
        # Validate explanations
        if 'explanations' in question:
            for opt_idx in range(len(question.get('options', []))):
                if str(opt_idx) not in question['explanations']:
                    errors.append(f"Question {idx + 1}: Missing explanation for option {opt_idx}")
    
    return len(errors) == 0, errors

@admin.route('/quizzes/validate', methods=['POST'])
@login_required
@admin_required
def validate_quiz():
    if 'quiz_file' not in request.files:
        return jsonify({'success': False, 'errors': ['No file uploaded']})
    
    file = request.files['quiz_file']
    if file.filename == '' or not file.filename.endswith('.json'):
        return jsonify({'success': False, 'errors': ['Invalid file format']})
    
    try:
        content = json.load(file)
        is_valid, errors = validate_quiz_json(content)
        
        if is_valid:
            # Generate quiz summary
            summary = {
                'total_questions': len(content),
                'domains': list(set(q['domain'] for q in content)),
                'domain_distribution': defaultdict(int),
                'sample_questions': content[:3]  # First 3 questions as preview
            }
            
            for question in content:
                summary['domain_distribution'][question['domain']] += 1
            
            return jsonify({
                'success': True,
                'summary': summary
            })
        else:
            return jsonify({
                'success': False,
                'errors': errors
            })
            
    except json.JSONDecodeError:
        return jsonify({'success': False, 'errors': ['Invalid JSON format']})
    except Exception as e:
        app.logger.error(f"Validation error: {str(e)}")
        return jsonify({'success': False, 'errors': [str(e)]})

@admin.route('/upload-quiz', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_quiz():
    form = FlaskForm()  # Create form for CSRF protection
    
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('CSRF token missing or invalid')
            return redirect(url_for('admin.quizzes'))

        if 'quiz_file' not in request.files:
            flash('No file uploaded')
            return redirect(url_for('admin.quizzes'))

        file = request.files['quiz_file']
        if not file or file.filename == '':
            flash('No file selected')
            return redirect(url_for('admin.quizzes'))

        try:
            questions = json.load(file)
            
            # Create quiz
            quiz = Quiz(
                title=file.filename.replace('.json', ''),
                description='',
                duration_minutes=30,
                created_by=current_user.id
            )
            db.session.add(quiz)
            db.session.flush()  # Get the ID without committing
            
            # Add questions
            for i, q in enumerate(questions):
                question = Question(
                    quiz_id=quiz.id,
                    text=q['question_text'],
                    options=q['options'],
                    correct_answers=q['correct_answers'],
                    explanations=q['explanations'],
                    domain=q['domain'],
                    order=i,
                    points=1
                )
                db.session.add(question)

            db.session.commit()
            flash('Quiz uploaded successfully!')

        except Exception as e:
            db.session.rollback()
            flash(f'Error uploading quiz: {str(e)}')

        return redirect(url_for('admin.quizzes'))

    # GET request - show upload form
    return render_template('admin/quiz_form.html', form=form)

@admin.route('/quiz/<quiz_title>/details')
@login_required
@admin_required
def quiz_details(quiz_title):
    quiz = Quiz.query.filter_by(title=quiz_title).first_or_404()
    attempts = QuizAttempt.query.filter_by(quiz_id=quiz.id).all()
    
    # Calculate statistics
    total_attempts = len(attempts)
    completed_attempts = len([a for a in attempts if a.completed_at])
    avg_score = sum(a.score for a in attempts if a.completed_at) / completed_attempts if completed_attempts > 0 else 0
    
    return render_template('admin/quiz_details.html', 
                         quiz=quiz, 
                         total_attempts=total_attempts,
                         completed_attempts=completed_attempts,
                         avg_score=avg_score)

# Add a new route for detailed user performance
@admin.route('/user/<string:user_id>/performance')
@login_required
@admin_required
def user_performance(user_id):
    # Use filter_by instead of get_or_404 to avoid UUID conversion
    user = User.query.filter_by(id=user_id).first_or_404()
    attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.started_at.desc()).all()
    
    return render_template('admin/user_performance.html',
                         user=user,
                         attempts=attempts)
