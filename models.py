from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, time
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Astrological information
    birth_date = db.Column(db.Date)
    birth_time = db.Column(db.Time)
    birth_location = db.Column(db.String(200))  # Legacy field for backward compatibility
    birth_country = db.Column(db.String(100))   # Country code or name
    birth_region = db.Column(db.String(100))    # State/Province/Region
    birth_city = db.Column(db.String(100))      # City name
    timezone = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Current location (for location-dependent features like houses, rising sign)
    current_location = db.Column(db.String(200))    # Current location string
    current_country = db.Column(db.String(100))     # Current country
    current_region = db.Column(db.String(100))      # Current state/province  
    current_city = db.Column(db.String(100))        # Current city
    current_timezone = db.Column(db.String(50))     # Current timezone
    current_latitude = db.Column(db.Float)          # Current latitude
    current_longitude = db.Column(db.Float)         # Current longitude
    
    # User preferences
    email_notifications = db.Column(db.Boolean, default=True)
    preferred_astrology_system = db.Column(db.String(20), default='western')  # western, vedic
    theme_preference = db.Column(db.String(10), default='auto')  # auto, light, dark
    use_current_location = db.Column(db.Boolean, default=False)  # Whether to use current location for location-dependent features
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    mood_entries = db.relationship('MoodEntry', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    horoscope_readings = db.relationship('HoroscopeReading', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def username(self):
        """Get username (using email)"""
        return self.email.split('@')[0]
    
    @property
    def is_premium(self):
        """Check if user has premium status (free during testing phase)"""
        return True  # Everyone gets premium during testing phase
    
    def has_complete_birth_info(self):
        """Check if user has provided complete birth information for chart calculation"""
        has_basic_info = all([self.birth_date, self.birth_time])
        has_location = (self.birth_location or (self.birth_country and self.birth_city))
        has_coordinates = (self.latitude is not None and self.longitude is not None)
        
        # Debug logging
        print(f"Birth info check for user {self.id}:")
        print(f"  - has_basic_info: {has_basic_info} (date: {self.birth_date}, time: {self.birth_time})")
        print(f"  - has_location: {has_location} (location: {self.birth_location}, country: {self.birth_country}, city: {self.birth_city})")
        print(f"  - has_coordinates: {has_coordinates} (lat: {self.latitude}, lng: {self.longitude})")
        
        return has_basic_info and has_location and has_coordinates
    
    def get_full_birth_location(self):
        """Get formatted birth location string"""
        if self.birth_city and self.birth_country:
            location_parts = [self.birth_city]
            if self.birth_region:
                location_parts.append(self.birth_region)
            location_parts.append(self.birth_country)
            return ', '.join(location_parts)
        return self.birth_location or 'Unknown Location'
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'birth_location': self.birth_location,
            'has_complete_birth_info': self.has_complete_birth_info()
        }

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Mood information
    mood_description = db.Column(db.Text, nullable=False)
    current_situation = db.Column(db.Text)
    stress_level = db.Column(db.Integer)  # 1-10 scale
    emotions = db.Column(db.Text)  # JSON string of emotion tags
    
    # AI response
    ai_guidance = db.Column(db.Text)
    astrological_context = db.Column(db.Text)  # Current planetary influences
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_emotions(self, emotion_list):
        """Set emotions as JSON string"""
        self.emotions = json.dumps(emotion_list) if emotion_list else None
    
    def get_emotions(self):
        """Get emotions as list"""
        return json.loads(self.emotions) if self.emotions else []
    
    def to_dict(self):
        """Convert mood entry to dictionary"""
        return {
            'id': self.id,
            'mood_description': self.mood_description,
            'current_situation': self.current_situation,
            'stress_level': self.stress_level,
            'emotions': self.get_emotions(),
            'ai_guidance': self.ai_guidance,
            'created_at': self.created_at.isoformat()
        }

class HoroscopeReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Horoscope content
    reading_type = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, on-demand
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    
    # Astrological data used
    planetary_positions = db.Column(db.Text)  # JSON string
    current_transits = db.Column(db.Text)  # JSON string
    aspects = db.Column(db.Text)  # JSON string
    structured_data = db.Column(db.Text)  # Enhanced JSON data for structured horoscopes
    
    # Metadata
    reading_date = db.Column(db.Date, default=date.today)
    ai_model_used = db.Column(db.String(50))
    confidence_score = db.Column(db.Float)  # AI confidence in reading
    
    # User interaction
    user_rating = db.Column(db.Integer)  # 1-5 star rating
    user_feedback = db.Column(db.Text)
    was_accurate = db.Column(db.Boolean)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_planetary_data(self, positions, transits, aspects):
        """Set astrological data as JSON strings"""
        self.planetary_positions = json.dumps(positions) if positions else None
        self.current_transits = json.dumps(transits) if transits else None
        self.aspects = json.dumps(aspects) if aspects else None
    
    def get_planetary_data(self):
        """Get astrological data as dictionaries"""
        return {
            'positions': json.loads(self.planetary_positions) if self.planetary_positions else {},
            'transits': json.loads(self.current_transits) if self.current_transits else {},
            'aspects': json.loads(self.aspects) if self.aspects else {}
        }
    
    def to_dict(self):
        """Convert horoscope reading to dictionary"""
        return {
            'id': self.id,
            'reading_type': self.reading_type,
            'title': self.title,
            'content': self.content,
            'reading_date': self.reading_date.isoformat(),
            'user_rating': self.user_rating,
            'created_at': self.created_at.isoformat()
        }

class AstrologicalEvent(db.Model):
    """Store significant astrological events for reference"""
    id = db.Column(db.Integer, primary_key=True)
    
    event_type = db.Column(db.String(50), nullable=False)  # full_moon, new_moon, retrograde, etc.
    event_date = db.Column(db.DateTime, nullable=False)
    celestial_body = db.Column(db.String(20))  # planet/luminary involved
    sign = db.Column(db.String(20))  # astrological sign
    degree = db.Column(db.Float)  # exact degree
    
    description = db.Column(db.Text)
    influence_keywords = db.Column(db.Text)  # JSON array of influence keywords
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_keywords(self, keyword_list):
        """Set influence keywords as JSON string"""
        self.influence_keywords = json.dumps(keyword_list) if keyword_list else None
    
    def get_keywords(self):
        """Get influence keywords as list"""
        return json.loads(self.influence_keywords) if self.influence_keywords else []