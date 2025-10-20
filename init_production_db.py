#!/usr/bin/env python3
"""
Production Database Initialization Script
Creates database schema without demo data for production deployment.
"""

import os
from app import app, db
from models import User, MoodEntry, DailyHoroscope

def init_production_db():
    """Initialize production database with schema only."""
    
    print("🚀 Initializing production database...")
    
    with app.app_context():
        # Create all tables
        print("📊 Creating database schema...")
        db.create_all()
        
        print("✅ Production database initialized successfully!")
        print("📋 Database schema created:")
        print("  - Users table")
        print("  - Mood entries table") 
        print("  - Daily horoscopes table")
        print("")
        print("🔐 Security notes:")
        print("  - No demo users created")
        print("  - No test data inserted")
        print("  - Ready for production use")
        print("")
        print("👤 To create admin user, use the application's registration page")

if __name__ == '__main__':
    init_production_db()