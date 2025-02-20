// Monitors activeTab, extracts videoId from YouTube videos, sends ID to backend 
// to extract video info from YouTube API to include title, audio language, duration
chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
    if (changeInfo['url'] && changeInfo['url'].includes("youtube.com/watch")) {
        const url = new URL(changeInfo.url);
        const videoId = url.searchParams.get("v");
        console.log(`Extracted video ID: ${videoId}`);    
        
        // Fetch YouTube API data from Flask server
        const sendDataToBackend = async (data) => {
            try {
                const response = await fetch("http://127.0.0.1:5000/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(data),
                });
        
                const result = await response.json();
                console.log("Response from server:", result);
            } catch (error) {
                console.error("Error sending data:", error);
            }
        };
        
        // Example usage
        sendDataToBackend({ 'videoId': videoId });
    }
})

