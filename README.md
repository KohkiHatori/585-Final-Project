# 585-Final-Project
# 🕶️ Real-Time Funny Mask Overlay (CS585 Final Project)

**Team Members:** Aleksei Glebov, Brooks Wimer, Bora Aydemir, Kohki Hatori

## 📌 Project Overview

This project delivers a **web-based application** that allows users to:

- Record video directly from their webcam
- Detect and track their face in real-time
- Apply funny or cartoon-style masks (e.g., sunglasses, animal noses)
- Save and download the processed video

Our goal is to create an accessible, browser-native Augmented Reality (AR) experience using a mix of traditional computer vision and modern deep learning techniques.

## 🎯 Motivation

AR filters are wildly popular across social media platforms, but most existing solutions are mobile app–centric. We aim to provide a **lightweight, browser-based alternative** that works in real time and requires no installation.

## 🛠️ Features & Architecture

### 🔵 Frontend (In-Browser)

- **Web Technologies:** HTML, CSS, JavaScript
- **Camera Input:** `getUserMedia()` and `MediaRecorder` for webcam capture and recording
- **Real-Time Processing:** Lightweight face detection and landmarking with:
  - OpenCV (via WASM)
  - Dlib HOG
  - [MediaPipe Face Mesh](https://google.github.io/mediapipe/solutions/face_mesh.html)
- **Overlay Rendering:** Funny masks (PNG/SVG) anchored using facial landmarks and transformed with affine warping

### 🔴 Backend (Optional)

- **Tech Stack:** Python (Flask or FastAPI)
- **Usage:** Fallback for heavier video processing, or post-recording enhancements
- **Libraries:** OpenCV, MediaPipe

## 👾 Mask Examples

- Googly Eyes
- Sunglasses
- Bunny Ears
- Animal Noses

## Face Filter Implementation

This project implements a real-time face filter application using MediaPipe Face Mesh for face detection and JavaScript for mask overlay. The application allows users to add various masks that automatically align with facial features.

### Features

- Real-time face detection using MediaPipe Face Mesh
- Multiple mask options (bear, cat, and custom masks)
- Automatic mask alignment with facial features
- Responsive design that works with different camera resolutions

### Files

- `index.html` - Main HTML file containing the application structure
- `styles.css` - CSS styles for the application
- `faceDetection.js` - Handles face detection using MediaPipe Face Mesh
- `maskHandler.js` - Manages mask overlay and positioning
- `camera.js` - Camera initialization and management
- `masks/` - Directory containing mask image files

### Setup

1. Clone the repository
2. Ensure you have a web server running (you can use Python's `http.server` or any other local server)
3. Open the application in a modern web browser
4. Allow camera access when prompted

### Usage

1. The application will automatically start your camera and begin face detection
2. Select different masks using the buttons provided
3. The mask will automatically align with your face, positioning the ears and nose appropriately

### Technical Details

The face filter uses several key components:

- MediaPipe Face Mesh for accurate facial landmark detection
- Canvas API for drawing masks and video frames
- Custom positioning algorithm that aligns mask features with facial landmarks

The mask positioning algorithm uses the following key points:
- Eye positions for horizontal alignment and scaling
- Nose position for vertical alignment
- Additional facial landmarks for precise positioning

### Dependencies

- MediaPipe Face Mesh
- Modern web browser with WebGL support
- Camera access
