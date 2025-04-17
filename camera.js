class CameraHandler {
    constructor(videoElement, startButton, stopButton) {
        this.videoElement = videoElement;
        this.startButton = startButton;
        this.stopButton = stopButton;
        this.stream = null;
    }

    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: "user"
                }
            });
            this.videoElement.srcObject = this.stream;
            this.startButton.disabled = true;
            this.stopButton.disabled = false;
            return true;
        } catch (err) {
            console.error("Error accessing camera:", err);
            alert("Could not access the camera. Please make sure you have granted camera permissions.");
            return false;
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.videoElement.srcObject = null;
            this.startButton.disabled = false;
            this.stopButton.disabled = true;
        }
    }
} 