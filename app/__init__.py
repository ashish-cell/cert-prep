import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config  # Import config directly since backend is removed

# Ensure the app can find the necessary modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_class=Config):
    """ Factory function to create Flask app """
    app = Flask(__name__,
                template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/templates")),
                static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/static")))

    # Load configuration
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Ensure secret key is set
    app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF protection

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Register blueprints (without `backend`)
    from app.routes.auth import auth as auth_blueprint
    from app.routes.main import main as main_blueprint
    from app.routes.admin import admin as admin_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)

    # Ensure database tables exist
    with app.app_context():
        db.create_all()

    return app

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(user_id)

# Export create_app and db
__all__ = ['create_app', 'db']
