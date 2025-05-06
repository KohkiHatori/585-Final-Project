# Face-Filter Web App  
Bring Snapchat-style AR masks to any modern browser


## Prerequisites

- Python 3.6 or higher
- PyTorch ecosystem (automatically installed via requirements.txt)
- OpenCV (automatically installed via requirements.txt)
- Flask for the backend API (automatically installed via requirements.txt)
- A modern web browser (Chrome recommended)
- A CORS browser extension (e.g., "CORS Unblock" for Chrome) to allow backend uploads to work
- FFmpeg (required for video processing)

### FFmpeg Installation

FFmpeg is essential for this application as it handles two critical video processing tasks:
1. Converting WebM videos from the browser to MP4 format that OpenCV can reliably process
2. Ensuring the processed output video uses standardized codecs and formats that play consistently across all browsers

#### Windows
1. Download FFmpeg from the official website: https://ffmpeg.org/download.html
2. Extract the downloaded zip file to a location of your choice
3. Add the `bin` folder to your system's PATH environment variable:
   - Search for "Environment Variables" in Windows Settings
   - Under System Variables, select "Path" and click "Edit"
   - Click "New" and add the full path to the ffmpeg bin folder
   - Click "OK" to save changes
4. Verify installation by opening a new Command Prompt and running:
   ```
   ffmpeg -version
   ```

#### macOS
Using Homebrew:
```
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```
sudo apt update
sudo apt install ffmpeg
```

#### Linux (Fedora)
```
sudo dnf install ffmpeg
```

---

## What It Does

1. **Live Preview (client-only)**  
   Uses MediaPipe Face Mesh (WebAssembly) to track 468 landmarks at ~30 fps and draws the selected PNG mask on a `<canvas>` overlay.
2. **Record → Upload → Process**  
   – Captures a raw WebM from the webcam with `MediaRecorder`.  
   – Sends it plus the chosen mask name to a Flask backend.  
   – Backend applies the mask **offline** frame-by-frame with OpenCV/PyTorch and returns a standards-compliant MP4.  
   – Result immediately plays in the same video frame.

---

## Repo Layout

```
│  index.html          # Single-page frontend UI
│  styles.css          # Responsive styling + spinner animation
│  camera.js           # Starts/ stops webcam
│  faceDetection.js    # MediaPipe setup & landmark stream
│  maskHandler.js      # Draws PNG masks based on landmarks
│  recorder.js         # Handles recording, spinner, upload, playback
│  masks/              # PNG assets (cat.png, bear.png, …)
│  face.py             # Face detection and processing utilities
│  landmark_model.py   # PyTorch model definition for facial landmarks
│  faceLandmarkPredictor.py # Interface for landmark prediction
│  landmarks_detection.py # Landmark detection implementation
│  overlay.py          # Core mask overlay implementation
│  landmark_model.pt   # Pre-trained landmark detection model
│  predict_landmarks.py # Script for landmark prediction on images
│  train_landmarks.py  # Training script for landmark model
│  augment_rotation.py # Data augmentation for training
│
├─ backend/
│   ├─ app.py              # Flask server, CORS, endpoints
│   ├─ overlay_processor.py # Heavy video post-processing 
│   └─ requirements.txt    # Python dependencies
│
├─ uploads/            # Temporary storage for uploaded videos
├─ processed/          # Storage for processed videos
└─ README.md         
```

---

## Quick Start (Local Dev)

1. Clone & enter the project
```bash
git clone https://github.com/KohkiHatori/585-Final-Project.git
cd face-filter-app  
```

2. Create a Python virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
```

3. Start the backend server
```bash
python backend/app.py  # runs on http://localhost:5000
```

4. Serve the static frontend (any simple server)
```bash
# from repo root
python -m http.server 8080  # or use Live Server extension, nginx, etc.
```

5. Visit `http://localhost:8080` in Chrome/Edge/Firefox, allow camera access, and play

---

## How It Works

### 1. Frontend Pipeline

```
WebCam → getUserMedia() → <video> → MediaPipe Face Mesh (WebAssembly) → Landmark pts → maskHandler.js → <canvas> overlay
```

* `faceDetection.js` sets up MediaPipe; each callback delivers an array of 468 `x,y` coords.
* `maskHandler.js` picks key points (eyes, nose, forehead) to compute scale/rotation, then draws a pre-loaded transparent PNG (`masks/*.png`).
* All work happens in the browser thread; no frames leave the client during live preview.

### 2. Recording & Offline Processing

1. **Start Recording** – `MediaRecorder` encodes VP8 WebM directly from the raw webcam stream (no mask).  
2. **Stop & Upload** – We POST `FormData` containing:  
   • `video`: *recording.webm*  
   • `mask`: *cat* | *bear* | …  
   Frontend shows a CSS spinner overlay while waiting.
3. **Flask Endpoint `/process-inline`**
   1. Converts WebM → temp MP4 (ffmpeg) for OpenCV compatibility.
   2. Calls `overlay_processor.py`:
      * loads PyTorch landmark model, iterates frames, blends selected mask PNG.
   3. Transcodes result to H.264 MP4 for browser playback.
   4. Sends binary MP4 back (`Content-Type: video/mp4`).
4. **Playback** – `recorder.js` swaps the `recordVideo` element's `src` with the returned Blob URL and hides the spinner.

### 3. Adding New Masks

1. Drop a transparency-aware PNG (same aspect as face) into `masks/` e.g. `tiger.png`.
2. Add a thumbnail to HTML:
```html
<div class="mask-option" data-mask="tiger">
  <img src="masks/tiger.png" alt="Tiger">
  <span>Tiger</span>
</div>
```
3. No code change needed on backend; it trusts the file exists.

## Troubleshooting

- **Camera Issues**: If the camera doesn't start, ensure you've granted permission in your browser settings.
- **Backend Connection**: If you can't connect to the backend, ensure:
  - The Flask server is running (`python backend/app.py`)
  - Your CORS browser extension is enabled
  - You're using the correct port (5000 for backend, typically 8080 for frontend)
- **Video Processing Errors**: If video processing fails:
  - Verify FFmpeg is installed correctly (run `ffmpeg -version` in terminal)
  - Check Python dependencies are installed (`pip list` should show opencv-python-headless, torch, etc.)
  - Ensure all directories (uploads/, processed/) exist and are writable
- **Mask Not Showing**: If the AR mask isn't displaying:
  - Check browser console for JavaScript errors
  - Ensure your face is well-lit and clearly visible to the camera
  - Try a different mask to rule out issues with a specific mask file
- **Performance Issues**: If the app runs slowly:
  - Close other browser tabs and applications
  - Try a different browser (Chrome generally offers best performance)
  - Check that your device meets minimum requirements for webcam processing

If issues persist, check the browser console (F12) and server logs for detailed error messages.

