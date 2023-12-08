// Define the functions in the global scope
    function showTypingIndicator() {
        $('#typing-container').show();
    }
    
    function hideTypingIndicator() {
        $('#typing-container').hide();
    }
    
    // Function to initialize WebSocket connection
    function initializeWebSocket() {
        var socket = new WebSocket('wss://www.whattogrill.com:8055');
        socket.onopen = function() {
            console.log('WebSocket connected!');
        // Send session_id when the WebSocket connection is established
        socket.send(JSON.stringify({ session_id: sessionId }));
        // Store session_id in local storage
        localStorage.setItem('session_id', sessionId);
        };
    
        socket.onmessage = function(event) {
            var msg = JSON.parse(event.data);
            hideTypingIndicator();
            $('#messages').append($('<div class="message bot">').html(msg.response));
            $('#messages').scrollTop($('#messages')[0].scrollHeight);
        };
    
        socket.onerror = function(error) {
            console.error('WebSocket Error:', error);
        };
    
        socket.onclose = function(event) {
            // Basic logging
            console.log('WebSocket closed:', event);
        
            // Detailed logging
            console.log('Close event properties:');
            console.log('  - wasClean:', event.wasClean); // Indicates whether the connection was closed cleanly or not
            console.log('  - code:', event.code); // Numeric code indicating the status code explaining why the connection has been closed
            console.log('  - reason:', event.reason); // Human-readable string explaining why the connection was closed
            console.log('  - type:', event.type); // Type of the event ('close' in this case)
            console.log('  - target URL:', event.target.url); // URL of the WebSocket connection
            console.log('  - readyState:', event.target.readyState); // The readyState of the WebSocket at the time it was closed
        
            // Additional diagnostics
            if (!event.wasClean) {
                console.warn('WebSocket closed unexpectedly.');
            }
        
            // Reconnect after 5 seconds
            setTimeout(initializeWebSocket, 5000);
        };
    
        function sendMessage() {
            var message = $('#message-input').val();
            if (message.trim().length > 0) {
                if (socket.readyState === WebSocket.OPEN) {
                    socket.send(JSON.stringify({'message': message}));
                    $('#message-input').val('');
                    $('#messages').append($('<div class="message user">').text('You: ' + message));
                    showTypingIndicator();
                    $('#messages').scrollTop($('#messages')[0].scrollHeight);
                } else {
                    console.error('WebSocket is not open. ReadyState:', socket.readyState);
                }
            }
        }
    
        $('#send-button').click(function() {
            sendMessage();
        });
    
        $('#message-input').keypress(function(e) {
            if (e.which == 13) { // Enter key has a keycode of 13
                sendMessage();
                return false; // Prevent form submission
            }
        });
    
        // Initially, hide the typing indicator
        hideTypingIndicator();
    
        // Expose the sendMessage function to the global scope
        window.sendMessage = sendMessage;
    }
    
    // Use the document ready function to initialize WebSocket connection
    $(document).ready(function() {
        initializeWebSocket();
    });
document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.hamburger-menu').addEventListener('click', function() {
        document.querySelector('.options-menu').classList.toggle('show');
    });
document.addEventListener('DOMContentLoaded', (event) => {
    let sessionId = localStorage.getItem('session_id');
    if (sessionId) {
        // Re-establish websocket connection with the session ID
        // replace 'initWebSocket' with your actual function to initialize the websocket connection
        initWebSocket(sessionId);
    } else {
        // Redirect to login or show an error message
        window.location.href = '/login'; // Redirect to login
    }
    });
    

    document.getElementById('about').addEventListener('click', function() {
        showOverlay('About', 'This is some information about our service...');
    });
});

function showOverlay(title, content) {
    const overlay = document.createElement('div');
    overlay.classList.add('overlay');

    const overlayContent = document.createElement('div');
    overlayContent.classList.add('overlay-content');

    const overlayTitle = document.createElement('h2');
    overlayTitle.textContent = title;

    const overlayText = document.createElement('p');
    overlayText.textContent = content;

    const closeButton = document.createElement('button');
    closeButton.textContent = 'Close';
    closeButton.onclick = function() {
        overlay.remove();
    };

    overlayContent.appendChild(overlayTitle);
    overlayContent.appendChild(overlayText);
    overlayContent.appendChild(closeButton);
    overlay.appendChild(overlayContent);

    document.body.appendChild(overlay);
    overlay.style.display = 'block';
};
