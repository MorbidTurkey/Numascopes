#!/usr/bin/env python3
"""
Simple migration to add theme_preference column to user table
"""
import sqlite3
import os

def migrate():
    db_path = 'instance/horoscope.db'
    
    print(f"🔍 Looking for database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return False
    
    file_size = os.path.getsize(db_path)
    print(f"📊 Database file size: {file_size} bytes")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute('PRAGMA table_info(user)')
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Current columns: {columns}")
        
        if 'theme_preference' not in columns:
            # Add the column
            cursor.execute('ALTER TABLE user ADD COLUMN theme_preference VARCHAR(10) DEFAULT "auto"')
            conn.commit()
            print('✅ Added theme_preference column to user table')
            return True
        else:
            print('✅ theme_preference column already exists')
            return True
            
    except Exception as e:
        print(f'❌ Error: {e}')
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()