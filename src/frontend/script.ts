// Create WebSocket connection.
const socket = new WebSocket('ws://localhost:8765');

// Connection opened
socket.addEventListener('open', (event) => {
    socket.send('Hello Server!');
});

// Listen for messages
socket.addEventListener('message', (event) => {
    // const trainTimesElem = document.getElementById('train-times');
    // if (trainTimesElem) {
    //     trainTimesElem.textContent = event.data;
    // } else {ƒ
    //     console.warn("Element with id 'train-times' not found.");
    // }
    console.log('Message from server ', event.data);
});
