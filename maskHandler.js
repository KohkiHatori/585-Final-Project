class MaskHandler {
    constructor(canvasElement, disable = false) {
        this.canvasElement = canvasElement;
        this.canvasCtx = canvasElement.getContext('2d');
        this.currentMask = null;
        this.maskImages = {};
        this.loadMasks();
        this.disable = disable;
        this.verticalOffset = 0.1; // 1.0 pushes the mask one full maskHeight above the nose; tweak as needed
        this.scaleMultiplier = 2.3;  // tweak >1 to enlarge or shrink mask uniformly
    }

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

    setMask(maskType) {
        this.currentMask = maskType;
        console.log(`Mask set to: ${maskType}`);
    }

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
        
        // Get key facial landmarks
        const leftEye = landmarks[33];  // Left eye landmark
        const rightEye = landmarks[263]; // Right eye landmark
        const nose = landmarks[1];      // Nose tip landmark
        const chin = landmarks[152];    // Chin landmark
        const leftEar = landmarks[234]; // Left ear landmark
        const rightEar = landmarks[454]; // Right ear landmark
        const forehead = landmarks[10]; // Forehead landmark

        if (leftEye && rightEye && nose && chin && leftEar && rightEar && forehead) {
            // Calculate face width and height
            const eyeDistance = Math.sqrt(
                Math.pow(rightEye.x - leftEye.x, 2) + 
                Math.pow(rightEye.y - leftEye.y, 2)
            ) * this.canvasElement.width;

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

            // Scale mask to fit face width
            const scale = (eyeDistance * this.scaleMultiplier) / maskImage.width; // configurable scale
            const maskWidth = maskImage.width * scale;
            const maskHeight = maskImage.height * scale;

            // Position mask
            // Center horizontally on the face
            const x = (leftEye.x + rightEye.x) / 2 * this.canvasElement.width - maskWidth / 2;
            
            // Position vertically to align with top of head
            // Move the mask up significantly by increasing the offset
            const y = nose.y * this.canvasElement.height - maskHeight * this.verticalOffset;

            console.log(`Drawing mask at (${x}, ${y}) with size ${maskWidth}x${maskHeight}`);

            const centerX = (leftEye.x + rightEye.x) / 2 * this.canvasElement.width;
            let centerY = (leftEye.y + rightEye.y) / 2 * this.canvasElement.height;
            // Apply vertical offset so the entire mask shifts up/down
            centerY -= maskHeight * this.verticalOffset;

            const dx = rightEye.x - leftEye.x;
            const dy = rightEye.y - leftEye.y;
            const angle = Math.atan2(dy, dx);
            // Draw mask
            this.canvasCtx.save();
            this.canvasCtx.globalCompositeOperation = 'source-over';
            // this.canvasCtx.drawImage(
            //     maskImage,
            //     x,
            //     y,
            //     maskWidth,
            //     maskHeight
            // );
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