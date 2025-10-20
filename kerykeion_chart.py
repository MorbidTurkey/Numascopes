"""
Professional Astrology Chart Generator using Kerykeion
Supports Placidus house system and professional astrology standards
"""

from kerykeion import AstrologicalSubject, KerykeionChartSVG
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

# Sign name mappings from abbreviations to full names
SIGN_NAMES = {
    'Ari': 'Aries',
    'Tau': 'Taurus', 
    'Gem': 'Gemini',
    'Can': 'Cancer',
    'Leo': 'Leo',
    'Vir': 'Virgo',
    'Lib': 'Libra',
    'Sco': 'Scorpio',
    'Sag': 'Sagittarius',
    'Cap': 'Capricorn',
    'Aqu': 'Aquarius',
    'Pis': 'Pisces'
}

# House name mappings to clean format
HOUSE_NAMES = {
    'First_House': 'First',
    'Second_House': 'Second',
    'Third_House': 'Third',
    'Fourth_House': 'Fourth',
    'Fifth_House': 'Fifth',
    'Sixth_House': 'Sixth',
    'Seventh_House': 'Seventh',
    'Eighth_House': 'Eighth',
    'Ninth_House': 'Ninth',
    'Tenth_House': 'Tenth',
    'Eleventh_House': 'Eleventh',
    'Twelfth_House': 'Twelfth'
}

def decimal_to_dms(decimal_degrees):
    """Convert decimal degrees to degrees, minutes, seconds format"""
    degrees = int(decimal_degrees)
    minutes_float = (decimal_degrees - degrees) * 60
    minutes = int(minutes_float)
    seconds = int((minutes_float - minutes) * 60)
    return f"{degrees}°{minutes:02d}'{seconds:02d}\""

def get_position_in_sign(longitude):
    """Get the position within the sign (0-30 degrees)"""
    return longitude % 30

