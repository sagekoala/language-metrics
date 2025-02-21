from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import re
import requests
import sqlite3

# Load environmental variables
load_dotenv()

# YouTube API key
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"

# Instance of app, CORS to enable communication with chrome extension
app = Flask(__name__)
CORS(app)

# Helper function to get a connection to the database
def get_db():
    # Connect to database
    conn = sqlite3.connect("video_logs.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        json_data = request.get_json()
        video_id = json_data['videoId']
        timestamp = datetime.strptime(json_data['timestamp'], "%m/%d/%Y, %I:%M:%S %p")

        if not video_id:
            return jsonify({"error": "Missing videoId parameter"}), 400

        # Make API request to YouTube
        params = {
            'part': ['snippet','contentDetails'],  # You can adjust based on what you need
            'id': video_id,
            'key': YOUTUBE_API_KEY,
        }

        response = requests.get(YOUTUBE_API_URL, params=params)
        data = response.json()

        # Verify YouTube API returned data 
        if not data:
            return jsonify({"error": "Missing response data"}), 400
        
        # Verify YouTube API returned sufficient data
        if "items" in data and data['items']:
            snippet = data['items'][0]['snippet']
            content_details = data['items'][0]['contentDetails']

            # Define return values
            title = snippet['title']
            if 'defaultAudioLanguage' in snippet:
                language = snippet['defaultAudioLanguage'] 
            else:
                language = "Unknown"
            duration = content_details['duration']

            # Print to server 
            print(f"Viewed at: {str(timestamp)}")
            print(title)
            print(language)
            
            # Need to convert duration to seconds
            # Parse ISO 8601 duration format (handles hours, minutes, seconds)
            duration_match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
            hours = int(duration_match.group(1)) if duration_match.group(1) else 0
            minutes = int(duration_match.group(2)) if duration_match.group(2) else 0
            seconds = int(duration_match.group(3)) if duration_match.group(3) else 0
            duration = (hours * 3600) + (minutes * 60) + seconds

            print(duration)

            video_data = { 
                "title": title,
                "duration": duration,
                "language": language,
                "timestamp": timestamp 
            }
            
            # If language is target language, update database
            if 'es' in video_data['language']:
                return update_database(video_data)
            
            return jsonify(video_data)

    return jsonify({"error": "Couldn't return data"}), 400

@app.route("/metrics")
def metrics():
    '''Returns data from database to popup.js
    Note: duration stored in db as seconds, conversion to minutes made accordingly below'''

    # Connect to db
    conn = get_db()
    cursor = conn.cursor()
    
    # Query for yesterday's minutes (local time): 00:00:00 to 23:59:59 yesterday
    cursor.execute("""
        SELECT SUM(duration)
        FROM videos
        WHERE timestamp >= datetime('now', '-1 day', 'start of day', 'localtime')
        AND timestamp < datetime('now', 'start of day', 'localtime')
    """)
    yesterday_minutes = (cursor.fetchone()[0] or 0) // 60

    # Query for today's minutes (local time): 00:00:00 to 23:59:59 today
    cursor.execute("""
        SELECT SUM(duration)
        FROM videos
        WHERE timestamp >= datetime('now', 'start of day', 'localtime')
        AND timestamp < datetime('now', '+1 day', 'start of day', 'localtime')
    """)
    today_minutes = (cursor.fetchone()[0] or 0) // 60
    
    # Get total minutes watched all time
    cursor.execute("SELECT SUM(duration) FROM videos")
    total_minutes_all_time = (cursor.fetchone()[0] // 60) or 0
    
    target_language = "Spanish"
    conn.close()

    return jsonify({'yesterday_minutes': yesterday_minutes,
        'today_minutes': today_minutes,
        'total_minutes_all_time': total_minutes_all_time,
        'target_language': target_language})

@app.route("/history")
def history():
    '''Return watch (listening) history'''
    # Connect to db
    conn = get_db()
    cursor = conn.cursor()

    # Query history
    cursor.execute("SELECT * FROM videos")
    history = cursor.fetchall()

    # Query totals
    cursor.execute("SELECT SUM(duration) FROM videos")
    total_seconds = cursor.fetchone()[0] or 0
    total_minutes = total_seconds // 60

    conn.close()

    print(total_minutes)

    return render_template('history.html', history=history, total_minutes=total_minutes)


# Helper function
def update_database(video_data):

    # Update database here with the current video data
    print(f"Updating database with: {video_data}")

    # Connect to database
    conn = get_db()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    try:

        # Create cursor object, execute query
        cursor = conn.cursor() 
        cursor.execute(
            "INSERT INTO videos(title, duration, language, timestamp) VALUES(?, ?, ?, ?)",
            [video_data['title'], video_data['duration'], video_data['language'], video_data['timestamp']]
        )
        
        conn.commit()
        return jsonify({"message": "Video logged successfully"}), 201

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    
    finally:
        conn.close()
