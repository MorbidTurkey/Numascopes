from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User, MoodEntry, HoroscopeReading
from forms import LoginForm, RegistrationForm, BirthInfoForm, MoodForm, PreferencesForm
from auth import auth_bp
from enhanced_calculator import EnhancedProfessionalCalculator  # Enhanced ★★★★★ system
from ai_integration import AIHoroscopeGenerator
from datetime import datetime, date, time
import os

# ✅ Writable directories for serverless (Vercel)
TMP_DIR = "/tmp"
INSTANCE_PATH = os.path.join(TMP_DIR, "instance")
os.makedirs(INSTANCE_PATH, exist_ok=True)

# ✅ Flask app init
app = Flask(__name__, instance_path=INSTANCE_PATH)
app.config.from_object(Config)

# ✅ --- Add stable SECRET_KEYs for sessions and CSRF ---
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
app.config["WTF_CSRF_SECRET_KEY"] = os.getenv("WTF_CSRF_SECRET_KEY", app.config["SECRET_KEY"])

# ✅ --- Secure, consistent session cookies ---
app.config.update(
    SESSION_COOKIE_SECURE=True,           # Always secure (HTTPS on Vercel)
    REMEMBER_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",        # Safer default (or "None" if embedded cross-site)
    REMEMBER_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 7  # 7 days (persistent login)
)

# ✅ --- Database config ---
# Prefer persistent DB if provided (e.g. Neon, Supabase, PlanetScale)
db_url = os.getenv("DATABASE_URL")

if db_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
else:
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not uri or uri.startswith("sqlite:///"):
        # fallback to /tmp only if no real DB is provided
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/app.db"

# optional but recommended
app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

# ✅ Initialize database
from sqlalchemy import inspect, text
db.init_app(app)

_DB_READY = {"once": False}

def _ensure_db_ready():
    if _DB_READY["once"]:
        return
    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
            insp = inspect(db.engine)
            if not insp.has_table("user") and not insp.has_table("users"):
                db.create_all()
        _DB_READY["once"] = True
    except Exception as e:
        print(f"[DB bootstrap] Skipped or failed: {e}")

@app.before_request
def _bootstrap_db_once():
    _ensure_db_ready()

# ✅ CSRF and LoginManager setup
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# ✅ Blueprint registration
app.register_blueprint(auth_bp, url_prefix='/auth')

# ✅ Optional: user_loader (make sure this exists)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Make csrf_token available to all templates
@app.context_processor
def inject_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return dict(csrf_token=generate_csrf)

@app.context_processor
def inject_moment():
    """Make moment.js-like date formatting available in templates"""
    from datetime import datetime
    
    def moment(date=None):
        if date is None:
            date = datetime.now()
        
        class MomentFormatter:
            def __init__(self, dt):
                self.dt = dt if dt else datetime.now()
            
            def format(self, fmt):
                # Convert moment.js format to Python strftime format
                fmt_map = {
                    'MMMM Do, YYYY': '%B %d, %Y',
                    'YYYY-MM-DD': '%Y-%m-%d',
                    'MMM DD, YYYY': '%b %d, %Y',
                    'MMMM YYYY': '%B %Y',
                    'DD/MM/YYYY': '%d/%m/%Y',
                    'MM/DD/YYYY': '%m/%d/%Y'
                }
                python_fmt = fmt_map.get(fmt, fmt)
                try:
                    return self.dt.strftime(python_fmt)
                except:
                    return "Invalid Date"
            
            def fromNow(self):
                """Return human-readable time difference"""
                try:
                    now = datetime.now()
                    if self.dt.tzinfo is not None:
                        now = now.replace(tzinfo=self.dt.tzinfo)
                    
                    diff = now - self.dt
                    
                    if diff.days > 365:
                        years = diff.days // 365
                        return f"{years} year{'s' if years != 1 else ''} ago"
                    elif diff.days > 30:
                        months = diff.days // 30
                        return f"{months} month{'s' if months != 1 else ''} ago"
                    elif diff.days > 0:
                        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
                    elif diff.seconds > 3600:
                        hours = diff.seconds // 3600
                        return f"{hours} hour{'s' if hours != 1 else ''} ago"
                    elif diff.seconds > 60:
                        minutes = diff.seconds // 60
                        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                    else:
                        return "just now"
                except:
                    return "some time ago"
        
        return MomentFormatter(date)
    
    return dict(moment=moment)

# Initialize astrology calculation service with accurate messaging
print("🔍 Initializing astrology calculation system...")

# Check what calculators are actually available
calculators_available = []

# Check for our Enhanced Calculator (best in-house option)
try:
    from enhanced_calculator import EnhancedProfessionalCalculator
    calculators_available.append("Enhanced Calculator (★★★★★)")
except ImportError:
    pass

# Check for Professional Calculator  
try:
    from professional_astrology import ProfessionalAstrologyCalculator
    calculators_available.append("Astronomical Calculator (★★★★☆)")
except ImportError:
    pass

# Check for Simple Calculator (always available)
try:
    # Using Enhanced Professional Calculator as fallback (no more matplotlib dependency)
    from enhanced_calculator import EnhancedProfessionalCalculator
    calculators_available.append("Enhanced Fallback (★★★★★)")
except ImportError:
    print("⚠️  Warning: Enhanced Calculator not available")

print(f"📊 Available calculators: {', '.join(calculators_available)}")

# Initialize the Enhanced Calculator (★★★★★)
try:
    from enhanced_calculator import EnhancedProfessionalCalculator
    astrology_calc = EnhancedProfessionalCalculator()
    calc_name = "Enhanced Calculator"
    calc_rating = "★★★★★"
except ImportError:
    # Fallback to Professional if Enhanced not available
    try:
        from professional_astrology import ProfessionalAstrologyCalculator
        astrology_calc = ProfessionalAstrologyCalculator()
        calc_name = "Astronomical Calculator"
        calc_rating = "★★★★☆"
    except ImportError:
        print("❌ Critical: No calculators available!")
        astrology_calc = None

print(f"✅ Using {calc_name} ({calc_rating}) for basic operations")
print(f"🎯 Enhanced Calculator (★★★★★) used for natal charts when available")
print(f"� Zero licensing costs - all calculators are commercially free!")

ai_generator = AIHoroscopeGenerator()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    """Home page - shows daily horoscope if logged in"""
    if current_user.is_authenticated and current_user.birth_date:
        # Generate today's horoscope with enhanced data
        horoscope = ai_generator.generate_daily_horoscope(current_user)
        
        # Get enhanced horoscope data if available
        from models import HoroscopeReading
        from datetime import date
        today = date.today()
        
        horoscope_reading = HoroscopeReading.query.filter_by(
            user_id=current_user.id,
            reading_type='daily',
            reading_date=today
        ).first()
        
        enhanced_data = None
        if horoscope_reading and horoscope_reading.structured_data:
            try:
                import json
                enhanced_data = json.loads(horoscope_reading.structured_data)
            except:
                enhanced_data = None
        
        # Generate enhanced natal chart preview for dashboard
        natal_chart_image = None
        if current_user.has_complete_birth_info():
            try:
                # Try to get chart data from enhanced calculator
                from enhanced_calculator import EnhancedProfessionalCalculator
                calc = EnhancedProfessionalCalculator()
                
                birth_datetime = datetime.combine(current_user.birth_date, current_user.birth_time)
                
                # Convert UTC offset to pytz timezone format
                timezone_offset = current_user.timezone or 'UTC'
                if timezone_offset.startswith('UTC') and timezone_offset != 'UTC':
                    # Convert UTC-6 to Etc/GMT+6 format (note: Etc/GMT is inverted)
                    tz_offset_str = timezone_offset.replace('UTC', '')
                    try:
                        tz_offset_int = int(tz_offset_str)
                        if tz_offset_int == 0:
                            timezone_str = 'UTC'
                        elif tz_offset_int > 0:
                            # UTC+5 becomes Etc/GMT-5
                            timezone_str = f'Etc/GMT-{tz_offset_int}'
                        else:
                            # UTC-6 becomes Etc/GMT+6 (removing minus and flipping sign)
                            timezone_str = f'Etc/GMT+{abs(tz_offset_int)}'
                    except ValueError:
                        timezone_str = 'UTC'
                else:
                    timezone_str = 'UTC'
                
                chart_data = calc.calculate_full_chart(
                    birth_datetime,
                    current_user.latitude,
                    current_user.longitude,
                    timezone_str  # Pass string instead of integer
                )
                
                if chart_data:
                    from simple_chart import create_simple_chart
                    natal_chart_image = create_simple_chart(chart_data, "Dashboard Preview", current_user)
                
            except Exception as e:
                print(f"Dashboard chart generation failed: {e}")
                # No fallback - let user know chart generation failed
                natal_chart_image = None
        
        # Get counts and recent activity for dashboard
        readings_count = current_user.horoscope_readings.count()
        recent_readings = current_user.horoscope_readings.order_by(HoroscopeReading.created_at.desc()).limit(3).all()
        
        # Get real-time cosmic events for dashboard
        cosmic_events = calculate_upcoming_cosmic_events(
            lat=current_user.latitude, 
            lng=current_user.longitude
        )
        
        return render_template('dashboard.html', 
                             horoscope=horoscope, 
                             enhanced_data=enhanced_data,
                             natal_chart=natal_chart_image,
                             readings_count=readings_count,
                             recent_readings=recent_readings,
                             cosmic_events=cosmic_events[:4])  # Show first 4 events on dashboard
    return render_template('index.html')

