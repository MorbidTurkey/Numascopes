"""
Enhanced Daily Horoscope Generator using Transit Data and Structured AI Prompts
"""

import openai
import json
from datetime import datetime, date
from typing import Dict, List, Optional
from models import HoroscopeReading
from daily_transit_calculator import DailyTransitCalculator
import os

class EnhancedDailyHoroscopeGenerator:
    """Generate structured daily horoscopes using transit data and AI"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-3.5-turbo"
        self.transit_calculator = DailyTransitCalculator()
        
        # System prompt for consistent AI responses
        self.system_prompt = """You are an experienced astrologer and clear, compassionate writer.

Constraints:
- Base interpretations strictly on the provided natal and transit data.
- Be practical and non-deterministic: offer guidance, not predictions.
- Keep it personal, grounded, and concise (300–450 words).
- Use neutral, supportive tone. No medical, legal, or financial claims.
- Reflect the user's natal core (Sun, Moon, Rising) and today's top transits.
- Respect timing windows if provided. Avoid jargon unless explained briefly.

Output sections in this order with short headings:
1) Headline (one sentence)
2) Today at a Glance (3 bullets)
3) Transit Highlights (2–5 items, one sentence each, include house focus)
4) Timing Windows (if present)
5) Do / Don't (2 bullets each)
6) Closing Nudge (one sentence)

When referencing houses, add a parenthetical of the life area (e.g., "11th—friends, networks").
When referencing signs or planets, avoid clichés and give practical guidance (e.g., "schedule the talk before noon").
If a transit could be sensitive (e.g., Mars square Moon), frame it as self-awareness + a concrete coping tip.
If no strong transits exist, write a gentler, maintenance-style day (habits, tidying, small wins)."""

    def generate_enhanced_daily_horoscope(self, user, target_date: datetime = None) -> Dict:
        """
        Generate comprehensive daily horoscope with transit data
        Returns structured data for dashboard display
        """
        if target_date is None:
            target_date = datetime.now()
            
        # Check for existing horoscope today
        today_str = target_date.strftime("%Y-%m-%d")
        existing_reading = HoroscopeReading.query.filter(
            HoroscopeReading.user_id == user.id,
            HoroscopeReading.reading_date == target_date.date()
        ).first()
        
        if existing_reading and existing_reading.structured_data:
            try:
                return json.loads(existing_reading.structured_data)
            except:
                pass  # Fall through to regenerate
                
        # Get transit data
        transit_data = self.transit_calculator.get_daily_transit_data(user, target_date)
        
        # Generate AI horoscope
        horoscope_text = self._generate_ai_horoscope(transit_data)
        
        # Calculate mood bars and timing
        mood_bars = self._calculate_mood_bars(transit_data)
        timing_windows = self.transit_calculator.calculate_timing_windows(
            transit_data.get('transits_today', [])
        )
        
        # Build structured response
        structured_data = {
            "date": today_str,
            "season_info": self._get_season_info(target_date),
            "headline": self._extract_headline(horoscope_text),
            "mood_bars": mood_bars,
            "takeaways": self._extract_takeaways(horoscope_text),
            "transit_highlights": self._format_transit_highlights(transit_data),
            "house_focus": self._format_house_focus(transit_data),
            "timing_windows": timing_windows,
            "do_dont": self._extract_do_dont(horoscope_text),
            "growth_nudge": self._extract_growth_nudge(horoscope_text),
            "moon_info": transit_data.get('today_moon', {}),
            "retrogrades": transit_data.get('retrogrades', []),
            "full_text": horoscope_text,
            "raw_transit_data": transit_data
        }
        
        # Save to database
        self._save_horoscope_reading(user, target_date, horoscope_text, structured_data)
        
        return structured_data

    def _generate_ai_horoscope(self, transit_data: Dict) -> str:
        """Generate AI horoscope text using transit data"""
        try:
            user_prompt = f"""Here is the user's astrological context for TODAY in JSON.
Use only this data:

{json.dumps(transit_data, indent=2)}

