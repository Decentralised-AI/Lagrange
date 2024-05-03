// Initialize the Showdown converter globally
var converter = new showdown.Converter();

function addMessage(message, isSender) {
    const chatContainer = document.getElementById('chat-container');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', isSender ? 'text-right' : 'text-left');

    // Convert all messages assuming they could contain Markdown
    messageElement.innerHTML = converter.makeHtml(message);
    chatContainer.appendChild(messageElement);
}

function handleUserInput(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function handleFileUpload() {
    const fileInput = document.getElementById('file-upload');
    const files = fileInput.files;

    if (files.length > 0) {
        const file = files[0]; // We will send the first file to the server
        const formData = new FormData();
        formData.append('document', file);

        fetch('http://127.0.0.1:5000/input_m', {
            method: 'POST',
            body: formData
        }).then(response => response.text())
        .then(result => {
            console.log('File upload response:', result);
            addMessage(`Uploaded: ${file.name}`, true);
        })
        .catch(error => console.error('Error:', error));
    }
}

function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return;

    addMessage(userInput, true); // Show user's message on the chat interface

    fetch('http://127.0.0.1:5000/input_t', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok'); // Handling HTTP error statuses
        }
        return response.text();  // Assuming server responds with text
    })
    .then(data => {
        console.log('Server response:', data);
        addMessage(data, false); // Optionally, display the server's response
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage(`Error: ${error.message}`, false); // Display error message in the chat interface
    });

    document.getElementById('user-input').value = ''; // Clear input after sending
}

function fetchString() {
    fetch('http://127.0.0.1:5000/send_string')
        .then(response => response.text())
        .then(data => {
            addMessage(data, false); // Displaying the fetched string from send_string endpoint
        })
        .catch(error => console.error('Error fetching from send_string:', error));
}

// Note: Your script had two definitions for initializeChat(). Ensure to only have one.
// This is the one that will be used.
document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('send-btn');
    const fileUploadInput = document.getElementById('file-upload');
    const userInput = document.getElementById('user-input');

    sendButton.addEventListener('click', sendMessage);
    fileUploadInput.addEventListener('change', handleFileUpload);
    userInput.addEventListener('keypress', handleUserInput);
});