@app.route('/profile')
@login_required
def profile():
    """Enhanced user profile with chart preview and service overview"""
    form = BirthInfoForm()
    
    # Pre-populate form with current user data
    if current_user.birth_date:
        form.birth_date.data = current_user.birth_date
    if current_user.birth_time:
        # Set the hidden field as a string for the form
        form.birth_time.data = current_user.birth_time.strftime('%H:%M:%S')
        # Also populate the individual time fields for display
        hour = current_user.birth_time.hour
        minute = current_user.birth_time.minute
        
        # Convert 24-hour to 12-hour format
        if hour == 0:
            form.birth_time_hour.data = '12'
            form.birth_time_ampm.data = 'AM'
        elif hour < 12:
            form.birth_time_hour.data = str(hour)
            form.birth_time_ampm.data = 'AM'
        elif hour == 12:
            form.birth_time_hour.data = '12'
            form.birth_time_ampm.data = 'PM'
        else:
            form.birth_time_hour.data = str(hour - 12)
            form.birth_time_ampm.data = 'PM'
        
        form.birth_time_minute.data = f"{minute:02d}"
    
    if current_user.birth_country:
        form.birth_country.data = current_user.birth_country
    if current_user.birth_region:
        form.birth_region.data = current_user.birth_region
    if current_user.birth_city:
        form.birth_city.data = current_user.birth_city
    if current_user.timezone:
        form.timezone.data = current_user.timezone
    if current_user.preferred_astrology_system:
        form.astrology_system.data = current_user.preferred_astrology_system
    
    form.email_notifications.data = current_user.email_notifications
    
    quick_chart = None
    chart_preview = None
    recent_readings = None
    
    # Get recent readings
    recent_readings = HoroscopeReading.query.filter_by(user_id=current_user.id)\
                                          .order_by(HoroscopeReading.created_at.desc())\
                                          .limit(3).all()
    
    # If user has complete birth info, generate quick chart data
    if current_user.has_complete_birth_info():
        try:
            # Try Enhanced Calculator for quick chart info
            from enhanced_calculator import EnhancedProfessionalCalculator
            calc = EnhancedProfessionalCalculator()
            
            birth_datetime = datetime.combine(current_user.birth_date, current_user.birth_time)
            
            # Convert UTC offset to proper timezone format
            timezone_offset = current_user.timezone or 'UTC'
            if timezone_offset.startswith('UTC') and timezone_offset != 'UTC':
                # Convert UTC-6 to Etc/GMT+6 format (note: Etc/GMT is inverted)
                tz_offset_str = timezone_offset.replace('UTC', '')
                try:
                    tz_offset_int = int(tz_offset_str)
                    if tz_offset_int == 0:
                        timezone_str = 'UTC'
                    elif tz_offset_int > 0:
                        # UTC+5 becomes Etc/GMT-5
                        timezone_str = f'Etc/GMT-{tz_offset_int}'
                    else:
                        # UTC-6 becomes Etc/GMT+6 (removing minus and flipping sign)
                        timezone_str = f'Etc/GMT+{abs(tz_offset_int)}'
                except ValueError:
                    timezone_str = 'UTC'
            else:
                timezone_str = 'UTC'
            
            chart_data = calc.calculate_full_chart(
                birth_datetime,
                current_user.latitude,
                current_user.longitude,
                timezone_str  # Use converted timezone format
            )
            
            if chart_data:
                # Generate chart summary for quick display
                chart_summary = calc.get_chart_summary(chart_data)
                quick_chart = chart_summary
                
                # Generate small chart preview
                try:
                    chart_preview = create_chart_preview(chart_data)
                except Exception as preview_error:
                    print(f"Chart preview generation failed: {preview_error}")
                    
        except Exception as calc_error:
            print(f"Quick chart calculation failed: {calc_error}")
            # Try to get basic info from simple calculator
            try:
                quick_chart = {
                    'sun_sign': astrology_calc.get_sun_sign(current_user),
                    'moon_sign': 'Unknown',
                    'rising_sign': 'Unknown'
                }
            except:
                pass
    
    # Create and populate preferences form
    preferences_form = PreferencesForm()
    preferences_form.theme_preference.data = getattr(current_user, 'theme_preference', 'auto') or 'auto'
    preferences_form.email_notifications.data = current_user.email_notifications
    
    # Populate current location fields
    preferences_form.use_current_location.data = getattr(current_user, 'use_current_location', False) or False
    preferences_form.current_country.data = getattr(current_user, 'current_country', None)
    preferences_form.current_region.data = getattr(current_user, 'current_region', None)
    preferences_form.current_city.data = getattr(current_user, 'current_city', None)
    preferences_form.current_timezone.data = getattr(current_user, 'current_timezone', None)
    
    return render_template('profile.html', 
                         form=form,
                         preferences_form=preferences_form,
                         quick_chart=quick_chart,
                         chart_preview=chart_preview,
                         recent_readings=recent_readings)

@app.route('/update_preferences', methods=['POST'])
@login_required
def update_preferences():
    """Update user preferences"""
    form = PreferencesForm()
    
    if form.validate_on_submit():
        try:
            # Update theme preference if the field exists
            if hasattr(current_user, 'theme_preference'):
                current_user.theme_preference = form.theme_preference.data
            
            # Update email notifications preference
            current_user.email_notifications = form.email_notifications.data
            
            # Update current location preferences
            if hasattr(current_user, 'use_current_location'):
                current_user.use_current_location = form.use_current_location.data
                current_user.current_country = form.current_country.data if form.current_country.data else None
                current_user.current_region = form.current_region.data if form.current_region.data else None
                current_user.current_city = form.current_city.data if form.current_city.data else None
                current_user.current_timezone = form.current_timezone.data if form.current_timezone.data else None
                
                # Build current_location string from components
                if form.use_current_location.data and form.current_city.data:
                    location_parts = []
                    if form.current_city.data:
                        location_parts.append(form.current_city.data)
                    if form.current_region.data:
                        location_parts.append(form.current_region.data)
                    if form.current_country.data:
                        location_parts.append(form.current_country.data)
                    current_user.current_location = ', '.join(location_parts)
                    
                    # For now, we'll just store the text. Later we can add geocoding
                    # to get coordinates for current_latitude and current_longitude
            
            db.session.commit()
            flash('Your preferences have been updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your preferences. Please try again.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('profile'))

def create_chart_preview(chart_data, size=(400, 400)):
    """Create a smaller chart preview for profile page"""
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Circle
    import io
    import base64
    
    plt.switch_backend('Agg')
    
    fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), facecolor='white')
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Draw basic chart circle
    chart_circle = Circle((0, 0), 1, fill=False, linewidth=2, color='black')
    ax.add_patch(chart_circle)
    
    # Planet colors and symbols
    planet_colors = {
        'sun': '#FFA500', 'moon': '#C0C0C0', 'mercury': '#FFD700',
        'venus': '#FF69B4', 'mars': '#FF4500', 'jupiter': '#4169E1',
        'saturn': '#8B4513'
    }
    
    planet_symbols = {
        'sun': '☉', 'moon': '☽', 'mercury': '☿',
        'venus': '♀', 'mars': '♂', 'jupiter': '♃',
        'saturn': '♄'
    }
    
    # Draw zodiac signs (simplified)
    signs = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
    for i, symbol in enumerate(signs):
        angle = (90 - i * 30) * np.pi / 180
        x = 1.05 * np.cos(angle)
        y = 1.05 * np.sin(angle)
        ax.text(x, y, symbol, fontsize=12, ha='center', va='center', weight='bold')
    
    # Draw planets (simplified)
    if 'planets' in chart_data:
        for planet, data in chart_data['planets'].items():
            if planet in planet_symbols:
                longitude = data['longitude']
                angle = (90 - longitude) * np.pi / 180
                
                radius = 0.85
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                
                color = planet_colors.get(planet, 'black')
                symbol = planet_symbols[planet]
                
                ax.text(x, y, symbol, fontsize=10, ha='center', va='center',
                       color=color, weight='bold',
                       bbox=dict(boxstyle="circle,pad=0.1", facecolor='white', 
                               edgecolor=color, alpha=0.9))
    
    plt.tight_layout()
    
    # Save to base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    img_data = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    return f"data:image/png;base64,{img_data}"


