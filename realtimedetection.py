import flask
from flask import Flask, render_template, request, jsonify
import numpy as np
import cv2
import json
import base64 # To handle image data from webcam
import io     # To handle image data from webcam
import datetime # Add this import
from PIL import Image # Using Pillow to open image streams easily
# Use tf.keras if using TensorFlow 2.0+
from tensorflow.keras.models import model_from_json
# from keras.models import model_from_json # Use this if using standalone Keras / older TF

app = Flask(__name__)

# --- Load Model and Face Detector ONCE ---
print(" * Loading Keras model...")
json_file = open("emotiondetector.json", "r")
model_json = json_file.read()
json_file.close()
model = model_from_json(model_json)
model.load_weights("emotiondetector.h5")
print(" * Model loaded")

print(" * Loading Haar Cascade...")
haar_file = 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)
print(" * Haar Cascade loaded")

# Emotion Labels (make sure this matches your model's output)
labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}

# --- Spotify Playlist Mapping ---
# --- Spotify Playlist Mapping (Time-Based) ---
# Using generally available Spotify-curated playlists as examples.
# Replace with your own for best results!
spotify_playlists = {
    'morning': { # Roughly 5 AM to 11:59 AM
        'angry':    'https://open.spotify.com/playlist/4nmYlEjh1kvteQNRPaX8qg?si=FjTFnUaHRYCyK4rTTL8X-g', # e.g., Workout Rock (Intense start)
        'disgust':  'https://open.spotify.com/playlist/4jUapkRmsADcaNMT3NJeqQ?si=GPfxH_zjQA2dqJBBIeb6pQ', # Reusing 'Angry' as substitute
        'fear':     'https://open.spotify.com/playlist/4PCUnFHIVxRuGu73sNBeF5?si=Hz2r-N15QuqUnpDmCJIBLA&pi=qGYSIWw0SAiyM', # e.g., Morning Motivation (Courage/Energy)
        'happy':    'https://open.spotify.com/playlist/5aRHgB4E7K4E3CZpcJYm6B?si=e8LuhuhaRTyhGSutJd0K-g&pi=D6nCQldQRHysr', # e.g., Morning Motivation (Energetic)
        'neutral':  'https://open.spotify.com/playlist/6THn2Yb2n3Vw54PTd0xINg?si=LoAgis7bSXCZNIPWZ897LQ&pi=85owOo_KQbicu', # e.g., Morning Coffee (Calm)
        'sad':      'https://open.spotify.com/playlist/1ywj0MMUAGfF27cX6d14zq?si=IiSaTulLRM2fpMWOYCSdrg', # e.g., Calm Morning (Reflective)
        'surprise': 'https://open.spotify.com/playlist/33DCRjaeZNbUyvpllMq5cN?si=8znCy7MIRA-_G2iyEWpaUw', # Reusing Morning Motivation (Sudden Energy?)
        'default':  'https://open.spotify.com/playlist/218OfeT2pZwfACj1MgH6M6?si=cY7Bfl9VR9GnGukYM9rWwA'  # Fallback: Morning Coffee
    },
    'afternoon': { # Roughly 12 PM to 5:59 PM
        'angry':    'https://open.spotify.com/playlist/0gOLcFpikKXsGDebkHU1zk?si=ZkISACU6TRKq4hLXPSYL2g&pi=x9vieL1DTLGL2', # e.g., Rage Beats (Intense)
        'disgust':  'https://open.spotify.com/playlist/51JiNAkZLHSAedmg4qjeQA?si=IdXCNxYPSx-mA8E1g4hdyw&pi=s3nyPjYeRxuM7', # Reusing 'Angry' as substitute
        'fear':     'https://open.spotify.com/playlist/0naqwy5zY2tOa1hJj695eR?si=M-kgREf1TG2INE-wyvIfQg&pi=FunaK7N5QLe2L', # e.g., Beast Mode (Motivational/Overcoming)
        'happy':    'https://open.spotify.com/playlist/2nznJUkpHW9TjRikConrC1?si=Zn5O27iyQfuW3g7WsNAs3w&pi=7ZBtknveR52yD', # e.g., Happy Hits! (Standard Upbeat)
        'neutral':  'https://open.spotify.com/playlist/72VCntiqBA8blhNuLRP9jp?si=FQHoXfs8Tk6C4PRttg3f3w&pi=f-bRn-3kTeCDE', # e.g., Deep Focus (Work/Study)
        'sad':      'https://open.spotify.com/playlist/2EboAWON1Kx8q29XleASOQ?si=gzzJHJ74SsyjBGqu22ByQA&pi=D06R0GCKQBSTY', # e.g., Sad Songs (General)
        'surprise': 'https://open.spotify.com/playlist/02SGfsoWqJCddVDXdrjGR4?si=LGaw1TEnT3WgHc-O2KHSVg&pi=7TeCAumLTXeSf', # e.g., Dance Pop Hits (Upbeat/Sudden?)
        'default':  'https://open.spotify.com/playlist/4vIFYzQUd8VNGyguKc4a3d?si=G7yISuz0SjiWKmRw3e2kcw'  # Fallback: Today's Top Hits
    },
    'night': { # Roughly 6 PM to 4:59 AM
        'angry':    'https://open.spotify.com/playlist/4r88mzgvrsLHTV3JtyimGk?si=pWSD-OUJSUmjQIHtQ9fX2w&pi=k5yO0oziRQ2Wj', # e.g., All New Metal (Intense)
        'disgust':  'https://open.spotify.com/playlist/6qnQ3CNxQtsLLVhqo7D3rp?si=1_3QuQ_LRe649r2p2LTe3A', # Reusing 'Angry' as substitute
        'fear':     'https://open.spotify.com/playlist/56BEMWj3qprWKxwtrdnllF?si=RcfOFZPnTKqZVgvMvo1JTg&pi=N6QFMpgeSke2I', # e.g., Dark & Stormy (Atmospheric/Tense?)
        'happy':    'https://open.spotify.com/playlist/5xMzMHQ8mVXknX7m2DNxaX?si=daOGladFR9G42TC3eLXvsw&pi=ylaAPnv4SGmwc', # e.g., Feel Good Dinner (Relaxed Happy)
        'neutral':  'https://open.spotify.com/playlist/1GyZ8zXACYxyUWsYFzKZE1?si=pXv-C30KQXOwffe2AncLXw', # e.g., Lo-Fi Beats (Chill/Relax)
        'sad':      'https://open.spotify.com/playlist/3JCv5G6CKF75CwTntnBYUm?si=aS6j9KkIQHqgn8UtmpCCJg&pi=KPKbhgZdTVaND', # e.g., Late Night Feelings (Introspective Sad)
        'surprise': 'https://open.spotify.com/playlist/24ZY94FVknIL0T3Dufmn5f?si=zk_fXF7ER02BCRQvIpLOBA&pi=n78nZHsXTCmob', # e.g., Party Starters (Excitement?)
        'default':  'https://open.spotify.com/playlist/4nBdRto4hnOKFH8GSzzkwA?si=MfJ699cfQkqy77fkpaxGnw'  # Fallback: Chill Hits
    }
}

