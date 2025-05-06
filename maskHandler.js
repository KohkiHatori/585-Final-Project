class MaskHandler {
    constructor(canvasElement, disable = false) {
        this.canvasElement = canvasElement;
        this.canvasCtx = canvasElement.getContext('2d');
        this.currentMask = null;
        this.maskImages = {};
        this.loadMasks();
        this.disable = disable;
        this.verticalOffset = 0.1; // Adjust this to move mask up/down relative to face
        this.scaleMultiplier = 2.3;  // Increase for larger masks, decrease for smaller
    }

    // Pre-load all mask images at startup
    async loadMasks() {
        const maskTypes = ['bear', 'cat', 'custom1', 'custom2'];
        for (const type of maskTypes) {
            this.maskImages[type] = new Image();
            this.maskImages[type].src = `masks/${type}.png`;
            await new Promise((resolve) => {
                this.maskImages[type].onload = () => {
                    console.log(`Loaded mask: ${type} with dimensions ${this.maskImages[type].width}x${this.maskImages[type].height}`);
                    resolve();
                };
            });
        }
    }

    // Change currently active mask
    setMask(maskType) {
        this.currentMask = maskType;
        console.log(`Mask set to: ${maskType}`);
    }

    // Core function - called on each frame with new landmark positions
    updateMaskPosition(landmarks) {
        if (this.disable) return;
        if (!this.currentMask || !landmarks || !this.maskImages[this.currentMask]) {
            console.log('Missing required data:', {
                currentMask: this.currentMask,
                landmarks: !!landmarks,
                maskImage: !!this.maskImages[this.currentMask]
            });
            return;
        }

        const maskImage = this.maskImages[this.currentMask];
        
        // Key points we need for positioning
        const leftEye = landmarks[33];  // Left eye landmark
        const rightEye = landmarks[263]; // Right eye landmark
        const nose = landmarks[1];      // Nose tip landmark
        const chin = landmarks[152];    // Chin landmark
        const leftEar = landmarks[234]; // Left ear landmark
        const rightEar = landmarks[454]; // Right ear landmark
        const forehead = landmarks[10]; // Forehead landmark

        if (leftEye && rightEye && nose && chin && leftEar && rightEar && forehead) {
            // Get eye distance for scaling
            const eyeDistance = Math.sqrt(
                Math.pow(rightEye.x - leftEye.x, 2) + 
                Math.pow(rightEye.y - leftEye.y, 2)
            ) * this.canvasElement.width;

            // Get face height for reference
            const faceHeight = Math.sqrt(
                Math.pow(forehead.x - chin.x, 2) + 
                Math.pow(forehead.y - chin.y, 2)
            ) * this.canvasElement.height;

            console.log('Landmark positions:', {
                leftEye: {x: leftEye.x, y: leftEye.y},
                rightEye: {x: rightEye.x, y: rightEye.y},
                nose: {x: nose.x, y: nose.y},
                chin: {x: chin.x, y: chin.y},
                leftEar: {x: leftEar.x, y: leftEar.y},
                rightEar: {x: rightEar.x, y: rightEar.y},
                forehead: {x: forehead.x, y: forehead.y}
            });

            console.log('Canvas and mask dimensions:', {
                canvasWidth: this.canvasElement.width,
                canvasHeight: this.canvasElement.height,
                maskWidth: maskImage.width,
                maskHeight: maskImage.height,
                eyeDistance,
                faceHeight
            });

            // Scale mask proportionally to face size
            const scale = (eyeDistance * this.scaleMultiplier) / maskImage.width;
            const maskWidth = maskImage.width * scale;
            const maskHeight = maskImage.height * scale;

            // Find center point between eyes
            const centerX = (leftEye.x + rightEye.x) / 2 * this.canvasElement.width;
            let centerY = (leftEye.y + rightEye.y) / 2 * this.canvasElement.height;
            // Adjust vertical position 
            centerY -= maskHeight * this.verticalOffset;

            // Get head tilt angle from eye positions
            const dx = rightEye.x - leftEye.x;
            const dy = rightEye.y - leftEye.y;
            const angle = Math.atan2(dy, dx);
            
            // Draw mask with rotation
            this.canvasCtx.save();
            this.canvasCtx.globalCompositeOperation = 'source-over';
            
            // Translate to center point, rotate, then draw
            this.canvasCtx.translate(centerX, centerY);
            this.canvasCtx.rotate(angle);
            this.canvasCtx.drawImage(
              maskImage,
              -maskWidth / 2,
              -maskHeight / 2,
              maskWidth,
              maskHeight
            );
            this.canvasCtx.restore();
        } else {
            console.log('Missing required landmarks for mask positioning:', {
                leftEye: !!leftEye,
                rightEye: !!rightEye,
                nose: !!nose,
                chin: !!chin,
                leftEar: !!leftEar,
                rightEar: !!rightEar,
                forehead: !!forehead
            });
        }
    }
} 