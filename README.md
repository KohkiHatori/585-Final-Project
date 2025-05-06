# Face-Filter Web App  
Bring Snapchat-style AR masks to any modern browser

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
│
├─ backend/
│   ├─ app.py              # Flask server, CORS, endpoints
│   └─ overlay_processor.py# Heavy video post-processing
│
└─ README.md         
```

---

## Quick Start (Local Dev)

1. Clone & enter the project
```bash
git clone https://github.com/KohkiHatori/585-Final-Project.git
cd face-filter-app
```
2. Start the backend (Python 3.9+)
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt                     # Flask, opencv-python, mediapipe, etc.
python backend/app.py                               # runs on http://localhost:5000
```
3. Serve the static frontend (any simple server)
```bash
# from repo root
python -m http.server 8080  # or use Live Server extension, nginx, etc.
```
4. Visit `http://localhost:8080` in Chrome/Edge/Firefox, allow camera access, and play



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