class ProfessionalAstrologyChart:
    """
    Professional astrology chart generator using Swiss Ephemeris via Kerykeion
    Supports Placidus house system and professional astrology standards
    """
    
    def __init__(self):
        self.house_system = "P"  # Placidus house system
        
    def create_astrological_subject(self, user):
        """
        Create a Kerykeion AstrologicalSubject from user data
        """
        try:
            # Convert user timezone to pytz timezone if it's a string
            if isinstance(user.timezone, str):
                # Handle UTC offset formats like 'UTC-6'
                if user.timezone.startswith('UTC'):
                    # Convert UTC-6 to Etc/GMT+6 (note the reversed sign for Etc/GMT)
                    if '-' in user.timezone:
                        offset = user.timezone.split('-')[1]
                        user_tz = pytz.timezone(f'Etc/GMT+{offset}')
                    elif '+' in user.timezone:
                        offset = user.timezone.split('+')[1]
                        user_tz = pytz.timezone(f'Etc/GMT-{offset}')
                    else:
                        user_tz = pytz.timezone('UTC')
                else:
                    user_tz = pytz.timezone(user.timezone)
            else:
                user_tz = user.timezone
            
            # Combine birth date and time
            birth_datetime = datetime.combine(user.birth_date, user.birth_time)
            
            # Localize to user's timezone
            birth_datetime_tz = user_tz.localize(birth_datetime)
            
            # Create AstrologicalSubject
            user_name = f"{getattr(user, 'first_name', 'User')} {getattr(user, 'last_name', '')}" if hasattr(user, 'first_name') else f"User_{getattr(user, 'id', 'Unknown')}"
            
            # Extract city and country from user's birth_location if available
            birth_city = getattr(user, 'birth_city', None) or getattr(user, 'birth_location', 'Unknown City')
            birth_country = getattr(user, 'birth_country', None) or 'Unknown Country'
            
            # If birth_location contains comma-separated values, parse them
            if hasattr(user, 'birth_location') and ',' in user.birth_location:
                location_parts = [part.strip() for part in user.birth_location.split(',')]
                if len(location_parts) >= 2:
                    birth_city = location_parts[0]
                    birth_country = location_parts[-1]  # Last part is usually country
            
            subject = AstrologicalSubject(
                name=user_name.strip(),
                year=birth_datetime.year,
                month=birth_datetime.month,
                day=birth_datetime.day,
                hour=birth_datetime.hour,
                minute=birth_datetime.minute,
                city=birth_city,
                nation=birth_country,
                lat=float(user.latitude),
                lng=float(user.longitude),
                tz_str=str(user_tz),
                houses_system_identifier="P"  # Placidus house system
            )
            
            logger.info(f"Created AstrologicalSubject for {subject.name}")
            return subject
            
        except Exception as e:
            logger.error(f"Error creating AstrologicalSubject: {e}")
            return None
    
    def generate_svg_chart(self, user, chart_type="Natal"):
        """
        Generate professional SVG chart using Kerykeion
        Returns SVG data as base64 string
        """
        try:
            # Create astrological subject
            subject = self.create_astrological_subject(user)
            if not subject:
                return None
            
            # Create SVG chart with custom settings for larger size
            chart = KerykeionChartSVG(
                first_obj=subject,
                chart_type=chart_type,
                new_output_directory="charts_output"
            )
            
            # Generate the chart and get SVG content
            chart.makeSVG()
            
            # Read the generated SVG file
            import os
            chart_filename = f"{subject.name} - {chart_type} Chart.svg"
            chart_path = os.path.join("charts_output", chart_filename)
            
            if os.path.exists(chart_path):
                with open(chart_path, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
                
                # Enhance SVG for better web display
                svg_content = self.enhance_svg_for_web(svg_content)
                
                # Convert to base64 data URL
                import base64
                svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
                data_url = f"data:image/svg+xml;base64,{svg_base64}"
                
                # Clean up the file
                try:
                    os.remove(chart_path)
                except:
                    pass
                
                logger.info(f"Generated enhanced SVG chart for {subject.name}")
                return data_url
            else:
                logger.error(f"SVG file not found: {chart_path}")
                return None
            
        except Exception as e:
            logger.error(f"Error generating SVG chart: {e}")
            return None
    
    def enhance_svg_for_web(self, svg_content):
        """
        Enhance SVG content for better web display
        """
        try:
            # Make chart responsive and larger
            import re
            
            # Find existing width and height
            width_match = re.search(r'width="(\d+)"', svg_content)
            height_match = re.search(r'height="(\d+)"', svg_content)
            
            if width_match and height_match:
                current_width = int(width_match.group(1))
                current_height = int(height_match.group(1))
                
                # Make it larger (1.5x bigger)
                new_width = int(current_width * 1.5)
                new_height = int(current_height * 1.5)
                
                # Update SVG dimensions
                svg_content = re.sub(r'width="\d+"', f'width="{new_width}"', svg_content)
                svg_content = re.sub(r'height="\d+"', f'height="{new_height}"', svg_content)
                
                # Add viewBox for responsiveness
                viewbox_match = re.search(r'viewBox="[^"]*"', svg_content)
                if not viewbox_match:
                    svg_content = svg_content.replace(
                        '<svg',
                        f'<svg viewBox="0 0 {new_width} {new_height}"'
                    )
                
                # Enhance text readability
                svg_content = svg_content.replace(
                    'font-size="8"', 'font-size="12"'
                ).replace(
                    'font-size="10"', 'font-size="14"'
                ).replace(
                    'font-size="12"', 'font-size="16"'
                )
                
                # Add a professional border
                border_style = f'''
                <rect x="5" y="5" width="{new_width-10}" height="{new_height-10}" 
                      fill="none" stroke="#007bff" stroke-width="3" rx="10"/>
                '''
                svg_content = svg_content.replace('</svg>', border_style + '</svg>')
            
            return svg_content
            
        except Exception as e:
            logger.warning(f"Could not enhance SVG: {e}")
            return svg_content
    
    def get_detailed_chart_data(self, user):
        """
        Get comprehensive astrological data including all Kerykeion features
        """
        try:
            subject = self.create_astrological_subject(user)
            if not subject:
                return None
            
            # Extract comprehensive chart data
            chart_data = {
                'planets': {},
                'houses': {},
                'angles': {},
                'lunar_data': {},
                'additional_points': {},
                'aspects': [],
                'chart_metadata': {},
                'subject_info': {
                    'name': subject.name,
                    'birth_date': f"{subject.year}-{subject.month:02d}-{subject.day:02d}",
                    'birth_time': f"{subject.hour:02d}:{subject.minute:02d}",
                    'location': f"{subject.city}, {subject.nation}",
                    'coordinates': f"{subject.lat:.4f}, {subject.lng:.4f}",
                    'timezone': subject.tz_str,
                    'julian_day': getattr(subject, 'julian_day', None)
                }
            }
            
            # Extract planets data with full details
            planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
            for planet_name in planets:
                if hasattr(subject, planet_name):
                    planet = getattr(subject, planet_name)
                    sign_name = SIGN_NAMES.get(planet.sign, planet.sign)
                    house_name = HOUSE_NAMES.get(planet.house, planet.house)
                    
                    chart_data['planets'][planet.name] = {
                        'longitude': planet.abs_pos,
                        'longitude_dms': decimal_to_dms(planet.abs_pos),
                        'sign': sign_name,
                        'sign_num': planet.sign_num,
                        'position_in_sign': planet.position,
                        'position_in_sign_dms': decimal_to_dms(planet.position),
                        'house': house_name,
                        'retrograde': planet.retrograde,
                        'element': getattr(planet, 'element', None),
                        'quality': getattr(planet, 'quality', None),
                        'emoji': getattr(planet, 'emoji', None)
                    }
            
            # Extract additional celestial points
            additional_points = ['chiron', 'mean_lilith', 'mean_node', 'true_node', 'mean_south_node', 'true_south_node']
            for point_name in additional_points:
                if hasattr(subject, point_name):
                    point = getattr(subject, point_name)
                    if hasattr(point, 'abs_pos'):  # Check if it's a celestial object
                        sign_name = SIGN_NAMES.get(getattr(point, 'sign', ''), getattr(point, 'sign', ''))
                        house_name = HOUSE_NAMES.get(getattr(point, 'house', ''), getattr(point, 'house', ''))
                        position_in_sign = getattr(point, 'position', point.abs_pos % 30)
                        
                        chart_data['additional_points'][point.name if hasattr(point, 'name') else point_name] = {
                            'longitude': point.abs_pos,
                            'longitude_dms': decimal_to_dms(point.abs_pos),
                            'sign': sign_name,
                            'position_in_sign': position_in_sign,
                            'position_in_sign_dms': decimal_to_dms(position_in_sign),
                            'house': house_name,
                            'retrograde': getattr(point, 'retrograde', False)
                        }
            
            # Extract angular points (Ascendant, Descendant, MC, IC)
            angular_points = {
                'ascendant': getattr(subject, 'ascendant', None),
                'descendant': getattr(subject, 'descendant', None), 
                'midheaven': getattr(subject, 'medium_coeli', None),
                'imum_coeli': getattr(subject, 'imum_coeli', None)
            }
            
            for angle_name, angle_value in angular_points.items():
                if angle_value is not None:
                    if hasattr(angle_value, 'abs_pos'):
                        longitude = angle_value.abs_pos
                        sign_name = SIGN_NAMES.get(getattr(angle_value, 'sign', ''), '')
                        position_in_sign = getattr(angle_value, 'position', longitude % 30)
                    else:
                        longitude = float(angle_value)
                        # Calculate sign from longitude
                        sign_num = int(longitude // 30)
                        sign_name = list(SIGN_NAMES.values())[sign_num] if sign_num < 12 else ''
                        position_in_sign = longitude % 30
                    
                    chart_data['angles'][angle_name] = {
                        'longitude': longitude,
                        'longitude_dms': decimal_to_dms(longitude),
                        'sign': sign_name,
                        'position_in_sign': position_in_sign,
                        'position_in_sign_dms': decimal_to_dms(position_in_sign)
                    }
            
            # Extract houses data with full details
            houses = ['first_house', 'second_house', 'third_house', 'fourth_house', 
                     'fifth_house', 'sixth_house', 'seventh_house', 'eighth_house',
                     'ninth_house', 'tenth_house', 'eleventh_house', 'twelfth_house']
            for i, house_name in enumerate(houses, 1):
                if hasattr(subject, house_name):
                    house = getattr(subject, house_name)
                    sign_name = SIGN_NAMES.get(house.sign, house.sign)
                    position_in_sign = house.abs_pos % 30
                    
                    chart_data['houses'][f'house_{i}'] = {
                        'cusp': house.abs_pos,
                        'cusp_dms': decimal_to_dms(position_in_sign),  # Use position in sign, not absolute
                        'sign': sign_name,
                        'sign_num': house.sign_num,
                        'position_in_sign': position_in_sign,
                        'position_in_sign_dms': decimal_to_dms(position_in_sign),
                        'quality': getattr(house, 'quality', None),
                        'element': getattr(house, 'element', None)
                    }
            
            # Extract lunar data
            if hasattr(subject, 'lunar_phase'):
                lunar_data = {
                    'phase': getattr(subject, 'lunar_phase', None),
                    'moon_sign': chart_data['planets'].get('Moon', {}).get('sign')
                }
                # Only add emoji if it exists and can be safely encoded
                try:
                    if hasattr(subject, 'lunar_phase_emoji'):
                        emoji = getattr(subject, 'lunar_phase_emoji', None)
                        if emoji:
                            lunar_data['moon_phase_emoji'] = emoji
                except UnicodeError:
                    pass  # Skip emoji if encoding issues
                chart_data['lunar_data'] = lunar_data
            
            # Chart metadata
            chart_data['chart_metadata'] = {
                'house_system': 'Placidus',
                'zodiac_type': getattr(subject, 'zodiac_type', 'Tropical'),
                'perspective_type': getattr(subject, 'perspective_type', 'Geocentric'),
                'calculation_date': f"{subject.year}-{subject.month:02d}-{subject.day:02d}",
                'local_time': getattr(subject, 'local_time', None),
                'utc_time': getattr(subject, 'utc_time', None)
            }
            
            # TODO: Extract aspects (will be implemented in next update)
            chart_data['aspects'] = []
            
            logger.info(f"Extracted comprehensive chart data for {subject.name}")
            return chart_data
            
        except Exception as e:
            logger.error(f"Error extracting comprehensive chart data: {e}")
            return None

def create_professional_chart(user, chart_format="svg"):
    """
    Main function to create professional astrology chart
    
    Args:
        user: User object with birth data
        chart_format: 'svg' for SVG chart, 'data' for raw data
    
    Returns:
        Chart data URL or detailed chart data
    """
    chart_generator = ProfessionalAstrologyChart()
    
    if chart_format == "svg":
        return chart_generator.generate_svg_chart(user)
    elif chart_format == "data":
        return chart_generator.get_detailed_chart_data(user)
    else:
        # Return both
        return {
            'chart_svg': chart_generator.generate_svg_chart(user),
            'chart_data': chart_generator.get_detailed_chart_data(user)
        }

# Test function
def test_kerykeion_chart():
    """Test the Kerykeion chart generation"""
    from datetime import date, time
    
    # Mock user object for testing
    class MockUser:
        def __init__(self):
            self.name = "Test User"
            self.birth_date = date(1990, 6, 15)
            self.birth_time = time(14, 30, 0)
            self.latitude = 40.7128
            self.longitude = -74.0060
            self.timezone = "America/New_York"
            self.birth_location = "New York, NY"
    
    user = MockUser()
    chart_data = create_professional_chart(user, "data")
    
    if chart_data:
        print("✅ Kerykeion chart generation successful!")
        print(f"Planets found: {len(chart_data.get('planets', {}))}")
        print(f"Houses found: {len(chart_data.get('houses', {}))}")
        print(f"Aspects found: {len(chart_data.get('aspects', []))}")
        return True
    else:
        print("❌ Kerykeion chart generation failed")
        return False

if __name__ == "__main__":
    test_kerykeion_chart()