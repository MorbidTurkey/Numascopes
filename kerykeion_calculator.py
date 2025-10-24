"""
Kerykeion-powered Professional Astrology Calculator
This module integrates the Kerykeion library for maximum astronomical accuracy
"""

from datetime import datetime, date, time
from typing import Dict, List, Tuple, Optional
import pytz

# Try to import Kerykeion
try:
    from kerykeion import AstrologicalSubject, KerykeionChartSVG
    from kerykeion.utilities import get_moon_phase
    KERYKEION_AVAILABLE = True
    print("✅ Kerykeion library available - using professional Swiss Ephemeris calculations")
except ImportError as e:
    KERYKEION_AVAILABLE = False
    print(f"⚠️ Kerykeion not available: {e}")

# Fallback to our professional calculator
try:
    from professional_astrology import ProfessionalAstrologyCalculator
    PROFESSIONAL_CALC_AVAILABLE = True
except ImportError:
    PROFESSIONAL_CALC_AVAILABLE = False

# Ultimate fallback
from astrology import AstrologyCalculator as SimpleCalculator

class KerykeionAstrologyCalculator:
    """
    Advanced astrology calculator using Kerykeion library
    Provides Swiss Ephemeris accuracy with graceful fallbacks
    """
    
    def __init__(self, house_system: str = 'Placidus'):
        self.house_system = house_system
        
        # Initialize available calculators
        if PROFESSIONAL_CALC_AVAILABLE:
            self.professional_calc = ProfessionalAstrologyCalculator(house_system)
        
        self.simple_calc = SimpleCalculator()
        
        # Kerykeion to internal mapping
        self.kerykeion_to_internal = {
            'Sun': 'sun',
            'Moon': 'moon', 
            'Mercury': 'mercury',
            'Venus': 'venus',
            'Mars': 'mars',
            'Jupiter': 'jupiter',
            'Saturn': 'saturn',
            'Uranus': 'uranus',
            'Neptune': 'neptune',
            'Pluto': 'pluto'
        }
        
        # Enhanced interpretations for modern planets
        self.modern_planet_meanings = {
            'uranus': 'Innovation, rebellion, sudden change, technology, freedom',
            'neptune': 'Spirituality, illusion, dreams, compassion, confusion',
            'pluto': 'Transformation, power, death/rebirth, hidden depths'
        }
    
    def create_astrological_subject(self, user) -> Optional['AstrologicalSubject']:
        """Create Kerykeion AstrologicalSubject from user data"""
        if not KERYKEION_AVAILABLE or not user.birth_date:
            return None
        
        try:
            # Get birth location
            if user.birth_city and user.birth_country:
                city = user.birth_city
                nation = user.birth_country
            elif user.birth_location:
                # Try to parse legacy location
                parts = user.birth_location.split(',')
                city = parts[0].strip() if parts else 'Unknown'
                nation = parts[-1].strip() if len(parts) > 1 else 'Unknown'
            else:
                return None
            
            # Get birth time or default to noon
            birth_time = user.birth_time or time(12, 0)
            
            # Create Kerykeion subject
            subject = AstrologicalSubject(
                name=user.get_full_name(),
                year=user.birth_date.year,
                month=user.birth_date.month,
                day=user.birth_date.day,
                hour=birth_time.hour,
                minute=birth_time.minute,
                city=city,
                nation=nation,
                timezone_str=user.timezone or 'UTC',
                house_system=self.house_system
            )
            
            return subject
            
        except Exception as e:
            print(f"Error creating AstrologicalSubject: {e}")
            return None
    
    def generate_natal_chart(self, user) -> Optional[Dict]:
        """Generate natal chart using Kerykeion if available, otherwise fallback"""
        if not user.birth_date:
            return None
        
        # Try Kerykeion first
        if KERYKEION_AVAILABLE:
            try:
                return self._generate_kerykeion_chart(user)
            except Exception as e:
                print(f"Kerykeion calculation failed: {e}")
        
        # Fallback to professional calculator
        if PROFESSIONAL_CALC_AVAILABLE:
            try:
                return self.professional_calc.generate_natal_chart(user)
            except Exception as e:
                print(f"Professional calculation failed: {e}")
        
        # Ultimate fallback
        return self.simple_calc.generate_natal_chart(user)
    
    def _generate_kerykeion_chart(self, user) -> Dict:
        """Generate chart using Kerykeion library"""
        subject = self.create_astrological_subject(user)
        if not subject:
            raise Exception("Could not create AstrologicalSubject")
        
        # Extract planetary positions
        planets = {}
        for kerykeion_name, internal_name in self.kerykeion_to_internal.items():
            if hasattr(subject, kerykeion_name.lower()):
                planet_data = getattr(subject, kerykeion_name.lower())
                
                planets[internal_name] = {
                    'longitude': planet_data['abs_pos'],
                    'sign': planet_data['sign'],
                    'degree': planet_data['pos'],
                    'sign_degree': f"{int(planet_data['pos'])}°{int((planet_data['pos'] % 1) * 60):02d}'",
                    'house': planet_data['house'],
                    'retrograde': planet_data.get('retrograde', False)
                }
        
        # Extract house information
        houses = {}
        for i in range(1, 13):
            house_attr = f"house_{i}"
            if hasattr(subject, house_attr):
                house_data = getattr(subject, house_attr)
                houses[i] = {
                    'cusp': house_data['abs_pos'],
                    'sign': house_data['sign'],
                    'degree': house_data['pos']
                }
        
        # Calculate aspects
        aspects = self._calculate_kerykeion_aspects(subject)
        
        # Get moon phase
        moon_phase = None
        try:
            moon_phase = get_moon_phase(
                year=user.birth_date.year,
                month=user.birth_date.month,
                day=user.birth_date.day
            )
        except:
            pass
        
        chart_data = {
            'planets': planets,
            'houses': houses,
            'aspects': aspects,
            'moon_phase': moon_phase,
            'birth_info': {
                'coordinates': {
                    'latitude': subject.lat,
                    'longitude': subject.lng,
                    'city': subject.city,
                    'nation': subject.nation
                },
                'timezone': subject.timezone_str,
                'house_system': self.house_system,
                'calculation_method': 'Kerykeion (Swiss Ephemeris)',
                'julian_day': subject.julian_day
            },
            'interpretations': self._generate_kerykeion_interpretations(planets, houses)
        }
        
        return chart_data
    
    def _calculate_kerykeion_aspects(self, subject: 'AstrologicalSubject') -> List[Dict]:
        """Calculate aspects using Kerykeion's aspect calculation"""
        aspects = []
        
        try:
            # Kerykeion provides aspect calculations
            if hasattr(subject, 'aspects_list'):
                for aspect in subject.aspects_list:
                    aspects.append({
                        'planet1': aspect['p1_name'].lower(),
                        'planet2': aspect['p2_name'].lower(),
                        'aspect': aspect['aspect'],
                        'orbit': aspect['orbit'],
                        'aspect_degrees': aspect['aspect_degrees'],
                        'color': aspect.get('color', '#000000')
                    })
        except Exception as e:
            print(f"Error calculating Kerykeion aspects: {e}")
        
        return aspects
    
    def _generate_kerykeion_interpretations(self, planets: Dict, houses: Dict) -> Dict:
        """Generate enhanced interpretations using Kerykeion data"""
        interpretations = {}
        
        try:
            # Enhanced interpretations with retrograde and modern planets
            for planet_name, planet_data in planets.items():
                retrograde_text = " (Retrograde)" if planet_data.get('retrograde') else ""
                
                # Get planet meaning
                if planet_name in ['uranus', 'neptune', 'pluto']:
                    meaning = self.modern_planet_meanings.get(planet_name, '')
                else:
                    meaning = self._get_traditional_meaning(planet_name)
                
                interpretations[planet_name] = {
                    'placement': f"{planet_name.title()} in {planet_data['sign']} in House {planet_data['house']}{retrograde_text}",
                    'sign': planet_data['sign'],
                    'house': planet_data['house'],
                    'retrograde': planet_data.get('retrograde', False),
                    'meaning': meaning,
                    'description': f"Your {planet_name} energy expresses through {planet_data['sign']} in the {planet_data['house']} house{' with retrograde introspection' if planet_data.get('retrograde') else ''}."
                }
            
            # Add house information
            if 1 in houses:
                interpretations['ascendant'] = {
                    'placement': f"Ascendant in {houses[1]['sign']}",
                    'sign': houses[1]['sign'],
                    'meaning': 'Your outer personality and how others perceive you',
                    'description': f"You present yourself to the world with {houses[1]['sign']} energy."
                }
            
            if 10 in houses:
                interpretations['midheaven'] = {
                    'placement': f"Midheaven in {houses[10]['sign']}",
                    'sign': houses[10]['sign'],
                    'meaning': 'Your career path and public reputation',
                    'description': f"Your professional identity is expressed through {houses[10]['sign']} qualities."
                }
                
        except Exception as e:
            print(f"Error generating Kerykeion interpretations: {e}")
        
        return interpretations
    
    def _get_traditional_meaning(self, planet: str) -> str:
        """Get traditional planetary meanings"""
        meanings = {
            'sun': 'Core identity, ego, life purpose, vitality',
            'moon': 'Emotions, instincts, subconscious, nurturing',
            'mercury': 'Communication, thinking, learning, short trips',
            'venus': 'Love, beauty, values, relationships, money',
            'mars': 'Action, desire, energy, conflict, motivation',
            'jupiter': 'Expansion, optimism, philosophy, higher learning',
            'saturn': 'Discipline, limitation, responsibility, structure'
        }
        return meanings.get(planet, '')
    
    def generate_chart_svg(self, user) -> Optional[str]:
        """Generate SVG chart using Kerykeion"""
        if not KERYKEION_AVAILABLE:
            return None
        
        try:
            subject = self.create_astrological_subject(user)
            if not subject:
                return None
            
            # Create SVG chart
            chart = KerykeionChartSVG(subject)
            svg_content = chart.make_svg()
            
            return svg_content
            
        except Exception as e:
            print(f"Error generating Kerykeion SVG: {e}")
            return None
    
    def get_detailed_chart(self, user) -> Optional[Dict]:
        """Get detailed chart data formatted for template display"""
        return self.generate_natal_chart(user)
    
    def generate_chart_image(self, user) -> Optional[str]:
        """Generate chart image - try SVG first, then fallback"""
        # Try Kerykeion SVG first
        svg = self.generate_chart_svg(user)
        if svg:
            # Could convert SVG to base64 image here if needed
            return svg
        
        # Fallback to existing image generation
        if PROFESSIONAL_CALC_AVAILABLE:
            return self.professional_calc.generate_chart_image(user)
        else:
            return self.simple_calc.generate_chart_image(user)

# Installation and setup instructions:
"""
KERYKEION SETUP INSTRUCTIONS:

Option 1: Install with Visual Studio Build Tools (Recommended)
1. Download and install Microsoft Visual Studio Build Tools:
   https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install with C++ build tools option
3. Run: pip install kerykeion

Option 2: Use pre-compiled wheels (if available)
1. Check if wheel available: pip install kerykeion --only-binary=all
2. If not available, use Option 1

Option 3: Docker approach (for production)
1. Use a Docker container with build tools pre-installed
2. Install kerykeion in the container

Current Status:
- ⚠️ Kerykeion requires C++ compilation (pyswisseph dependency)
- ✅ Graceful fallback system implemented
- ✅ Ready to use Kerykeion when compilation environment available
- ✅ Professional calculations available as intermediate solution

Benefits of Kerykeion integration:
- Swiss Ephemeris accuracy (most precise planetary positions)
- Modern planets (Uranus, Neptune, Pluto)
- Retrograde calculations
- Professional-grade aspect calculations
- SVG chart generation
- Built-in geocoding
- Active development and maintenance
"""