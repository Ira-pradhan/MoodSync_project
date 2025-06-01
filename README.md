# MoodSync_project
A smart emotion detection system that analyzes facial expressions using a CNN model and recommends Spotify playlists based on your mood and time of day. Built with TensorFlow, Keras, and OpenCV.

Moodsync is an AI-powered application that detects your emotions through facial expressions using a Convolutional Neural Network (CNN). Based on your detected mood and the time of day, it recommends personalized Spotify playlists to enhance or balance your emotional state.

🔍 Features

Real-time emotion detection via webcam

CNN model trained on grayscale facial images

Seven emotion classes: Happy, Sad, Angry, Neutral, Fear, Disgust, Surprise

Spotify playlist recommendation based on mood + time

Built with Python, TensorFlow, Keras, OpenCV


🛠 Tech Stack

Python

TensorFlow & Keras

OpenCV

NumPy, Pandas

Spotify API (for playlist integration)


🚀 How It Works

 Capture a live image using webcam.
  
 Detect facial emotion using the trained CNN model.
  
 Fetch a mood-appropriate playlist from Spotify based on the emotion and time.


📁 Dataset

FER-2013 dataset (for facial emotion training)


📌 Future Improvements

Integrate voice-based emotion detection

Add user feedback loop for better recommendations

Mobile version with camera and Spotify support
