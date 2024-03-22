document.addEventListener("DOMContentLoaded", function() {
    // Establish WebSocket connection
    var socket = io.connect('http://100.20.92.101:10000');
    // Check WebSocket connection status
    socket.on('connect', function() {
        console.log('Socket connection status:', socket.readyState === WebSocket.OPEN);
    });

    // Function to handle user logout
    function logout() {
        window.location.href = '/logout';
    }

    // Event listener for logout button
    const logoutButton = document.getElementById('logout-button');
    logoutButton.addEventListener('click', logout);

    // Function to send a message
    function sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value;
        const receiverUsername = document.getElementById('chatting-with').innerText.replace('Chatting with: ', '');
        const senderUsername = document.getElementById('sender').innerText.replace('Sender: ', '');

        // Data object to send over WebSocket
        const messageData = {
            sender: senderUsername,
            receiver: receiverUsername,
            content: message
        };

        // Append sent message to chat interface
        appendMessage('You', message);
        messageInput.value = '';

        // Emit 'send_message' event to server via WebSocket
        socket.emit('send_message', messageData);
    }

    // Event listener for send button
    const sendButton = document.getElementById('send-button');
    sendButton.addEventListener('click', sendMessage);

    // Function to append a message to the chat interface
    function appendMessage(sender, message) {
        const chatBox = document.querySelector('.messages');
        const messageDiv = document.createElement('div');
        messageDiv.innerHTML = `<p>${sender}:</p><p>${message}</p>`;
        chatBox.appendChild(messageDiv);
        scrollDownChatBox(chatBox);
    }

    // Function to scroll down the chat interface
    function scrollDownChatBox(chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Function to toggle dark mode
    const modeSwitch = document.getElementById('modeSwitch');
    const body = document.body;
    const chatContainer = document.querySelector('.chat-container');

    modeSwitch.addEventListener('change', () => {
        body.classList.toggle('dark-mode');
        chatContainer.classList.toggle('dark-mode');
    });

    // Function to fetch new messages from the server using AJAX
    function fetchNewMessages() {
        $.ajax({
            url: '/fetch_messages', // URL of your server-side endpoint
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response && response.messages) {
                    // Update the chat interface with new messages
                    response.messages.forEach(function(message) {
                        appendMessage(message.sender, message.content);
                    });
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching messages:', error);
            }
        });
    }

    // Call fetchNewMessages function initially
    fetchNewMessages();

    // Periodically fetch new messages without refreshing the page
    setInterval(fetchNewMessages, 5000); // Adjust the interval as needed
});
