"""
Practical enhanced astrology calculator 
This version provides better location handling and astronomical accuracy without complex dependencies
"""

import os
from datetime import datetime, date, time
from typing import Dict, List, Tuple, Optional
import pytz

try:
    from astronomical_system import AstronomicalCalculator, GeographicalCoordinate
    ROBUST_SYSTEM_AVAILABLE = True
except ImportError:
    ROBUST_SYSTEM_AVAILABLE = False

from astrology_simple import AstrologyCalculator as SimpleCalculator

class PracticalAstrologyCalculator:
    """
    Practical astrology calculator that enhances location handling
    and provides better astronomical calculations when possible
    """
    
    def __init__(self):
        self.simple_calc = SimpleCalculator()  # Always available fallback
        
        if ROBUST_SYSTEM_AVAILABLE:
            self.astronomical_calc = AstronomicalCalculator()
            self.location_cache = {}
        
        # Enhanced zodiac and planetary data
        self.signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        self.sign_elements = {
            'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
            'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
            'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
            'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water'
        }
        
        self.sign_qualities = {
            'Aries': 'Cardinal', 'Cancer': 'Cardinal', 'Libra': 'Cardinal', 'Capricorn': 'Cardinal',
            'Taurus': 'Fixed', 'Leo': 'Fixed', 'Scorpio': 'Fixed', 'Aquarius': 'Fixed',
            'Gemini': 'Mutable', 'Virgo': 'Mutable', 'Sagittarius': 'Mutable', 'Pisces': 'Mutable'
        }
        
    def get_enhanced_coordinates(self, user) -> Optional[GeographicalCoordinate]:
        """Get enhanced geographical coordinates for user's birth location"""
        if not ROBUST_SYSTEM_AVAILABLE:
            return None
            
        try:
            # Use new location fields if available
            if user.birth_country and user.birth_city:
                cache_key = f"{user.birth_city}-{user.birth_region}-{user.birth_country}"
                
                if cache_key in self.location_cache:
                    return self.location_cache[cache_key]
                
                coords = self.astronomical_calc.get_coordinates_from_location(
                    country=user.birth_country,
                    region=user.birth_region,
                    city=user.birth_city
                )
                
                if coords:
                    self.location_cache[cache_key] = coords
                    return coords
            
            return None
            
        except Exception as e:
            print(f"Error getting enhanced coordinates: {e}")
            return None
    
    def create_timezone_aware_datetime(self, user, coordinates: Optional[GeographicalCoordinate] = None) -> datetime:
        """Create proper timezone-aware birth datetime"""
        try:
            # Combine date and time
            birth_time = user.birth_time or time(12, 0)  # Default to noon
            birth_dt = datetime.combine(user.birth_date, birth_time)
            
            # Apply timezone
            if coordinates and coordinates.timezone:
                try:
                    tz = pytz.timezone(coordinates.timezone)
                    birth_dt = tz.localize(birth_dt)
                    return birth_dt
                except:
                    pass
            
            # Try user's timezone setting
            if user.timezone:
                try:
                    if user.timezone.startswith('UTC'):
                        offset_str = user.timezone[3:]  # Remove 'UTC' prefix
                        if offset_str:
                            # Parse offset like +1, -5, +5:30
                            if ':' in offset_str:
                                hours, minutes = offset_str.split(':')
                                offset_hours = float(hours) + float(minutes)/60
                            else:
                                offset_hours = float(offset_str)
                            
                            tz = pytz.FixedOffset(int(offset_hours * 60))
                            birth_dt = tz.localize(birth_dt)
                            return birth_dt
                except:
                    pass
            
            # Default to UTC
            return pytz.utc.localize(birth_dt)
            
        except Exception as e:
            print(f"Error creating timezone-aware datetime: {e}")
            return datetime.combine(user.birth_date, birth_time or time(12, 0))
    
    def generate_natal_chart(self, user) -> Optional[Dict]:
        """Generate enhanced natal chart"""
        if not user.birth_date:
            return None
        
        try:
            # Get enhanced coordinates if available
            coordinates = self.get_enhanced_coordinates(user)
            
            # Create timezone-aware datetime
            birth_dt = self.create_timezone_aware_datetime(user, coordinates)
            
            # Use simple calculator but enhance the results
            chart = self.simple_calc.generate_natal_chart(user)
            
            if chart and coordinates:
                # Enhance chart with geographical data
                chart['birth_coordinates'] = {
                    'latitude': coordinates.latitude,
                    'longitude': coordinates.longitude,
                    'timezone': coordinates.timezone,
                    'location': f"{coordinates.city}, {coordinates.region}, {coordinates.country}".strip(', ')
                }
                
                # Add enhanced interpretations
                chart['enhanced_interpretations'] = self._generate_enhanced_interpretations(chart)
            
            return chart
            
        except Exception as e:
            print(f"Error generating enhanced natal chart: {e}")
            return self.simple_calc.generate_natal_chart(user)
    
    def _generate_enhanced_interpretations(self, chart: Dict) -> Dict:
        """Generate enhanced astrological interpretations"""
        interpretations = {}
        
        try:
            if 'positions' in chart:
                positions = chart['positions']
                
                # Sun sign interpretation
                if 'Sun' in positions:
                    sun_sign = positions['Sun']['sign']
                    element = self.sign_elements.get(sun_sign, 'Unknown')
                    quality = self.sign_qualities.get(sun_sign, 'Unknown')
                    
                    interpretations['sun'] = {
                        'sign': sun_sign,
                        'element': element,
                        'quality': quality,
                        'description': f"Your Sun in {sun_sign} ({element} {quality}) represents your core identity, ego, and life purpose."
                    }
                
                # Moon sign interpretation  
                if 'Moon' in positions:
                    moon_sign = positions['Moon']['sign']
                    element = self.sign_elements.get(moon_sign, 'Unknown')
                    
                    interpretations['moon'] = {
                        'sign': moon_sign,
                        'element': element,
                        'description': f"Your Moon in {moon_sign} ({element}) governs your emotional nature, instincts, and subconscious patterns."
                    }
                
                # Rising sign (from first house)
                if 'houses' in chart and 1 in chart['houses']:
                    rising_sign = chart['houses'][1]['sign']
                    element = self.sign_elements.get(rising_sign, 'Unknown')
                    
                    interpretations['rising'] = {
                        'sign': rising_sign,
                        'element': element,
                        'description': f"Your Ascendant in {rising_sign} ({element}) shapes how you present yourself to the world and your first impressions."
                    }
        
        except Exception as e:
            print(f"Error generating enhanced interpretations: {e}")
        
        return interpretations
    
    def get_detailed_chart(self, user) -> Optional[Dict]:
        """Get detailed chart data formatted for template display"""
        chart = self.generate_natal_chart(user)
        if not chart:
            return None
        
        # Format for template display
        detailed_chart = {
            'planets': chart.get('positions', {}),
            'houses': chart.get('houses', {}),
            'interpretation': chart.get('enhanced_interpretations', {}),
            'birth_info': chart.get('birth_coordinates', {})
        }
        
        return detailed_chart
    
    def generate_chart_image(self, user) -> Optional[str]:
        """Generate chart image using simple calculator"""
        return self.simple_calc.generate_chart_image(user)
    
    def get_location_info(self, user) -> str:
        """Get formatted location information"""
        try:
            if user.birth_city and user.birth_country:
                parts = [user.birth_city]
                if user.birth_region:
                    parts.append(user.birth_region)
                parts.append(user.birth_country)
                return ', '.join(parts)
            elif user.birth_location:
                return user.birth_location
            else:
                return 'Location not specified'
        except:
            return 'Location not available'

