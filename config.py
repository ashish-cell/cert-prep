import os
from datetime import timedelta

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:Diehard10*@localhost/quiz_app')

    # Convert postgres:// to postgresql:// for SQLAlchemy 1.4+
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Fix session expiration issues
    PERMANENT_SESSION_LIFETIME = timedelta(hours=6)  # Increase session to 6 hours
    SESSION_REFRESH_EACH_REQUEST = True  # Refresh session on every request

    # CSRF and Session Security Settings
    WTF_CSRF_TIME_LIMIT = None  # Disable CSRF expiration
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access for security
    SESSION_COOKIE_SECURE = False  # Set False unless using HTTPS
    SESSION_PERMANENT = True  # Keep session persistent
    WTF_CSRF_CHECK_DEFAULT = True  # Ensure CSRF is always checked

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
