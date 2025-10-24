# api/index.py - Vercel serverless function entry point
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to Python path so we can import app.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger.info("Starting Flask app import...")

try:
    from app import app  # import the Flask app instance
    logger.info("✅ Successfully imported Flask app")
    logger.info(f"Flask app name: {app.name}")
    logger.info(f"Flask routes: {list(app.url_map.iter_rules())[:5]}")  # Show first 5 routes
except Exception as e:
    logger.error(f"❌ Failed to import app: {e}")
    import traceback
    logger.error(traceback.format_exc())
    raise

# Add a test route to verify it's working
@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Flask app is running on Vercel'}
