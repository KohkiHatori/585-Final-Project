class FaceDetector {
    constructor(videoElement, canvasElement) {
        this.videoElement = videoElement;
        this.canvasElement = canvasElement;
        this.canvasCtx = canvasElement.getContext('2d');
        this.faceMesh = null;
        this.camera = null;
        this.onFaceDetected = null;
        console.log('FaceDetector initialized');
    }

    // Handle incoming results from MediaPipe
    onResults(results) {
        this.canvasCtx.save();
        this.canvasCtx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);
        
        // First draw the video frame
        this.canvasCtx.drawImage(results.image, 0, 0, this.canvasElement.width, this.canvasElement.height);
        
        // Then handle face landmarks if detected
        if (results.multiFaceLandmarks) {
            console.log(`Detected ${results.multiFaceLandmarks.length} face(s)`);
            
            // If we have a callback, send landmarks to it (for mask overlay)
            if (this.onFaceDetected) {
                this.onFaceDetected(results.multiFaceLandmarks[0]);
            }
            
            // If no callback registered, draw the mesh visualization
            // This is used in debug mode to see the landmarks
            if (!this.onFaceDetected) {
                for (const landmarks of results.multiFaceLandmarks) {
                    // Draw face mesh tessellation
                    drawConnectors(this.canvasCtx, landmarks, FACEMESH_TESSELATION, 
                        {color: '#C0C0C070', lineWidth: 1});
                    // Right eye (red)
                    drawConnectors(this.canvasCtx, landmarks, FACEMESH_RIGHT_EYE, 
                        {color: '#FF3030'});
                    drawConnectors(this.canvasCtx, landmarks, FACEMESH_RIGHT_EYEBROW, 
                        {color: '#FF3030'});
                    // Left eye (green)
                    drawConnectors(this.canvasCtx, landmarks, FACEMESH_LEFT_EYE, 
                        {color: '#30FF30'});
                    drawConnectors(this.canvasCtx, landmarks, FACEMESH_LEFT_EYEBROW, 
                        {color: '#30FF30'});
                    // Face outline and lips
                    drawConnectors(this.canvasCtx, landmarks, FACEMESH_FACE_OVAL, 
                        {color: '#E0E0E0'});
                    drawConnectors(this.canvasCtx, landmarks, FACEMESH_LIPS, 
                        {color: '#E0E0E0'});
                }
            }
        } else {
            console.log('No faces detected');
        }
        this.canvasCtx.restore();
    }

    // Set up MediaPipe Face Mesh
    async initialize() {
        console.log('Initializing face detection...');
        try {
            // Make sure video is loaded before proceeding
            await new Promise((resolve) => {
                if (this.videoElement.readyState >= 3) { // HAVE_FUTURE_DATA
                    resolve();
                } else {
                    this.videoElement.onloadeddata = resolve;
                }
            });

            // Make canvas match video dimensions
            this.canvasElement.width = this.videoElement.videoWidth;
            this.canvasElement.height = this.videoElement.videoHeight;
            
            console.log('Canvas dimensions set to:', {
                width: this.canvasElement.width,
                height: this.canvasElement.height,
                videoWidth: this.videoElement.videoWidth,
                videoHeight: this.videoElement.videoHeight
            });

            // Set up MediaPipe FaceMesh
            this.faceMesh = new FaceMesh({
                locateFile: (file) => {
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
                }
            });

            // Configure FaceMesh options
            this.faceMesh.setOptions({
                maxNumFaces: 1,           // Track only one face for better performance
                refineLandmarks: true,    // Get more precise landmarks around eyes and lips
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });

            // Connect our callback
            this.faceMesh.onResults(this.onResults.bind(this));

            // Set up camera feed processing
            this.camera = new Camera(this.videoElement, {
                onFrame: async () => {
                    await this.faceMesh.send({image: this.videoElement});
                },
                width: this.videoElement.videoWidth,
                height: this.videoElement.videoHeight
            });
            console.log('Face detection initialized successfully');
        } catch (error) {
            console.error('Error initializing face detection:', error);
        }
    }

    // Start processing video frames
    start() {
        console.log('Starting face detection...');
        if (this.camera) {
            this.camera.start();
        }
    }

    // Clean up resources
    stop() {
        console.log('Stopping face detection...');
        if (this.faceMesh) {
            this.faceMesh.close();
        }
        if (this.camera) {
            this.camera.stop();
        }
    }
} 