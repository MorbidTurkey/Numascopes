from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField, TimeField, SelectField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional
from wtforms.widgets import DateInput, TimeInput

class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """User registration form"""
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

class BirthInfoForm(FlaskForm):
    """Form for collecting birth information"""
    birth_date = DateField('Birth Date', validators=[Optional()], widget=DateInput())
    
    # Enhanced birth time with options
    birth_time_hour = SelectField('Hour', choices=[
        ('', 'Hour'),
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'),
        ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')
    ], validators=[Optional()])
    
    birth_time_minute = SelectField('Minute', choices=[
        ('', 'Min'),
        ('00', '00'), ('05', '05'), ('10', '10'), ('15', '15'), ('20', '20'), ('25', '25'),
        ('30', '30'), ('35', '35'), ('40', '40'), ('45', '45'), ('50', '50'), ('55', '55')
    ], validators=[Optional()])
    
    birth_time_ampm = SelectField('AM/PM', choices=[
        ('', 'AM/PM'),
        ('AM', 'AM'),
        ('PM', 'PM')
    ], validators=[Optional()])
    
    birth_time_unknown = BooleanField("I don't know my birth time (will use 12:00 PM)")
    
    # Keep the original field for backward compatibility, but make it optional now
    birth_time = StringField('Birth Time', validators=[Optional()], render_kw={'style': 'display: none;'})
    
    # Improved location selection
    birth_country = SelectField('Country', choices=[
        ('', 'Select Country'),
        ('AF', 'Afghanistan'),
        ('AL', 'Albania'),
        ('DZ', 'Algeria'),
        ('AD', 'Andorra'),
        ('AO', 'Angola'),
        ('AG', 'Antigua and Barbuda'),
        ('AR', 'Argentina'),
        ('AM', 'Armenia'),
        ('AU', 'Australia'),
        ('AT', 'Austria'),
        ('AZ', 'Azerbaijan'),
        ('BS', 'Bahamas'),
        ('BH', 'Bahrain'),
        ('BD', 'Bangladesh'),
        ('BB', 'Barbados'),
        ('BY', 'Belarus'),
        ('BE', 'Belgium'),
        ('BZ', 'Belize'),
        ('BJ', 'Benin'),
        ('BT', 'Bhutan'),
        ('BO', 'Bolivia'),
        ('BA', 'Bosnia and Herzegovina'),
        ('BW', 'Botswana'),
        ('BR', 'Brazil'),
        ('BN', 'Brunei'),
        ('BG', 'Bulgaria'),
        ('BF', 'Burkina Faso'),
        ('BI', 'Burundi'),
        ('CV', 'Cabo Verde'),
        ('KH', 'Cambodia'),
        ('CM', 'Cameroon'),
        ('CA', 'Canada'),
        ('CF', 'Central African Republic'),
        ('TD', 'Chad'),
        ('CL', 'Chile'),
        ('CN', 'China'),
        ('CO', 'Colombia'),
        ('KM', 'Comoros'),
        ('CG', 'Republic of the Congo'),
        ('CD', 'Democratic Republic of the Congo'),
        ('CR', 'Costa Rica'),
        ('CI', "Côte d'Ivoire"),
        ('HR', 'Croatia'),
        ('CU', 'Cuba'),
        ('CY', 'Cyprus'),
        ('CZ', 'Czech Republic'),
        ('DK', 'Denmark'),
        ('DJ', 'Djibouti'),
        ('DM', 'Dominica'),
        ('DO', 'Dominican Republic'),
        ('EC', 'Ecuador'),
        ('EG', 'Egypt'),
        ('SV', 'El Salvador'),
        ('GQ', 'Equatorial Guinea'),
        ('ER', 'Eritrea'),
        ('EE', 'Estonia'),
        ('SZ', 'Eswatini'),
        ('ET', 'Ethiopia'),
        ('FJ', 'Fiji'),
        ('FI', 'Finland'),
        ('FR', 'France'),
        ('GA', 'Gabon'),
        ('GM', 'Gambia'),
        ('GE', 'Georgia'),
        ('DE', 'Germany'),
        ('GH', 'Ghana'),
        ('GR', 'Greece'),
        ('GD', 'Grenada'),
        ('GT', 'Guatemala'),
        ('GN', 'Guinea'),
        ('GW', 'Guinea-Bissau'),
        ('GY', 'Guyana'),
        ('HT', 'Haiti'),
        ('HN', 'Honduras'),
        ('HU', 'Hungary'),
        ('IS', 'Iceland'),
        ('IN', 'India'),
        ('ID', 'Indonesia'),
        ('IR', 'Iran'),
        ('IQ', 'Iraq'),
        ('IE', 'Ireland'),
        ('IL', 'Israel'),
        ('IT', 'Italy'),
        ('JM', 'Jamaica'),
        ('JP', 'Japan'),
        ('JO', 'Jordan'),
        ('KZ', 'Kazakhstan'),
        ('KE', 'Kenya'),
        ('KI', 'Kiribati'),
        ('KP', 'North Korea'),
        ('KR', 'South Korea'),
        ('KW', 'Kuwait'),
        ('KG', 'Kyrgyzstan'),
        ('LA', 'Laos'),
        ('LV', 'Latvia'),
        ('LB', 'Lebanon'),
        ('LS', 'Lesotho'),
        ('LR', 'Liberia'),
        ('LY', 'Libya'),
        ('LI', 'Liechtenstein'),
        ('LT', 'Lithuania'),
        ('LU', 'Luxembourg'),
        ('MG', 'Madagascar'),
        ('MW', 'Malawi'),
        ('MY', 'Malaysia'),
        ('MV', 'Maldives'),
        ('ML', 'Mali'),
        ('MT', 'Malta'),
        ('MH', 'Marshall Islands'),
        ('MR', 'Mauritania'),
        ('MU', 'Mauritius'),
        ('MX', 'Mexico'),
        ('FM', 'Micronesia'),
        ('MD', 'Moldova'),
        ('MC', 'Monaco'),
        ('MN', 'Mongolia'),
        ('ME', 'Montenegro'),
        ('MA', 'Morocco'),
        ('MZ', 'Mozambique'),
        ('MM', 'Myanmar'),
        ('NA', 'Namibia'),
        ('NR', 'Nauru'),
        ('NP', 'Nepal'),
        ('NL', 'Netherlands'),
        ('NZ', 'New Zealand'),
        ('NI', 'Nicaragua'),
        ('NE', 'Niger'),
        ('NG', 'Nigeria'),
        ('MK', 'North Macedonia'),
        ('NO', 'Norway'),
        ('OM', 'Oman'),
        ('PK', 'Pakistan'),
        ('PW', 'Palau'),
        ('PA', 'Panama'),
        ('PG', 'Papua New Guinea'),
        ('PY', 'Paraguay'),
        ('PE', 'Peru'),
        ('PH', 'Philippines'),
        ('PL', 'Poland'),
        ('PT', 'Portugal'),
        ('QA', 'Qatar'),
        ('RO', 'Romania'),
        ('RU', 'Russia'),
        ('RW', 'Rwanda'),
        ('KN', 'Saint Kitts and Nevis'),
        ('LC', 'Saint Lucia'),
        ('VC', 'Saint Vincent and the Grenadines'),
        ('WS', 'Samoa'),
        ('SM', 'San Marino'),
        ('ST', 'Sao Tome and Principe'),
        ('SA', 'Saudi Arabia'),
        ('SN', 'Senegal'),
        ('RS', 'Serbia'),
        ('SC', 'Seychelles'),
        ('SL', 'Sierra Leone'),
        ('SG', 'Singapore'),
        ('SK', 'Slovakia'),
        ('SI', 'Slovenia'),
        ('SB', 'Solomon Islands'),
        ('SO', 'Somalia'),
        ('ZA', 'South Africa'),
        ('SS', 'South Sudan'),
        ('ES', 'Spain'),
        ('LK', 'Sri Lanka'),
        ('SD', 'Sudan'),
        ('SR', 'Suriname'),
        ('SE', 'Sweden'),
        ('CH', 'Switzerland'),
        ('SY', 'Syria'),
        ('TW', 'Taiwan'),
        ('TJ', 'Tajikistan'),
        ('TZ', 'Tanzania'),
        ('TH', 'Thailand'),
        ('TL', 'Timor-Leste'),
        ('TG', 'Togo'),
        ('TO', 'Tonga'),
        ('TT', 'Trinidad and Tobago'),
        ('TN', 'Tunisia'),
        ('TR', 'Turkey'),
        ('TM', 'Turkmenistan'),
        ('TV', 'Tuvalu'),
        ('UG', 'Uganda'),
        ('UA', 'Ukraine'),
        ('AE', 'United Arab Emirates'),
        ('GB', 'United Kingdom'),
        ('US', 'United States'),
        ('UY', 'Uruguay'),
        ('UZ', 'Uzbekistan'),
        ('VU', 'Vanuatu'),
        ('VA', 'Vatican City'),
        ('VE', 'Venezuela'),
        ('VN', 'Vietnam'),
        ('YE', 'Yemen'),
        ('ZM', 'Zambia'),
        ('ZW', 'Zimbabwe'),
        ('Other', 'Other')
    ], validators=[Optional()])

    
    birth_region = StringField('State/Province/Region', validators=[
        Optional(),
        Length(max=100, message='Region name too long')
    ], render_kw={'placeholder': 'Enter state, province, or region (if applicable)'})
    
    birth_city = StringField('City', validators=[
        Optional(), 
        Length(min=2, max=100, message='Please enter a valid city name')
    ], render_kw={'placeholder': 'Enter your birth city'})
    timezone = SelectField('Timezone', choices=[
        ('UTC-12', 'UTC-12 (Baker Island)'),
        ('UTC-11', 'UTC-11 (American Samoa)'),
        ('UTC-10', 'UTC-10 (Hawaii)'),
        ('UTC-9', 'UTC-9 (Alaska)'),
        ('UTC-8', 'UTC-8 (Pacific Time)'),
        ('UTC-7', 'UTC-7 (Mountain Time)'),
        ('UTC-6', 'UTC-6 (Central Time)'),
        ('UTC-5', 'UTC-5 (Eastern Time)'),
        ('UTC-4', 'UTC-4 (Atlantic Time)'),
        ('UTC-3', 'UTC-3 (Argentina)'),
        ('UTC-2', 'UTC-2 (South Georgia)'),
        ('UTC-1', 'UTC-1 (Azores)'),
        ('UTC+0', 'UTC+0 (London, GMT)'),
        ('UTC+1', 'UTC+1 (Central Europe)'),
        ('UTC+2', 'UTC+2 (Eastern Europe)'),
        ('UTC+3', 'UTC+3 (Moscow)'),
        ('UTC+4', 'UTC+4 (Dubai)'),
        ('UTC+5', 'UTC+5 (Pakistan)'),
        ('UTC+5:30', 'UTC+5:30 (India)'),
        ('UTC+6', 'UTC+6 (Bangladesh)'),
        ('UTC+7', 'UTC+7 (Thailand)'),
        ('UTC+8', 'UTC+8 (China, Singapore)'),
        ('UTC+9', 'UTC+9 (Japan, Korea)'),
        ('UTC+10', 'UTC+10 (Australia East)'),
        ('UTC+11', 'UTC+11 (Solomon Islands)'),
        ('UTC+12', 'UTC+12 (New Zealand)')
    ], validators=[Optional()])
    
    astrology_system = SelectField('Astrology System', choices=[
        ('western', 'Western Astrology'),
        ('vedic', 'Vedic Astrology')
    ], default='western')
    
    email_notifications = BooleanField('Receive daily horoscope emails', default=True)
    submit = SubmitField('Update Birth Information')

