from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__,
                template_folder='../frontend/templates',  # Ensure correct template path
                static_folder='../frontend/static')

    # Load config
    app.config.from_object(config_class)

    # ✅ Fix session expiration issue
    app.permanent_session_lifetime = timedelta(hours=6)  # Match config.py

    # ✅ Refresh session each request to keep it alive
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    # ✅ Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)
    csrf.init_app(app)  # Ensure CSRF is initialized

    # Register blueprints
    from app.routes.auth import auth as auth_blueprint
    from app.routes.main import main as main_blueprint
    from app.routes.admin import admin as admin_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)

    # ✅ Ensure database tables exist
    with app.app_context():
        db.create_all()

    return app

# ✅ Fix Flask-Login User Loader
@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(user_id)

# Export create_app and db
__all__ = ['create_app', 'db']
