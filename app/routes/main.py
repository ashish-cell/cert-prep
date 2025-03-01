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
    
    # Get all quiz attempts for the current user
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id).all()
    
    # Calculate summary statistics
    total_attempts = len(attempts)
    completed_attempts = [a for a in attempts if a.completed_at]
    total_completed = len(completed_attempts)
    
    # Calculate average score
    avg_score = 0
    if total_completed > 0:
        avg_score = sum(a.score for a in completed_attempts) / total_completed
    
    # Get unique quizzes attempted
    unique_quizzes = set(a.quiz_id for a in attempts)
    total_unique_quizzes = len(unique_quizzes)
    
    # Get recent attempts (last 5)
    recent_attempts = QuizAttempt.query.filter_by(user_id=current_user.id)\
        .order_by(QuizAttempt.started_at.desc())\
        .limit(5).all()
    
    # Get best performances
    best_performances = []
    for quiz_id in unique_quizzes:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            continue
            
        # Find best attempt for this quiz
        best_attempt = QuizAttempt.query.filter_by(
            user_id=current_user.id,
            quiz_id=quiz_id,
        ).filter(QuizAttempt.completed_at != None).order_by(QuizAttempt.score.desc()).first()
        
        if best_attempt:
            best_performances.append({
                'quiz': quiz,
                'score': best_attempt.score,
                'date': best_attempt.completed_at
            })
    
    # Sort by score (highest first)
    best_performances.sort(key=lambda x: x['score'], reverse=True)
    
    # Get available quizzes that the user hasn't attempted yet
    attempted_quiz_ids = list(unique_quizzes)
    available_quizzes = Quiz.query.filter(
        Quiz.is_active == True,
        ~Quiz.id.in_(attempted_quiz_ids) if attempted_quiz_ids else True
    ).all()
    
    return render_template('user/dashboard.html', 
                          total_attempts=total_attempts,
                          total_completed=total_completed,
                          avg_score=avg_score,
                          total_unique_quizzes=total_unique_quizzes,
                          recent_attempts=recent_attempts,
                          best_performances=best_performances,
                          available_quizzes=available_quizzes)

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
    try:
        # Find the quiz
        quiz = Quiz.query.filter_by(title=quiz_title).first()
        if not quiz:
            return "Quiz not found", 404
            
        # Find the attempt
        attempt = QuizAttempt.query.filter_by(
            user_id=current_user.id,
            quiz_id=quiz.id,
            completed_at=None
        ).first()
        
        if not attempt:
            return "No active attempt found", 404
            
        # Process answers
        answers = {}
        for key, value in request.form.lists():
            if key.startswith('question_'):
                # Extract question_id and remove any [] suffix
                question_id = key.split('_')[1].split('[')[0]  # Remove any [] suffix
                # Convert values to integers and sort them for consistent comparison
                answers[question_id] = sorted([int(v) for v in value if v.isdigit()])
                
        # Calculate correct answers
        correct_questions = []
        for question in quiz.questions:
            question_id = str(question.id)  # Convert to string for comparison
            
            if question_id in answers:
                user_answers = sorted(answers[question_id])
                correct = sorted([int(ca) for ca in question.correct_answers])
                
                if user_answers == correct:
                    correct_questions.append(question.id)
        
        # Update attempt
        attempt.answers = answers
        attempt.correct_questions = correct_questions
        attempt.completed_at = datetime.utcnow()
        attempt.score = (len(correct_questions) / len(quiz.questions)) * 100 if quiz.questions else 0
        
        db.session.commit()
        
        return redirect(url_for('main.view_result', quiz_title=quiz.title))
        
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 500