class MoodForm(FlaskForm):
    """Form for mood tracking and situation input"""
    mood_description = TextAreaField('How are you feeling today?', validators=[
        DataRequired(),
        Length(min=10, max=1000, message='Please describe your mood in 10-1000 characters')
    ], render_kw={'placeholder': 'Describe your current mood, feelings, or emotional state...'})
    
    current_situation = TextAreaField('What\'s on your mind?', validators=[
        Optional(),
        Length(max=2000, message='Please keep your situation description under 2000 characters')
    ], render_kw={'placeholder': 'Share any specific situations, challenges, or decisions you\'re facing...'})
    
    stress_level = SelectField('Stress Level', choices=[
        (1, '1 - Very Calm'),
        (2, '2 - Calm'),
        (3, '3 - Slightly Stressed'),
        (4, '4 - Moderately Stressed'),
        (5, '5 - Neutral'),
        (6, '6 - Somewhat Stressed'),
        (7, '7 - Stressed'),
        (8, '8 - Very Stressed'),
        (9, '9 - Extremely Stressed'),
        (10, '10 - Overwhelmed')
    ], coerce=int, validators=[DataRequired()])
    
    emotions = SelectField('Primary Emotion', choices=[
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('anxious', 'Anxious'),
        ('excited', 'Excited'),
        ('frustrated', 'Frustrated'),
        ('confused', 'Confused'),
        ('hopeful', 'Hopeful'),
        ('worried', 'Worried'),
        ('content', 'Content'),
        ('angry', 'Angry'),
        ('peaceful', 'Peaceful'),
        ('overwhelmed', 'Overwhelmed'),
        ('inspired', 'Inspired'),
        ('lonely', 'Lonely'),
        ('grateful', 'Grateful'),
        ('uncertain', 'Uncertain')
    ], validators=[Optional()])
    
    submit = SubmitField('Get Astrological Guidance')

