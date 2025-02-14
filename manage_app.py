import os
import sys
import subprocess
import signal
import time

def cleanup_database():
    """Clean up all quizzes, questions and attempts"""
    from app import create_app, db
    from app.models.quiz import Quiz
    from app.models.question import Question
    from app.models.quiz_attempt import QuizAttempt

    app = create_app()
    with app.app_context():
        try:
            QuizAttempt.query.delete()
            Question.query.delete()
            Quiz.query.delete()
            db.session.commit()
            print("Database cleaned successfully")
        except Exception as e:
            print(f"Database cleanup error: {str(e)}")

def start_background_app():
    """Start the application in the background with nohup"""
    try:
        # Kill any existing gunicorn processes
        subprocess.run(['pkill', 'gunicorn'], check=False)
        
        # Start gunicorn in the background
        cmd = [
            'nohup', 
            'gunicorn',
            '--bind', '127.0.0.1:8000',
            '--workers', '3',
            '--daemon',  # Run in background
            '--access-logfile', 'access.log',
            '--error-logfile', 'error.log',
            'application:application'
        ]
        
        subprocess.run(cmd, check=True)
        print("Application started in background")
        
        # Verify it's running
        time.sleep(2)
        result = subprocess.run(['ps', 'aux', '|', 'grep', 'gunicorn'], 
                              shell=True, capture_output=True, text=True)
        print("\nRunning processes:")
        print(result.stdout)
        
    except Exception as e:
        print(f"Error starting application: {str(e)}")

def check_app_status():
    """Check if the application is running"""
    try:
        result = subprocess.run(['ps', 'aux', '|', 'grep', 'gunicorn'], 
                              shell=True, capture_output=True, text=True)
        print("Application status:")
        print(result.stdout)
        
        # Check nginx status
        nginx_status = subprocess.run(['sudo', 'systemctl', 'status', 'nginx'], 
                                    capture_output=True, text=True)
        print("\nNginx status:")
        print(nginx_status.stdout)
    except Exception as e:
        print(f"Error checking status: {str(e)}")

if __name__ == "__main__":
    command = input("""
    Choose an action:
    1. Clean database (delete all quizzes)
    2. Start application in background
    3. Check application status
    Enter number: """)
    
    if command == "1":
        cleanup_database()
    elif command == "2":
        start_background_app()
    elif command == "3":
        check_app_status()
    else:
        print("Invalid command")