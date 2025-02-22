import os
import sys
from pathlib import Path
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import Config
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

from app import create_app, db
from app.models.user import User

def init_database():
    try:
        # Extract database name from URL
        db_url = urlparse( Config.SQLALCHEMY_DATABASE_URI)
        db_name = db_url.path.lstrip('/')
        
        logger.info(f"Attempting to create database: {db_name}")
        
        # Connect to PostgreSQL server (to postgres database initially)
        conn = psycopg2.connect(
            user="postgres",
            password=os.getenv("POSTGRES_PASSWORD"),
            host="localhost",
            port="5432",
            database="postgres"  # Connect to default postgres database first
        )
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE {db_name}')
            logger.info(f"Database '{db_name}' created successfully!")
        else:
            logger.info(f"Database '{db_name}' already exists!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Database creation error: {str(e)}")
        return False

def init_db():
    try:
        # First create the database
        if not init_database():
            logger.error("Failed to create database, aborting...")
            return

        logger.info("Creating application context...")
        app = create_app()
        
        with app.app_context():
            logger.info("Creating database tables...")
            db.create_all()
            
            # Check if admin user exists
            logger.info("Checking for admin user...")
            admin = User.query.filter_by(email='admin@example.com').first()
            
            if not admin:
                logger.info("Creating admin user...")
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    role='admin',
                    approved=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                logger.info("Admin user created successfully!")
            else:
                logger.info("Admin user already exists!")
                
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == '__main__':
    init_db()
