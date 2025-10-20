# AI-Powered Astrology Platform

A comprehensive web application that provides accurate, real-time astrological calculations with AI-powered personalized horoscopes. Built with precision astronomical data from Swiss Ephemeris and enhanced with intelligent content generation.

## Features

- **Real-Time Astronomical Data**: Live calculations using Kerykeion and Swiss Ephemeris
- **Personalized Daily Horoscopes**: AI-generated content based on actual planetary positions
- **Accurate Retrograde Detection**: Real-time tracking of planetary retrogrades
- **Live Moon Phase Calculations**: Precise lunar phase determination using Sun-Moon angles
- **Professional Natal Charts**: High-quality birth chart generation and visualization
- **Data Validation System**: Comprehensive verification of astronomical accuracy
- **User Authentication**: Secure login/registration with session management
- **Enhanced Dashboard**: Intuitive interface with mood tracking and cosmic insights

## Technology Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite with optimized schema
- **Astronomical Engine**: Kerykeion + Swiss Ephemeris for precision calculations
- **AI Integration**: OpenAI GPT-4o-mini with astronomical data validation
- **Frontend**: HTML5, CSS3, JavaScript with Bootstrap 5
- **Chart Generation**: Professional-grade natal chart visualization
- **Data Validation**: Real-time verification of astronomical accuracy
- **Calculation System**: Enhanced Calculator (★★★★★) - commercially free

## Installation

1. Clone the repository
2. Create and activate virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables in `.env` file (see Configuration section)
5. Initialize the database:
   ```bash
   python create_db.py
   ```
6. Run the application:
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Configuration

Create a `.env` file with the following variables:
```env
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=sqlite:///horoscope_app.db
FLASK_ENV=development
```

### OpenAI API Setup
1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add it to your `.env` file
3. The system uses GPT-4o-mini for cost-effective, high-quality horoscope generation

## Project Structure

```
/
├── app.py                    # Main Flask application with routes
├── ai_integration.py         # AI horoscope generation with data validation
├── enhanced_calculator.py    # Primary astronomical calculation engine (★★★★★)
├── kerykeion_chart.py       # Professional natal chart generation
├── models.py                # Database models and schema
├── forms.py                 # WTForms for user input validation
├── auth.py                  # Authentication and user management
├── config.py                # Application configuration
├── create_db.py             # Database initialization
├── static/                  # CSS, JavaScript, images
├── templates/               # Jinja2 HTML templates
│   ├── dashboard.html       # Enhanced user dashboard
│   ├── natal_chart.html     # Natal chart display
│   └── auth/               # Authentication templates
├── charts_output/          # Generated natal chart images
├── instance/               # Database and instance files
└── .env                    # Environment configuration (create this)
```

## Astronomical Accuracy

This platform prioritizes astronomical precision:

- **Swiss Ephemeris Integration**: Professional-grade planetary calculations
- **Real-Time Data**: Live planetary positions, not static databases
- **Retrograde Detection**: Accurate tracking of planetary retrograde periods
- **Moon Phase Calculations**: Precise lunar phase determination using celestial mechanics
- **Data Validation System**: Comprehensive verification ensuring no fallback or fake data
- **Timezone Handling**: Proper UTC conversion and local time calculations

### Data Sources
- **Primary**: Kerykeion library with Swiss Ephemeris
- **Fallback Detection**: System identifies and flags any non-real data (marked with .5 endings)
- **Validation**: 4-point verification system ensures astronomical accuracy

## AI Integration

The AI system is designed to work with real astronomical data:

- **GPT-4o-mini**: Cost-effective, high-quality text generation
- **Data-Grounded Prompts**: AI receives actual planetary positions and aspects
- **Validation Layer**: Prevents AI hallucinations about astronomical facts
- **Personalized Content**: Generated based on real birth chart data and current transits

## Data Protection

- **Password Security**: Bcrypt hashing with salt
- **Session Management**: Secure Flask-Login implementation
- **Data Encryption**: Personal information protected in database
- **HTTPS Ready**: SSL/TLS support for production deployment
- **Privacy Focused**: Minimal data collection, maximum security
- **GDPR Compliance**: European data protection standards

## Development Features

- **Clean Architecture**: Modular design with separated concerns
- **Comprehensive Testing**: Validated astronomical calculations
- **Error Handling**: Graceful fallbacks and user feedback
- **Performance Optimized**: Efficient database queries and caching
- **Documentation**: Extensive inline comments and technical docs
- **Maintainable Code**: Clear structure and consistent patterns

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with proper testing
4. Ensure astronomical accuracy for any calculation changes
5. Submit a pull request with detailed description

## License

This project is for educational and personal use. Commercial deployment requires review of Swiss Ephemeris licensing terms. Please ensure compliance with relevant data protection laws.

---

**Built with precision astronomical calculations and intelligent AI integration for the modern astrology enthusiast.**