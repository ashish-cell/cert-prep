import os
from datetime import timedelta

class Config:
    # Database configuration
    # Use DATABASE_URL from AWS if available, otherwise use local database
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

class ProductionConfig(Config):
    DEBUG = False
    # Add any production-specific settings here

class DevelopmentConfig(Config):
    DEBUG = True
    # Add any development-specific settings here 