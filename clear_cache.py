#!/usr/bin/env python3
"""Clear today's cached horoscope to test new format"""

from app import app
from models import HoroscopeReading, db
from datetime import date

def clear_todays_horoscopes():
    """Clear all daily horoscopes for today to test new format"""
    with app.app_context():
        today = date.today()
        
        # Find all daily horoscopes for today
        todays_readings = HoroscopeReading.query.filter_by(
            reading_type='daily',
            reading_date=today
        ).all()
        
        count = len(todays_readings)
        print(f"Found {count} daily horoscope(s) for {today}")
        
        if count > 0:
            # Delete them
            for reading in todays_readings:
                db.session.delete(reading)
            
            db.session.commit()
            print(f"✅ Cleared {count} horoscope(s) - new format will be generated on next load")
        else:
            print("No horoscopes found for today")

if __name__ == "__main__":
    clear_todays_horoscopes()