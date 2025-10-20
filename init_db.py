#!/usr/bin/env python3
"""
Database initialization script for the Horoscope application.
Run this script to create all database tables.
"""

from app import app
from models import db, User, MoodEntry, HoroscopeReading, AstrologicalEvent
from datetime import datetime, date, time
import os

def init_database():
    """Initialize the database with all tables"""
    print("Initializing database...")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Verify User table has theme_preference column
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = inspector.get_columns('user')
            column_names = [col['name'] for col in columns]
            
            if 'theme_preference' in column_names:
                print('✓ theme_preference column exists in user table')
            else:
                print('❌ theme_preference column missing from user table')
                
            print(f'User table columns: {column_names}')
        except Exception as e:
            print(f'Warning: Could not verify columns: {e}')
        
        # Check if we should create sample data
        if User.query.count() == 0:
            create_sample_data()
        
        print("✓ Database initialization complete!")

def create_sample_data():
    """Create sample data for testing (optional)"""
    print("Creating sample data...")
    
    try:
        # Create a sample user
        sample_user = User(
            email='demo@horoscope.app',
            first_name='Demo',
            last_name='User',
            birth_date=date(1990, 6, 15),
            birth_time=time(14, 30),
            birth_location='New York, NY, USA',
            timezone='UTC-5',
            email_notifications=True
        )
        sample_user.set_password('demopassword')
        
        db.session.add(sample_user)
        db.session.commit()
        
        print("✓ Sample user created:")
        print(f"  Email: {sample_user.email}")
        print(f"  Password: demopassword")
        
        # Create sample mood entry
        sample_mood = MoodEntry(
            user_id=sample_user.id,
            mood_description="Feeling excited about new opportunities but also a bit anxious about the changes ahead.",
            current_situation="Starting a new job next week and moving to a new city.",
            stress_level=6,
            ai_guidance="This is a time of significant growth and expansion. Trust in your abilities and embrace the adventure ahead."
        )
        sample_mood.set_emotions(['excited', 'anxious', 'hopeful'])
        
        db.session.add(sample_mood)
        
        # Create sample horoscope reading
        sample_horoscope = HoroscopeReading(
            user_id=sample_user.id,
            reading_type='daily',
            title=f"Daily Horoscope - {datetime.now().strftime('%B %d, %Y')}",
            content="""Today brings a wonderful blend of stability and excitement, dear Gemini. 
            
            The cosmic energies are supporting your natural curiosity and communication skills. 
            This is an excellent time to reach out to others, share your ideas, and explore new learning opportunities.
            
            In relationships, your charm and wit are particularly magnetic today. Use this energy to deepen connections 
            with those who matter most to you. For career matters, trust your instincts when it comes to networking 
            and presenting your ideas.
            
            Your affirmation for today: 'I embrace change as an opportunity for growth and discovery.'""",
            ai_model_used='gpt-3.5-turbo',
            confidence_score=0.85
        )
        
        db.session.add(sample_horoscope)
        
        # Create sample astrological events
        sample_events = [
            AstrologicalEvent(
                event_type='full_moon',
                event_date=datetime(2024, 10, 15, 12, 0),
                celestial_body='Moon',
                sign='Aries',
                degree=22.5,
                description='Full Moon in Aries - Time for action and new beginnings'
            ),
            AstrologicalEvent(
                event_type='new_moon',
                event_date=datetime(2024, 10, 30, 8, 0),
                celestial_body='Moon',
                sign='Scorpio',
                degree=7.2,
                description='New Moon in Scorpio - Deep transformation and renewal'
            )
        ]
        
        for event in sample_events:
            event.set_keywords(['transformation', 'new beginnings', 'emotional renewal'])
            db.session.add(event)
        
        db.session.commit()
        print("✓ Sample data created successfully")
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creating sample data: {e}")

def reset_database():
    """Reset the database (WARNING: This will delete all data!)"""
    confirm = input("⚠️  WARNING: This will delete all data! Type 'RESET' to confirm: ")
    
    if confirm == 'RESET':
        print("Resetting database...")
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("✓ Database reset complete!")
    else:
        print("Database reset cancelled.")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        init_database()