from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
import json

# Add this route to your existing app.py
@app.route('/modern')
def modern_astrology():
    """Modern JavaScript-based astrology interface"""
    return render_template('modern_astrology.html')

@app.route('/api/chart-data', methods=['POST'])
def get_chart_data():
    """API endpoint to get chart data for the modern interface"""
    try:
        data = request.get_json()
        
        # Extract birth information
        birth_date = data.get('birth_date')
        birth_time = data.get('birth_time') 
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        
        # For now, return the user's existing birth info if available
        if current_user.is_authenticated and current_user.has_complete_birth_info():
            birth_datetime = datetime.combine(current_user.birth_date, current_user.birth_time)
            
            response_data = {
                'birth_datetime': birth_datetime.isoformat(),
                'latitude': current_user.latitude,
                'longitude': current_user.longitude,
                'city': current_user.location or '',
                'timezone': current_user.timezone or 'UTC'
            }
            
            return jsonify(response_data)
        else:
            return jsonify({'error': 'No birth information available'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500