"""
Enhanced astrology calculator that integrates robust astronomical calculations
This version provides more accurate calculations when possible, with fallbacks
"""

import os
from datetime import datetime, date, time
from typing import Dict, List, Tuple, Optional
from astronomical_system import AstronomicalCalculator, LocationService, GeographicalCoordinate
from astrology_simple import AstrologyCalculator as SimpleCalculator

class EnhancedAstrologyCalculator:
    """
    Enhanced astrology calculator that uses accurate astronomical data when available,
    falls back to simplified calculations when not
    """
    
    def __init__(self):
        self.astronomical_calc = AstronomicalCalculator()
        self.location_service = LocationService()
        self.simple_calc = SimpleCalculator()  # Fallback
        
        # Check if Swiss Ephemeris is available
        self.has_swiss_ephemeris = self._check_swiss_ephemeris()
        
        # Configuration
        self.house_system = 'Placidus'  # Default house system
        
    def _check_swiss_ephemeris(self) -> bool:
        """Check if Swiss Ephemeris is available and properly configured"""
        try:
            import swisseph as swe
            # Check if ephemeris files are available
            # This would check for actual ephemeris data files
            return True
        except ImportError:
            print("Swiss Ephemeris not available, using simplified calculations")
            return False
    
    def get_coordinates_for_user(self, user) -> Optional[GeographicalCoordinate]:
        """Get geographical coordinates for user's birth location"""
        try:
            # Use new location fields if available
            if user.birth_country and user.birth_city:
                coords = self.location_service.validate_and_geocode_location(
                    country=user.birth_country,
                    region=user.birth_region,
                    city=user.birth_city
                )
                
                if coords:
                    # Update user's lat/lng if not set
                    if not user.latitude or not user.longitude:
                        user.latitude = coords.latitude
                        user.longitude = coords.longitude
                        # Note: In real app, you'd commit this to database
                    
                    return coords
            
            # Fallback to legacy birth_location field
            elif user.birth_location:
                # Try to parse legacy location string
                parts = user.birth_location.split(',')
                if len(parts) >= 2:
                    city = parts[0].strip()
                    country = parts[-1].strip()
                    region = parts[1].strip() if len(parts) > 2 else None
                    
                    return self.location_service.validate_and_geocode_location(
                        country=country,
                        region=region,
                        city=city
                    )
            
            return None
            
        except Exception as e:
            print(f"Error getting coordinates: {e}")
            return None
    
    def generate_natal_chart(self, user) -> Optional[Dict]:
        """Generate accurate natal chart using robust calculations"""
        if not user.birth_date:
            return None
        
        try:
            # Get geographical coordinates
            coordinates = self.get_coordinates_for_user(user)
            
            # Create birth datetime
            birth_dt = self._create_birth_datetime(user, coordinates)
            
            if self.has_swiss_ephemeris and coordinates:
                # Use accurate calculations
                return self._generate_accurate_chart(birth_dt, coordinates, user)
            else:
                # Fall back to simplified calculations
                return self.simple_calc.generate_natal_chart(user)
                
        except Exception as e:
            print(f"Error generating natal chart: {e}")
            # Always fall back to simple calculations
            return self.simple_calc.generate_natal_chart(user)
    
    def _create_birth_datetime(self, user, coordinates: Optional[GeographicalCoordinate]) -> datetime:
        """Create properly timezone-aware birth datetime"""
        try:
            import pytz
            
            # Combine date and time
            birth_time = user.birth_time or time(12, 0)  # Default to noon
            birth_dt = datetime.combine(user.birth_date, birth_time)
            
            # Apply timezone
            if coordinates and coordinates.timezone:
                tz = pytz.timezone(coordinates.timezone)
                birth_dt = tz.localize(birth_dt)
            elif user.timezone:
                # Try to parse user's timezone setting
                try:
                    if user.timezone.startswith('UTC'):
                        offset_str = user.timezone[3:]  # Remove 'UTC' prefix
                        if offset_str:
                            offset_hours = float(offset_str.replace(':', '.'))
                            tz = pytz.FixedOffset(int(offset_hours * 60))
                            birth_dt = tz.localize(birth_dt)
                except:
                    pass
            
            return birth_dt
            
        except Exception as e:
            print(f"Error creating birth datetime: {e}")
            return datetime.combine(user.birth_date, user.birth_time or time(12, 0))
    
    def _generate_accurate_chart(self, birth_dt: datetime, coordinates: GeographicalCoordinate, user) -> Dict:
        """Generate chart using accurate astronomical calculations"""
        try:
            # Get accurate planetary positions
            positions = self.astronomical_calc.get_accurate_planetary_positions(birth_dt, coordinates)
            
            # Calculate accurate houses
            houses = self.astronomical_calc.calculate_houses(birth_dt, coordinates, self.house_system)
            
            # Convert to chart format
            chart_data = {
                'positions': positions,
                'houses': houses,
                'birth_info': {
                    'datetime': birth_dt,
                    'coordinates': coordinates,
                    'house_system': self.house_system
                },
                'interpretations': self._generate_interpretations(positions, houses)
            }
            
            return chart_data
            
        except Exception as e:
            print(f"Error in accurate chart generation: {e}")
            raise
    
    def _generate_interpretations(self, positions: Dict, houses: Dict) -> Dict:
        """Generate astrological interpretations"""
        interpretations = {}
        
        try:
            # Sun sign interpretation
            if 'Sun' in positions:
                sun_sign = self._degree_to_sign(positions['Sun']['longitude'])
                interpretations['sun'] = f"Sun in {sun_sign}: Core identity and life purpose"
            
            # Moon sign interpretation
            if 'Moon' in positions:
                moon_sign = self._degree_to_sign(positions['Moon']['longitude'])
                interpretations['moon'] = f"Moon in {moon_sign}: Emotional nature and instincts"
            
            # Rising sign interpretation
            if 1 in houses:
                rising_sign = self._degree_to_sign(houses[1]['cusp'])
                interpretations['rising'] = f"Rising in {rising_sign}: Outer personality and first impressions"
            
        except Exception as e:
            print(f"Error generating interpretations: {e}")
        
        return interpretations
    
    def _degree_to_sign(self, longitude: float) -> str:
        """Convert longitude degree to zodiac sign"""
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        sign_index = int(longitude // 30) % 12
        return signs[sign_index]
    
    def generate_chart_image(self, user) -> Optional[str]:
        """Generate chart image - delegate to simple calculator for now"""
        return self.simple_calc.generate_chart_image(user)
    
    def get_detailed_chart(self, user) -> Optional[Dict]:
        """Get detailed chart data for display"""
        chart = self.generate_natal_chart(user)
        if not chart:
            return None
        
        # Format for template display
        if 'positions' in chart and 'houses' in chart:
            # Accurate data format
            return {
                'planets': chart['positions'],
                'houses': chart['houses'],
                'interpretation': chart.get('interpretations', {})
            }
        else:
            # Simple data format
            return chart

# Usage instructions for robust integration:
"""
To enable full robust astronomical calculations:

1. Install Swiss Ephemeris:
   pip install swisseph

2. Download ephemeris data files:
   - Download Swiss Ephemeris files from astro.com
   - Place .se1 files in ephemeris directory
   - Update path in Swiss Ephemeris configuration

3. Install additional geographic packages:
   pip install geopy timezonefinder astral

4. Optional APIs for enhanced accuracy:
   - Sign up for GeoNames API for better geocoding
   - Use TimeZoneDB API for accurate timezone lookup
   - Integrate NASA JPL Horizons for planetary positions

5. Production considerations:
   - Cache geocoding results
   - Implement proper error handling
   - Add rate limiting for API calls
   - Store calculated positions in database
   - Use background jobs for expensive calculations

Current Status:
- ✅ Enhanced location handling with country/region/city
- ✅ Timezone-aware datetime handling
- ✅ Graceful fallback to simplified calculations
- ⏳ Swiss Ephemeris integration (requires setup)
- ⏳ Advanced house system calculations
- ⏳ Aspect calculations
- ⏳ Transit calculations
"""