"""
Professional Astrology Chart Generator
Powered by Enhanced Professional Calculator (★★★★★)

Copyright Notice:
- Chart rendering system: Custom implementation
- Astrological calculations: Enhanced Professional Calculator
- Future compatibility: Designed for kerykeion integration when available
- Additional features: Extensible for tarot and other divination tools

This module creates professional-quality natal charts following traditional
astrological chart conventions without requiring external astrology libraries.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import io
import base64
from math import cos, sin, radians, degrees, atan2

class ProfessionalAstrologyChart:
    """
    Professional astrology chart generator following traditional conventions.
    
    Features:
    - Proper zodiac wheel with accurate degree markers
    - Professional house system with correct cusp lines
    - Aspect lines between planets
    - Traditional astrology symbols and colors
    - Clean, readable design for web embedding
    """
    
    def __init__(self):
        self.zodiac_symbols = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
        self.zodiac_names = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                           'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        # Professional astrology colors
        self.zodiac_colors = {
            'fire': '#E74C3C',     # Aries, Leo, Sagittarius
            'earth': '#8E44AD',    # Taurus, Virgo, Capricorn  
            'air': '#3498DB',      # Gemini, Libra, Aquarius
            'water': '#27AE60'     # Cancer, Scorpio, Pisces
        }
        
        self.element_cycle = ['fire', 'earth', 'air', 'water'] * 3
        
        self.planet_info = {
            'sun': {'symbol': '☉', 'color': '#F39C12', 'size': 16, 'name': 'Sun'},
            'moon': {'symbol': '☽', 'color': '#95A5A6', 'size': 14, 'name': 'Moon'},
            'mercury': {'symbol': '☿', 'color': '#F39C12', 'size': 12, 'name': 'Mercury'},
            'venus': {'symbol': '♀', 'color': '#E91E63', 'size': 14, 'name': 'Venus'},
            'mars': {'symbol': '♂', 'color': '#E74C3C', 'size': 14, 'name': 'Mars'},
            'jupiter': {'symbol': '♃', 'color': '#3498DB', 'size': 16, 'name': 'Jupiter'},
            'saturn': {'symbol': '♄', 'color': '#8E44AD', 'size': 16, 'name': 'Saturn'},
            'uranus': {'symbol': '♅', 'color': '#1ABC9C', 'size': 14, 'name': 'Uranus'},
            'neptune': {'symbol': '♆', 'color': '#9B59B6', 'size': 14, 'name': 'Neptune'},
            'pluto': {'symbol': '♇', 'color': '#34495E', 'size': 12, 'name': 'Pluto'}
        }
    
    def create_natal_chart(self, chart_data, width=10, height=10):
        """
        Create a professional natal chart from enhanced calculator data.
        
        Args:
            chart_data: Dictionary from Enhanced Professional Calculator
            width, height: Chart dimensions in inches
            
        Returns:
            Base64 encoded PNG image string
        """
        try:
            # Use non-interactive backend
            plt.switch_backend('Agg')
            
            # Create figure with professional proportions
            fig, ax = plt.subplots(figsize=(width, height), facecolor='white')
            ax.set_xlim(-1.3, 1.3)
            ax.set_ylim(-1.3, 1.3)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_facecolor('white')
            
            # Draw chart structure
            self._draw_chart_circles(ax)
            self._draw_zodiac_wheel(ax)
            self._draw_house_cusps(ax, chart_data.get('houses', []))
            self._draw_planets(ax, chart_data.get('planets', {}))
            self._draw_aspects(ax, chart_data.get('planets', {}))
            
            # Add copyright notice
            self._add_copyright(ax)
            
            # Save to base64
            return self._save_to_base64(fig)
            
        except Exception as e:
            print(f"Professional chart generation error: {e}")
            return None
    
    def _draw_chart_circles(self, ax):
        """Draw the main chart circles with professional styling."""
        # Outer circle - zodiac boundary
        outer = patches.Circle((0, 0), 1.0, fill=False, linewidth=2, 
                              color='#2C3E50', alpha=0.8)
        ax.add_patch(outer)
        
        # House circle - planet placement area
        house = patches.Circle((0, 0), 0.75, fill=False, linewidth=1.5, 
                              color='#34495E', alpha=0.6)
        ax.add_patch(house)
        
        # Inner circle - aspect center
        inner = patches.Circle((0, 0), 0.3, fill=False, linewidth=1, 
                              color='#7F8C8D', alpha=0.4)
        ax.add_patch(inner)
    
    def _draw_zodiac_wheel(self, ax):
        """Draw zodiac signs with traditional positioning."""
        for i, (symbol, element) in enumerate(zip(self.zodiac_symbols, self.element_cycle)):
            # Calculate position (Aries at 0°, moving counterclockwise)
            angle_deg = i * 30  # Each sign is 30 degrees
            angle_rad = radians(90 - angle_deg)  # Start from top, move clockwise
            
            # Position symbol
            radius = 1.12
            x = radius * cos(angle_rad)
            y = radius * sin(angle_rad)
            
            color = self.zodiac_colors[element]
            ax.text(x, y, symbol, fontsize=18, ha='center', va='center',
                   color=color, weight='bold', family='serif')
            
            # Draw degree markers for sign boundaries
            inner_radius = 0.95
            outer_radius = 1.0
            x1 = inner_radius * cos(angle_rad)
            y1 = inner_radius * sin(angle_rad)
            x2 = outer_radius * cos(angle_rad)
            y2 = outer_radius * sin(angle_rad)
            
            ax.plot([x1, x2], [y1, y2], color='#2C3E50', linewidth=1, alpha=0.6)
    
    def _draw_house_cusps(self, ax, houses):
        """Draw house cusps with traditional lines."""
        if not houses:
            return
            
        # Handle different house data formats
        house_cusps = []
        if isinstance(houses, list):
            house_cusps = houses[:12]  # First 12 houses
        elif isinstance(houses, dict):
            for i in range(1, 13):
                if i in houses:
                    cusp = houses[i]
                    if isinstance(cusp, dict):
                        house_cusps.append(cusp.get('cusp', 0))
                    else:
                        house_cusps.append(cusp)
        
        # Draw main angles (1st, 4th, 7th, 10th houses) with thicker lines
        main_angles = [0, 3, 6, 9]  # ASC, IC, DSC, MC
        
        for i, cusp_deg in enumerate(house_cusps):
            if cusp_deg is None:
                continue
                
            angle_rad = radians(90 - cusp_deg)
            
            # Line from center to house circle
            x1, y1 = 0, 0
            x2 = 0.75 * cos(angle_rad)
            y2 = 0.75 * sin(angle_rad)
            
            # Thicker lines for main angles
            linewidth = 2 if i in main_angles else 1
            alpha = 0.8 if i in main_angles else 0.5
            
            ax.plot([x1, x2], [y1, y2], color='#3498DB', 
                   linewidth=linewidth, alpha=alpha)
            
            # House numbers
            label_radius = 0.85
            x_label = label_radius * cos(angle_rad + radians(15))
            y_label = label_radius * sin(angle_rad + radians(15))
            ax.text(x_label, y_label, str(i + 1), fontsize=10, 
                   ha='center', va='center', color='#2C3E50',
                   weight='bold' if i in main_angles else 'normal')
    
    def _draw_planets(self, ax, planets):
        """Draw planets with professional symbols and positioning."""
        if not planets:
            return
            
        for planet_name, planet_data in planets.items():
            planet_key = planet_name.lower()
            if planet_key not in self.planet_info:
                continue
                
            info = self.planet_info[planet_key]
            
            # Get longitude
            longitude = 0
            if isinstance(planet_data, dict):
                longitude = planet_data.get('longitude', planet_data.get('position', 0))
            elif isinstance(planet_data, (int, float)):
                longitude = planet_data
            else:
                longitude = getattr(planet_data, 'longitude', 
                                  getattr(planet_data, 'position', 0))
            
            # Calculate position
            angle_rad = radians(90 - longitude)
            radius = 0.82
            x = radius * cos(angle_rad)
            y = radius * sin(angle_rad)
            
            # Draw planet symbol
            ax.text(x, y, info['symbol'], fontsize=info['size'], 
                   ha='center', va='center', color=info['color'], 
                   weight='bold', family='serif')
            
            # Add degree label
            degree_text = f"{longitude:.0f}°"
            degree_radius = 0.65
            x_deg = degree_radius * cos(angle_rad)
            y_deg = degree_radius * sin(angle_rad)
            ax.text(x_deg, y_deg, degree_text, fontsize=8, 
                   ha='center', va='center', color='#2C3E50', 
                   alpha=0.7)
    
    def _draw_aspects(self, ax, planets):
        """Draw major aspects between planets."""
        if not planets or len(planets) < 2:
            return
            
        # Major aspects and their colors
        aspects = {
            'conjunction': {'orb': 8, 'color': '#E74C3C', 'alpha': 0.6},
            'opposition': {'orb': 8, 'color': '#E74C3C', 'alpha': 0.6},
            'trine': {'orb': 6, 'color': '#27AE60', 'alpha': 0.5},
            'square': {'orb': 6, 'color': '#E67E22', 'alpha': 0.5},
            'sextile': {'orb': 4, 'color': '#3498DB', 'alpha': 0.4}
        }
        
        planet_positions = {}
        for planet_name, planet_data in planets.items():
            if planet_name.lower() in self.planet_info:
                longitude = 0
                if isinstance(planet_data, dict):
                    longitude = planet_data.get('longitude', planet_data.get('position', 0))
                elif isinstance(planet_data, (int, float)):
                    longitude = planet_data
                else:
                    longitude = getattr(planet_data, 'longitude', 
                                      getattr(planet_data, 'position', 0))
                planet_positions[planet_name] = longitude
        
        # Check for aspects between planets
        planet_names = list(planet_positions.keys())
        for i, planet1 in enumerate(planet_names):
            for planet2 in planet_names[i+1:]:
                lon1 = planet_positions[planet1]
                lon2 = planet_positions[planet2]
                
                # Calculate angular separation
                diff = abs(lon1 - lon2)
                if diff > 180:
                    diff = 360 - diff
                
                # Check for major aspects
                aspect_found = None
                if diff <= aspects['conjunction']['orb']:
                    aspect_found = 'conjunction'
                elif abs(diff - 180) <= aspects['opposition']['orb']:
                    aspect_found = 'opposition'
                elif abs(diff - 120) <= aspects['trine']['orb']:
                    aspect_found = 'trine'
                elif abs(diff - 90) <= aspects['square']['orb']:
                    aspect_found = 'square'
                elif abs(diff - 60) <= aspects['sextile']['orb']:
                    aspect_found = 'sextile'
                
                if aspect_found:
                    # Draw aspect line
                    angle1 = radians(90 - lon1)
                    angle2 = radians(90 - lon2)
                    radius = 0.3
                    
                    x1 = radius * cos(angle1)
                    y1 = radius * sin(angle1)
                    x2 = radius * cos(angle2)
                    y2 = radius * sin(angle2)
                    
                    aspect_style = aspects[aspect_found]
                    ax.plot([x1, x2], [y1, y2], 
                           color=aspect_style['color'],
                           alpha=aspect_style['alpha'],
                           linewidth=1)
    
    def _add_copyright(self, ax):
        """Add copyright and attribution notice."""
        copyright_text = (
            "Powered by Enhanced Professional Calculator (★★★★★)\n"
            "Chart System: Professional Astrology Renderer\n"
            "© Future-compatible with kerykeion & tarot features"
        )
        ax.text(-1.25, -1.25, copyright_text, fontsize=7, 
               ha='left', va='bottom', color='#7F8C8D', 
               alpha=0.7, style='italic')
    
    def _save_to_base64(self, fig):
        """Save figure to base64 string."""
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, 
                   bbox_inches='tight', facecolor='white', 
                   edgecolor='none', pad_inches=0.1)
        img_buffer.seek(0)
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        return f"data:image/png;base64,{img_data}"


# Factory function for easy integration
def create_professional_chart(chart_data, accuracy_level="Professional"):
    """
    Create a professional natal chart using Enhanced Professional Calculator data.
    
    This function maintains compatibility with the existing chart generation
    interface while providing professional-quality output.
    
    Args:
        chart_data: Dictionary from Enhanced Professional Calculator
        accuracy_level: Chart detail level (maintained for compatibility)
        
    Returns:
        Base64 encoded PNG image string
    """
    chart_generator = ProfessionalAstrologyChart()
    return chart_generator.create_natal_chart(chart_data)