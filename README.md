# YouTube Language Metrics
#### Video Demo:  <(https://www.youtube.com/watch?v=12AKnAqowyQ)>

#### Description:
Chrome extension that tracks time spent listening to target language on YouTube for language learners

Structure:
language_metrics/
    chrome_extension/
        manifest.json
        background.js
        popup.html
        popup.js
        icons/
    flask_backend/
        app.py
    REQUIREMENTS.txt

The chrome_extension directory includes: manifest.json, background.js, popup.html, popup.js, and icons/. manifest.json defines extension name, version, description, permission (in this case activeTab), as well as the script for the service_worker (background.js) and the "action" which includes: popup.html, popup.js, and the icons. The service_worker script (background.js) leverages the chrome API to put an event listener on the active tab. When the activeTab is updated and includes "youtube.com/watch" then the url is stored and parsed for the videoId - which is stored at the end of the url for the video being watched with the key "v". Additionally, a timestamp is created to capture the time at which the video was being watched.

The videoId (and timestamp) are subsequently sent to the flask server (app.py). On the server side, flask makes a call to the YouTube API at "https://www.googleapis.com/youtube/v3/videos". In order to access this API, I enabled the the API within console.cloud.google.com/apis and stored my API key in an environmental variable to be used by my project code. This environmental variable includes in the .gitignore file, along with __pycache__, and the database so that sensitive or unnecessary info isn't being tracked on GitHub. The YouTube API is called by the flask server with the videoId parameter, API KEY, and the data we are requesting back parts=['snippet', 'contentDetails']. Note, snippet provides the video's 'title' and 'defaultAudioLanguage', while contentDetails provides the video's 'duration'. After these values are obtained, if the 'defaultAudioLanguage' is equal to the target language (Spanish in my case), a helper function is called to update the sqlite database "video_logs.db with the video's information, else a JSON is return to background.js with the video information (no updates to db, just logging activity to console). 

My main goal when creating this chrome extension was to see if I could somehow get the language for each YouTube video I watched and determine how many videos, and for how much time, I was watching in my "target language". The task of determining the audio of a video isn't trivial. I was essentially left with two options, obtain the language of the video by getting it from the captions or leverage the YouTube API and it's corresponding "defaultAudioLanguage" data point. I decided to leverage the YouTube API because it is not always the case that a YouTube video has captions. That is, fetching this data from the YouTube API is a more reliable approach and provides a convenient way to fetch other important data points - duration, title - so that I could keep an accurate running log of my langage learning on YouTube.  

Popup.html displays and html page with metrics for "Target Language", "Time Spent Listening Yesterday", "Time Spent Listening Today", and "Time Spent Listening All Time". These are data points that are motivating for a learner. On a given day, a learner can click on the extension icon to display the metrics and feel motivated to listen to more videos to increase total time in contact with the target language and ultimately improve as a non-native learner. These metrics are updated dynamically by popup.js. The script fetches the metrics from "/metrics" route on the Flask server and dynamically updates the popup.html webpage. Popup.html also displays an anchor tag for "View Watch History". Again, popup.js controls behavior by setting an event listener on the anchor tag. The script, onClick, will open a new tab to display the entire video_log history to include videos, their associated titles, durations, and timestamps, and a total time listening value. This information is fetched from the Flask server through the "/history" route which queries the database and returns data.

The final result is a chrome extension that logs all of the videos that a person "watches" on their chrome browser. I have been studying Spanish for a number of years and have kepy a manual log in an Excel spreadsheet. This extension allows me to automate the process of logging time spent listening to my target language while also giving me the opportunity to have a few metrics to keep me motivated during studying.