class FeedbackForm(FlaskForm):
    """Form for rating and providing feedback on horoscope readings"""
    rating = SelectField('How accurate was this reading?', choices=[
        (5, '5 - Very Accurate'),
        (4, '4 - Mostly Accurate'),
        (3, '3 - Somewhat Accurate'),
        (2, '2 - Not Very Accurate'),
        (1, '1 - Not Accurate At All')
    ], coerce=int, validators=[DataRequired()])
    
    feedback = TextAreaField('Additional Feedback (Optional)', validators=[
        Optional(),
        Length(max=500, message='Feedback must be under 500 characters')
    ], render_kw={'placeholder': 'Share your thoughts on the reading...'})
    
    was_helpful = BooleanField('This reading was helpful to me')
    submit = SubmitField('Submit Feedback')

class ContactForm(FlaskForm):
    """Contact/support form"""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = SelectField('Subject', choices=[
        ('general', 'General Inquiry'),
        ('technical', 'Technical Issue'),
        ('billing', 'Billing Question'),
        ('feedback', 'Feedback'),
        ('feature_request', 'Feature Request'),
        ('privacy', 'Privacy Concern')
    ], validators=[DataRequired()])
    
    message = TextAreaField('Message', validators=[
        DataRequired(),
        Length(min=20, max=2000, message='Message must be between 20-2000 characters')
    ])
    
    submit = SubmitField('Send Message')