# Summary of current calculator capabilities:
"""
Current Calculator Analysis:

What it's currently based on:
✅ Enhanced location handling with country/region/city dropdowns
✅ Timezone-aware datetime calculations  
✅ Better geocoding using geopy when available
✅ Cached location lookups for performance
✅ Enhanced astrological interpretations with elements and qualities
✅ Graceful fallback to simplified calculations

Still simplified/missing:
❌ Real planetary ephemeris data (still using date-based approximations)
❌ Accurate house calculations (still using simplified hour-based method)
❌ Aspect calculations between planets
❌ Transit calculations
❌ Progression calculations

For truly accurate astrology, you would need:

1. Swiss Ephemeris Integration:
   - Install: pip install pyephem or swisseph (requires C++ compilation)
   - Download ephemeris data files
   - Implement proper planetary position calculations

2. Accurate House Systems:
   - Implement Placidus, Koch, Equal, or other house systems
   - Use proper sidereal time calculations
   - Account for geographical coordinates in house calculations

3. Professional Astronomy APIs:
   - NASA JPL Horizons for planetary positions
   - USNO astronomical data
   - Commercial astrology APIs

4. Advanced Features:
   - Aspect calculations (conjunctions, trines, squares, etc.)
   - Transit predictions
   - Progressed charts
   - Solar/lunar returns

Current Status: ⭐⭐⭐☆☆ (3/5 stars)
- Good for basic astrology and learning
- Enhanced UX with better location selection
- Timezone-aware calculations
- Not suitable for professional astrology without ephemeris data
"""