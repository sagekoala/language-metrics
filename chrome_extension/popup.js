    // Function to fetch data from Flask backend
    async function fetchMetrics() {
        try {
            const response = await fetch('http://127.0.0.1:5000/metrics');
            const data = await response.json();

            // Display metrics in the popup
            document.getElementById('metrics').innerHTML = `
                <p><strong>Target Language:</strong> ${data.target_language}</p>
                <p><strong>Time Spent Listening in the Last 7 Days:</strong> ${data.total_minutes_7_days} minutes</p>
                <p><strong>Time Spent Listening All Time:</strong> ${data.total_minutes_all_time} minutes</p>
            `;
        } catch (error) {
            console.error("Error fetching metrics:", error);
            document.getElementById('metrics').innerHTML = '<p><strong>Error fetching metrics.</strong></p>';
        }
    }

    // Fetch and display the metrics when the popup is loaded
    fetchMetrics();