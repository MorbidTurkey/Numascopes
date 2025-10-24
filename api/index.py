# api/index.py - Vercel serverless function entry point
import sys
import os

# Add parent directory to Python path so we can import app.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from app import app  # import the Flask app instance
    print("✅ Successfully imported Flask app")
except Exception as e:
    print(f"❌ Failed to import app: {e}")
    import traceback
    traceback.print_exc()
    raise
