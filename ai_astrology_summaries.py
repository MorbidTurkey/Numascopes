"""
AI-powered astrology summaries for sign positions
Generates personalized 1-2 sentence summaries for Sun, Moon, and Rising signs
"""

def generate_sign_summary(sign: str, position: str) -> str:
    """
    Generate AI-like astrology summaries for sign positions
    
    Args:
        sign (str): The astrological sign (e.g., "Capricorn", "Pisces")
        position (str): The position type ("sun", "moon", "rising")
    
    Returns:
        str: 1-2 sentence summary
    """
    
    # Comprehensive sign characteristics for each position
    summaries = {
        "aries": {
            "sun": "Your core identity burns with pioneering fire and natural leadership. You approach life with courage, enthusiasm, and an instinct to initiate new ventures.",
            "moon": "Your emotional world thrives on excitement, independence, and immediate action. You process feelings quickly and need freedom to express your passionate nature.",
            "rising": "You present yourself as confident, energetic, and ready for action. Others see you as a natural leader who approaches life head-first with enthusiasm."
        },
        "taurus": {
            "sun": "Your core identity is grounded in stability, sensuality, and appreciation for life's tangible pleasures. You build your life with patience, determination, and practical wisdom.",
            "moon": "Your emotional world needs security, comfort, and steady rhythms. You find peace in nature, good food, and the simple pleasures that ground your soul.",
            "rising": "You present yourself as calm, reliable, and naturally attractive. Others see you as someone who moves with purpose and has an appreciation for quality and beauty."
        },
        "gemini": {
            "sun": "Your core identity sparkles with curiosity, versatility, and a love for communication. You thrive on mental stimulation, variety, and connecting ideas across different worlds.",
            "moon": "Your emotional world needs constant mental stimulation and variety. You process feelings through talking, learning, and exploring multiple perspectives on any situation.",
            "rising": "You present yourself as witty, adaptable, and intellectually engaging. Others see you as someone who's always interesting to talk to and full of fresh ideas."
        },
        "cancer": {
            "sun": "Your core identity flows through deep emotional sensitivity and protective nurturing instincts. You approach life through feeling first, creating safe havens for yourself and others.",
            "moon": "Your emotional world is rich, intuitive, and deeply connected to family and home. You need emotional security and express care through nurturing those you love.",
            "rising": "You present yourself as caring, intuitive, and emotionally aware. Others see you as someone who creates warmth and makes them feel understood and protected."
        },
        "leo": {
            "sun": "Your core identity radiates confidence, creativity, and natural magnetism. You approach life as a stage where you can express your unique talents and inspire others.",
            "moon": "Your emotional world needs appreciation, creative expression, and heartfelt recognition. You process feelings dramatically and need to feel special and loved.",
            "rising": "You present yourself as warm, confident, and naturally charismatic. Others see you as someone who lights up a room and has a regal, magnetic presence."
        },
        "virgo": {
            "sun": "Your core identity is built on service, precision, and the pursuit of perfection through practical action. You approach life with analytical skill and genuine desire to help.",
            "moon": "Your emotional world finds peace through organization, helpful service, and attention to detail. You process feelings by analyzing them and finding practical solutions.",
            "rising": "You present yourself as helpful, organized, and quietly competent. Others see you as someone they can rely on for practical advice and thoughtful assistance."
        },
        "libra": {
            "sun": "Your core identity seeks harmony, beauty, and meaningful partnerships. You approach life through relationships, aesthetic appreciation, and the art of balanced decision-making.",
            "moon": "Your emotional world needs harmony, beauty, and peaceful relationships. You process feelings through sharing with others and creating balance in your environment.",
            "rising": "You present yourself as charming, diplomatic, and aesthetically aware. Others see you as someone who brings grace and fairness to every interaction."
        },
        "scorpio": {
            "sun": "Your core identity runs deep with intensity, transformation, and penetrating insight. You approach life as a mystery to be explored with passion and unwavering determination.",
            "moon": "Your emotional world is intense, private, and powerfully transformative. You process feelings deeply and need authentic connections that honor your emotional complexity.",
            "rising": "You present yourself as mysterious, intense, and magnetically powerful. Others see you as someone who sees beneath the surface and commands respect through quiet strength."
        },
        "sagittarius": {
            "sun": "Your core identity expands through adventure, philosophy, and the quest for higher meaning. You approach life as a journey of discovery, learning, and shared wisdom.",
            "moon": "Your emotional world needs freedom, adventure, and philosophical exploration. You process feelings through movement, learning, and connecting with diverse perspectives.",
            "rising": "You present yourself as optimistic, adventurous, and intellectually curious. Others see you as someone who inspires them to think bigger and explore new horizons."
        },
        "capricorn": {
            "sun": "Your core identity is built on ambition, responsibility, and steady progress toward meaningful goals. You approach life with maturity, discipline, and respect for tradition.",
            "moon": "Your emotional world needs structure, achievement, and practical progress. You process feelings through goal-setting and find security in building something lasting.",
            "rising": "You present yourself as competent, responsible, and naturally authoritative. Others see you as someone who has their life together and can be trusted with important matters."
        },
        "aquarius": {
            "sun": "Your core identity flows through innovation, humanitarian ideals, and unique individual expression. You approach life as an opportunity to revolutionize and improve the world.",
            "moon": "Your emotional world needs freedom, intellectual stimulation, and connection to groups and causes. You process feelings through detached analysis and progressive thinking.",
            "rising": "You present yourself as original, independent, and intellectually forward-thinking. Others see you as someone who marches to their own drum and brings fresh perspectives."
        },
        "pisces": {
            "sun": "Your core identity flows through compassion, imagination, and spiritual sensitivity. You approach life through intuition, creativity, and deep empathy for all beings.",
            "moon": "Your emotional world is fluid, compassionate, and deeply intuitive. You process feelings through artistic expression and need time alone to recharge your sensitive spirit.",
            "rising": "You present yourself as gentle, intuitive, and spiritually aware. Others see you as someone who understands their feelings and brings a touch of magic to everyday life."
        }
    }
    
    # Get the summary for the sign and position
    sign_lower = sign.lower()
    if sign_lower in summaries and position in summaries[sign_lower]:
        return summaries[sign_lower][position]
    
    # Fallback for unknown signs
    return f"Your {position} in {sign} brings unique energy to your personality. This placement adds its own special influence to how you express yourself."

def get_signs_summary(sun_sign: str, moon_sign: str, rising_sign: str = None) -> dict:
    """
    Get complete summary for all three main signs
    
    Args:
        sun_sign (str): Sun sign
        moon_sign (str): Moon sign  
        rising_sign (str): Rising sign (optional)
    
    Returns:
        dict: Dictionary with summaries for each position
    """
    return {
        'sun': generate_sign_summary(sun_sign, 'sun'),
        'moon': generate_sign_summary(moon_sign, 'moon'),
        'rising': generate_sign_summary(rising_sign, 'rising') if rising_sign else "Rising sign calculation in progress..."
    }