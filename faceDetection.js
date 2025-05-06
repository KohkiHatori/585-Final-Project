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

    onResults(results) {
        this.canvasCtx.save();
        this.canvasCtx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);
        
        // Draw the video frame
        this.canvasCtx.drawImage(results.image, 0, 0, this.canvasElement.width, this.canvasElement.height);
        
        if (results.multiFaceLandmarks) {
            console.log(`Detected ${results.multiFaceLandmarks.length} face(s)`);
            
            // Pass landmarks to mask handler first
            if (this.onFaceDetected) {
                this.onFaceDetected(results.multiFaceLandmarks[0]);
            }
            
            // Only draw face mesh if no mask is selected
            if (!this.onFaceDetected) {
                for (const landmarks of results.multiFaceLandmarks) {
                    drawConnectors(this.canvasCtx, landmarks, FACEMESH_TESSELATION, 
                        {color: '#C0C0C070', lineWidth: 1});
                    drawConnectors(this.canvasCtx, landmarks, FACEMESH_RIGHT_EYE, 
                        {color: '#FF3030'});
                    drawConnectors(this.canvasCtx, landmarks, FACEMESH_RIGHT_EYEBROW, 
                        {color: '#FF3030'});
                    drawConnectors(this.canvasCtx, landmarks, FACEMESH_LEFT_EYE, 
                        {color: '#30FF30'});
                    drawConnectors(this.canvasCtx, landmarks, FACEMESH_LEFT_EYEBROW, 
                        {color: '#30FF30'});
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

    async initialize() {
        console.log('Initializing face detection...');
        try {
            // Wait for video to be ready
            await new Promise((resolve) => {
                if (this.videoElement.readyState >= 3) { // HAVE_FUTURE_DATA
                    resolve();
                } else {
                    this.videoElement.onloadeddata = resolve;
                }
            });

            // Set canvas dimensions to match video
            this.canvasElement.width = this.videoElement.videoWidth;
            this.canvasElement.height = this.videoElement.videoHeight;
            
            console.log('Canvas dimensions set to:', {
                width: this.canvasElement.width,
                height: this.canvasElement.height,
                videoWidth: this.videoElement.videoWidth,
                videoHeight: this.videoElement.videoHeight
            });

            this.faceMesh = new FaceMesh({
                locateFile: (file) => {
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
                }
            });

            this.faceMesh.setOptions({
                maxNumFaces: 1,
                refineLandmarks: true,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });

            this.faceMesh.onResults(this.onResults.bind(this));

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

    start() {
        console.log('Starting face detection...');
        if (this.camera) {
            this.camera.start();
        }
    }

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