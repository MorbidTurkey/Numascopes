# api/index.py - Vercel serverless function entry point
from app import app

# Vercel will look for the 'app' variable here
# This imports the Flask instance from your main app.py file
