"""
Vercel serverless function entry point for Flask app
"""
from app import app

# Vercel looks for a variable named 'app' or a function named 'handler'
# Since we already have 'app' from Flask, we're good to go
