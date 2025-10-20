import swisseph as swe
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle
import numpy as np
from datetime import datetime, date, time
import pytz
import io
import base64
from typing import Dict, List, Tuple, Optional

class AstrologyCalculator:
    """Handles astrological calculations using Swiss Ephemeris"""
    
    def __init__(self):
        # Set ephemeris path (you may need to download ephemeris files)
        swe.set_ephe_path('./ephemeris')  # Create this directory and download files
        
        # Planet constants
        self.planets = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS,
            'Mars': swe.MARS,
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN,
            'Uranus': swe.URANUS,
            'Neptune': swe.NEPTUNE,
            'Pluto': swe.PLUTO,
            'North Node': swe.MEAN_NODE,
            'Chiron': swe.CHIRON
        }
        
        # Zodiac signs
        self.signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        # Houses (Placidus system)
        self.house_meanings = {
            1: "Self, Identity, Appearance",
            2: "Money, Values, Possessions",
            3: "Communication, Siblings, Short trips",
            4: "Home, Family, Roots",
            5: "Creativity, Romance, Children",
            6: "Health, Work, Daily routine",
            7: "Partnerships, Marriage, Open enemies",
            8: "Transformation, Shared resources, Death/rebirth",
            9: "Philosophy, Higher learning, Long journeys",
            10: "Career, Reputation, Authority",
            11: "Friends, Groups, Hopes and wishes",
            12: "Spirituality, Hidden things, Subconscious"
        }
    
    def julian_day(self, birth_date: date, birth_time: time, timezone_str: str) -> float:
        """Convert birth date/time to Julian Day Number"""
        # Convert to UTC
        tz = pytz.timezone(timezone_str.replace('UTC', 'Etc/GMT'))
        dt = datetime.combine(birth_date, birth_time)
        dt_utc = tz.localize(dt).astimezone(pytz.UTC)
        
        return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                         dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
    
    def get_coordinates(self, location: str) -> Tuple[float, float]:
        """Get latitude and longitude for a location (simplified - in production use geocoding API)"""
        # This is a simplified version - you should use a real geocoding service
        # For now, return coordinates for major cities
        coordinates = {
            'new york': (40.7128, -74.0060),
            'los angeles': (34.0522, -118.2437),
            'chicago': (41.8781, -87.6298),
            'london': (51.5074, -0.1278),
            'paris': (48.8566, 2.3522),
            'tokyo': (35.6762, 139.6503),
            'sydney': (-33.8688, 151.2093),
            'mumbai': (19.0760, 72.8777),
            'delhi': (28.7041, 77.1025)
        }
        
        location_lower = location.lower()
        for city, coords in coordinates.items():
            if city in location_lower:
                return coords
        
        # Default to London if location not found
        return (51.5074, -0.1278)
    
    def calculate_planetary_positions(self, jd: float) -> Dict[str, Dict]:
        """Calculate positions of all planets for given Julian Day"""
        positions = {}
        
        for planet_name, planet_id in self.planets.items():
            try:
                result = swe.calc_ut(jd, planet_id)
                longitude = result[0]
                
                # Convert to sign and degree
                sign_num = int(longitude // 30)
                degree = longitude % 30
                
                positions[planet_name] = {
                    'longitude': longitude,
                    'sign': self.signs[sign_num],
                    'degree': degree,
                    'sign_degree': f"{int(degree)}°{int((degree % 1) * 60):02d}'",
                    'retrograde': result[3] < 0 if len(result) > 3 else False
                }
            except Exception as e:
                print(f"Error calculating {planet_name}: {e}")
                continue
        
        return positions
    
    def calculate_houses(self, jd: float, lat: float, lon: float) -> Dict[int, Dict]:
        """Calculate house cusps using Placidus system"""
        try:
            houses = swe.houses(jd, lat, lon, b'P')  # Placidus system
            house_cusps = houses[0]
            
            house_data = {}
            for i, cusp in enumerate(house_cusps[:12], 1):
                sign_num = int(cusp // 30)
                degree = cusp % 30
                
                house_data[i] = {
                    'cusp': cusp,
                    'sign': self.signs[sign_num],
                    'degree': degree,
                    'meaning': self.house_meanings[i]
                }
            
            return house_data
        except Exception as e:
            print(f"Error calculating houses: {e}")
            return {}
    
    def calculate_aspects(self, positions: Dict[str, Dict]) -> List[Dict]:
        """Calculate major aspects between planets"""
        aspects = []
        aspect_orbs = {
            'conjunction': (0, 8),
            'opposition': (180, 8),
            'trine': (120, 6),
            'square': (90, 6),
            'sextile': (60, 4),
            'quincunx': (150, 3)
        }
        
        planet_list = list(positions.keys())
        
        for i, planet1 in enumerate(planet_list):
            for planet2 in planet_list[i+1:]:
                if planet1 == planet2:
                    continue
                
                # Calculate angular distance
                long1 = positions[planet1]['longitude']
                long2 = positions[planet2]['longitude']
                
                diff = abs(long1 - long2)
                if diff > 180:
                    diff = 360 - diff
                
                # Check for aspects
                for aspect_name, (angle, orb) in aspect_orbs.items():
                    if abs(diff - angle) <= orb:
                        aspects.append({
                            'planet1': planet1,
                            'planet2': planet2,
                            'aspect': aspect_name,
                            'angle': diff,
                            'orb': abs(diff - angle),
                            'exact': abs(diff - angle) < 1
                        })
                        break
        
        return aspects
    
    def generate_natal_chart(self, user) -> Optional[str]:
        """Generate natal chart data for user"""
        if not user.has_complete_birth_info():
            return None
        
        try:
            # Get coordinates
            lat, lon = self.get_coordinates(user.birth_location)
            
            # Calculate Julian Day
            jd = self.julian_day(user.birth_date, user.birth_time, user.timezone)
            
            # Calculate positions and houses
            positions = self.calculate_planetary_positions(jd)
            houses = self.calculate_houses(jd, lat, lon)
            aspects = self.calculate_aspects(positions)
            
            return {
                'positions': positions,
                'houses': houses,
                'aspects': aspects,
                'coordinates': {'latitude': lat, 'longitude': lon}
            }
        
        except Exception as e:
            print(f"Error generating natal chart: {e}")
            return None
    
    def get_detailed_chart(self, user) -> Optional[Dict]:
        """Get detailed chart interpretation"""
        chart_data = self.generate_natal_chart(user)
        if not chart_data:
            return None
        
        # Add interpretations
        interpretations = self.generate_interpretations(chart_data)
        chart_data['interpretations'] = interpretations
        
        return chart_data
    
    def generate_interpretations(self, chart_data: Dict) -> Dict:
        """Generate basic interpretations for chart elements"""
        interpretations = {
            'sun_sign': self.interpret_sun_sign(chart_data['positions']),
            'moon_sign': self.interpret_moon_sign(chart_data['positions']),
            'rising_sign': self.interpret_rising_sign(chart_data['houses']),
            'major_aspects': self.interpret_major_aspects(chart_data['aspects'])
        }
        
        return interpretations
    
    def interpret_sun_sign(self, positions: Dict) -> str:
        """Basic Sun sign interpretation"""
        if 'Sun' not in positions:
            return "Sun position not available"
        
        sign = positions['Sun']['sign']
        interpretations = {
            'Aries': "Bold, pioneering, and energetic. Natural leader with strong initiative.",
            'Taurus': "Stable, practical, and determined. Values security and comfort.",
            'Gemini': "Curious, adaptable, and communicative. Loves learning and variety.",
            'Cancer': "Nurturing, intuitive, and emotional. Strong connection to home and family.",
            'Leo': "Creative, confident, and generous. Natural performer with strong presence.",
            'Virgo': "Analytical, helpful, and detail-oriented. Strives for perfection and service.",
            'Libra': "Harmonious, diplomatic, and artistic. Seeks balance and beautiful relationships.",
            'Scorpio': "Intense, transformative, and mysterious. Deep emotional and psychic nature.",
            'Sagittarius': "Adventurous, philosophical, and optimistic. Loves freedom and exploration.",
            'Capricorn': "Ambitious, disciplined, and practical. Strong drive for achievement and status.",
            'Aquarius': "Independent, innovative, and humanitarian. Unique perspective and progressive ideals.",
            'Pisces': "Compassionate, intuitive, and artistic. Deep spiritual and emotional sensitivity."
        }
        
        return interpretations.get(sign, "Interpretation not available")
    
    def interpret_moon_sign(self, positions: Dict) -> str:
        """Basic Moon sign interpretation"""
        if 'Moon' not in positions:
            return "Moon position not available"
        
        sign = positions['Moon']['sign']
        # Similar interpretation logic for Moon signs (emotional nature)
        return f"Moon in {sign}: Your emotional nature and inner self"
    
    def interpret_rising_sign(self, houses: Dict) -> str:
        """Basic Rising sign interpretation"""
        if 1 not in houses:
            return "Rising sign not available"
        
        sign = houses[1]['sign']
        return f"Rising sign {sign}: How you present yourself to the world"
    
    def interpret_major_aspects(self, aspects: List[Dict]) -> List[str]:
        """Interpret major aspects"""
        interpretations = []
        
        for aspect in aspects[:5]:  # Top 5 aspects
            planet1 = aspect['planet1']
            planet2 = aspect['planet2']
            aspect_type = aspect['aspect']
            
            interpretation = f"{planet1} {aspect_type} {planet2}: "
            
            if aspect_type == 'conjunction':
                interpretation += "Energies blend and amplify each other"
            elif aspect_type == 'opposition':
                interpretation += "Tension requiring balance and integration"
            elif aspect_type == 'trine':
                interpretation += "Harmonious flow of energy"
            elif aspect_type == 'square':
                interpretation += "Dynamic tension motivating growth"
            elif aspect_type == 'sextile':
                interpretation += "Supportive opportunities for growth"
            
            interpretations.append(interpretation)
        
        return interpretations
    
    def generate_chart_image(self, user) -> Optional[str]:
        """Generate a visual representation of the natal chart"""
        chart_data = self.generate_natal_chart(user)
        if not chart_data:
            return None
        
        try:
            # Create matplotlib figure
            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            
            # Draw outer circle (zodiac)
            circle_outer = Circle((0, 0), 1, fill=False, linewidth=2)
            ax.add_patch(circle_outer)
            
            # Draw inner circle (houses)
            circle_inner = Circle((0, 0), 0.7, fill=False, linewidth=1)
            ax.add_patch(circle_inner)
            
            # Draw zodiac signs
            for i, sign in enumerate(self.signs):
                angle = i * 30 - 90  # Start from top (Aries)
                x = 0.85 * math.cos(math.radians(angle))
                y = 0.85 * math.sin(math.radians(angle))
                ax.text(x, y, sign[:3], ha='center', va='center', fontsize=10, weight='bold')
            
            # Draw planets
            colors = {
                'Sun': 'orange', 'Moon': 'lightblue', 'Mercury': 'gray',
                'Venus': 'pink', 'Mars': 'red', 'Jupiter': 'purple',
                'Saturn': 'brown', 'Uranus': 'cyan', 'Neptune': 'blue',
                'Pluto': 'darkred', 'North Node': 'green', 'Chiron': 'maroon'
            }
            
            for planet_name, position in chart_data['positions'].items():
                angle = position['longitude'] - 90  # Adjust for 0° Aries at top
                radius = 0.8
                x = radius * math.cos(math.radians(angle))
                y = radius * math.sin(math.radians(angle))
                
                color = colors.get(planet_name, 'black')
                ax.plot(x, y, 'o', color=color, markersize=8)
                
                # Planet symbol (simplified - use first letter)
                symbol = planet_name[0]
                ax.text(x, y, symbol, ha='center', va='center', color='white', 
                       fontsize=8, weight='bold')
            
            # Draw house cusps
            for house_num, house_data in chart_data['houses'].items():
                angle = house_data['cusp'] - 90
                x1 = 0.7 * math.cos(math.radians(angle))
                y1 = 0.7 * math.sin(math.radians(angle))
                x2 = 1.0 * math.cos(math.radians(angle))
                y2 = 1.0 * math.sin(math.radians(angle))
                
                ax.plot([x1, x2], [y1, y2], 'k-', linewidth=1)
                
                # House number
                x_text = 0.6 * math.cos(math.radians(angle + 15))
                y_text = 0.6 * math.sin(math.radians(angle + 15))
                ax.text(x_text, y_text, str(house_num), ha='center', va='center', 
                       fontsize=8, style='italic')
            
            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-1.2, 1.2)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title(f"Natal Chart - {user.get_full_name()}", fontsize=14, weight='bold')
            
            # Convert to base64 string
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            img_string = base64.b64encode(img_buffer.read()).decode()
            plt.close()
            
            return img_string
            
        except Exception as e:
            print(f"Error generating chart image: {e}")
            return None
    
    def get_current_transits(self, user) -> Optional[Dict]:
        """Get current planetary transits affecting user's chart"""
        if not user.has_complete_birth_info():
            return None
        
        # Get current planetary positions
        current_jd = swe.julday(datetime.now().year, datetime.now().month, 
                               datetime.now().day, datetime.now().hour)
        current_positions = self.calculate_planetary_positions(current_jd)
        
        # Get natal positions
        natal_chart = self.generate_natal_chart(user)
        if not natal_chart:
            return None
        
        natal_positions = natal_chart['positions']
        
        # Calculate transits (simplified)
        transits = []
        for transit_planet, transit_data in current_positions.items():
            for natal_planet, natal_data in natal_positions.items():
                # Check for major aspects
                diff = abs(transit_data['longitude'] - natal_data['longitude'])
                if diff > 180:
                    diff = 360 - diff
                
                # Major transit aspects
                if abs(diff - 0) < 3:  # Conjunction
                    transits.append({
                        'type': 'conjunction',
                        'transit_planet': transit_planet,
                        'natal_planet': natal_planet,
                        'orb': abs(diff - 0)
                    })
                elif abs(diff - 180) < 3:  # Opposition
                    transits.append({
                        'type': 'opposition',
                        'transit_planet': transit_planet,
                        'natal_planet': natal_planet,
                        'orb': abs(diff - 180)
                    })
        
        return {
            'current_positions': current_positions,
            'major_transits': transits
        }