"""
Professional Astrology Chart Generation
NOW POWERED BY SWISS EPHEMERIS via Kerykeion
★★★★★ Professional Placidus House System Support

This module provides professional-quality natal chart generation
using Swiss Ephemeris accuracy with Placidus house calculations.

Copyright Notice:
- Swiss Ephemeris calculations: Kerykeion + pyswisseph
- Professional house systems: Placidus (P) as default
- Chart rendering: Professional SVG with full astrology conventions
- Fallback system: Web APIs with Enhanced Professional Calculator
"""

import logging
from kerykeion_chart import create_professional_chart

logger = logging.getLogger(__name__)

def create_simple_chart(chart_data=None, accuracy_level="Professional", user=None):
    """
    Create professional astrology chart using Kerykeion + Swiss Ephemeris
    
    Args:
        chart_data: Legacy parameter (kept for compatibility)
        accuracy_level: Chart detail level ("Professional" or "Dashboard Preview")
        user: User object with birth data (REQUIRED for Kerykeion)
        
    Returns:
        Base64 encoded chart image or None if failed
    """
    try:
        if user is None:
            logger.warning("No user provided - cannot generate chart without birth data")
            return None
        
        # Use Kerykeion + Swiss Ephemeris for professional chart generation
        logger.info(f"🔮 Generating PROFESSIONAL chart using Kerykeion + Swiss Ephemeris")
        logger.info(f"👤 User: {getattr(user, 'name', 'Unknown')}")
        logger.info(f"🏠 Using Placidus house system for maximum accuracy")
        
        # Generate professional SVG chart with Kerykeion
        chart_svg = create_professional_chart(user, "svg")
        if chart_svg:
            logger.info("✅ SUCCESS: Professional Swiss Ephemeris chart generated!")
            return chart_svg
        else:
            logger.error("❌ Kerykeion chart generation failed")
            return None
        
    except Exception as e:
        logger.error(f"Critical error in create_simple_chart: {e}")
        import traceback
        traceback.print_exc()
        return None

# Legacy compatibility
def generate_simple_chart(chart_data):
    """Legacy function for backwards compatibility"""
    return create_simple_chart(chart_data, "Professional")