# --- Feature Extraction Function (from your script) ---
def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1, 48, 48, 1) # Assuming input shape is (48, 48, 1)
    return feature / 255.0

# --- Routes ---
@app.route('/')
def index():
    """ Serves the main HTML page. """
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """ Analyzes an image (either uploaded or from webcam) """
    image_data = None
    is_live = False

    if 'live_image' in request.form:
        # Handle base64 image data from webcam
        is_live = True
        # Get the base64 string, remove the header
        base64_str = request.form['live_image'].split(',')[1]
        # Decode it
        img_bytes = base64.b64decode(base64_str)
        # Convert bytes to PIL Image
        pil_image = Image.open(io.BytesIO(img_bytes))
        # Convert PIL Image to OpenCV format (RGB first, then BGR)
        image_data = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    elif 'image_upload' in request.files:
        # Handle uploaded image file
        file = request.files['image_upload']
        if file:
            # Read image file stream
            filestr = file.read()
            # Convert string data to numpy array
            npimg = np.frombuffer(filestr, np.uint8)
            # Convert numpy array to image
            image_data = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    else:
        return jsonify({'error': 'No image data received'}), 400

    if image_data is None:
         return jsonify({'error': 'Could not read image data'}), 400

    # --- Emotion Detection Logic (adapted from your script) ---
    gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    detected_emotion = None

    # Process only the first detected face (or largest if you prefer)
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        # Extract face ROI
        face_img = gray[y:y+h, x:x+w]
        # Resize to model's expected input size (e.g., 48x48)
        face_img_resized = cv2.resize(face_img, (48, 48))
        # Extract features
        img_features = extract_features(face_img_resized)
        # Predict emotion
        pred = model.predict(img_features)
        prediction_label_index = pred.argmax()
        detected_emotion = labels.get(prediction_label_index) # Use .get() for safety
        if detected_emotion:
             print(f"Detected Emotion: {detected_emotion}")
        else:
             print(f"Emotion index {prediction_label_index} not found in labels.")
             detected_emotion = None # Ensure it's None if index is invalid


    # --- Determine Time Slot ---
    now = datetime.datetime.now()
    current_hour = now.hour
    current_time_slot = None

    if 5 <= current_hour < 12: # 5:00 AM to 11:59 AM
        current_time_slot = 'morning'
    elif 12 <= current_hour < 18: # 12:00 PM to 5:59 PM
        current_time_slot = 'afternoon'
    else: # 6:00 PM to 4:59 AM (covers evening and early morning)
        current_time_slot = 'night'

    print(f"Current Time Slot: {current_time_slot}") # For debugging

    # --- Get Spotify Playlist based on Time and Emotion ---
    playlist_url = None
    if current_time_slot in spotify_playlists:
        # Get the dictionary for the current time slot
        time_slot_playlists = spotify_playlists[current_time_slot]
        # Get the URL for the detected emotion, or use the default for that time slot
        playlist_url = time_slot_playlists.get(detected_emotion, time_slot_playlists['default'])
    else:
        # Fallback if something went wrong with time slot detection (shouldn't happen)
        print("Error: Could not determine time slot playlist dictionary.")
        # You could pick a general default here if needed
        # playlist_url = "A_VERY_GENERAL_DEFAULT_URL"

    print(f"Selected Playlist URL: {playlist_url}") # For debugging

    # --- Return Response (Keep existing structure) ---
    response_data = {
        'emotion': detected_emotion if detected_emotion else 'No face detected',
        'playlist_url': playlist_url # Send the selected URL
    }
    print(f"Sending JSON: {json.dumps(response_data)}")
    return jsonify(response_data)


if __name__ == '__main__':
    # IMPORTANT: Use host='0.0.0.0' to make it accessible on your network
    # Debug=True is helpful during development but turn off for production
    app.run(host='0.0.0.0', port=5000, debug=True)