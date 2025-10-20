#!/usr/bin/env python3
"""
Generate secure SECRET_KEY for Flask application production deployment.
Run this script to generate a cryptographically secure secret key.
"""

import secrets
import string

def generate_secret_key(length=64):
    """
    Generate a cryptographically secure secret key for Flask.
    
    Args:
        length (int): Length of the secret key (default 64 characters)
        
    Returns:
        str: Secure random string suitable for Flask SECRET_KEY
    """
    # Use a mix of letters, digits, and some safe symbols
    alphabet = string.ascii_letters + string.digits + '-_'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_keys():
    """Generate and display secure keys for production."""
    
    print("🔐 SECURE KEY GENERATOR")
    print("=" * 50)
    print()
    
    # Generate Flask secret key
    flask_key = generate_secret_key(64)
    print("🔑 Flask SECRET_KEY (64 characters):")
    print(f"SECRET_KEY={flask_key}")
    print()
    
    # Generate alternative hex key
    hex_key = secrets.token_hex(32)  # 32 bytes = 64 hex characters
    print("🔑 Alternative SECRET_KEY (hex format):")
    print(f"SECRET_KEY={hex_key}")
    print()
    
    # Generate URL-safe token
    url_safe_key = secrets.token_urlsafe(48)  # ~64 characters
    print("🔑 URL-safe SECRET_KEY:")
    print(f"SECRET_KEY={url_safe_key}")
    print()
    
    print("📋 USAGE INSTRUCTIONS:")
    print("1. Copy one of the SECRET_KEY values above")
    print("2. Set it as an environment variable on your hosting platform:")
    print("   - Heroku: heroku config:set SECRET_KEY=your-key-here")
    print("   - Railway: railway variables set SECRET_KEY=your-key-here")
    print("   - Render: Set in environment variables section")
    print("3. Never commit this key to version control!")
    print()
    
    print("⚠️  SECURITY NOTES:")
    print("- Each key is cryptographically secure (high entropy)")
    print("- Keys are 64+ characters long as recommended")
    print("- Use different keys for development/staging/production")
    print("- Regenerate keys if compromised")

if __name__ == '__main__':
    generate_keys()