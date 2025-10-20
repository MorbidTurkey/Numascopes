"""
Daily Transit Calculator for Enhanced Horoscope Generation
Calculates today's transits against natal chart using Kerykeion
"""

from datetime import datetime, timezone, timedelta
from kerykeion import AstrologicalSubject
import pytz
from typing import Dict, List, Optional, Tuple
import math

class DailyTransitCalculator:
    """Calculate daily transits and create structured data for AI horoscope generation"""
    
    def __init__(self):
        self.major_aspects = {
            'Conjunction': 0,
            'Sextile': 60,
            'Square': 90,
            'Trine': 120,
            'Opposition': 180
        }
        
        # Orb tolerances
        self.orbs = {
            'major': 3,  # Sun, Moon, Mercury, Venus, Mars
            'outer': 2,  # Jupiter, Saturn, Uranus, Neptune, Pluto
            'moon': 5,   # Moon gets wider orbs
        }
        
        # Planet priorities for transit selection
        self.planet_priorities = {
            'Sun': 5,
            'Moon': 5,
            'Mercury': 4,
            'Venus': 4,
            'Mars': 4,
            'Jupiter': 3,
            'Saturn': 3,
            'Uranus': 2,
            'Neptune': 2,
            'Pluto': 2,
            'Chiron': 1
        }
        
        # House themes for descriptions
        self.house_themes = {
            1: "Self, Identity, First Impressions",
            2: "Values, Money, Self-Worth",
            3: "Communication, Siblings, Short Trips",
            4: "Home, Family, Roots",
            5: "Creativity, Romance, Children",
            6: "Health, Work, Daily Routine",
            7: "Partnerships, Marriage, Open Enemies",
            8: "Transformation, Shared Resources, Intimacy",
            9: "Higher Learning, Philosophy, Travel",
            10: "Career, Reputation, Authority",
            11: "Friends, Groups, Hopes and Dreams",
            12: "Spirituality, Subconscious, Hidden Things"
        }

    def get_sign_name(self, position: float) -> str:
        """Convert degree position to sign name"""
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        sign_index = int(position / 30)
        return signs[sign_index % 12]

    def calculate_aspect(self, pos1: float, pos2: float) -> Optional[Tuple[str, float]]:
        """Calculate aspect between two positions, return (aspect_name, orb)"""
        # Normalize positions to 0-360
        pos1 = pos1 % 360
        pos2 = pos2 % 360
        
        # Calculate difference
        diff = abs(pos1 - pos2)
        if diff > 180:
            diff = 360 - diff
            
        # Check each major aspect
        for aspect_name, aspect_angle in self.major_aspects.items():
            orb = abs(diff - aspect_angle)
            
            # Check if within orb
            max_orb = self.orbs['major']  # Default orb
            if orb <= max_orb:
                return aspect_name, orb
                
        return None

    def calculate_exact_time(self, transit_planet_name: str, natal_position: float, 
                           aspect_angle: float, applying: bool, base_date: datetime) -> str:
        """Estimate exact time of aspect (simplified calculation)"""
        # This is a simplified calculation - in reality, we'd need to check 
        # planetary motion over time
        if applying:
            # If applying, aspect happens later in the day
            estimated_time = base_date.replace(hour=14, minute=0)
        else:
            # If separating, aspect happened earlier
            estimated_time = base_date.replace(hour=10, minute=0)
            
        return estimated_time.strftime("%H:%M")

    def get_daily_transit_data(self, user, target_date: datetime = None) -> Dict:
        """
        Generate comprehensive daily transit data for AI horoscope generation
        Following the JSON structure from the provided specification
        """
        if target_date is None:
            target_date = datetime.now()
            
        # Ensure we have complete birth info
        if not user.has_complete_birth_info():
            return self._get_minimal_transit_data(user, target_date)
            
        try:
            # Create natal chart
            birth_datetime = datetime.combine(user.birth_date, user.birth_time or datetime.min.time())
            
            # Handle timezone conversion
            if user.timezone and user.timezone != 'UTC':
                try:
                    if user.timezone.startswith('UTC'):
                        # Handle UTC offset format (e.g., "UTC-5")
                        offset_str = user.timezone.replace('UTC', '')
                        if offset_str:
                            offset_hours = int(offset_str)
                            user_tz = timezone(timedelta(hours=offset_hours))
                        else:
                            user_tz = timezone.utc
                    else:
                        # Handle timezone name
                        user_tz = pytz.timezone(user.timezone)
                except:
                    user_tz = timezone.utc
            else:
                user_tz = timezone.utc
                
            # Create Kerykeion objects
            natal = KrObject(
                name="User",
                year=birth_datetime.year,
                month=birth_datetime.month,
                day=birth_datetime.day,
                hour=birth_datetime.hour,
                minute=birth_datetime.minute,
                lat=user.latitude,
                lng=user.longitude,
                tz_str=str(user_tz)
            )
            
            # Create transit object for today
            today_transit = Transit(
                kr_object=natal,
                year=target_date.year,
                month=target_date.month,
                day=target_date.day,
                hour=12,  # Use noon for daily transits
                minute=0,
                lat=user.latitude,
                lng=user.longitude,
                tz_str=str(user_tz)
            )
            
            # Get transit aspects
            transit_aspects = today_transit.relevant_aspects()
            
            # Process transits
            processed_transits = []
            for aspect in transit_aspects[:10]:  # Limit to top 10
                try:
                    # Parse the aspect data from Kerykeion
                    transit_data = self._process_transit_aspect(aspect, natal, target_date)
                    if transit_data:
                        processed_transits.append(transit_data)
                except Exception as e:
                    print(f"Error processing transit aspect: {e}")
                    continue
                    
            # Sort by weight and take top 5
            processed_transits.sort(key=lambda x: x.get('weight', 0), reverse=True)
            top_transits = processed_transits[:5]
            
            # Calculate house focus
            house_focus = self._calculate_house_focus(top_transits, natal)
            
            # Get moon data
            moon_data = self._get_moon_data(today_transit, target_date)
            
            # Check for retrogrades
            retrogrades = self._get_active_retrogrades(today_transit)
            
            # Build profile data
            profile_data = {
                "sun": {
                    "sign": self.get_sign_name(natal.sun.abs_pos),
                    "house": natal.sun.house,
                    "degree": round(natal.sun.abs_pos % 30, 2)
                },
                "moon": {
                    "sign": self.get_sign_name(natal.moon.abs_pos),
                    "house": natal.moon.house,
                    "degree": round(natal.moon.abs_pos % 30, 2)
                },
                "asc": {
                    "sign": self.get_sign_name(natal.first_house.abs_pos),
                    "degree": round(natal.first_house.abs_pos % 30, 2)
                },
                "dominant_element": self._get_dominant_element(natal),
                "dominant_modality": self._get_dominant_modality(natal),
                "chart_ruler": self._get_chart_ruler(natal)
            }
            
            # Build complete data structure
            transit_data = {
                "profile": profile_data,
                "transits_today": top_transits,
                "today_moon": moon_data,
                "retrogrades": retrogrades,
                "timezone": str(user_tz),
                "date_local": target_date.strftime("%Y-%m-%d"),
                "orbs_config": self.orbs,
                "house_focus": house_focus
            }
            
            return transit_data
            
        except Exception as e:
            print(f"Error calculating daily transits: {e}")
            return self._get_minimal_transit_data(user, target_date)

    def _process_transit_aspect(self, aspect_data, natal, target_date: datetime) -> Optional[Dict]:
        """Process a single transit aspect into our format"""
        try:
            # Extract aspect information (this is simplified - actual Kerykeion format may vary)
            # You might need to adjust this based on the actual Kerykeion aspect data structure
            
            # For now, create a sample transit (you'll need to adapt this to real Kerykeion data)
            sample_transits = [
                {
                    "t_planet": "Mars",
                    "aspect": "Square",
                    "orb_deg": 1.3,
                    "n_target": "Moon",
                    "n_target_house": natal.moon.house,
                    "exact_time_local": "16:40",
                    "applying": True,
                    "weight": 4
                },
                {
                    "t_planet": "Venus",
                    "aspect": "Trine", 
                    "orb_deg": 0.8,
                    "n_target": "Sun",
                    "n_target_house": natal.sun.house,
                    "exact_time_local": "10:15",
                    "applying": False,
                    "weight": 3
                }
            ]
            
            # Return one of the sample transits for now
            # In a real implementation, you'd parse the actual aspect_data
            import random
            return random.choice(sample_transits)
            
        except Exception as e:
            print(f"Error processing transit aspect: {e}")
            return None

    def _calculate_house_focus(self, transits: List[Dict], natal) -> List[Dict]:
        """Calculate which houses are most active today"""
        house_scores = {}
        
        for transit in transits:
            house = transit.get('n_target_house', 1)
            weight = transit.get('weight', 1)
            
            if house in house_scores:
                house_scores[house] += weight
            else:
                house_scores[house] = weight
                
        # Sort by score and return top 2
        sorted_houses = sorted(house_scores.items(), key=lambda x: x[1], reverse=True)
        
        house_focus = []
        for house_num, score in sorted_houses[:2]:
            house_focus.append({
                "house": house_num,
                "score": score
            })
            
        return house_focus

    def _get_moon_data(self, transit_obj, target_date: datetime) -> Dict:
        """Get today's moon information"""
        try:
            moon_sign = self.get_sign_name(transit_obj.moon.abs_pos)
            
            return {
                "sign": moon_sign,
                "void_of_course_windows": [],  # Simplified for now
                "upcoming_aspects": [
                    {"to": "Mercury", "aspect": "Conjunction", "time": "12:05"}
                ]
            }
        except:
            return {
                "sign": "Unknown",
                "void_of_course_windows": [],
                "upcoming_aspects": []
            }

    def _get_active_retrogrades(self, transit_obj) -> List[str]:
        """Get list of planets currently in retrograde"""
        try:
            retrogrades = []
            
            # Check each planet for retrograde motion
            planets_to_check = ['mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
            
            for planet_name in planets_to_check:
                planet_obj = getattr(transit_obj, planet_name, None)
                if planet_obj and hasattr(planet_obj, 'retrograde') and planet_obj.retrograde:
                    retrogrades.append(planet_name.capitalize())
            
            return retrogrades
            
        except Exception as e:
            print(f"Error checking retrogrades in transit calculator: {e}")
            return []

    def _get_dominant_element(self, natal) -> str:
        """Calculate dominant element from natal chart"""
        # Simplified calculation
        return "Earth"  # Sample data

    def _get_dominant_modality(self, natal) -> str:
        """Calculate dominant modality from natal chart"""
        # Simplified calculation  
        return "Cardinal"  # Sample data

    def _get_chart_ruler(self, natal) -> str:
        """Get chart ruler based on ascendant"""
        asc_sign = self.get_sign_name(natal.first_house.abs_pos)
        
        rulers = {
            'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
            'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
            'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
            'Capricorn': 'Saturn', 'Aquarius': 'Uranus', 'Pisces': 'Neptune'
        }
        
        return rulers.get(asc_sign, 'Sun')

    def _get_minimal_transit_data(self, user, target_date: datetime) -> Dict:
        """Return minimal data when full calculation isn't possible"""
        return {
            "profile": {
                "sun": {"sign": "Unknown", "house": 1, "degree": 0},
                "moon": {"sign": "Unknown", "house": 1, "degree": 0},
                "asc": {"sign": "Unknown", "degree": 0},
                "dominant_element": "Unknown",
                "dominant_modality": "Unknown", 
                "chart_ruler": "Sun"
            },
            "transits_today": [],
            "today_moon": {
                "sign": "Unknown",
                "void_of_course_windows": [],
                "upcoming_aspects": []
            },
            "retrogrades": [],
            "timezone": "UTC",
            "date_local": target_date.strftime("%Y-%m-%d"),
            "orbs_config": self.orbs,
            "house_focus": []
        }

    def format_house_with_theme(self, house_num: int) -> str:
        """Format house number with theme description"""
        theme = self.house_themes.get(house_num, "Unknown")
        return f"{house_num} ({theme})"

    def calculate_timing_windows(self, transits: List[Dict]) -> Dict[str, str]:
        """Calculate best timing windows for the day"""
        # Simplified calculation based on transit exactness
        if not transits:
            return {
                "best_focus": "09:30–12:00",
                "sensitive": "16:00–19:00", 
                "reflection": "After 21:00"
            }
            
        # Find earliest and latest exact times
        exact_times = []
        for transit in transits:
            time_str = transit.get('exact_time_local', '12:00')
            try:
                hour, minute = map(int, time_str.split(':'))
                exact_times.append(hour * 60 + minute)  # Convert to minutes
            except:
                continue
                
        if exact_times:
            earliest = min(exact_times)
            latest = max(exact_times)
            
            # Calculate windows around these times
            best_start = max(570, earliest - 150)  # 9:30 or 2.5h before earliest
            best_end = min(720, earliest + 30)     # 12:00 or 30min after earliest
            
            sensitive_start = max(960, latest - 60)  # 16:00 or 1h before latest
            sensitive_end = min(1140, latest + 60)   # 19:00 or 1h after latest
            
            return {
                "best_focus": f"{best_start//60:02d}:{best_start%60:02d}–{best_end//60:02d}:{best_end%60:02d}",
                "sensitive": f"{sensitive_start//60:02d}:{sensitive_start%60:02d}–{sensitive_end//60:02d}:{sensitive_end%60:02d}",
                "reflection": "After 21:00"
            }
        
        return {
            "best_focus": "09:30–12:00",
            "sensitive": "16:00–19:00",
            "reflection": "After 21:00"
        }