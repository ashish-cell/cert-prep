#!/usr/bin/env python
def setup_database():
    app = create_app()
    with app.app_context():
        confirm = input("⚠ WARNING: This will DROP all tables! Type 'yes' to continue: ")
        if confirm.lower() != 'yes':
            print("Operation canceled.")
            return
        
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database setup complete!")
