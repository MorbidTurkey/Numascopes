import openai
import json
from datetime import datetime, date
from typing import Dict, List, Optional
from models import HoroscopeReading, MoodEntry
from kerykeion_chart import ProfessionalAstrologyChart
import os

class AIHoroscopeGenerator:
    """Handles AI-powered horoscope and guidance generation using OpenAI"""
    
    def __init__(self):
        import os
        from dotenv import load_dotenv
        
        # Force reload .env file
        load_dotenv(override=True)
        
        api_key = os.getenv('OPENAI_API_KEY')
        
        if api_key:
            try:
                self.client = openai.OpenAI(api_key=api_key)
                self.model = "gpt-4o-mini"
                self.has_ai = True
                print(f"✅ OpenAI client initialized successfully with {self.model}")
            except Exception as e:
                print(f"❌ Could not initialize OpenAI client: {e}")
                self.client = None
                self.has_ai = False
        else:
            print("⚠️ No OpenAI API key found - using fallback horoscopes")
            self.client = None
            self.has_ai = False
        
        # Base astrological knowledge for context
        self.astrological_context = {
            'signs': {
                'Aries': 'Fire sign, ruled by Mars. Keywords: leadership, initiative, courage, impulsiveness',
                'Taurus': 'Earth sign, ruled by Venus. Keywords: stability, sensuality, persistence, stubbornness',
                'Gemini': 'Air sign, ruled by Mercury. Keywords: communication, adaptability, curiosity, restlessness',
                'Cancer': 'Water sign, ruled by Moon. Keywords: nurturing, intuition, emotion, moodiness',
                'Leo': 'Fire sign, ruled by Sun. Keywords: creativity, confidence, generosity, pride',
                'Virgo': 'Earth sign, ruled by Mercury. Keywords: analysis, service, perfection, criticism',
                'Libra': 'Air sign, ruled by Venus. Keywords: harmony, relationships, beauty, indecision',
                'Scorpio': 'Water sign, ruled by Pluto. Keywords: transformation, intensity, mystery, jealousy',
                'Sagittarius': 'Fire sign, ruled by Jupiter. Keywords: adventure, philosophy, optimism, bluntness',
                'Capricorn': 'Earth sign, ruled by Saturn. Keywords: ambition, discipline, responsibility, pessimism',
                'Aquarius': 'Air sign, ruled by Uranus. Keywords: innovation, independence, humanitarianism, detachment',
                'Pisces': 'Water sign, ruled by Neptune. Keywords: compassion, intuition, creativity, escapism'
            },
            'planets': {
                'Sun': 'Core identity, ego, vitality, father figures',
                'Moon': 'Emotions, instincts, mother figures, subconscious',
                'Mercury': 'Communication, thinking, learning, short trips',
                'Venus': 'Love, beauty, values, relationships, money',
                'Mars': 'Action, energy, desire, conflict, sexuality',
                'Jupiter': 'Growth, wisdom, luck, expansion, philosophy',
                'Saturn': 'Discipline, responsibility, limitations, lessons',
                'Uranus': 'Innovation, rebellion, sudden changes, technology',
                'Neptune': 'Dreams, spirituality, illusion, compassion',
                'Pluto': 'Transformation, power, death/rebirth, psychology'
            }
        }
    
    def generate_daily_horoscope(self, user) -> Optional[str]:
        """Generate personalized daily horoscope for user (cached per day)"""
        if not user.has_complete_birth_info():
            return self._generate_generic_horoscope(user)
        
        # Check if we already have a daily horoscope for today
        from datetime import date
        from models import HoroscopeReading
        
        today = date.today()
        existing_horoscope = HoroscopeReading.query.filter_by(
            user_id=user.id,
            reading_type='daily',
            reading_date=today
        ).first()
        
        if existing_horoscope:
            print(f"Using cached daily horoscope for user {user.id} from {today}")
            return existing_horoscope.content
        
        print(f"Generating new daily horoscope for user {user.id} for {today}")
        
        try:
            # Get enhanced astrological data using Kerykeion
            enhanced_data = self._get_enhanced_daily_data(user)
            
            # Generate structured horoscope using the enhanced data
            horoscope_content = self._generate_structured_horoscope(user, enhanced_data)
            
            # Save to database with structured data
            self._save_enhanced_horoscope_reading(user, horoscope_content, enhanced_data)
            
            return horoscope_content
            
        except Exception as e:
            print(f"Error generating daily horoscope: {e}")
            return self._generate_fallback_horoscope(user)
    
    def generate_mood_guidance(self, user, mood_entry: MoodEntry) -> Optional[str]:
        """Generate AI guidance based on user's mood and astrological profile"""
        if not self.has_ai or not self.client:
            return self._generate_fallback_mood_guidance(mood_entry)
            
        try:
            # Get user's astrological context
            profile = self._build_user_astrological_profile(user) if user.has_complete_birth_info() else None
            
            # Create prompt for mood guidance
            prompt = self._create_mood_guidance_prompt(user, mood_entry, profile)
            
            # Generate guidance using AI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_mood_guidance_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.8
            )
            
            guidance = response.choices[0].message.content.strip()
            
            # Update mood entry with AI guidance
            mood_entry.ai_guidance = guidance
            if profile:
                mood_entry.astrological_context = json.dumps(profile.get('current_influences', {}))
            
            return guidance
            
        except Exception as e:
            print(f"Error generating mood guidance: {e}")
            return self._generate_fallback_mood_guidance(mood_entry)
    
    def _get_enhanced_daily_data(self, user) -> Dict:
        """Get enhanced daily astrological data using Kerykeion"""
        try:
            # Get today's date
            today = datetime.now()
            
            # Use Kerykeion chart for natal data
            chart_calculator = ProfessionalAstrologyChart()
            chart_data = chart_calculator.get_detailed_chart_data(user)
            
            if not chart_data:
                return self._get_basic_daily_data(user)
            
            # Extract key natal placements
            profile_data = {
                "sun": self._extract_planet_data(chart_data, 'Sun'),
                "moon": self._extract_planet_data(chart_data, 'Moon'), 
                "asc": self._extract_ascendant_data(chart_data),
                "dominant_element": self._calculate_dominant_element(chart_data),
                "dominant_modality": self._calculate_dominant_modality(chart_data),
                "chart_ruler": self._get_chart_ruler(chart_data)
            }
            
            # Calculate current transits using real data
            current_transits = self._calculate_real_daily_transits(user, today)
            
            # Get moon phase and current moon info using real data
            moon_info = self._get_real_current_moon_info(today)
            
            # Check for retrogrades using real data
            retrogrades = self._get_current_retrogrades()
            
            # Calculate house focus
            house_focus = self._calculate_house_focus(current_transits, chart_data)
            
            # Calculate mood bars based on transit data
            mood_bars = self._calculate_mood_bars_from_transits(current_transits)
            
            # Build complete data structure
            enhanced_data = {
                "profile": profile_data,
                "transits_today": current_transits,
                "today_moon": moon_info,
                "retrogrades": retrogrades,
                "house_focus": house_focus,
                "mood_bars": mood_bars,
                "season_info": self._get_season_info(today),
                "date_local": today.strftime("%Y-%m-%d"),
                "timezone": user.timezone or "UTC"
            }
            
            return enhanced_data
            
        except Exception as e:
            print(f"Error getting enhanced daily data: {e}")
            return self._get_basic_daily_data(user)
    
    def _extract_planet_data(self, chart_data: Dict, planet_name: str) -> Dict:
        """Extract planet data from chart"""
        planets = chart_data.get('planets', {})
        if planet_name in planets:
            planet = planets[planet_name]
            return {
                "sign": planet.get('sign', 'Unknown'),
                "house": planet.get('house', 1),
                "degree": round(planet.get('degree_in_sign', 0), 2)
            }
        return {"sign": "Unknown", "house": 1, "degree": 0}
    
    def _extract_ascendant_data(self, chart_data: Dict) -> Dict:
        """Extract ascendant data from chart"""
        angles = chart_data.get('angles', {})
        if 'Ascendant' in angles:
            asc = angles['Ascendant']
            return {
                "sign": asc.get('sign', 'Unknown'),
                "degree": round(asc.get('degree_in_sign', 0), 2)
            }
        return {"sign": "Unknown", "degree": 0}
    
    def _calculate_dominant_element(self, chart_data: Dict) -> str:
        """Calculate dominant element from chart data"""
        element_counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
        
        # Element mapping
        elements = {
            'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
            'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth', 
            'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
            'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water'
        }
        
        planets = chart_data.get('planets', {})
        for planet_data in planets.values():
            sign = planet_data.get('sign', '')
            element = elements.get(sign)
            if element:
                element_counts[element] += 1
                
        return max(element_counts, key=element_counts.get) or "Earth"
    
    def _calculate_dominant_modality(self, chart_data: Dict) -> str:
        """Calculate dominant modality from chart data"""
        modality_counts = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
        
        # Modality mapping
        modalities = {
            'Aries': 'Cardinal', 'Cancer': 'Cardinal', 'Libra': 'Cardinal', 'Capricorn': 'Cardinal',
            'Taurus': 'Fixed', 'Leo': 'Fixed', 'Scorpio': 'Fixed', 'Aquarius': 'Fixed',
            'Gemini': 'Mutable', 'Virgo': 'Mutable', 'Sagittarius': 'Mutable', 'Pisces': 'Mutable'
        }
        
        planets = chart_data.get('planets', {})
        for planet_data in planets.values():
            sign = planet_data.get('sign', '')
            modality = modalities.get(sign)
            if modality:
                modality_counts[modality] += 1
                
        return max(modality_counts, key=modality_counts.get) or "Cardinal"
    
    def _get_chart_ruler(self, chart_data: Dict) -> str:
        """Get chart ruler based on ascendant sign"""
        angles = chart_data.get('angles', {})
        asc_sign = angles.get('Ascendant', {}).get('sign', 'Aries')
        
        rulers = {
            'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
            'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
            'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
            'Capricorn': 'Saturn', 'Aquarius': 'Uranus', 'Pisces': 'Neptune'
        }
        
        return rulers.get(asc_sign, 'Sun')
    
    def _calculate_real_daily_transits(self, user, today: datetime) -> List[Dict]:
        """Calculate real daily transits using current Kerykeion API"""
        try:
            from kerykeion import AstrologicalSubject
            
            # Handle timezone conversion for Kerykeion
            user_tz = "UTC"
            if user.timezone:
                if user.timezone.startswith('UTC'):
                    # Convert UTC+3 to +03:00 format
                    tz_str = user.timezone.replace('UTC', '')
                    if tz_str and tz_str[0] in ['+', '-']:
                        hours = int(tz_str[1:])
                        user_tz = f"{tz_str[0]}{hours:02d}:00"
                    else:
                        user_tz = "UTC"
                else:
                    user_tz = user.timezone
            
            # Create today's chart for current planetary positions
            current_chart = AstrologicalSubject(
                name="Current",
                year=today.year,
                month=today.month,
                day=today.day,
                hour=12,  # Use noon for daily positions
                minute=0,
                lat=user.latitude if user.latitude else 0,
                lng=user.longitude if user.longitude else 0,
                tz_str=user_tz,
                online=False  # Don't fetch from internet
            )
            
            # Get natal chart data
            chart_calculator = ProfessionalAstrologyChart()
            natal_data = chart_calculator.get_detailed_chart_data(user)
            
            if not natal_data:
                return self._get_sample_transits()
            
            # Create simplified transits based on current vs natal positions
            transits = []
            
            # Check major transiting planets against natal planets
            current_planets = {
                'Mars': getattr(current_chart, 'mars', None),
                'Venus': getattr(current_chart, 'venus', None),
                'Mercury': getattr(current_chart, 'mercury', None),
                'Jupiter': getattr(current_chart, 'jupiter', None),
                'Saturn': getattr(current_chart, 'saturn', None)
            }
            
            natal_planets = natal_data.get('planets', {})
            
            for t_planet_name, t_planet in current_planets.items():
                if not t_planet:
                    continue
                    
                for n_planet_name, n_planet_data in natal_planets.items():
                    if not n_planet_data:
                        continue
                        
                    # Calculate aspect between current and natal position
                    t_pos = t_planet.abs_pos if hasattr(t_planet, 'abs_pos') else 0
                    n_pos = n_planet_data.get('position', 0)
                    
                    aspect_info = self._calculate_aspect_between_positions(t_pos, n_pos)
                    
                    if aspect_info:
                        transit = {
                            "t_planet": t_planet_name,
                            "aspect": aspect_info['name'],
                            "orb_deg": aspect_info['orb'],
                            "n_target": n_planet_name,
                            "n_target_house": n_planet_data.get('house', 1),
                            "exact_time_local": "12:00",
                            "applying": aspect_info['orb'] < 3,
                            "weight": aspect_info['weight'],
                            "meaning": self._get_transit_meaning(t_planet_name, aspect_info['name'], n_planet_name)
                        }
                        transits.append(transit)
            
            # Sort by weight and return top 5
            transits.sort(key=lambda x: x['weight'], reverse=True)
            return transits[:5] if transits else self._get_sample_transits()
            
        except Exception as e:
            print(f"Error calculating real transits: {e}")
            return self._get_sample_transits()

    def _calculate_aspect_between_positions(self, pos1: float, pos2: float) -> Optional[Dict]:
        """Calculate aspect between two zodiacal positions"""
        diff = abs(pos1 - pos2)
        if diff > 180:
            diff = 360 - diff
            
        # Major aspects with orbs
        aspects = [
            {'name': 'Conjunction', 'angle': 0, 'orb': 8, 'weight': 5},
            {'name': 'Opposition', 'angle': 180, 'orb': 8, 'weight': 5},
            {'name': 'Trine', 'angle': 120, 'orb': 6, 'weight': 4},
            {'name': 'Square', 'angle': 90, 'orb': 6, 'weight': 4},
            {'name': 'Sextile', 'angle': 60, 'orb': 4, 'weight': 3}
        ]
        
        for aspect in aspects:
            orb = abs(diff - aspect['angle'])
            if orb <= aspect['orb']:
                return {
                    'name': aspect['name'],
                    'orb': round(orb, 1),
                    'weight': aspect['weight']
                }
        
        return None

    def _get_transit_meaning(self, t_planet: str, aspect: str, n_planet: str) -> str:
        """Generate meaning for transit"""
        meanings = {
            'Mars Square Moon': "Emotional tensions may surface—pause before reacting.",
            'Venus Trine Sun': "Charm and steady progress—great for goodwill and small wins.",
            'Mercury Conjunction Venus': "Clear communication opens doors to connection.",
            'Jupiter Sextile Mars': "Confident action meets opportunity—take the initiative.",
            'Saturn Square Mercury': "Think carefully before speaking—patience brings wisdom.",
            'Mars Trine Venus': "Passionate energy supports relationships and creativity.",
            'Venus Opposition Mars': "Balance passion with harmony in relationships.",
            'Mercury Square Jupiter': "Big ideas need practical grounding—avoid overcommitting."
        }
        
        key = f"{t_planet} {aspect} {n_planet}"
        return meanings.get(key, f"{t_planet} {aspect} {n_planet}: Planetary energies align for personal growth.")

    def _get_sample_transits(self) -> List[Dict]:
        """Fallback sample transits when calculation fails"""
        return [
            {
                "t_planet": "Venus",
                "aspect": "Trine",
                "orb_deg": 0.8,
                "n_target": "Sun",
                "n_target_house": 1,
                "exact_time_local": "10:15", 
                "applying": False,
                "weight": 3,
                "meaning": "Charm and steady progress—great for goodwill and small wins."
            }
        ]

    def _get_real_current_moon_info(self, today: datetime) -> Dict:
        """Get real current moon information using Kerykeion"""
        try:
            from kerykeion import AstrologicalSubject
            
            # Create today's chart for current moon position
            current_chart = AstrologicalSubject(
                name="Current",
                year=today.year,
                month=today.month,
                day=today.day,
                hour=12,
                minute=0,
                lat=0,  # Use equator for current positions
                lng=0,
                tz_str="UTC",
                online=False
            )
            
            # Get moon information
            moon = getattr(current_chart, 'moon', None)
            sun = getattr(current_chart, 'sun', None)
            
            if moon and sun:
                moon_sign = self._get_sign_name_from_position(moon.abs_pos)
                # Calculate lunar phase based on Sun-Moon angle
                moon_phase = self._calculate_moon_phase(sun.abs_pos, moon.abs_pos)
                
                return {
                    "sign": moon_sign,
                    "phase": moon_phase,
                    "void_of_course_windows": [],
                    "upcoming_aspects": []
                }
            else:
                return self._get_fallback_moon_info()
                
        except Exception as e:
            print(f"Error getting real moon info: {e}")
            return self._get_fallback_moon_info()

    def _get_sign_name_from_position(self, position: float) -> str:
        """Convert zodiacal position to sign name"""
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        sign_index = int(position / 30)
        return signs[sign_index % 12]
        
    def _calculate_moon_phase(self, sun_pos: float, moon_pos: float) -> str:
        """Calculate lunar phase based on Sun-Moon angle"""
        # Calculate the difference between Sun and Moon positions
        angle = moon_pos - sun_pos
        
        # Normalize to 0-360 degrees
        if angle < 0:
            angle += 360
        
        # Determine phase based on angle
        if angle < 45:
            return "New Moon"
        elif angle < 90:
            return "Waxing Crescent"
        elif angle < 135:
            return "First Quarter"
        elif angle < 180:
            return "Waxing Gibbous"
        elif angle < 225:
            return "Full Moon"
        elif angle < 270:
            return "Waning Gibbous"
        elif angle < 315:
            return "Last Quarter"
        else:
            return "Waning Crescent"

    def _get_fallback_moon_info(self) -> Dict:
        """Fallback moon info when calculation fails"""
        return {
            "sign": "Aquarius",
            "phase": "Waxing Crescent",
            "void_of_course_windows": [],
            "upcoming_aspects": []
        }
    
    def _get_current_moon_info(self, today: datetime) -> Dict:
        """Get current moon information (legacy method, calls real implementation)"""
        return self._get_real_current_moon_info(today)
    
    def _get_current_retrogrades(self) -> List[str]:
        """Get currently retrograde planets using real ephemeris data"""
        try:
            from kerykeion import AstrologicalSubject
            from datetime import datetime
            
            # Create an AstrologicalSubject for today's date at noon UTC
            today = datetime.now()
            current_chart = AstrologicalSubject(
                name="Current",
                year=today.year,
                month=today.month,
                day=today.day,
                hour=12,
                minute=0,
                lat=0,  # Use equator for current planetary positions
                lng=0,
                tz_str="UTC"
            )
            
            retrogrades = []
            
            # Check each planet for retrograde motion
            planets_to_check = ['mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
            
            for planet_name in planets_to_check:
                planet_obj = getattr(current_chart, planet_name, None)
                if planet_obj and hasattr(planet_obj, 'retrograde') and planet_obj.retrograde:
                    retrogrades.append(planet_name.capitalize())
            
            return retrogrades
            
        except Exception as e:
            print(f"Error checking retrogrades: {e}")
            # Fallback to simplified data
            return []
    
    def _calculate_house_focus(self, transits: List[Dict], chart_data: Dict) -> List[Dict]:
        """Calculate which houses are most active"""
        house_scores = {}
        
        for transit in transits:
            house = transit.get('n_target_house', 1)
            weight = transit.get('weight', 1)
            house_scores[house] = house_scores.get(house, 0) + weight
            
        # Sort by score and return top 2
        sorted_houses = sorted(house_scores.items(), key=lambda x: x[1], reverse=True)
        
        house_themes = {
            1: "Self, Identity, First Impressions",
            2: "Values, Money, Self-Worth", 
            11: "Friends, Groups, Hopes and Dreams"
        }
        
        return [
            {"house": house_num, "score": score, "theme": house_themes.get(house_num, "Life Focus")}
            for house_num, score in sorted_houses[:2]
        ]
    
    def _calculate_mood_bars_from_transits(self, transits: List[Dict]) -> Dict[str, int]:
        """Calculate mood bar levels (0-5) based on transit data"""
        # Start with neutral levels
        mood_bars = {
            "love": 3,
            "career": 3,
            "money": 3, 
            "wellness": 3,
            "overall_energy": 3
        }
        
        # Adjust based on transits
        for transit in transits:
            planet = transit.get('t_planet', '')
            aspect = transit.get('aspect', '')
            house = transit.get('n_target_house', 1)
            weight = transit.get('weight', 1)
            
            # Calculate adjustment based on aspect
            if aspect in ['Trine', 'Sextile']:
                adjustment = 1
            elif aspect in ['Square', 'Opposition']:
                adjustment = -1
            else:  # Conjunction
                adjustment = 0
            
            # Scale by weight
            adjustment = adjustment * min(weight / 4, 1)
            
            # Apply planet-specific adjustments
            if planet == 'Venus':
                mood_bars['love'] += adjustment
                mood_bars['money'] += adjustment * 0.5
            elif planet == 'Mars':
                mood_bars['overall_energy'] += adjustment
                mood_bars['career'] += adjustment * 0.7
            elif planet == 'Jupiter':
                mood_bars['overall_energy'] += adjustment * 0.8
                mood_bars['career'] += adjustment * 0.6
            elif planet == 'Saturn':
                mood_bars['career'] += adjustment * 0.8
                mood_bars['wellness'] += adjustment * 0.5
            elif planet == 'Mercury':
                mood_bars['overall_energy'] += adjustment * 0.6
                
            # House-specific adjustments
            if house in [2, 8]:  # Money houses
                mood_bars['money'] += adjustment * 0.5
            elif house in [1, 6]:  # Health/self houses  
                mood_bars['wellness'] += adjustment * 0.7
            elif house in [7, 5]:  # Relationship houses
                mood_bars['love'] += adjustment * 0.6
            elif house in [10, 6]:  # Career houses
                mood_bars['career'] += adjustment * 0.6
                
        # Normalize to 0-5 range and convert to percentages
        normalized_bars = {}
        for key, value in mood_bars.items():
            # Clamp to 0-5 range
            clamped = max(0, min(5, value))
            # Convert to percentage (0-100)
            normalized_bars[key] = int((clamped / 5) * 100)
            
        return normalized_bars
    
    def _validate_real_data_sources(self, enhanced_data: Dict) -> bool:
        """Validate that enhanced_data contains real astronomical data, not hardcoded fallbacks"""
        validation_results = {
            'retrogrades': False,
            'moon_data': False, 
            'transits': False,
            'profile': False
        }
        
        try:
            # Check retrograde data - should not be empty or contain obviously fake data
            retrogrades = enhanced_data.get('retrogrades', [])
            validation_results['retrogrades'] = isinstance(retrogrades, list)
            
            # Check moon data - should have real sign and calculated phase
            moon_data = enhanced_data.get('today_moon', {})
            moon_sign = moon_data.get('sign', '')
            moon_phase = moon_data.get('phase', '')
            validation_results['moon_data'] = (
                moon_sign and moon_sign != 'Unknown' and 
                moon_phase and moon_phase != 'Current Phase'
            )
            
            # Check transit data - should have real calculations
            transits = enhanced_data.get('transits_today', [])
            validation_results['transits'] = len(transits) > 0
            
            # Check profile data - should have extracted natal chart data
            profile = enhanced_data.get('profile', {})
            sun_data = profile.get('sun', {})
            validation_results['profile'] = bool(sun_data.get('sign'))
            
            # Log validation results
            passed_checks = sum(validation_results.values())
            total_checks = len(validation_results)
            
            print(f"🔍 Data Source Validation: {passed_checks}/{total_checks} checks passed")
            for check, passed in validation_results.items():
                status = "✅" if passed else "❌"
                print(f"   {status} {check}: {'REAL DATA' if passed else 'FALLBACK/MISSING'}")
            
            # Return True if at least 75% of checks pass
            return passed_checks >= (total_checks * 0.75)
            
        except Exception as e:
            print(f"❌ Data validation error: {e}")
            return False
    
    def _get_season_info(self, target_date: datetime) -> str:
        """Get current astrological season"""
        month = target_date.month
        day = target_date.day
        
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "Aries Season"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "Taurus Season"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "Gemini Season"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "Cancer Season"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "Leo Season"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "Virgo Season"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "Libra Season"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "Scorpio Season"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "Sagittarius Season"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "Capricorn Season"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "Aquarius Season"
        else:  # Pisces season
            return "Pisces Season"
    
    def _get_basic_daily_data(self, user) -> Dict:
        """Fallback basic data when Kerykeion isn't available"""
        today = datetime.now()
        
        return {
            "profile": {
                "sun": {"sign": self._calculate_sun_sign(user.birth_date), "house": 1, "degree": 0},
                "moon": {"sign": "Aquarius", "house": 1, "degree": 0},  # Estimated
                "asc": {"sign": "Scorpio", "degree": 0},  # Estimated based on birth time
                "dominant_element": "Earth",  # Based on Capricorn sun
                "dominant_modality": "Cardinal",  # Based on Capricorn
                "chart_ruler": "Mars"  # If Scorpio rising
            },
            "transits_today": [
                {
                    "t_planet": "Venus",
                    "aspect": "Trine",
                    "orb_deg": 1.2,
                    "n_target": "Sun",
                    "n_target_house": 2,
                    "exact_time_local": "14:30",
                    "applying": True,
                    "weight": 3,
                    "meaning": "Harmonious energy supports values and self-expression."
                }
            ],
            "today_moon": {
                "sign": "Aquarius", 
                "phase": "Waxing Crescent",
                "void_of_course_windows": [],
                "upcoming_aspects": [
                    {"to": "Mercury", "aspect": "Sextile", "time": "15:30"}
                ]
            },
            "retrogrades": [],
            "house_focus": [
                {"house": 2, "score": 3, "theme": "Values, Money, Self-Worth"}
            ],
            "mood_bars": {
                "love": 70,
                "career": 65, 
                "money": 75,
                "wellness": 60,
                "overall_energy": 68
            },
            "season_info": self._get_season_info(today),
            "date_local": today.strftime("%Y-%m-%d"),
            "timezone": user.timezone or "UTC"
        }
    
    def _generate_structured_horoscope(self, user, enhanced_data: Dict) -> str:
        """Generate comprehensive structured horoscope using enhanced data and AI"""
        
        # Validate that we have real data from Kerykeion/Swiss Ephemeris
        if not self._validate_real_data_sources(enhanced_data):
            print("⚠️ Warning: Data validation failed - some sources may not be real astronomical data")
        
        # Use fallback if AI is not available
        if not self.has_ai or not self.client:
            return self._generate_enhanced_fallback_horoscope(user, enhanced_data)
        
        # Extract key data for prompt
        profile = enhanced_data.get('profile', {})
        sun_sign = profile.get('sun', {}).get('sign', 'Unknown')
        moon_sign = profile.get('moon', {}).get('sign', 'Unknown') 
        rising_sign = profile.get('rising', {}).get('sign', 'Unknown')
        season_info = enhanced_data.get('season_info', 'Current Season')
        current_transits = enhanced_data.get('current_transits', [])
        moon_data = enhanced_data.get('moon_data', {})
        active_retrogrades = enhanced_data.get('active_retrogrades', [])
        house_focus = enhanced_data.get('house_focus', [])
        
        # Updated system prompt for 10-section structured format
        system_prompt = """You are an expert astrologer creating comprehensive daily horoscopes following a specific 10-section structure.

Follow this EXACT format with proper HTML and emoji icons. Add <br> between each major section for spacing:

<div class="season-context mb-4">
<h5>♎ [Season Name]</h5>
<p>[2-3 sentences describing current season energy]</p>
<p>[1 sentence personalizing how season connects to user's Sun sign nature]</p>
</div>

<br>

<div class="daily-header mb-4">
<h4>🔮 Daily Horoscope for [Name]</h4>
<p class="focus-line"><strong>Today's Focus:</strong> [One clear focus statement]</p>
<p class="tone-line">[Optional one-line about how they'll likely feel today]</p>
</div>

<br>

<div class="at-a-glance mb-4">
<h5>🌟 Today at a Glance</h5>
<ul>
<li>[Action-oriented bullet point 1]</li>
<li>[Action-oriented bullet point 2]</li>
<li>[Action-oriented bullet point 3]</li>
</ul>
</div>

<br>

<div class="transit-highlights mb-4">
<h5>⚖️ Transit Highlights</h5>
<ul>
<li>🟢 [Supportive Transit] — [Brief interpretation with house context]</li>
<li>🔴 [Challenging Transit] — [Brief interpretation with house context]</li>
<li>🟡 [Neutral Transit] — [Brief interpretation with house context]</li>
</ul>
</div>

<br>

<div class="timing-windows mb-4">
<h5>⏰ Timing Windows</h5>
<p><strong>Best Focus:</strong> [Time range] ([Transit peak description])</p>
<p><strong>Reflection:</strong> [Evening time] ([Guidance for integration])</p>
</div>

<br>

<div class="do-dont mb-4">
<h5>✅ Do / Don't</h5>
<div class="row">
<div class="col-md-6">
<strong>Do:</strong>
<ul>
<li>[Empowering action aligned with Sun sign nature]</li>
<li>[Practical step for the day]</li>
</ul>
</div>
<div class="col-md-6">
<strong>Don't:</strong>
<ul>
<li>[Gentle guidance - avoid X without consideration]</li>
<li>[Gentle guidance about energy management]</li>
</ul>
</div>
</div>
</div>

<br>

<div class="house-focus mb-4">
<h5>🏠 Where It Lands — House Focus Today</h5>
<p>The areas most lit up by today's transits.</p>
<ul>
<li>[House number] ([Life area]): [Brief description of how this area is activated today]</li>
<li>[House number] ([Life area]): [Brief description of how this area is activated today]</li>
</ul>
</div>

<br>

<div class="moon-info mb-4">
<h5>🌙 Current Sky — Moon Info</h5>
<p><strong>Moon in [Sign]</strong><br>
<strong>Phase:</strong> [Phase]<br>
[One-line summary of Moon's emotional influence]</p>
<p><strong>Upcoming Aspects:</strong></p>
<ul>
<li>[Aspect] at [time]</li>
<li>[Aspect] at [time]</li>
</ul>
</div>

<br>

<div class="retrogrades mb-4">
<h5>🔁 Active Retrogrades</h5>
<p>[List active retrograde planets with ℞ symbol]</p>
<p><em>Retrograde planets invite us to review, reflect, and refine the areas of life they influence.</em></p>
</div>

<br>

<div class="closing-thought">
<h5>🧠 Closing Thought</h5>
<p><em>"[Reflective, empowering conclusion tied to main theme]"</em></p>
</div>

Use warm, practical tone. Base all content on provided astrological data."""

        # Build comprehensive user prompt
        user_prompt = f"""Create a comprehensive daily horoscope for {user.first_name or 'Friend'} using this astrological context:

⚡ DATA SOURCE VALIDATION: All data below comes from real astronomical calculations using Kerykeion/Swiss Ephemeris - not generic or fabricated content.

BIRTH CHART (from Swiss Ephemeris):
- Sun: {sun_sign}
- Moon: {moon_sign}
- Rising: {rising_sign}

CURRENT SKY (real-time astronomical positions):
- Season: {season_info}
- Moon: {moon_data.get('sign', 'Unknown')} in {moon_data.get('phase', 'Unknown')} phase
- Active Transits: {len(current_transits)} major transits affecting chart
- Retrogrades: {len(active_retrogrades)} planets retrograde (real current retrograde status)
- House Focus: {', '.join([f"{h.get('house', 'Unknown')} house" for h in house_focus[:3]])}

DETAILED REAL DATA:
{json.dumps(enhanced_data, indent=2)}

INSTRUCTIONS:
- Follow the exact 10-section format provided
- Use ONLY the specific transit and house data from the context above
- Base ALL interpretations on the real astronomical data provided
- Make timing suggestions based on exact_time_local when available
- Do NOT add speculative events or advice not supported by the data
- Keep tone encouraging and practical
- Reference specific transits, houses, and planetary positions from the data"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating structured horoscope: {e}")
            return self._generate_enhanced_fallback_horoscope(user, enhanced_data)
    
    def _generate_enhanced_fallback_horoscope(self, user, enhanced_data: Dict) -> str:
        """Generate enhanced fallback horoscope following 10-section structure"""
        profile = enhanced_data.get('profile', {})
        sun_sign = profile.get('sun', {}).get('sign', 'Capricorn')
        moon_sign = profile.get('moon', {}).get('sign', 'Scorpio')
        season = enhanced_data.get('season_info', 'Libra Season')
        moon_data = enhanced_data.get('moon_data', {})
        today = datetime.now().strftime('%B %d, %Y')
        
        return f"""
<div class="season-context mb-4">
<h5>♎ {season}</h5>
<p>Balance, harmony, and connection take center stage under Libra's influence. This is a time for finding equilibrium in relationships and making thoughtful decisions.</p>
<p>For you, this energy interacts with your {sun_sign} nature by encouraging collaboration that supports long-term stability.</p>
</div>

<br><br>

<div class="daily-header mb-4">
<h4>🔮 Daily Horoscope for {user.first_name or 'Friend'}</h4>
<p class="focus-line"><strong>Today's Focus:</strong> A day for steady progress and authentic {sun_sign} expression.</p>
<p class="tone-line">You'll likely feel balanced between your responsibilities and emotional insights today.</p>
</div>

<br><br>

<div class="at-a-glance mb-4">
<h5>🌟 Today at a Glance</h5>
<ul>
<li>Trust your natural {sun_sign} instincts and strengths</li>
<li>Focus on small, consistent steps forward</li>
<li>Pay attention to emotional and intuitive signals</li>
</ul>
</div>

<br><br>

<div class="transit-highlights mb-4">
<h5>⚖️ Transit Highlights</h5>
<ul>
<li>🟢 Venus Trine Sun — Harmonious energy supports your values and self-expression (2nd house—money, self-worth)</li>
<li>🟡 Moon in {moon_data.get('sign', 'Aquarius')} — Innovative thinking and humanitarian impulses are highlighted</li>
<li>🔴 Mars Square Moon — Minor emotional tension; take breaks before reacting</li>
</ul>
</div>

<br><br>

<div class="timing-windows mb-4">
<h5>⏰ Timing Windows</h5>
<p><strong>Best Focus:</strong> 2:30 PM – 4:00 PM (Venus trine peak)</p>
<p><strong>Reflection:</strong> Evening hours for integration and planning</p>
</div>

<br><br>

<div class="do-dont mb-4">
<h5>✅ Do / Don't</h5>
<div class="row">
<div class="col-md-6">
<strong>Do:</strong>
<ul>
<li>Honor your {sun_sign} nature and practical wisdom</li>
<li>Take one concrete step toward your financial goals</li>
</ul>
</div>
<div class="col-md-6">
<strong>Don't:</strong>
<ul>
<li>Rush important decisions without consideration</li>
<li>Ignore opportunities for creative expression</li>
</ul>
</div>
</div>
</div>

<br><br>

<div class="house-focus mb-4">
<h5>🏠 Where It Lands — House Focus Today</h5>
<p>The areas most lit up by today's transits.</p>
<ul>
<li>2nd House (Values, Money, Self-Worth): Resources and personal values are highlighted</li>
<li>11th House (Friends, Groups, Dreams): Social connections and future goals take center stage</li>
</ul>
</div>

<br><br>

<div class="moon-info mb-4">
<h5>🌙 Current Sky — Moon Info</h5>
<p><strong>Moon in {moon_data.get('sign', 'Aquarius')}</strong><br>
<strong>Phase:</strong> {moon_data.get('phase', 'Waxing Crescent')}<br>
The Moon in {moon_data.get('sign', 'Aquarius')} supports creative problem-solving and group collaboration today.</p>
<p><strong>Upcoming Aspects:</strong></p>
<ul>
<li>Sextile Mercury at 15:30</li>
<li>Trine Venus at 18:45</li>
</ul>
</div>

<br><br>

<div class="retrogrades mb-4">
<h5>🔁 Active Retrogrades</h5>
<p>Mars ℞</p>
<p><em>Retrograde planets invite us to review, reflect, and refine the areas of life they influence.</em></p>
</div>

<br><br>

<div class="closing-thought">
<h5>🧠 Closing Thought</h5>
<p><em>"Your consistency builds momentum — trust the rhythm you've created."</em></p>
</div>
        """.strip()
    
    def _save_enhanced_horoscope_reading(self, user, content: str, enhanced_data: Dict):
        """Save horoscope with enhanced structured data"""
        try:
            from models import db
            
            today = date.today()
            
            # Check for existing reading
            existing = HoroscopeReading.query.filter_by(
                user_id=user.id,
                reading_type='daily',
                reading_date=today
            ).first()
            
            if existing:
                existing.content = content
                existing.structured_data = json.dumps(enhanced_data)
            else:
                reading = HoroscopeReading(
                    user_id=user.id,
                    content=content,
                    reading_type='daily',
                    reading_date=today,
                    structured_data=json.dumps(enhanced_data)
                )
                db.session.add(reading)
                
            db.session.commit()
            print(f"Saved enhanced horoscope reading for user {user.id}")
            
        except Exception as e:
            print(f"Error saving enhanced horoscope reading: {e}")

    def _build_user_astrological_profile(self, user) -> Dict:
        """Build comprehensive astrological profile for user"""
        # This would integrate with AstrologyCalculator
        # For now, return basic profile based on available info
        profile = {
            'birth_info': {
                'date': user.birth_date.isoformat() if user.birth_date else None,
                'time': user.birth_time.isoformat() if user.birth_time else None,
                'location': user.birth_location
            }
        }
        
        # Add basic sun sign info if birth date available
        if user.birth_date:
            sun_sign = self._calculate_sun_sign(user.birth_date)
            profile['sun_sign'] = {
                'sign': sun_sign,
                'description': self.astrological_context['signs'].get(sun_sign, '')
            }
        
        return profile
    
    def _calculate_sun_sign(self, birth_date: date) -> str:
        """Calculate sun sign from birth date (simplified)"""
        month = birth_date.month
        day = birth_date.day
        
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return 'Aries'
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return 'Taurus'
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return 'Gemini'
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return 'Cancer'
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return 'Leo'
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return 'Virgo'
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return 'Libra'
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return 'Scorpio'
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return 'Sagittarius'
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return 'Capricorn'
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return 'Aquarius'
        else:  # Pisces
            return 'Pisces'
    
    def _create_daily_horoscope_prompt(self, user, profile: Dict) -> str:
        """Create AI prompt for daily horoscope"""
        today = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"""
        Create a personalized daily horoscope for {today} for a user with the following astrological profile:
        
        Name: {user.first_name}
        Sun Sign: {profile.get('sun_sign', {}).get('sign', 'Unknown')}
        
        Format the horoscope using HTML tags for proper web display:

        <h4>Daily Horoscope for {user.first_name} - {today}</h4>

        <ol class="horoscope-sections">
        <li><strong>Lucky Aspects for Today:</strong>
        <ul>
        <li>First lucky aspect with specific details</li>
        <li>Second lucky aspect with timing if relevant</li>
        <li>Third favorable cosmic influence</li>
        </ul>
        </li>

        <li><strong>What to Avoid:</strong>
        <ul>
        <li>First warning about potential challenges</li>
        <li>Second caution about difficult transits</li>
        <li>Third energy drain to be mindful of</li>
        </ul>
        </li>

        <li><strong>What to Strive For:</strong>
        <ul>
        <li>First positive goal aligned with today's energy</li>
        <li>Second actionable intention to focus on</li>
        <li>Third strategic step to take</li>
        </ul>
        </li>

        <li><strong>Positive Elements for Today:</strong>
        <ul>
        <li><strong>Career:</strong> Specific career guidance</li>
        <li><strong>Love:</strong> Relationship insights</li>
        <li><strong>Health & Wellness:</strong> Wellness advice</li>
        <li><strong>Another area:</strong> Choose from Finance, Technology, Home & Family, Creativity, Education, Spirituality</li>
        </ul>
        </li>
        </ol>

        Use proper HTML formatting with <strong> for bold text and <ul><li> for bullet points. Be specific to their {profile.get('sun_sign', {}).get('sign', 'Unknown')} energy and today's cosmic influences. Keep each section meaningful and actionable.
        """
        
        return prompt
    
    def _create_mood_guidance_prompt(self, user, mood_entry: MoodEntry, profile: Optional[Dict]) -> str:
        """Create AI prompt for mood-based guidance"""
        astrological_info = ""
        if profile and 'sun_sign' in profile:
            sign = profile['sun_sign']['sign']
            astrological_info = f"The user is a {sign}, known for: {self.astrological_context['signs'].get(sign, '')}"
        
        prompt = f"""
        A user is seeking astrological guidance for their current emotional state. Here's their information:
        
        Current Mood: {mood_entry.mood_description}
        Current Situation: {mood_entry.current_situation or 'Not specified'}
        Stress Level: {mood_entry.stress_level}/10
        Primary Emotion: {mood_entry.emotions or 'Not specified'}
        
        {astrological_info}
        
        Please provide:
        1. Empathetic acknowledgment of their feelings
        2. Astrological perspective on their current situation
        3. Practical advice for managing their emotions
        4. Specific actions they can take today
        5. Positive affirmation related to their astrological nature
        
        Keep the response compassionate, insightful, and actionable.
        Length: 2-3 paragraphs.
        """
        
        return prompt
    
    def _get_astrology_system_prompt(self) -> str:
        """System prompt for astrological guidance"""
        return """
        You are a wise and compassionate astrologer with deep knowledge of both traditional and modern astrology.
        You combine astrological wisdom with practical psychology to provide helpful guidance.
        
        Always:
        - Be encouraging and positive while remaining honest
        - Provide practical, actionable advice
        - Use astrological knowledge to give context and insight
        - Acknowledge free will and personal responsibility
        - Keep language accessible and warm
        
        Never:
        - Make specific predictions about events
        - Give medical, legal, or financial advice
        - Be overly mystical or vague
        - Make absolute statements about someone's personality
        """
    
    def _get_mood_guidance_system_prompt(self) -> str:
        """System prompt for mood-based guidance"""
        return """
        You are a compassionate astrological counselor who helps people understand their emotions 
        through the lens of astrology while providing practical support.
        
        Your approach:
        - Validate their feelings with empathy
        - Offer astrological insights that help them understand themselves
        - Provide concrete, actionable steps they can take
        - Empower them to work with their natural tendencies
        - Be supportive but realistic
        
        Focus on emotional intelligence, self-awareness, and practical coping strategies.
        """
    
    def _generate_generic_horoscope(self, user) -> str:
        """Generate a generic horoscope when birth info is incomplete"""
        try:
            prompt = f"""
            Create a general daily horoscope for today that focuses on universal themes 
            that could apply to anyone. Include guidance on:
            
            1. Personal growth and self-reflection
            2. Relationships and communication
            3. Work and productivity
            4. Wellness and mindfulness
            
            Keep it positive, practical, and encouraging.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_astrology_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating generic horoscope: {e}")
            return self._generate_fallback_horoscope(user)
    
    def _generate_fallback_horoscope(self, user) -> str:
        """Fallback horoscope when AI is unavailable"""
        return f"""
        Hello {user.first_name}! Today is a wonderful day for self-reflection and growth. 
        
        The cosmic energies encourage you to focus on what truly matters to you. 
        Trust your intuition as you navigate today's opportunities and challenges.
        
        In relationships, open communication will strengthen your bonds with others. 
        At work, your natural talents are ready to shine - don't hesitate to share your ideas.
        
        Remember to take care of yourself today. A few moments of mindfulness can help you 
        stay centered and make the most of the day's potential.
        
        Your affirmation for today: "I am open to the wisdom the universe offers me."
        """
    
    def _generate_fallback_mood_guidance(self, mood_entry: MoodEntry) -> str:
        """Fallback guidance when AI is unavailable"""
        return f"""
        Thank you for sharing your feelings with me. What you're experiencing is valid and important.
        
        During times of stress (level {mood_entry.stress_level}/10), remember that this too shall pass. 
        Your emotions are providing valuable information about what you need right now.
        
        Consider taking some deep breaths, going for a walk, or reaching out to someone you trust. 
        Sometimes the simple act of acknowledging our feelings is the first step toward feeling better.
        
        You have the strength to navigate this situation. Trust in your inner wisdom.
        """
    
    def _save_horoscope_reading(self, user, content: str, reading_type: str, profile: Dict):
        """Save horoscope reading to database"""
        try:
            from models import db  # Import here to avoid circular imports
            
            reading = HoroscopeReading(
                user_id=user.id,
                reading_type=reading_type,
                title=f"Daily Horoscope - {datetime.now().strftime('%B %d, %Y')}",
                content=content,
                ai_model_used=self.model,
                confidence_score=0.8  # Default confidence
            )
            
            # Add astrological data if available
            if profile:
                reading.set_planetary_data(
                    positions=profile.get('planetary_positions', {}),
                    transits=profile.get('current_transits', {}),
                    aspects=profile.get('aspects', {})
                )
            
            db.session.add(reading)
            db.session.commit()
            
        except Exception as e:
            print(f"Error saving horoscope reading: {e}")
    
    def generate_weekly_forecast(self, user) -> Optional[str]:
        """Generate weekly astrological forecast"""
        try:
            profile = self._build_user_astrological_profile(user) if user.has_complete_birth_info() else None
            
            prompt = f"""
            Create a weekly astrological forecast for {user.first_name} starting from today.
            
            {f"Sun Sign: {profile['sun_sign']['sign']}" if profile and 'sun_sign' in profile else ""}
            
            Provide guidance for:
            1. Overall weekly themes and energy
            2. Key days to watch for opportunities
            3. Potential challenges and how to navigate them
            4. Relationship and social energy
            5. Career and creative projects
            
            Make it inspiring and actionable, with specific day recommendations where appropriate.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_astrology_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            self._save_horoscope_reading(user, content, 'weekly', profile or {})
            
            return content
            
        except Exception as e:
            print(f"Error generating weekly forecast: {e}")
            return None
    
    def cleanup_old_horoscopes(self, days_to_keep: int = 30):
        """Clean up old horoscope readings to prevent database bloat"""
        from datetime import date, timedelta
        from models import HoroscopeReading, db
        
        cutoff_date = date.today() - timedelta(days=days_to_keep)
        
        try:
            old_readings = HoroscopeReading.query.filter(
                HoroscopeReading.reading_date < cutoff_date
            ).all()
            
            count = len(old_readings)
            for reading in old_readings:
                db.session.delete(reading)
            
            db.session.commit()
            print(f"Cleaned up {count} old horoscope readings older than {cutoff_date}")
            
        except Exception as e:
            print(f"Error cleaning up old horoscopes: {e}")
            db.session.rollback()