class PreferencesForm(FlaskForm):
    """User preferences form"""
    # Theme preferences
    theme_preference = SelectField('Theme Preference', choices=[
        ('auto', 'Auto (System Default)'),
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme')
    ], default='auto')
    
    # Email notification preference
    email_notifications = BooleanField('Receive daily horoscope emails')
    
    # Current location preferences
    use_current_location = BooleanField('Use current location for location-dependent features (houses, rising sign)')
    
    # Current location fields (matching birth location structure)
    current_country = SelectField('Current Country', choices=[
        ('', 'Select Country'),
        ('AF', 'Afghanistan'),
        ('AL', 'Albania'),
        ('DZ', 'Algeria'),
        ('AD', 'Andorra'),
        ('AO', 'Angola'),
        ('AG', 'Antigua and Barbuda'),
        ('AR', 'Argentina'),
        ('AM', 'Armenia'),
        ('AU', 'Australia'),
        ('AT', 'Austria'),
        ('AZ', 'Azerbaijan'),
        ('BS', 'Bahamas'),
        ('BH', 'Bahrain'),
        ('BD', 'Bangladesh'),
        ('BB', 'Barbados'),
        ('BY', 'Belarus'),
        ('BE', 'Belgium'),
        ('BZ', 'Belize'),
        ('BJ', 'Benin'),
        ('BT', 'Bhutan'),
        ('BO', 'Bolivia'),
        ('BA', 'Bosnia and Herzegovina'),
        ('BW', 'Botswana'),
        ('BR', 'Brazil'),
        ('BN', 'Brunei'),
        ('BG', 'Bulgaria'),
        ('BF', 'Burkina Faso'),
        ('BI', 'Burundi'),
        ('CV', 'Cabo Verde'),
        ('KH', 'Cambodia'),
        ('CM', 'Cameroon'),
        ('CA', 'Canada'),
        ('CF', 'Central African Republic'),
        ('TD', 'Chad'),
        ('CL', 'Chile'),
        ('CN', 'China'),
        ('CO', 'Colombia'),
        ('KM', 'Comoros'),
        ('CG', 'Republic of the Congo'),
        ('CD', 'Democratic Republic of the Congo'),
        ('CR', 'Costa Rica'),
        ('CI', "Côte d'Ivoire"),
        ('HR', 'Croatia'),
        ('CU', 'Cuba'),
        ('CY', 'Cyprus'),
        ('CZ', 'Czech Republic'),
        ('DK', 'Denmark'),
        ('DJ', 'Djibouti'),
        ('DM', 'Dominica'),
        ('DO', 'Dominican Republic'),
        ('EC', 'Ecuador'),
        ('EG', 'Egypt'),
        ('SV', 'El Salvador'),
        ('GQ', 'Equatorial Guinea'),
        ('ER', 'Eritrea'),
        ('EE', 'Estonia'),
        ('SZ', 'Eswatini'),
        ('ET', 'Ethiopia'),
        ('FJ', 'Fiji'),
        ('FI', 'Finland'),
        ('FR', 'France'),
        ('GA', 'Gabon'),
        ('GM', 'Gambia'),
        ('GE', 'Georgia'),
        ('DE', 'Germany'),
        ('GH', 'Ghana'),
        ('GR', 'Greece'),
        ('GD', 'Grenada'),
        ('GT', 'Guatemala'),
        ('GN', 'Guinea'),
        ('GW', 'Guinea-Bissau'),
        ('GY', 'Guyana'),
        ('HT', 'Haiti'),
        ('HN', 'Honduras'),
        ('HU', 'Hungary'),
        ('IS', 'Iceland'),
        ('IN', 'India'),
        ('ID', 'Indonesia'),
        ('IR', 'Iran'),
        ('IQ', 'Iraq'),
        ('IE', 'Ireland'),
        ('IL', 'Israel'),
        ('IT', 'Italy'),
        ('JM', 'Jamaica'),
        ('JP', 'Japan'),
        ('JO', 'Jordan'),
        ('KZ', 'Kazakhstan'),
        ('KE', 'Kenya'),
        ('KI', 'Kiribati'),
        ('KP', 'North Korea'),
        ('KR', 'South Korea'),
        ('KW', 'Kuwait'),
        ('KG', 'Kyrgyzstan'),
        ('LA', 'Laos'),
        ('LV', 'Latvia'),
        ('LB', 'Lebanon'),
        ('LS', 'Lesotho'),
        ('LR', 'Liberia'),
        ('LY', 'Libya'),
        ('LI', 'Liechtenstein'),
        ('LT', 'Lithuania'),
        ('LU', 'Luxembourg'),
        ('MG', 'Madagascar'),
        ('MW', 'Malawi'),
        ('MY', 'Malaysia'),
        ('MV', 'Maldives'),
        ('ML', 'Mali'),
        ('MT', 'Malta'),
        ('MH', 'Marshall Islands'),
        ('MR', 'Mauritania'),
        ('MU', 'Mauritius'),
        ('MX', 'Mexico'),
        ('FM', 'Micronesia'),
        ('MD', 'Moldova'),
        ('MC', 'Monaco'),
        ('MN', 'Mongolia'),
        ('ME', 'Montenegro'),
        ('MA', 'Morocco'),
        ('MZ', 'Mozambique'),
        ('MM', 'Myanmar'),
        ('NA', 'Namibia'),
        ('NR', 'Nauru'),
        ('NP', 'Nepal'),
        ('NL', 'Netherlands'),
        ('NZ', 'New Zealand'),
        ('NI', 'Nicaragua'),
        ('NE', 'Niger'),
        ('NG', 'Nigeria'),
        ('MK', 'North Macedonia'),
        ('NO', 'Norway'),
        ('OM', 'Oman'),
        ('PK', 'Pakistan'),
        ('PW', 'Palau'),
        ('PA', 'Panama'),
        ('PG', 'Papua New Guinea'),
        ('PY', 'Paraguay'),
        ('PE', 'Peru'),
        ('PH', 'Philippines'),
        ('PL', 'Poland'),
        ('PT', 'Portugal'),
        ('QA', 'Qatar'),
        ('RO', 'Romania'),
        ('RU', 'Russia'),
        ('RW', 'Rwanda'),
        ('KN', 'Saint Kitts and Nevis'),
        ('LC', 'Saint Lucia'),
        ('VC', 'Saint Vincent and the Grenadines'),
        ('WS', 'Samoa'),
        ('SM', 'San Marino'),
        ('ST', 'Sao Tome and Principe'),
        ('SA', 'Saudi Arabia'),
        ('SN', 'Senegal'),
        ('RS', 'Serbia'),
        ('SC', 'Seychelles'),
        ('SL', 'Sierra Leone'),
        ('SG', 'Singapore'),
        ('SK', 'Slovakia'),
        ('SI', 'Slovenia'),
        ('SB', 'Solomon Islands'),
        ('SO', 'Somalia'),
        ('ZA', 'South Africa'),
        ('SS', 'South Sudan'),
        ('ES', 'Spain'),
        ('LK', 'Sri Lanka'),
        ('SD', 'Sudan'),
        ('SR', 'Suriname'),
        ('SE', 'Sweden'),
        ('CH', 'Switzerland'),
        ('SY', 'Syria'),
        ('TW', 'Taiwan'),
        ('TJ', 'Tajikistan'),
        ('TZ', 'Tanzania'),
        ('TH', 'Thailand'),
        ('TL', 'Timor-Leste'),
        ('TG', 'Togo'),
        ('TO', 'Tonga'),
        ('TT', 'Trinidad and Tobago'),
        ('TN', 'Tunisia'),
        ('TR', 'Turkey'),
        ('TM', 'Turkmenistan'),
        ('TV', 'Tuvalu'),
        ('UG', 'Uganda'),
        ('UA', 'Ukraine'),
        ('AE', 'United Arab Emirates'),
        ('GB', 'United Kingdom'),
        ('US', 'United States'),
        ('UY', 'Uruguay'),
        ('UZ', 'Uzbekistan'),
        ('VU', 'Vanuatu'),
        ('VA', 'Vatican City'),
        ('VE', 'Venezuela'),
        ('VN', 'Vietnam'),
        ('YE', 'Yemen'),
        ('ZM', 'Zambia'),
        ('ZW', 'Zimbabwe')
    ], validators=[Optional()])
    
    current_region = StringField('State/Province/Region', validators=[
        Optional(),
        Length(max=100, message='Region name too long')
    ], render_kw={'placeholder': 'Enter state, province, or region (if applicable)'})
    
    current_city = StringField('City', validators=[
        Optional(), 
        Length(min=2, max=100, message='Please enter a valid city name')
    ], render_kw={'placeholder': 'Enter your current city'})
    
    current_timezone = SelectField('Current Timezone', choices=[
        ('', 'Select Timezone'),
        ('UTC-12', 'UTC-12 (Baker Island)'),
        ('UTC-11', 'UTC-11 (American Samoa)'),
        ('UTC-10', 'UTC-10 (Hawaii)'),
        ('UTC-9', 'UTC-9 (Alaska)'),
        ('UTC-8', 'UTC-8 (Pacific Time)'),
        ('UTC-7', 'UTC-7 (Mountain Time)'),
        ('UTC-6', 'UTC-6 (Central Time)'),
        ('UTC-5', 'UTC-5 (Eastern Time)'),
        ('UTC-4', 'UTC-4 (Atlantic Time)'),
        ('UTC-3', 'UTC-3 (Argentina)'),
        ('UTC-2', 'UTC-2 (South Georgia)'),
        ('UTC-1', 'UTC-1 (Azores)'),
        ('UTC+0', 'UTC+0 (London, GMT)'),
        ('UTC+1', 'UTC+1 (Central Europe)'),
        ('UTC+2', 'UTC+2 (Eastern Europe)'),
        ('UTC+3', 'UTC+3 (Moscow)'),
        ('UTC+4', 'UTC+4 (Dubai)'),
        ('UTC+5', 'UTC+5 (Pakistan)'),
        ('UTC+5:30', 'UTC+5:30 (India)'),
        ('UTC+6', 'UTC+6 (Bangladesh)'),
        ('UTC+7', 'UTC+7 (Thailand)'),
        ('UTC+8', 'UTC+8 (China, Singapore)'),
        ('UTC+9', 'UTC+9 (Japan, Korea)'),
        ('UTC+10', 'UTC+10 (Australia East)'),
        ('UTC+11', 'UTC+11 (Solomon Islands)'),
        ('UTC+12', 'UTC+12 (New Zealand)')
    ], validators=[Optional()])
    
    submit = SubmitField('Update Preferences')