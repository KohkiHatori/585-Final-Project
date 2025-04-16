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
