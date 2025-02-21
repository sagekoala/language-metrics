    // Function to fetch data from Flask backend
    async function fetchMetrics() {
        try {
            const response = await fetch('http://127.0.0.1:5000/metrics');
            const data = await response.json();

            // Display metrics in the popup
            document.getElementById('metrics').innerHTML = `
                <p><strong>Target Language:</strong> ${data.target_language}</p>
                <p><strong>Time Spent Listening Yesterday:</strong> ${data.yesterday_minutes} minutes</p>
                 <p><strong>Time Spent Listening Today:</strong> ${data.today_minutes} minutes</p>
                <p><strong>Time Spent Listening All Time:</strong> ${Math.floor(data.total_minutes_all_time/60)} hours ${data.total_minutes_all_time%60} minutes</p>
            `;
        } catch (error) {
            console.error("Error fetching metrics:", error);
            document.getElementById('metrics').innerHTML = '<p><strong>Error fetching metrics.</strong></p>';
        }
    }

    // Fetch and display the metrics when the popup is loaded
    fetchMetrics();

    // Add event listener to anchor tag
    document.getElementById('view-history').addEventListener('click', function(event) {
        event.preventDefault();  // Prevent default anchor behavior
        
        // Open the watch history page in a new tab
        chrome.tabs.create({ url: "http://127.0.0.1:5000/history" });
    });