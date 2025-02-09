#!/usr/bin/env python
from app import db, create_app

def setup_database():
    app = create_app()
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database setup complete!")

if __name__ == "__main__":
    setup_database()