@app.route('/edit_profile')
@login_required
def edit_profile():
    """Route to edit profile - shows the original profile form"""
    form = BirthInfoForm()
    if current_user.birth_date:
        form.birth_date.data = current_user.birth_date
        form.birth_time.data = current_user.birth_time
        form.birth_country.data = current_user.birth_country
        form.birth_region.data = current_user.birth_region
        form.birth_city.data = current_user.birth_city
        form.timezone.data = current_user.timezone
        form.astrology_system.data = current_user.preferred_astrology_system
        form.email_notifications.data = current_user.email_notifications
    return render_template('profile.html', form=form)

@app.route('/update_birth_info', methods=['POST'])
@login_required
def update_birth_info():
    """Update user's birth information with geocoding"""
    print("🎯 UPDATE_BIRTH_INFO ROUTE HIT!")
    print(f"Request method: {request.method}")
    print(f"Request endpoint: {request.endpoint}")
    
    form = BirthInfoForm()
    
    print("=== FORM SUBMISSION DEBUG ===")
    print(f"Form validation: {form.validate_on_submit()}")
    if form.errors:
        print(f"Form errors: {form.errors}")
    
    print(f"Raw form data:")
    print(f"  birth_date: {form.birth_date.data}")
    print(f"  birth_time: {form.birth_time.data}")
    print(f"  birth_time_unknown: {form.birth_time_unknown.data}")
    print(f"  birth_time_hour: '{form.birth_time_hour.data}'")
    print(f"  birth_time_minute: '{form.birth_time_minute.data}'")
    print(f"  birth_time_ampm: '{form.birth_time_ampm.data}'")
    print(f"  birth_country: {form.birth_country.data}")
    print(f"  birth_city: {form.birth_city.data}")
    
    # Print raw request data to see what's actually being submitted
    print(f"Raw request form data:")
    for key, value in request.form.items():
        print(f"  {key}: '{value}'")
    
    # Custom validation: if birth_date is provided, we need at least a city or country
    custom_validation_passed = True
    custom_errors = []
    
    if form.birth_date.data and not form.birth_time_unknown.data:
        # If they provide a birth date and don't check "unknown time", validate time fields
        if not form.birth_time_hour.data or not form.birth_time_ampm.data:
            if not form.birth_time.data:  # Also check the hidden field
                custom_errors.append("Please provide birth time or check 'I don't know my birth time'")
                custom_validation_passed = False
    
    if form.validate_on_submit() and custom_validation_passed:
        print("Form validation passed, updating user...")
        current_user.birth_date = form.birth_date.data
        
        # Handle the new birth time fields
        birth_time_set = False
        
        if form.birth_time_unknown.data:
            # User doesn't know birth time, set to 12:00 PM
            current_user.birth_time = datetime.strptime('12:00:00', '%H:%M:%S').time()
            birth_time_set = True
            print("✅ Set birth time to 12:00 PM (unknown)")
        else:
            # Try to get time from individual fields first
            hour = form.birth_time_hour.data
            minute = form.birth_time_minute.data or '00'
            ampm = form.birth_time_ampm.data
            
            print(f"Individual time fields: hour='{hour}', minute='{minute}', ampm='{ampm}'")
            
            if hour and ampm:
                try:
                    hour_24 = int(hour)
                    if ampm == 'PM' and hour_24 != 12:
                        hour_24 += 12
                    elif ampm == 'AM' and hour_24 == 12:
                        hour_24 = 0
                    
                    time_str = f"{hour_24:02d}:{minute}:00"
                    current_user.birth_time = datetime.strptime(time_str, '%H:%M:%S').time()
                    birth_time_set = True
                    print(f"✅ Set birth time from individual fields: {time_str}")
                except (ValueError, TypeError) as e:
                    print(f"❌ Error parsing individual time fields: {e}")
            
            # Fallback to hidden field if individual fields failed
            if not birth_time_set and form.birth_time.data:
                try:
                    # Parse the time string from the hidden field
                    time_obj = datetime.strptime(form.birth_time.data, '%H:%M:%S').time()
                    current_user.birth_time = time_obj
                    birth_time_set = True
                    print(f"✅ Set birth time from hidden field: {form.birth_time.data}")
                except (ValueError, TypeError) as e:
                    print(f"❌ Error parsing hidden field time: {e}")
            
            # Final fallback to 12:00 PM if nothing worked
            if not birth_time_set:
                current_user.birth_time = datetime.strptime('12:00:00', '%H:%M:%S').time()
                print("⚠️ No valid time provided, defaulting to 12:00 PM")
        current_user.birth_country = form.birth_country.data
        current_user.birth_region = form.birth_region.data
        current_user.birth_city = form.birth_city.data
        current_user.timezone = form.timezone.data
        current_user.preferred_astrology_system = form.astrology_system.data
        current_user.email_notifications = form.email_notifications.data
        
        # Handle current location data from the form
        if hasattr(request.form, 'get'):
            current_user.current_country = request.form.get('current_country', '')
            current_user.current_region = request.form.get('current_region', '')
            current_user.current_city = request.form.get('current_city', '')
            current_user.current_timezone = request.form.get('current_timezone', '')
        
        # Create legacy birth_location for backward compatibility
        current_user.birth_location = current_user.get_full_birth_location()
        
        # Geocode the location to get coordinates
        geocoding_success = False
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="astrology_app")
            
            # Build location query
            location_parts = []
            if current_user.birth_city:
                location_parts.append(current_user.birth_city)
            if current_user.birth_region:
                location_parts.append(current_user.birth_region)
            if current_user.birth_country:
                location_parts.append(current_user.birth_country)
            
            location_query = ', '.join(location_parts)
            print(f"Attempting to geocode: '{location_query}'")
            
            if location_query:
                try:
                    location = geolocator.geocode(location_query, timeout=10)
                    if location:
                        current_user.latitude = location.latitude
                        current_user.longitude = location.longitude
                        geocoding_success = True
                        print(f"✅ Geocoded '{location_query}' to {location.latitude}, {location.longitude}")
                    else:
                        print(f"❌ Geocoding returned no results for: '{location_query}'")
                except Exception as geo_error:
                    print(f"❌ Geocoding request failed: {geo_error}")
            else:
                print("ℹ️ No location provided for geocoding")
                
        except Exception as geocode_error:
            print(f"❌ Geocoding system error: {geocode_error}")
        
        # Set default coordinates if geocoding failed or no location provided
        if not geocoding_success:
            # Use configured defaults if available; fall back to New York for legacy support
            current_user.latitude = app.config.get('DEFAULT_LATITUDE', 40.7128)
            current_user.longitude = app.config.get('DEFAULT_LONGITUDE', -74.0060)
            if location_query:
                print(f"🔄 Using default coordinates due to geocoding failure: {current_user.latitude}, {current_user.longitude}")
                flash('Location geocoding failed, using default coordinates for chart calculation.', 'warning')
            else:
                print(f"🔄 Using default coordinates as no location was provided: {current_user.latitude}, {current_user.longitude}")
                flash('No location provided. Using default coordinates for chart calculation.', 'info')
        
        db.session.commit()
        flash('Birth information updated successfully!', 'success')
        return redirect(url_for('profile'))
    else:
        print("=== FORM VALIDATION FAILED ===")
        print(f"Form errors: {form.errors}")
        if custom_errors:
            print(f"Custom validation errors: {custom_errors}")
            for error in custom_errors:
                flash(error, 'error')
        else:
            flash('Please check the form for errors.', 'error')
    return render_template('profile.html', form=form)

@app.route('/debug_birth_info')
@login_required
def debug_birth_info():
    """Debug route to check user's birth information"""
    info = {
        'birth_date': str(current_user.birth_date) if current_user.birth_date else None,
        'birth_time': str(current_user.birth_time) if current_user.birth_time else None,
        'birth_country': current_user.birth_country,
        'birth_region': current_user.birth_region,
        'birth_city': current_user.birth_city,
        'birth_location': current_user.birth_location,
        'latitude': current_user.latitude,
        'longitude': current_user.longitude,
        'has_complete_info': current_user.has_complete_birth_info()
    }
    return jsonify(info)

@app.route('/fix_coordinates')
@login_required
def fix_coordinates():
    """Quick fix to add coordinates to current user"""
    if not current_user.latitude or not current_user.longitude:
        # Use configured defaults if available; fall back to New York for legacy support
        current_user.latitude = app.config.get('DEFAULT_LATITUDE', 40.7128)
        current_user.longitude = app.config.get('DEFAULT_LONGITUDE', -74.0060)
        db.session.commit()
        return jsonify({'message': 'Coordinates added successfully', 'lat': current_user.latitude, 'lng': current_user.longitude})
    else:
        return jsonify({'message': 'Coordinates already exist', 'lat': current_user.latitude, 'lng': current_user.longitude})