@main.route('/api/quiz/create', methods=['POST'])
@login_required
def create_quiz():
    if not current_user.role == 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    
    try:
        # Validate duration if provided
        duration = data.get('duration_minutes')
        if duration is not None:
            try:
                duration = int(duration)
                if duration <= 0:
                    return jsonify({'error': 'Duration must be a positive number'}), 400
            except ValueError:
                return jsonify({'error': 'Duration must be a valid number'}), 400
        
        quiz = Quiz(
            title=data['title'],
            description=data.get('description', ''),
            duration_minutes=duration if duration is not None else 90,  # Use provided duration or default
            created_by=current_user.id,
            is_active=data.get('is_active', True)
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        return jsonify({
            'message': 'Quiz created successfully', 
            'quiz': quiz.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@main.route('/quiz/upload', methods=['POST'])
@login_required
def upload_quiz():
    if not current_user.role == 'admin':
        flash('Unauthorized access')
        return redirect(url_for('main.index'))

    try:
        # Get the quiz time from form
        quiz_time = int(request.form.get('quiz_time', 60))
        if not 1 <= quiz_time <= 180:
            flash('Quiz time must be between 1 and 180 minutes')
            return redirect(url_for('admin.quizzes'))

        # Get the uploaded file
        if 'quiz_file' not in request.files:
            flash('No file uploaded')
            return redirect(url_for('admin.quizzes'))
        
        file = request.files['quiz_file']
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('admin.quizzes'))

        # Read and parse JSON
        quiz_data = json.load(file)
        if 'questions' not in quiz_data:
            flash('Invalid quiz format: missing questions array')
            return redirect(url_for('admin.quizzes'))

        # Create the quiz with the specified duration
        quiz = Quiz(
            title=f"Quiz_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            created_by=current_user.id,
            duration_minutes=quiz_time
        )
        db.session.add(quiz)

        # Add questions
        for i, q in enumerate(quiz_data['questions']):
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
        flash('Quiz uploaded successfully')
        return redirect(url_for('admin.quizzes'))

    except json.JSONDecodeError:
        flash('Invalid JSON file')
        return redirect(url_for('admin.quizzes'))
    except KeyError as e:
        flash(f'Missing required field: {str(e)}')
        return redirect(url_for('admin.quizzes'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error uploading quiz: {str(e)}')
        return redirect(url_for('admin.quizzes'))

@main.route('/my-quizzes')
@login_required
def my_quizzes():
    if not current_user.approved:
        flash('Your account is pending approval.')
        return redirect(url_for('main.index'))
    
    # Get all quiz attempts for the current user
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id).all()
    
    # Group attempts by quiz
    quiz_attempts = {}
    for attempt in attempts:
        quiz = Quiz.query.get(attempt.quiz_id)
        if quiz:
            if quiz.id not in quiz_attempts:
                quiz_attempts[quiz.id] = {
                    'quiz': quiz,
                    'attempts': [],
                    'best_score': 0,
                    'completed': False
                }
            
            quiz_attempts[quiz.id]['attempts'].append(attempt)
            
            # Update best score if this attempt is completed
            if attempt.completed_at and attempt.score is not None:
                quiz_attempts[quiz.id]['completed'] = True
                if attempt.score > quiz_attempts[quiz.id]['best_score']:
                    quiz_attempts[quiz.id]['best_score'] = attempt.score
    
    # Get available quizzes that the user hasn't attempted yet
    attempted_quiz_ids = list(quiz_attempts.keys())
    available_quizzes = Quiz.query.filter(
        Quiz.is_active == True,
        ~Quiz.id.in_(attempted_quiz_ids) if attempted_quiz_ids else True
    ).all()
    
    return render_template('user/my_quizzes.html', 
                          quiz_attempts=quiz_attempts.values(),
                          available_quizzes=available_quizzes)

@main.route('/quiz/<quiz_id>/delete', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
        
    try:
        # Find the quiz
        quiz = Quiz.query.get_or_404(quiz_id)
        
        # Delete all attempts for this quiz
        QuizAttempt.query.filter_by(quiz_id=quiz.id).delete()
        
        # Delete all questions for this quiz
        Question.query.filter_by(quiz_id=quiz.id).delete()
        
        # Delete the quiz
        db.session.delete(quiz)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Quiz deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting quiz: {str(e)}'}), 500
