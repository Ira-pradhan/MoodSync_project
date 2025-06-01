document.addEventListener('DOMContentLoaded', () => {
    // Screens
    const loginScreen = document.getElementById('login-screen');
    const homeScreen = document.getElementById('home-screen');
    const imageModeScreen = document.getElementById('image-mode');
    const liveModeScreen = document.getElementById('live-mode');
    const resultScreen = document.getElementById('result-screen');

    // Buttons
    const btnLogin = document.getElementById('btn-login');
    const btnLogout = document.getElementById('btn-logout');
    const btnImageMode = document.getElementById('btn-image-mode');
    const btnLiveMode = document.getElementById('btn-live-mode');
    const btnBack = document.querySelectorAll('.btn-back');
    const btnSubmitImage = document.getElementById('btn-submit-image');
    const btnStartCamera = document.getElementById('btn-start-camera');
    const btnAnalyzeLive = document.getElementById('btn-analyze-live');
    const btnStopCamera = document.getElementById('btn-stop-camera');
    const btnGoSpotify = document.getElementById('btn-go-spotify');

    // Inputs & Outputs
    const usernameInput = document.getElementById('username-input');
    const loginError = document.getElementById('login-error');
    const welcomeMessage = document.getElementById('welcome-message');
    const imageUploadInput = document.getElementById('image-upload-input');
    const imageStatus = document.getElementById('image-status');
    const liveVideo = document.getElementById('live-video');
    const liveCanvas = document.getElementById('live-canvas');
    const liveStatus = document.getElementById('live-status');
    const resultMessage = document.getElementById('result-message'); // Main message paragraph
    // *** ADDED References for new result elements ***
    const resultEmoji = document.getElementById('result-emoji');
    const resultEmotionName = document.getElementById('result-emotion-name');
    // *** END ADDED References ***
    const canvasContext = liveCanvas.getContext('2d');

    let stream = null; // To hold the camera stream

    // *** ADDED Emoji Mapping Object ***
    const emotionEmojis = {
        'happy': '😄',
        'sad': '😢',
        'angry': '😠',
        'fear': '😨',
        'disgust': '🤢',
        'surprise': '😮',
        'neutral': '😐',
        'default': '🤔' // Fallback for unknown or no face
    };
    // *** END ADDED Emoji Mapping ***

    // --- Screen Navigation Helper ---
    function showScreen(screenToShow) {
        // Hide all screens first
        loginScreen.style.display = 'none';
        homeScreen.style.display = 'none';
        imageModeScreen.style.display = 'none';
        liveModeScreen.style.display = 'none';
        resultScreen.style.display = 'none';
        // Show the target screen
        if (screenToShow) { // Added check to prevent errors if target is null
           screenToShow.style.display = 'block';
        } else {
            console.error("showScreen called with null target");
            loginScreen.style.display = 'block'; // Default to login if error
        }
    }

    // --- Login Logic ---
    btnLogin.addEventListener('click', () => {
        const username = usernameInput.value.trim();
        // Assuming you removed the password field again based on previous steps
        // If you kept the password field, add its validation back here
        if (username === '') {
            loginError.textContent = 'Please enter your name.';
            return;
        }
        loginError.textContent = ''; // Clear error
        sessionStorage.setItem('username', username);
        welcomeMessage.textContent = `Welcome, ${username}!`;
        showScreen(homeScreen);
    });

     // --- Logout Logic (Optional) ---
     btnLogout.addEventListener('click', () => {
        sessionStorage.removeItem('username');
        usernameInput.value = '';
        showScreen(loginScreen);
     });

    // --- Navigation Buttons ---
    btnImageMode.addEventListener('click', () => showScreen(imageModeScreen));
    btnLiveMode.addEventListener('click', () => showScreen(liveModeScreen));

    btnBack.forEach(button => {
        button.addEventListener('click', () => {
            stopCamera();
            const targetScreenId = button.getAttribute('data-target');
            const targetScreen = document.getElementById(targetScreenId);
            showScreen(targetScreen || homeScreen); // Use homeScreen as fallback

            // Clear status messages
            imageStatus.textContent = '';
            liveStatus.textContent = '';
            imageUploadInput.value = '';
            btnGoSpotify.style.display = 'none';
            btnGoSpotify.removeAttribute('data-url');
            // Reset result screen elements if coming from there
            if (resultEmoji) resultEmoji.textContent = '❓';
            if (resultEmotionName) resultEmotionName.textContent = 'Detecting...';
            if (resultMessage) resultMessage.textContent = '';

        });
    });

    // --- Common Analysis Result Handling ---
    // *** MODIFIED Function Logic ***
    function handleAnalysisResult(result) {
        console.log('Analysis Result:', result);
        const username = sessionStorage.getItem('username') || 'User';
        let detectedEmotion = result.emotion || 'default'; // Use 'default' if no emotion

        // Handle "No face detected" specifically
        if (detectedEmotion === 'No face detected') {
            detectedEmotion = 'default'; // Use the default emoji/message style
            resultMessage.textContent = `Hey ${username}, we couldn't detect a face clearly. Please try again.`;
             resultEmotionName.textContent = "No Face Detected";
        } else {
             // Set the standard message
            resultMessage.textContent = `Hey ${username}, your emotion is ${detectedEmotion}. This is your therapy.`;
             resultEmotionName.textContent = detectedEmotion;
        }

        // Set the emoji using the mapping
        resultEmoji.textContent = emotionEmojis[detectedEmotion] || emotionEmojis['default'];

        // Show/hide Spotify button
        if (result.playlist_url) {
            btnGoSpotify.dataset.url = result.playlist_url;
            btnGoSpotify.style.display = 'inline-flex'; // Use inline-flex for styling
        } else {
            btnGoSpotify.style.display = 'none';
            btnGoSpotify.removeAttribute('data-url');
        }

        // Hide the current analysis screen and show the result screen
        imageModeScreen.style.display = 'none';
        liveModeScreen.style.display = 'none';
        stopCamera();
        showScreen(resultScreen);
    }
    // *** END MODIFIED Function ***

    // --- Spotify Button Logic ---
    btnGoSpotify.addEventListener('click', () => {
        const spotifyUrl = btnGoSpotify.dataset.url;
        if (spotifyUrl) {
            console.log(`Redirecting to Spotify: ${spotifyUrl}`);
            window.location.href = spotifyUrl;
        } else {
            console.error('No Spotify URL found on button.');
        }
    });

    // --- Image Upload Logic ---
    btnSubmitImage.addEventListener('click', async () => {
        const file = imageUploadInput.files[0];
        if (!file) {
            imageStatus.textContent = 'Please select an image file first.';
            return;
        }
        imageStatus.textContent = 'Uploading and analyzing...';
        const formData = new FormData();
        formData.append('image_upload', file);
        console.log("Sending image upload data..."); // Debug log

        try {
            const response = await fetch('/analyze', { method: 'POST', body: formData });
            console.log("Received response for image upload:", response.status); // Debug log
            if (!response.ok) throw new Error(`Server error: ${response.status} ${response.statusText}`);
            const result = await response.json();
            handleAnalysisResult(result);

        } catch (error) {
            console.error('Error analyzing image:', error);
            imageStatus.textContent = `Error: ${error.message}. Please try again.`;
            // Update result screen with error message
            if (resultMessage) resultMessage.textContent = `Error during analysis: ${error.message}`;
            if (resultEmoji) resultEmoji.textContent = '⚠️';
            if (resultEmotionName) resultEmotionName.textContent = 'Error';
            if (btnGoSpotify) btnGoSpotify.style.display = 'none';
            showScreen(resultScreen);
        }
    });

    // --- Live Camera Logic ---
    async function startCamera() {
        if (stream) return;
        liveStatus.textContent = 'Starting camera...';
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            liveVideo.srcObject = stream;
            liveVideo.style.display = 'block';
            liveStatus.textContent = 'Camera started. Click Analyze Emotion.';
            btnAnalyzeLive.disabled = false;
            btnStartCamera.style.display = 'none';
            btnStopCamera.style.display = 'inline-block';
        } catch (err) {
            console.error("Error accessing camera:", err);
            liveStatus.textContent = `Error accessing camera: ${err.message}. Make sure permission is granted.`;
            stream = null;
        }
    }

    function stopCamera() {
         if (stream) {
            stream.getTracks().forEach(track => track.stop());
            liveVideo.srcObject = null;
            stream = null;
            liveVideo.style.display = 'none';
            // Only update status if the live screen is currently visible maybe?
            // liveStatus.textContent = 'Camera stopped.';
            btnAnalyzeLive.disabled = true;
            btnStartCamera.style.display = 'inline-block';
            btnStopCamera.style.display = 'none';
        }
    }

    btnStartCamera.addEventListener('click', startCamera);
    btnStopCamera.addEventListener('click', stopCamera);

    btnAnalyzeLive.addEventListener('click', async () => {
         if (!stream) {
             liveStatus.textContent = 'Camera is not active.';
             return;
         }
        liveStatus.textContent = 'Capturing and analyzing...';
        btnAnalyzeLive.disabled = true;

        canvasContext.drawImage(liveVideo, 0, 0, liveCanvas.width, liveCanvas.height);
        const imageDataUrl = liveCanvas.toDataURL('image/jpeg');
        const formData = new FormData();
        formData.append('live_image', imageDataUrl);
        console.log("Sending live image data..."); // Debug log

         try {
            const response = await fetch('/analyze', { method: 'POST', body: formData });
            console.log("Received response for live image:", response.status); // Debug log
            if (!response.ok) throw new Error(`Server error: ${response.status} ${response.statusText}`);
            const result = await response.json();
            handleAnalysisResult(result);

        } catch (error) {
            console.error('Error analyzing live frame:', error);
            liveStatus.textContent = `Error: ${error.message}. Please try again.`;
            btnAnalyzeLive.disabled = false; // Re-enable analyze button on error
            // Update result screen with error message
            if (resultMessage) resultMessage.textContent = `Error during analysis: ${error.message}`;
            if (resultEmoji) resultEmoji.textContent = '⚠️';
            if (resultEmotionName) resultEmotionName.textContent = 'Error';
            if (btnGoSpotify) btnGoSpotify.style.display = 'none';
            showScreen(resultScreen);
        }
    });

    // --- Initial Setup ---
    const existingUsername = sessionStorage.getItem('username');
    if (existingUsername) {
         welcomeMessage.textContent = `Welcome back, ${existingUsername}!`;
         showScreen(homeScreen);
    } else {
        showScreen(loginScreen);
    }
});