# @app.route('/mood')
# @login_required
# def mood():
#     """Mood tracking page"""
#     form = MoodForm()
#     recent_entries = MoodEntry.query.filter_by(user_id=current_user.id)\
#                                    .order_by(MoodEntry.created_at.desc())\
#                                    .limit(10).all()
#     return render_template('mood.html', form=form, recent_entries=recent_entries)

# @app.route('/submit_mood', methods=['POST'])
# @login_required
# def submit_mood():
#     """Submit mood entry and get AI guidance"""
#     form = MoodForm()
#     if form.validate_on_submit():
#         # Save mood entry
#         mood_entry = MoodEntry(
#             user_id=current_user.id,
#             mood_description=form.mood_description.data,
#             current_situation=form.current_situation.data,
#             stress_level=form.stress_level.data
#         )
#         db.session.add(mood_entry)
#         db.session.commit()
#         
#         # Generate AI guidance
#         guidance = ai_generator.generate_mood_guidance(current_user, mood_entry)
#         
#         return jsonify({
#             'success': True,
#             'guidance': guidance,
#             'message': 'Mood entry saved successfully!'
#         })
#     
#     return jsonify({'success': False, 'errors': form.errors})

@app.route('/test_natal_chart')
def test_natal_chart():
    """Test natal chart generation without authentication requirement"""
    from datetime import datetime
    
    # Get user 2 (we know has complete info)
    user = User.query.get(2)
    if not user:
        return "No test user found"
    
    print(f"=== TEST NATAL CHART ROUTE DEBUG ===")
    print(f"User ID: {user.id}")
    print(f"Has complete birth info: {user.has_complete_birth_info()}")
    
    try:
        # Try to use the most accurate calculator available
        chart_data = None
        chart_image = None
        accuracy_level = "Basic"
        
        try:
            # Try Enhanced Calculator first (highest in-house accuracy)
            print("Attempting Enhanced Calculator...")
            from enhanced_calculator import EnhancedProfessionalCalculator
            calc = EnhancedProfessionalCalculator()
            
            # Combine birth date and time
            birth_datetime = datetime.combine(user.birth_date, user.birth_time)
            
            # Convert UTC offset to pytz timezone format
            timezone_offset = user.timezone or 'UTC'
            if timezone_offset.startswith('UTC') and timezone_offset != 'UTC':
                # Convert UTC-6 to Etc/GMT+6 format (note: Etc/GMT is inverted)
                tz_offset_str = timezone_offset.replace('UTC', '')
                try:
                    tz_offset_int = int(tz_offset_str)
                    if tz_offset_int == 0:
                        timezone_str = 'UTC'
                    elif tz_offset_int > 0:
                        # UTC+5 becomes Etc/GMT-5
                        timezone_str = f'Etc/GMT-{tz_offset_int}'
                    else:
                        # UTC-6 becomes Etc/GMT+6 (removing minus and flipping sign)
                        timezone_str = f'Etc/GMT+{abs(tz_offset_int)}'
                except ValueError:
                    timezone_str = 'UTC'
            else:
                timezone_str = 'UTC'
            
            chart_data = calc.calculate_full_chart(
                birth_datetime,
                user.latitude,
                user.longitude,
                timezone_str
            )
            
            if chart_data:
                accuracy_level = "Enhanced Professional ★★★★★"
                
                # Generate chart summary
                chart_summary = calc.get_chart_summary(chart_data)
                chart_data['summary'] = chart_summary
                
                # Try to generate chart visualization
                try:
                    from simple_chart import create_simple_chart
                    chart_image = create_simple_chart(chart_data, accuracy_level, user)
                    print(f"Chart image generated: {len(chart_image) if chart_image else 0} characters")
                except Exception as img_error:
                    print(f"Enhanced chart image generation failed: {img_error}")
                    chart_image = None
            else:
                raise Exception("Enhanced calculation failed")
                
        except Exception as enhanced_error:
            print(f"Enhanced calculator error: {enhanced_error}")
            chart_data = {"error": "Chart generation temporarily unavailable"}
            chart_image = None
            accuracy_level = "Unavailable"
        
        # Pass the user instead of current_user to the template
        return render_template('natal_chart.html', 
                             chart_data=chart_data,
                             chart_image=chart_image,
                             accuracy_level=accuracy_level,
                             current_user=user)  # Pass user as current_user for template
                             
    except Exception as e:
        print(f"=== TEST NATAL CHART EXCEPTION ===")
        print(f"Exception type: {type(e)}")
        print(f"Exception message: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        print("=== END EXCEPTION DEBUG ===")
        return f'Error generating test natal chart: {str(e)}'

@app.route('/natal_chart')
@login_required
def natal_chart():
    """Display user's natal chart with enhanced accuracy"""
    print(f"=== NATAL CHART ROUTE DEBUG ===")
    print(f"User ID: {current_user.id}")
    print(f"Has complete birth info: {current_user.has_complete_birth_info()}")
    
    if not current_user.has_complete_birth_info():
        flash('Please complete your birth information first.', 'warning')
        return redirect(url_for('profile'))
    
    try:
        # Try to use the most accurate calculator available
        chart_data = None
        chart_image = None
        accuracy_level = "Basic"
        
        try:
            # Try Enhanced Professional Calculator first (highest in-house accuracy)
            print("Attempting Enhanced Professional Calculator...")
            from enhanced_calculator import EnhancedProfessionalCalculator
            calc = EnhancedProfessionalCalculator()
            
            # Combine birth date and time
            birth_datetime = datetime.combine(current_user.birth_date, current_user.birth_time)
            
            # Convert UTC offset to pytz timezone format
            timezone_offset = current_user.timezone or 'UTC'
            if timezone_offset.startswith('UTC') and timezone_offset != 'UTC':
                # Convert UTC-6 to Etc/GMT+6 format (note: Etc/GMT is inverted)
                tz_offset_str = timezone_offset.replace('UTC', '')
                try:
                    tz_offset_int = int(tz_offset_str)
                    if tz_offset_int == 0:
                        timezone_str = 'UTC'
                    elif tz_offset_int > 0:
                        # UTC+5 becomes Etc/GMT-5
                        timezone_str = f'Etc/GMT-{tz_offset_int}'
                    else:
                        # UTC-6 becomes Etc/GMT+6 (removing minus and flipping sign)
                        timezone_str = f'Etc/GMT+{abs(tz_offset_int)}'
                except ValueError:
                    timezone_str = 'UTC'
            else:
                timezone_str = 'UTC'
            
            chart_data = calc.calculate_full_chart(
                birth_datetime,
                current_user.latitude,
                current_user.longitude,
                timezone_str
            )
            
            if chart_data:
                accuracy_level = "Enhanced Professional ★★★★★"
                
                # Generate chart summary
                chart_summary = calc.get_chart_summary(chart_data)
                chart_data['summary'] = chart_summary
                
                # Try to generate chart visualization AND detailed data
                try:
                    from simple_chart import create_simple_chart
                    from kerykeion_chart import create_professional_chart
                    
                    # Generate professional chart with detailed data
                    professional_data = create_professional_chart(current_user, "data")
                    if professional_data:
                        chart_data.update(professional_data)  # Merge Swiss Ephemeris data
                    
                    # Generate chart image
                    chart_image = create_simple_chart(chart_data, accuracy_level, current_user)
                    
                except Exception as img_error:
                    print(f"Enhanced chart image generation failed: {img_error}")
                    chart_image = None
            else:
                raise Exception("Enhanced calculation failed")
                
        except Exception as enhanced_error:
            print(f"Enhanced calculator failed: {enhanced_error}")
            print(f"DEBUG: Enhanced calculator is not working properly")
            # Set chart_data to None instead of trying questionable fallbacks
            chart_data = None
            chart_image = None
            accuracy_level = "Calculation Failed"
        
        # Add AI-powered sign summaries
        if chart_data and chart_data.get('planets'):
            print(f"DEBUG: chart_data structure: {type(chart_data)}")
            print(f"DEBUG: chart_data keys: {chart_data.keys() if hasattr(chart_data, 'keys') else 'Not a dict'}")
            print(f"DEBUG: planets structure: {type(chart_data.get('planets'))}")
            if chart_data.get('planets'):
                print(f"DEBUG: planets keys: {list(chart_data['planets'].keys()) if hasattr(chart_data['planets'], 'keys') else 'Not a dict'}")
            
            try:
                from ai_astrology_summaries import get_signs_summary
                
                sun_sign = chart_data['planets'].get('Sun', {}).get('sign')
                moon_sign = chart_data['planets'].get('Moon', {}).get('sign') 
                rising_sign = None
                
                # Get rising sign from houses or angles
                if chart_data.get('houses', {}).get('house_1', {}).get('sign'):
                    rising_sign = chart_data['houses']['house_1']['sign']
                elif chart_data.get('angles', {}).get('ascendant', {}).get('sign'):
                    rising_sign = chart_data['angles']['ascendant']['sign']
                
                if sun_sign and moon_sign:
                    chart_data['sign_summaries'] = get_signs_summary(sun_sign, moon_sign, rising_sign)
                    
            except Exception as e:
                print(f"Error generating sign summaries: {e}")
        
        if not chart_data:
            flash('Chart calculation failed. Please check your birth information and try again.', 'error')
            return redirect(url_for('profile'))

        return render_template('natal_chart.html',
                             chart_data=chart_data,
                             chart_image=chart_image,
                             accuracy_level=accuracy_level)
                             
    except Exception as e:
        print(f"=== NATAL CHART EXCEPTION ===")
        print(f"Exception type: {type(e)}")
        print(f"Exception message: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        print("=== END EXCEPTION DEBUG ===")
        flash(f'Error generating natal chart: {str(e)}', 'error')
        return redirect(url_for('index'))


def create_enhanced_chart_image(chart_data, accuracy_level="Professional"):
    """Create a professional astrological chart with dark theme and enhanced visibility"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.patches import Circle
        import matplotlib.patches as mpatches
        
        # Use non-interactive backend for web safety
        plt.switch_backend('Agg')
        
        # Create figure with theme based on usage
        is_dashboard = (accuracy_level == "Dashboard Preview")
        bg_color = 'none' if is_dashboard else '#1a1a1a'
        
        fig, ax = plt.subplots(figsize=(16, 16), facecolor=bg_color if bg_color != 'none' else 'white')
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_facecolor(bg_color if bg_color != 'none' else 'white')
        
        # Enhanced chart circles with styling based on background
        circle_color = '#ffffff' if not is_dashboard else '#333333'
        center_bg = '#2a2a2a' if not is_dashboard else '#f8f9fa'
        
        outer_circle = Circle((0, 0), 1.0, fill=False, linewidth=4, color=circle_color, alpha=0.9)
        middle_circle = Circle((0, 0), 0.8, fill=False, linewidth=2, color=circle_color, alpha=0.7)
        inner_circle = Circle((0, 0), 0.6, fill=False, linewidth=2, color=circle_color, alpha=0.6)
        center_circle = Circle((0, 0), 0.12, fill=True, facecolor=center_bg, edgecolor=circle_color, linewidth=2)
        
        ax.add_patch(outer_circle)
        ax.add_patch(middle_circle) 
        ax.add_patch(inner_circle)
        ax.add_patch(center_circle)
        
        # Professional zodiac signs with high contrast
        zodiac_symbols = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
        sign_names = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        sign_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', 
                      '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA']
        
        # Draw enhanced zodiac wheel with adaptive colors
        text_color = '#ffffff' if not is_dashboard else '#333333'
        symbol_bg = '#2a2a2a' if not is_dashboard else '#ffffff'
        
        for i, (symbol, name, color) in enumerate(zip(zodiac_symbols, sign_names, sign_colors)):
            angle_deg = i * 30  # Each sign is 30 degrees
            angle_rad = np.radians(90 - angle_deg)  # Start from Aries at top
            
            # Symbol position with adaptive styling
            x_symbol = 1.15 * np.cos(angle_rad)
            y_symbol = 1.15 * np.sin(angle_rad)
            ax.text(x_symbol, y_symbol, symbol, fontsize=24, ha='center', va='center', 
                   weight='bold', color=color, 
                   bbox=dict(boxstyle="circle,pad=0.3", facecolor=symbol_bg, 
                           edgecolor=color, linewidth=2, alpha=0.9))
            
            # Sign name with adaptive visibility (only show on full chart)
            if not is_dashboard:
                x_name = 1.35 * np.cos(angle_rad)
                y_name = 1.35 * np.sin(angle_rad)
                ax.text(x_name, y_name, name, fontsize=12, ha='center', va='center', 
                       color=text_color, weight='bold', alpha=0.8)
            
            # Enhanced sign boundaries with adaptive color
            boundary_rad = np.radians(90 - angle_deg)
            x1, y1 = 0.6 * np.cos(boundary_rad), 0.6 * np.sin(boundary_rad)
            x2, y2 = 1.0 * np.cos(boundary_rad), 1.0 * np.sin(boundary_rad)
            boundary_color = '#666666' if not is_dashboard else '#cccccc'
            ax.plot([x1, x2], [y1, y2], color=boundary_color, alpha=0.7, linewidth=1.5)
        
        # Professional planet symbols and colors with high contrast
        planet_info = {
            'sun': {'symbol': '☉', 'color': '#FFD700', 'size': 20, 'name': 'Sun'},
            'moon': {'symbol': '☽', 'color': '#C0C0C0', 'size': 20, 'name': 'Moon'},
            'mercury': {'symbol': '☿', 'color': '#FFA500', 'size': 18, 'name': 'Mercury'},
            'venus': {'symbol': '♀', 'color': '#FF69B4', 'size': 18, 'name': 'Venus'},
            'mars': {'symbol': '♂', 'color': '#FF4500', 'size': 18, 'name': 'Mars'},
            'jupiter': {'symbol': '♃', 'color': '#4169E1', 'size': 19, 'name': 'Jupiter'},
            'saturn': {'symbol': '♄', 'color': '#8B4513', 'size': 19, 'name': 'Saturn'}
        }
        
        # Draw professional house cusps if available
        if 'houses' in chart_data and chart_data['houses']:
            for i in range(1, 13):
                if i in chart_data['houses']:
                    cusp_deg = chart_data['houses'][i]['cusp']
                    
                    # Draw enhanced house lines
                    angle_rad = np.radians(90 - cusp_deg)
                    x1, y1 = 0.12 * np.cos(angle_rad), 0.12 * np.sin(angle_rad)
                    x2, y2 = 0.6 * np.cos(angle_rad), 0.6 * np.sin(angle_rad)
                    ax.plot([x1, x2], [y1, y2], '#00BFFF', alpha=0.8, linewidth=3)
                    
                    # Professional house numbers with adaptive styling
                    x_num = 0.35 * np.cos(angle_rad)
                    y_num = 0.35 * np.sin(angle_rad)
                    house_bg = '#1a1a1a' if not is_dashboard else '#ffffff'
                    house_text = '#ffffff' if not is_dashboard else '#333333'
                    ax.text(x_num, y_num, str(i), fontsize=14, ha='center', va='center',
                           bbox=dict(boxstyle="circle,pad=0.2", facecolor=house_bg, 
                                   edgecolor='#00BFFF', linewidth=2, alpha=0.9), 
                           weight='bold', color=house_text)
        
        # Draw planets with professional styling
        if 'planets' in chart_data and chart_data['planets']:
            for planet_name, planet_data in chart_data['planets'].items():
                if planet_name in planet_info:
                    info = planet_info[planet_name]
                    
                    # Get planet longitude
                    longitude = planet_data.get('longitude', 0)
                    angle_rad = np.radians(90 - longitude)
                    
                    # Position planet on chart with better spacing
                    radius = 0.9
                    x = radius * np.cos(angle_rad)
                    y = radius * np.sin(angle_rad)
                    
                    # Draw planet symbol with adaptive visibility
                    planet_bg = '#1a1a1a' if not is_dashboard else '#ffffff'
                    ax.text(x, y, info['symbol'], fontsize=info['size'], ha='center', va='center',
                           color=info['color'], weight='bold',
                           bbox=dict(boxstyle="circle,pad=0.3", facecolor=planet_bg, 
                                   edgecolor=info['color'], linewidth=3, alpha=0.95))
                    
                    # Enhanced degree annotation (only on full chart)
                    if not is_dashboard:
                        sign = planet_data.get('sign', '')
                        degree = planet_data.get('degree', 0)
                        degree_text = f"{int(degree)}°{sign[:3]}"
                        
                        # Position degree text with better spacing
                        x_deg = (radius + 0.15) * np.cos(angle_rad)
                        y_deg = (radius + 0.15) * np.sin(angle_rad)
                        degree_bg = '#2a2a2a' if not is_dashboard else '#ffffff'
                        degree_text_color = '#ffffff' if not is_dashboard else '#333333'
                        ax.text(x_deg, y_deg, degree_text, fontsize=11, ha='center', va='center',
                               color=degree_text_color, weight='bold',
                               bbox=dict(boxstyle="round,pad=0.3", facecolor=degree_bg, 
                                       edgecolor=info['color'], alpha=0.9))
        
        # Calculate and draw major aspects with enhanced visibility
        if 'planets' in chart_data and len(chart_data['planets']) > 1:
            planets = chart_data['planets']
            aspect_info = {
                'conjunction': {'color': '#FF0000', 'width': 3, 'alpha': 0.8, 'style': '-'},
                'opposition': {'color': '#FF6600', 'width': 3, 'alpha': 0.8, 'style': '-'},
                'trine': {'color': '#0066FF', 'width': 2, 'alpha': 0.7, 'style': '-'},
                'sextile': {'color': '#00CC00', 'width': 2, 'alpha': 0.6, 'style': '--'},
                'square': {'color': '#FF3300', 'width': 2, 'alpha': 0.7, 'style': '-'}
            }
            
            planet_longitudes = {name: data.get('longitude', 0) for name, data in planets.items()}
            
            # Check for major aspects between planets
            for i, (planet1, lon1) in enumerate(planet_longitudes.items()):
                for planet2, lon2 in list(planet_longitudes.items())[i+1:]:
                    aspect_angle = abs(lon1 - lon2)
                    if aspect_angle > 180:
                        aspect_angle = 360 - aspect_angle
                    
                    aspect_type = None
                    orb_tolerance = 8  # degrees
                    
                    if abs(aspect_angle - 0) <= orb_tolerance:
                        aspect_type = 'conjunction'
                    elif abs(aspect_angle - 60) <= orb_tolerance:
                        aspect_type = 'sextile'
                    elif abs(aspect_angle - 90) <= orb_tolerance:
                        aspect_type = 'square'
                    elif abs(aspect_angle - 120) <= orb_tolerance:
                        aspect_type = 'trine'
                    elif abs(aspect_angle - 180) <= orb_tolerance:
                        aspect_type = 'opposition'
                    
                    if aspect_type and planet1 in planet_info and planet2 in planet_info:
                        # Draw enhanced aspect line
                        angle1_rad = np.radians(90 - lon1)
                        angle2_rad = np.radians(90 - lon2)
                        
                        x1, y1 = 0.75 * np.cos(angle1_rad), 0.75 * np.sin(angle1_rad)
                        x2, y2 = 0.75 * np.cos(angle2_rad), 0.75 * np.sin(angle2_rad)
                        
                        aspect_style = aspect_info[aspect_type]
                        ax.plot([x1, x2], [y1, y2], 
                               color=aspect_style['color'], 
                               alpha=aspect_style['alpha'],
                               linewidth=aspect_style['width'],
                               linestyle=aspect_style['style'])
        
        # Professional title with birth info (only for full chart, not dashboard)
        if accuracy_level != "Dashboard Preview":
            title_parts = [f"Natal Chart - {accuracy_level}"]
            if 'birth_info' in chart_data and chart_data['birth_info']:
                birth_info = chart_data['birth_info']
                if 'datetime' in birth_info:
                    dt = birth_info['datetime']
                    title_parts.append(f"{dt.strftime('%B %d, %Y at %I:%M %p')}")
                if 'coordinates' in birth_info:
                    coords = birth_info['coordinates']
                    if hasattr(coords, 'city') and coords.city:
                        title_parts.append(f"{coords.city}, {getattr(coords, 'region', '')}")
            
            plt.suptitle('\n'.join(title_parts), fontsize=16, fontweight='bold', 
                        color='#ffffff', y=0.95)
        
        # Professional legend (only for full chart, not dashboard preview)
        if accuracy_level != "Dashboard Preview":
            legend_elements = [
                mpatches.Patch(color='#FF0000', label='Challenging Aspects'),
                mpatches.Patch(color='#0066FF', label='Harmonious Aspects'),
                mpatches.Patch(color='#00CC00', label='Growth Aspects'),
                mpatches.Patch(color='#00BFFF', label='House Divisions')
            ]
            legend = ax.legend(handles=legend_elements, loc='upper right', 
                              bbox_to_anchor=(1.45, 1), frameon=True, 
                              fancybox=True, shadow=True, facecolor='#2a2a2a',
                              edgecolor='#ffffff', labelcolor='#ffffff')
        
        plt.tight_layout()
        
        # Save to base64 with adaptive background
        import io
        import base64
        
        img_buffer = io.BytesIO()
        
        # Set transparent background for dashboard, solid for full chart
        if is_dashboard:
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', 
                       facecolor='none', edgecolor='none', pad_inches=0.1,
                       transparent=True)
        else:
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', 
                       facecolor='#1a1a1a', edgecolor='none', pad_inches=0.1,
                       transparent=False)
        
        img_buffer.seek(0)
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()  # Important: close the figure to free memory
        
        return f"data:image/png;base64,{img_data}"
        
    except Exception as e:
        print(f"Chart image generation error: {e}")
        return None

# @app.route('/horoscope_history')
# @login_required
# def horoscope_history():
#     """View past horoscope readings"""
#     readings = HoroscopeReading.query.filter_by(user_id=current_user.id)\
#                                     .order_by(HoroscopeReading.created_at.desc())\
#                                     .paginate(per_page=10)
#     return render_template('horoscope_history.html', readings=readings)

@app.route('/modern')
def modern_astrology():
    """Modern JavaScript-based astrology interface"""
    return render_template('modern_astrology.html')

@app.route('/reading/<int:reading_id>')
@login_required
def view_reading(reading_id):
    """View a specific horoscope reading"""
    reading = HoroscopeReading.query.filter_by(id=reading_id, user_id=current_user.id).first_or_404()
    return render_template('view_reading.html', reading=reading)

def calculate_upcoming_cosmic_events(lat: float = None, lng: float = None):
    """Calculate real upcoming cosmic events using Kerykeion/Swiss Ephemeris.

    By default this uses coordinates provided here; if none are passed it falls back
    to the application config defaults (`DEFAULT_LATITUDE`, `DEFAULT_LONGITUDE`).
    """
    try:
        from kerykeion import AstrologicalSubject
        from datetime import datetime, timedelta, date
        import calendar
        
        events = []
        today = datetime.now()

        # Resolve coordinates: prefer explicit args, then app config, then Greenwich
        if lat is None:
            lat = app.config.get('DEFAULT_LATITUDE', 51.4769)  # Greenwich default
        if lng is None:
            lng = app.config.get('DEFAULT_LONGITUDE', -0.0005)  # Greenwich default
        
        # Calculate next 60 days of cosmic events
        for days_ahead in range(0, 61):
            check_date = today + timedelta(days=days_ahead)
            
            try:
                # Create astrological subject for this date (using UTC coordinates)
                transit_subject = AstrologicalSubject(
                    name="Transit",
                    year=check_date.year,
                    month=check_date.month,
                    day=check_date.day,
                    hour=12,  # Noon UTC
                    minute=0,
                    lat=lat,
                    lng=lng,
                    tz_str="UTC"
                )
                
                # Check for New Moon (Sun-Moon conjunction within 2 degrees)
                sun_lon = transit_subject.sun.abs_pos
                moon_lon = transit_subject.moon.abs_pos
                sun_moon_diff = abs(sun_lon - moon_lon)
                if sun_moon_diff > 180:
                    sun_moon_diff = 360 - sun_moon_diff
                
                if sun_moon_diff <= 2.0:  # New Moon
                    moon_sign = transit_subject.moon.sign
                    events.append({
                        'title': f'New Moon in {moon_sign}',
                        'date': check_date.strftime('%B %d, %Y'),
                        'description': f'New beginnings and fresh intentions in {moon_sign} energy',
                        'type': 'new_moon',
                        'icon': 'fas fa-circle',
                        'sort_date': check_date
                    })
                
                # Check for Full Moon (Sun-Moon opposition within 2 degrees)
                if abs(sun_moon_diff - 180) <= 2.0:  # Full Moon
                    moon_sign = transit_subject.moon.sign
                    events.append({
                        'title': f'Full Moon in {moon_sign}',
                        'date': check_date.strftime('%B %d, %Y'),
                        'description': f'Culmination and release in {moon_sign} energy',
                        'type': 'full_moon',
                        'icon': 'fas fa-circle',
                        'sort_date': check_date
                    })
                
                # Check for planetary retrogrades (simplified check)
                planets = ['mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
                for planet_name in planets:
                    planet = getattr(transit_subject, planet_name, None)
                    if planet and planet.retrograde:
                        # Check if this is the start of retrograde by comparing with yesterday
                        yesterday = check_date - timedelta(days=1)
                        try:
                            yesterday_subject = AstrologicalSubject(
                                name="Yesterday",
                                year=yesterday.year,
                                month=yesterday.month,
                                day=yesterday.day,
                                hour=12,
                                minute=0,
                                lat=51.4769,  # Greenwich latitude
                                lng=-0.0005,  # Greenwich longitude
                                tz_str="UTC"
                            )
                            yesterday_planet = getattr(yesterday_subject, planet_name, None)
                            
                            # If planet wasn't retrograde yesterday but is today, it's starting
                            if yesterday_planet and not yesterday_planet.retrograde and planet.retrograde:
                                events.append({
                                    'title': f'{planet_name.title()} Retrograde Begins',
                                    'date': check_date.strftime('%B %d, %Y'),
                                    'description': f'Time for review and reflection in {planet_name} themes',
                                    'type': 'retrograde',
                                    'icon': 'fas fa-undo',
                                    'sort_date': check_date
                                })
                        except:
                            pass  # Skip if yesterday calculation fails
                
                # Check for Equinoxes and Solstices (Sun entering cardinal signs)
                sun_degree = transit_subject.sun.position
                sun_sign = transit_subject.sun.sign
                
                # Check if Sun is at 0 degrees of cardinal signs (within 0.5 degrees)
                if abs(sun_degree) <= 0.5:
                    if sun_sign == "Aries":
                        events.append({
                            'title': 'Spring Equinox',
                            'date': check_date.strftime('%B %d, %Y'),
                            'description': 'Balance of light and dark, new beginnings',
                            'type': 'equinox',
                            'icon': 'fas fa-seedling',
                            'sort_date': check_date
                        })
                    elif sun_sign == "Cancer":
                        events.append({
                            'title': 'Summer Solstice',
                            'date': check_date.strftime('%B %d, %Y'),
                            'description': 'Longest day, peak solar energy',
                            'type': 'solstice',
                            'icon': 'fas fa-sun',
                            'sort_date': check_date
                        })
                    elif sun_sign == "Libra":
                        events.append({
                            'title': 'Autumn Equinox',
                            'date': check_date.strftime('%B %d, %Y'),
                            'description': 'Harvest time, balance and gratitude',
                            'type': 'equinox',
                            'icon': 'fas fa-leaf',
                            'sort_date': check_date
                        })
                    elif sun_sign == "Capricorn":
                        events.append({
                            'title': 'Winter Solstice',
                            'date': check_date.strftime('%B %d, %Y'),
                            'description': 'Longest night, deep reflection and renewal',
                            'type': 'solstice',
                            'icon': 'fas fa-snowflake',
                            'sort_date': check_date
                        })
                
            except Exception as calc_error:
                # Skip this date if calculation fails
                continue
        
        # Remove duplicates and sort by date
        unique_events = []
        seen_titles = set()
        for event in events:
            if event['title'] not in seen_titles:
                unique_events.append(event)
                seen_titles.add(event['title'])
        
        # Sort by date and return first 8 events
        unique_events.sort(key=lambda x: x['sort_date'])
        return unique_events[:8]
        
    except Exception as e:
        print(f"Error calculating cosmic events: {e}")
        # Fallback to basic events if calculation fails
        return [
            {
                'title': 'Cosmic Events Loading...',
                'date': 'Calculating real-time data',
                'description': 'Real astronomical calculations in progress',
                'type': 'loading',
                'icon': 'fas fa-spinner',
                'sort_date': datetime.now()
            }
        ]

@app.route('/cosmic_calendar')
@login_required
def cosmic_calendar():
    """View upcoming cosmic events and astrological calendar using real calculations"""
    events = calculate_upcoming_cosmic_events()
    return render_template('cosmic_calendar.html', events=events)

@app.route('/ask_numa')
@login_required
def ask_numa():
    """Ask Numa - AI Chat Interface"""
    try:
        user_context = None

        if current_user.has_complete_birth_info():
            from datetime import date
            today = date.today()
            today_reading = HoroscopeReading.query.filter_by(
                user_id=current_user.id,
                reading_date=today
            ).first()

            enhanced_data = None
            if today_reading and today_reading.structured_data:
                import json
                enhanced_data = json.loads(today_reading.structured_data)

            # Extract comprehensive profile data
            profile = (enhanced_data or {}).get('profile', {})
            season = (enhanced_data or {}).get('season_info', 'Current Season')
            current_transits = (enhanced_data or {}).get('current_transits', [])
            moon_data = (enhanced_data or {}).get('moon_data', {})
            mood_bars = (enhanced_data or {}).get('mood_bars', {})
            
            # Get upcoming cosmic events
            cosmic_events = calculate_upcoming_cosmic_events(
                lat=current_user.latitude,
                lng=current_user.longitude
            )
            
            # Format cosmic events for context
            upcoming_events = []
            for event in cosmic_events[:5]:  # Next 5 events
                upcoming_events.append({
                    'title': event['title'],
                    'date': event['date'],
                    'type': event['type']
                })

            user_context = {
                # Complete natal chart profile
                "profile": {
                    "sun": profile.get('sun', {}),
                    "moon": profile.get('moon', {}),
                    "rising": profile.get('rising', {}),
                    "mercury": profile.get('mercury', {}),
                    "venus": profile.get('venus', {}),
                    "mars": profile.get('mars', {}),
                    "jupiter": profile.get('jupiter', {}),
                    "saturn": profile.get('saturn', {}),
                    "houses": profile.get('houses', {}),
                    "angles": profile.get('angles', {})
                },
                
                # User birth information
                "birth_info": {
                    "date": current_user.birth_date.strftime('%Y-%m-%d') if current_user.birth_date else None,
                    "time": current_user.birth_time.strftime('%H:%M') if current_user.birth_time else None,
                    "location": current_user.get_full_birth_location(),
                    "timezone": current_user.timezone,
                    "coordinates": {
                        "latitude": current_user.latitude,
                        "longitude": current_user.longitude
                    }
                },
                
                # Current location and preferences
                "current_info": {
                    "location": f"{getattr(current_user, 'current_city', '')}, {getattr(current_user, 'current_region', '')}".strip(', '),
                    "timezone": getattr(current_user, 'current_timezone', None),
                    "theme": getattr(current_user, 'theme_preference', 'auto')
                },
                
                # Today's cosmic conditions
                "daily_context": {
                    "season": season,
                    "moon": {
                        "sign": moon_data.get('sign', 'Unknown'),
                        "phase": moon_data.get('phase', 'Unknown'),
                        "illumination": moon_data.get('illumination', 0)
                    },
                    "transits": current_transits[:3],  # Top 3 transits
                    "energy_levels": mood_bars,
                    "daily_focus": (enhanced_data or {}).get('daily_focus'),
                    "overall_energy": mood_bars.get('overall_energy') if mood_bars else None
                },
                
                # Full today's horoscope
                "todays_horoscope": {
                    "content": today_reading.content if today_reading else None,
                    "short_summary": getattr(today_reading, 'short_summary', None) if today_reading else None,
                    "reading_date": today_reading.reading_date.strftime('%Y-%m-%d') if today_reading else None,
                    "structured_data": enhanced_data
                },
                
                # Upcoming cosmic events
                "cosmic_events": upcoming_events,
                
                # Quick access fields for backward compatibility
                "sun": profile.get('sun', {}).get('sign', 'Unknown'),
                "moon": profile.get('moon', {}).get('sign', 'Unknown'),
                "rising": profile.get('rising', {}).get('sign', 'Unknown'),
                "moon_sign": moon_data.get('sign', 'Unknown'),
                "moon_phase": moon_data.get('phase', 'Unknown'),
                "main_transit": (
                    f"{current_transits[0].get('t_planet','')} "
                    f"{current_transits[0].get('aspect','')} "
                    f"{current_transits[0].get('n_planet','')}"
                ).strip() if current_transits else None
            }

        return render_template('ask_numa.html', user_context=user_context)

    except Exception as e:
        print(f"Error in ask_numa route: {e}")
        return render_template('ask_numa.html', user_context=None)

@app.route('/chat_numa', methods=['POST'])
@login_required
@csrf.exempt  # Exempt from CSRF for AJAX requests (remove if you handle CSRF in JS)
def chat_numa():
    """Handle chat messages to Numa"""
    try:
        data = request.get_json(force=True) or {}
        user_message = (data.get('message') or '').strip()
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Minimal user metadata
        user_data = {
            "first_name": (getattr(current_user, "first_name", None) or "Friend"),
            "timezone": (getattr(current_user, "timezone", None) or "UTC"),
        }

        # Load today's reading/context
        from datetime import date
        today = date.today()
        today_reading = HoroscopeReading.query.filter_by(
            user_id=current_user.id,
            reading_date=today
        ).first()

        enhanced_data = None
        if today_reading and today_reading.structured_data:
            import json
            try:
                enhanced_data = json.loads(today_reading.structured_data)
            except Exception:
                enhanced_data = None

        # Short daily summary: prefer a stored short_summary; fall back to trimmed content
        daily_summary = None
        try:
            if hasattr(today_reading, "short_summary") and today_reading.short_summary:
                daily_summary = today_reading.short_summary.strip()[:240]
            elif today_reading and today_reading.content:
                daily_summary = today_reading.content.strip()[:240]
        except Exception:
            daily_summary = None

        numa_response = generate_numa_response_simple(
            user_message=user_message,
            user_data=user_data,
            enhanced_data=enhanced_data,
            daily_summary=daily_summary
        )
        # Convert newlines to <br> tags for HTML rendering
        formatted_response = numa_response.replace("\n", "<br>")
        return jsonify({'response': formatted_response})

    except Exception as e:
        print(f"Error in chat_numa: {e}")
        return jsonify({'response': "I'm having trouble right now. Please try again in a moment."})


def generate_numa_response_simple(user_message: str, user_data: dict, enhanced_data: dict, daily_summary: str) -> str:
    """
    Generate Numa's response using stored database data with contextual reasoning.
    Now includes a short 'Energy Outlook' (soft, forward-looking) and richer natal hooks,
    while keeping tokens small and the tone safe.
    """
    try:
        ai_generator = AIHoroscopeGenerator()
        if not getattr(ai_generator, "has_ai", None) or not getattr(ai_generator, "client", None):
            print("🔄 AI not available - using fallback response")
            return get_numa_fallback_response_simple(user_message, user_data, enhanced_data)

        # -------- Extract compact context from enhanced_data --------
        profile = (enhanced_data or {}).get('profile', {}) or {}
        current_transits = (enhanced_data or {}).get('current_transits', []) or []
        upcoming_transits = (enhanced_data or {}).get('upcoming_transits', []) or []  # precomputed list (next 3–7 days)
        moon = (enhanced_data or {}).get('moon_data', {}) or {}
        season = (enhanced_data or {}).get('season_info', 'Current Season')
        mood = (enhanced_data or {}).get('mood_bars', {}) or {}

        # Helper: compact transit to a single readable string
        def _tstring(t: dict) -> str:
            if not t:
                return ""
            base = f"{t.get('t_planet','').strip()} {t.get('aspect','').strip()} {t.get('n_planet','').strip()}".strip()
            extras = []
            if t.get('n_target_house_label'):
                extras.append(t['n_target_house_label'])
            if t.get('tone'):
                extras.append(t['tone'])
            if t.get('window'):  # for upcoming only; e.g., "mid-week" / "evening" / "earlier next week"
                extras.append(t['window'])
            return " | ".join([s for s in [base] + extras if s])

        # Limit current to 2; upcoming to 2 for cost/clarity
        transits_list = [_tstring(t) for t in current_transits[:2] if t] or []
        upcoming_list = [_tstring(t) for t in upcoming_transits[:2] if t] or []

        # Core user data
        user_name = user_data.get("first_name", "Friend")
        sun_sign = profile.get('sun', {}).get('sign', 'Unknown')
        moon_sign = profile.get('moon', {}).get('sign', 'Unknown')
        rising_sign = profile.get('rising', {}).get('sign', 'Unknown')
        chart_ruler = profile.get('chart_ruler', None)  # optional

        moon_current_sign = moon.get('sign', 'Unknown')
        moon_phase = moon.get('phase', 'Unknown')

        daily_focus = (enhanced_data or {}).get("daily_focus")
        overall_energy = mood.get('overall_energy')

        # -------- Build slim JSON context --------
        context = {
            "user": {
                "name": user_name,
                "timezone": user_data.get("timezone", "UTC"),
                "sun": sun_sign,
                "moon": moon_sign,
                "rising": rising_sign,
                "chart_ruler": chart_ruler
            },
            "season": season,
            "moon": {"sign": moon_current_sign, "phase": moon_phase},
            "transits_today": transits_list,      # each like "Venus trine Sun | 2nd—values/self-worth | supportive"
            "upcoming_transits": upcoming_list,   # each like "... | 10th—role/reputation | supportive | mid-week"
            "daily_focus": daily_focus,
            "overall_energy": overall_energy
        }

        # Depth toggle: if user explicitly asks for "details"/"more context", allow a few more words
        lower_msg = (user_message or "").lower()
        wants_depth = any(k in lower_msg for k in ("details", "context", "explain", "why", "how"))
        max_tokens = 260 if wants_depth else 220
        word_note = "130–190 words" if wants_depth else "110–160 words"

        # -------- System prompt (concise + forward-looking but safe) --------
        system_prompt = (
            "You are Numa — a calm, insightful astrology companion.\n"
            "Use the user's natal chart and daily sky context to offer symbolic yet practical guidance.\n\n"
            "OUTPUT FORMAT (strict):\n"
            "Snapshot: <one short sentence summarizing the user's situation>\n"
            "Astro Angle: • <1–2 bullets linking natal + today's influences (season/Moon/transits)>\n"
            "Energy Outlook: • <0–2 bullets about upcoming influences (from 'upcoming_transits'), framed as soft possibilities>\n"
            "Next Step: • <1–2 gentle, realistic suggestions>\n"
            "Reflect: <one short question that invites clarity>\n\n"
            f"LENGTH:\n- Total {word_note}. Avoid long paragraphs or lists.\n\n"
            "STYLE:\n"
            "- Warm, clear, specific — not mystical or vague.\n"
            "- Mention at most 1–2 current transits and up to 2 upcoming transits.\n"
            "- Prefer house labels if provided (e.g., '2nd—values/self-worth', '10th—role/reputation').\n"
            "- You may reference chart ruler if relevant.\n"
            "- Offer a confident but balanced lean (e.g., 'this looks like a supportive time to have the conversation'), without guaranteeing outcomes.\n"
            "- Soft modals: might, could, tends to.\n"
            "- If the user didn’t name a life domain, speak in broader themes (confidence, collaboration, self-worth).\n\n"
            "BOUNDARIES:\n"
            "- No medical, legal, or financial advice.\n"
            "- No guarantees or outcome predictions; timing must be broad (morning/afternoon/evening or mid-week/earlier next week), never dates/hours.\n"
            "- Do not list all context — choose only what applies.\n"
            "- Avoid fear-based language or commands."
        )

        # -------- User prompt --------
        import json
        prompt_parts = [
            "User context (JSON):",
            json.dumps(context, indent=2)
        ]
        if daily_summary:
            prompt_parts += ["\nShort daily summary:", (daily_summary or "")[:180]]

        prompt_parts += [
            "\nUser question:",
            user_message,
            (
                "\nBe specific to the user's question. Use natal (Sun, Moon, Rising, chart ruler if present) and "
                "today's influences (season, Moon, transits), and optionally upcoming_transits for a soft Energy Outlook. "
                "Give a gentle lean (e.g., 'could be worth exploring gradually') without certainty. "
                "Do not repeat previous phrasing; choose a fresh astrological angle if asked again."
            )
        ]
        user_prompt = "\n".join(prompt_parts)

        # -------- Initial call --------
        response = ai_generator.client.chat.completions.create(
            model=ai_generator.model,  # e.g., "gpt-4o-mini"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.6
        )
        text = response.choices[0].message.content.strip()

        # -------- Anti-repetition guard --------
        if text.startswith(f"Hi {user_name}. It makes sense to want clarity"):
            user_prompt += (
                "\nPrevious answer was too generic. Rephrase concisely with a different astrological focus "
                "and include one succinct Energy Outlook bullet if relevant."
            )
            retry = ai_generator.client.chat.completions.create(
                model=ai_generator.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.65
            )
            text = retry.choices[0].message.content.strip()

        # -------- Format for readability (uses your existing helper) --------
        formatted_text = format_numa_text(text)
        return formatted_text

    except Exception as e:
        print(f"❌ Error generating Numa response: {e}")
        return get_numa_fallback_response_simple(user_message, user_data, enhanced_data)

def format_numa_text(text: str) -> str:
    """Format Numa's response text for better readability with line breaks"""
    import re
    
    # Add line breaks before each section title and make them bold
    text = re.sub(r"(Snapshot:)", r"\n<strong>\1</strong>", text)
    text = re.sub(r"(Astro Angle:)", r"\n<strong>\1</strong>", text)
    text = re.sub(r"(Next Step:)", r"\n<strong>\1</strong>", text)
    text = re.sub(r"(Reflect:)", r"\n<strong>\1</strong>", text)
    
    # Add line breaks before ALL bullet points, including right after colons
    text = re.sub(r"• ", r"\n• ", text)
    
    # Clean up multiple consecutive newlines to avoid large gaps
    text = re.sub(r"\n{3,}", r"\n\n", text)
    
    # Clean up any extra whitespace and return
    return text.strip()

def get_numa_fallback_response_simple(user_message: str, user_data: dict, enhanced_data: dict) -> str:
    """Minimal, neutral fallback with no keyword branching."""
    profile = (enhanced_data or {}).get('profile', {})
    sun = profile.get('sun', {}).get('sign', 'Your')
    name = user_data.get('first_name', 'Friend')

    return (
        f"Hi {name}. It makes sense to want clarity here. "
        f"With your {sun} Sun, steady preparation and honest reflection often help. "
        "Consider pacing yourself, noticing what feels grounded, and choosing moments when your energy is calm. "
        "You might take a small step that aligns with your values and see how it feels.\n\n"
        "What would a gentle, low-pressure next step look like for you?"
    )

@app.route('/favicon.ico')
def favicon():
    """Favicon placeholder - returns 204 No Content"""
    return '', 204

@app.route('/sw.js')
def service_worker():
    """Service worker placeholder - returns empty JS file"""
    return '', 200, {'Content-Type': 'application/javascript'}

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)