Write the daily horoscope as specified. 
When referencing houses, add a parenthetical of the life area (e.g., "11th—friends, networks").
When referencing signs or planets, avoid clichés and give practical guidance (e.g., "schedule the talk before noon").
If a transit could be sensitive (e.g., Mars square Moon), frame it as self-awareness + a concrete coping tip.
If no strong transits exist, write a gentler, maintenance-style day (habits, tidying, small wins)."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating AI horoscope: {e}")
            return self._generate_fallback_horoscope(transit_data)

    def _generate_fallback_horoscope(self, transit_data: Dict) -> str:
        """Generate simple fallback horoscope if AI fails"""
        profile = transit_data.get('profile', {})
        sun_sign = profile.get('sun', {}).get('sign', 'Unknown')
        
        return f"""
**Headline:** A day for steady progress and mindful awareness.

**Today at a Glance:**
• Focus on your core {sun_sign} strengths
• Take time for reflection and planning
• Small steps lead to meaningful progress

**Transit Highlights:**
Today's planetary movements encourage patience and persistence. Your {sun_sign} nature is highlighted, bringing opportunities for growth through consistent effort.

**Timing Windows:**
Best Focus: Morning hours
Reflection: Evening time

**Do:**
• Trust your natural {sun_sign} instincts
• Make one concrete plan for the week

**Don't:**
• Rush important decisions
• Overlook small but significant details

**Closing Nudge:**
Remember that authentic progress often happens in quiet, consistent moments.
        """.strip()

    def _calculate_mood_bars(self, transit_data: Dict) -> Dict[str, int]:
        """Calculate mood bar levels (0-5) based on transits"""
        # Default neutral levels
        mood_bars = {
            "love": 3,
            "career": 3, 
            "money": 3,
            "wellness": 3,
            "overall_energy": 3
        }
        
        # Adjust based on transits
        transits = transit_data.get('transits_today', [])
        for transit in transits:
            planet = transit.get('t_planet', '')
            aspect = transit.get('aspect', '')
            target = transit.get('n_target', '')
            house = transit.get('n_target_house', 1)
            
            # Positive aspects boost mood
            boost = 1 if aspect in ['Trine', 'Sextile'] else 0
            drain = -1 if aspect in ['Square', 'Opposition'] else 0
            
            # Planet-specific adjustments
            if planet == 'Venus':
                mood_bars['love'] += boost + drain
                mood_bars['money'] += boost + drain
            elif planet == 'Mars':
                mood_bars['overall_energy'] += boost + drain
                mood_bars['career'] += boost + drain
            elif planet == 'Jupiter':
                mood_bars['overall_energy'] += boost + drain
                mood_bars['career'] += boost + drain
            elif planet == 'Saturn':
                mood_bars['career'] += boost + drain
                mood_bars['wellness'] += boost + drain
                
            # House-specific adjustments
            if house in [2, 8]:  # Money houses
                mood_bars['money'] += boost + drain
            elif house in [1, 6]:  # Health/self houses
                mood_bars['wellness'] += boost + drain
            elif house in [7, 5]:  # Relationship houses
                mood_bars['love'] += boost + drain
            elif house in [10, 6]:  # Career houses
                mood_bars['career'] += boost + drain
                
        # Clamp values to 0-5 range
        for key in mood_bars:
            mood_bars[key] = max(0, min(5, mood_bars[key]))
            
        return mood_bars

    def _extract_headline(self, text: str) -> str:
        """Extract headline from AI-generated text"""
        lines = text.split('\n')
        for line in lines:
            if 'headline' in line.lower() or line.startswith('**'):
                cleaned = line.replace('**', '').replace('Headline:', '').strip()
                if cleaned and len(cleaned) > 10:
                    return cleaned
        return "A day for mindful progress and authentic connection."

    def _extract_takeaways(self, text: str) -> List[str]:
        """Extract 3 key takeaways from AI-generated text"""
        takeaways = []
        lines = text.split('\n')
        
        in_glance_section = False
        for line in lines:
            line = line.strip()
            if 'at a glance' in line.lower():
                in_glance_section = True
                continue
            elif line.startswith('**') and in_glance_section:
                break
            elif in_glance_section and line.startswith('•'):
                takeaways.append(line[1:].strip())
                
        # Fallback if extraction fails
        if len(takeaways) < 3:
            takeaways = [
                "Focus on clear communication",
                "Trust your intuitive insights", 
                "Take practical steps forward"
            ]
            
        return takeaways[:3]

    def _format_transit_highlights(self, transit_data: Dict) -> List[Dict]:
        """Format transit data for display"""
        highlights = []
        transits = transit_data.get('transits_today', [])
        
        for transit in transits[:3]:  # Top 3 transits
            house_num = transit.get('n_target_house', 1)
            house_theme = self.transit_calculator.house_themes.get(house_num, "Life Focus")
            
            highlight = {
                "transit": f"{transit.get('t_planet', '')} {self._get_aspect_symbol(transit.get('aspect', ''))} {transit.get('n_target', '')}",
                "aspect_details": f"{transit.get('aspect', '')} ({transit.get('orb_deg', 0):.1f}°)",
                "house_focus": f"{house_num} ({house_theme})",
                "timing": transit.get('exact_time_local', 'All day'),
                "meaning": self._get_transit_meaning(transit)
            }
            highlights.append(highlight)
            
        return highlights

    def _format_house_focus(self, transit_data: Dict) -> List[Dict]:
        """Format house focus data"""
        house_focus = transit_data.get('house_focus', [])
        formatted = []
        
        for house_data in house_focus[:2]:
            house_num = house_data.get('house', 1)
            theme = self.transit_calculator.house_themes.get(house_num, "Life Focus")
            
            formatted.append({
                "house": house_num,
                "theme": theme,
                "description": self._get_house_focus_description(house_num),
                "score": house_data.get('score', 0)
            })
            
        return formatted

    def _get_aspect_symbol(self, aspect: str) -> str:
        """Get unicode symbol for aspect"""
        symbols = {
            'Conjunction': '☌',
            'Sextile': '⚹', 
            'Square': '□',
            'Trine': '△',
            'Opposition': '☍'
        }
        return symbols.get(aspect, '~')

    def _get_transit_meaning(self, transit: Dict) -> str:
        """Generate meaning for transit"""
        planet = transit.get('t_planet', '')
        aspect = transit.get('aspect', '')
        target = transit.get('n_target', '')
        
        # Simplified meaning generation
        meanings = {
            'Mars Square Moon': "Emotional tensions may surface—pause before reacting.",
            'Venus Trine Sun': "Charm and steady progress—great for goodwill and small wins.",
            'Mercury Conjunction Venus': "Clear communication opens doors to connection.",
            'Jupiter Sextile Mars': "Confident action meets opportunity—take the initiative.",
            'Saturn Square Mercury': "Think carefully before speaking—patience brings wisdom."
        }
        
        key = f"{planet} {aspect} {target}"
        return meanings.get(key, "Planetary energies align for personal growth.")

    def _get_house_focus_description(self, house_num: int) -> str:
        """Get focus description for house"""
        descriptions = {
            1: "Personal identity and self-expression take center stage.",
            2: "Financial stability and self-worth come into focus.", 
            3: "Communication and local connections are highlighted.",
            4: "Home, family, and emotional security need attention.",
            5: "Creativity, romance, and self-expression flourish.",
            6: "Health, work routines, and daily habits are emphasized.",
            7: "Partnerships and one-on-one relationships are key.",
            8: "Transformation and shared resources require focus.",
            9: "Learning, travel, and expanding horizons are favored.",
            10: "Career, reputation, and public image are spotlighted.",
            11: "Friendships, groups, and future goals take priority.",
            12: "Spirituality, reflection, and release work are important."
        }
        return descriptions.get(house_num, "Life focus areas need attention.")

    def _extract_do_dont(self, text: str) -> Dict[str, List[str]]:
        """Extract do/don't recommendations"""
        do_items = []
        dont_items = []
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if 'do:' in line.lower() and 'don\'t' not in line.lower():
                current_section = 'do'
                continue
            elif 'don\'t:' in line.lower():
                current_section = 'dont'
                continue
            elif line.startswith('**') and current_section:
                break
            elif current_section and line.startswith('•'):
                item = line[1:].strip()
                if current_section == 'do':
                    do_items.append(item)
                else:
                    dont_items.append(item)
                    
        # Fallback recommendations
        if not do_items:
            do_items = ["Trust your instincts", "Take one concrete step forward"]
        if not dont_items:
            dont_items = ["Rush important decisions", "Ignore your inner voice"]
            
        return {"do": do_items[:2], "dont": dont_items[:2]}

    def _extract_growth_nudge(self, text: str) -> str:
        """Extract personal growth nudge"""
        lines = text.split('\n')
        for line in lines:
            if 'nudge' in line.lower() or 'closing' in line.lower():
                cleaned = line.replace('**', '').replace('Closing Nudge:', '').strip()
                if cleaned and len(cleaned) > 10:
                    return cleaned
                    
        return "Take a moment today to appreciate your unique journey and growth."

    def _get_season_info(self, target_date: datetime) -> str:
        """Get current astrological season"""
        month = target_date.month
        day = target_date.day
        
        # Simplified season calculation
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

    def _save_horoscope_reading(self, user, target_date: datetime, text: str, structured_data: Dict):
        """Save horoscope reading to database"""
        try:
            from models import db
            
            # Check for existing reading
            existing = HoroscopeReading.query.filter(
                HoroscopeReading.user_id == user.id,
                HoroscopeReading.reading_date == target_date.date()
            ).first()
            
            if existing:
                existing.content = text
                existing.structured_data = json.dumps(structured_data)
            else:
                reading = HoroscopeReading(
                    user_id=user.id,
                    content=text,
                    reading_date=target_date.date(),
                    structured_data=json.dumps(structured_data)
                )
                db.session.add(reading)
                
            db.session.commit()
            
        except Exception as e:
            print(f"Error saving horoscope reading: {e}")