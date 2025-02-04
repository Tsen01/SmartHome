// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
import { getDatabase, ref, onValue } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-database.js";

// Initialize Firebase (Replace with your Firebase configuration)
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
    databaseURL: "YOUR_Realtime_Database_URL",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT_ID.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
};


// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Realtime Database
const database = getDatabase(app);

// Reference the YLED and RLED path in the database
const yledRef = ref(database, 'data/YLED');
const rledRef = ref(database, 'data/RLED');

// Listen for changes in YLED
onValue(yledRef, (snapshot) => {
    const yledStatus = snapshot.val();
    const livingRoomLight = document.querySelector('#living-room-light');

    if (yledStatus) {
        // Update to light-on
        livingRoomLight.src = "../img/light_on.png";
        livingRoomLight.className = "light-on";
    } else {
        // Update to light-off
        livingRoomLight.src = "../img/light_off.png";
        livingRoomLight.className = "light-off";
    }
});

// Listen for changes in RLED
onValue(rledRef, (snapshot) => {
    const rledStatus = snapshot.val();
    const bedRoomLight = document.querySelector('#bedroom-light');

    if (rledStatus) {
        // Update to light-on
        bedRoomLight.src = "../img/bedroom_light_on.png";
        bedRoomLight.className = "light-on";
    } else {
        // Update to light-off
        bedRoomLight.src = "../img/bedroom_light_off.png";
        bedRoomLight.className = "light-off";
    }
});

// Function to toggle lights on or off
function toggleLight(room, status) {
    const roomRef = ref(database, `data/${room}`);  // Reference for the room's light status
    set(roomRef, status);  // Set the new status (true or false)
}

// Event listeners for the buttons to control the lights
document.querySelector('#turn-on-living-room').addEventListener('click', () => toggleLight('YLED', true));
document.querySelector('#turn-off-living-room').addEventListener('click', () => toggleLight('YLED', false));

document.querySelector('#turn-on-bedroom').addEventListener('click', () => toggleLight('RLED', true));
document.querySelector('#turn-off-bedroom').addEventListener('click', () => toggleLight('RLED', false));