document.addEventListener("DOMContentLoaded", function() {
    var socket = io.connect('http://127.0.0.1:5000');
    const receiverUsername = document.getElementById('chatting-with').innerText.replace('Chatting with: ', '');

    socket.on('connect', function() {
        console.log('Socket connection status:', socket.readyState === WebSocket.OPEN);
    });

    const sendButton = document.getElementById('send-button');
    sendButton.addEventListener('click', sendMessage);
    const logoutButton = document.getElementById('logout-button')
    logoutButton.addEventListener('click', logout);

    function logout() {
        window.location.href = '/logout';
    }

    const loggedInUser = {
        username: "{{ user.username }}",
    };

    socket.on('message', function(data) {
        appendMessage(data.sender, data.message);
    });

    function sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value;
        const receiverUsername = document.getElementById('chatting-with').innerText.replace('Chatting with: ', '');
        const senderUsername = document.getElementById('sender').innerText.replace('Sender: ', '');

        const messageData = {
            sender: senderUsername,
            receiver: receiverUsername,
            content: message
        };

        appendMessage('You', message);
        messageInput.value = '';

        socket.emit('send_message', messageData);
    }

    function appendMessage(sender, message) {
        const chatBox = document.querySelector('.messages');
        const messageDiv = document.createElement('div');
        messageDiv.innerHTML = `<p>${sender}:</p><p>${message}</p>`;
        chatBox.appendChild(messageDiv);
        scrollDownChatBox(chatBox);
    }

     function scrollDownChatBox(chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    const modeSwitch = document.getElementById('modeSwitch');
    const body = document.body;
    const chatContainer = document.querySelector('.chat-container');

    modeSwitch.addEventListener('change', () => {
        body.classList.toggle('dark-mode');
        chatContainer.classList.toggle('dark-mode');
    });

    // Listen for new messages from the server
    socket.on('receive_message', function(data) {
        console.log('Received message:', data);
        appendMessage(data.sender, data.content);
    });
});