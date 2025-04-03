// Add an event listener to the button
document.getElementById('fetch-button').addEventListener('click', () => {
    // Fetch data from the back-end when the button is clicked
    fetch('/api/message')
        .then(response => response.text()) // Get the plain text response
        .then(data => {
            // Display the message on the webpage
            document.getElementById('message').innerText = "done";
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.getElementById('message').innerText = 'Failed to load message.';
        });
});