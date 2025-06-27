let recognition;
let isListening = false;
let isCommandMode = false;
const responseDisplay = document.getElementById('response'); // Display response element
const socket = new WebSocket("ws://127.0.0.1:8000/ws"); // Connect to FastAPI backend via WebSocket

// WebSocket connection setup
socket.onopen = function() {
    console.log("WebSocket connection established");
};

socket.onmessage = function(event) {
    if (responseDisplay) {
        responseDisplay.textContent = event.data; // Display backend response
        console.log("Backend response: " + event.data);
    }
};

socket.onerror = function(error) {
    console.error("WebSocket error: ", error);
};

socket.onclose = function() {
    console.log("WebSocket connection closed.");
};

// Function to start speech recognition
function startRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false; // Only listen as needed
        recognition.interimResults = false; // Do not show interim results

        recognition.onstart = function() {
            console.log("Voice recognition started. Listening for 'JARVIS'.");
            isListening = true;
        };

        recognition.onspeechend = function() {
            console.log("Speech detected, processing...");
            isListening = false;
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript.trim().toLowerCase();
            console.log("You said: " + transcript);
            handleCommand(transcript); // Process the command
        };

        recognition.onerror = function(event) {
            console.error("Speech recognition error: ", event.error);
            isListening = false;
        };

        recognition.onend = function() {
            if (isListening || isCommandMode) {
                console.log("Recognition ended, listening for more commands...");
                if (!isCommandMode) startRecognition(); // Restart recognition if not in command mode
            }
        };

        recognition.start(); // Start recognition
    } else {
        console.error("Speech Recognition API not supported in this browser.");
    }
}

// Stop speech recognition if needed
function stopRecognition() {
    if (recognition) {
        recognition.stop();
        console.log("Recognition stopped.");
    }
}

// Handle incoming voice commands
function handleCommand(command) {
    if (isCommandMode) {
        console.log(`Executing command: ${command}`);
        socket.send(command); // Send command to backend via WebSocket
        isCommandMode = false; // Exit command mode after executing command
        startRecognition(); // Restart recognition for next wake word
    } else if (command === 'jarvis') {
        console.log("Wake word 'JARVIS' detected.");
        socket.send(command); // Notify backend that JARVIS was triggered
        isCommandMode = true; // Enable command mode
        startRecognition(); // Start listening for further commands
    } else if (command === 'stop jarvis') {
        console.log("Stopping JARVIS on command.");
        socket.send(command); // Send stop command to backend
        stopRecognition(); // Stop the recognition process
        responseDisplay.textContent = "As you wish, sir. Is there anything I can assist you with further?";
        isCommandMode = false;
    } else {
        console.log("Unknown command, continue listening...");
    }
}

// Start recognition automatically on page load
window.onload = function() {
    startRecognition(); // Start recognition automatically
};


