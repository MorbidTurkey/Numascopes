from app import app, db

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
    print("You can now create a new account or I can help restore your old data.")