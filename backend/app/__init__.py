from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__,
                template_folder='../../frontend/templates',
                static_folder='../../frontend/static')
    
    # Load config
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Make sure this is set
    app.config['WTF_CSRF_ENABLED'] = True
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth as auth_blueprint
    from app.routes.main import main as main_blueprint
    from app.routes.admin import admin as admin_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)
    
    # Create database tables and run migrations
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
