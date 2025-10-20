#!/usr/bin/env python3
"""
Fresh database creation script
"""

from app import app, db
from models import User, MoodEntry, HoroscopeReading

def create_fresh_database():
    """Create a completely fresh database"""
    print("🔄 Creating fresh database...")
    
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        print("🗑️ Dropped all tables")
        
        # Create all tables with current schema
        db.create_all()
        print("✅ Created all tables")
        
        # Verify table creation
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📊 Tables created: {tables}")
        
        if 'user' in tables:
            columns = inspector.get_columns('user')
            print("👤 User table columns:")
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
        
        print("🎯 Database is ready for testing!")

if __name__ == "__main__":
    create_fresh_database()