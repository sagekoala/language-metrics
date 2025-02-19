from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

# Load environmental variables
load_dotenv()

# YouTube API key
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"

## Instance of app, CORS to enable communication with chrome extension
app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        video_id = request.get_json()['videoId']
        if not video_id:
            return jsonify({"error": "Missing videoId parameter"}), 400

        ## Make API request to YouTube
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
            print(title)
            print(language)
            print(duration)

            return jsonify({ "title": title,
                            "language": language,
                            "duration": duration })

    return jsonify({"error": "Couldn't return data"}), 400
