from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db

# Create the blueprint
auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('auth/signup.html')
    
    if request.method == 'POST':
        print("Signup POST request received")
        print(f"Form data: {request.form}")
        print(f"CSRF token: {request.form.get('csrf_token')}")
        
        data = request.form
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            flash('Email already registered')
            return redirect(url_for('auth.signup'))
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please wait for admin approval.')
        return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    if request.method == 'POST':
        print("Login POST request received")
        print(f"Form data: {request.form}")
        print(f"CSRF token: {request.form.get('csrf_token')}")
        
        data = request.form
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
            
        if not user.approved:
            flash('Your account is pending approval')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        return redirect(url_for('main.dashboard'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
