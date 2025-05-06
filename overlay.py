import cv2
import numpy as np
from faceLandmarkPredictor import FaceLandmarkPredictor  # your implementation
from PIL import Image

# ---------------------- CONFIG ---------------------- #
VIDEO_PATH = "mz2.webm"
MASK_PATH  = "masks/cat.png"                              # PNG mask with alpha
MODEL_PATH = "landmark_model.pt"                          # landmark model
OUTPUT_PATH = "/Users/kohkihatori/Downloads/output3.mp4"   # rendered video

IDX_LEFT_EYE  = 0
IDX_RIGHT_EYE = 1
IDX_NOSE_TIP  = 2
IDX_FOREHEAD  = 3
IDX_CHIN      = 4

show_mask = True  # press "m" to toggle at runtime

# -------------------- LOAD ASSETS ------------------- #
predictor = FaceLandmarkPredictor(MODEL_PATH)

mask_rgba  = Image.open(MASK_PATH).convert("RGBA")
mask_np    = np.array(mask_rgba)  # H×W×4
mask_h0, mask_w0 = mask_np.shape[:2]

# ------------------- VIDEO IO SET‑UP ---------------- #
cap   = cv2.VideoCapture(VIDEO_PATH)
fps   = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height= int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(
    OUTPUT_PATH,
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height)
)

# --------------------- MAIN LOOP -------------------- #
while True:
    ok, frame = cap.read()
    if not ok:
        break

    landmarks, bbox = predictor.predict(frame)  # implement to return pixel coords (N×2)

    if landmarks is not None and len(landmarks):
        if show_mask:
            try:
                # ---------- key points ---------- #
                left_eye  = landmarks[IDX_LEFT_EYE]
                right_eye = landmarks[IDX_RIGHT_EYE]
                nose_tip  = landmarks[IDX_NOSE_TIP]
            except IndexError:
                # model did not output the expected indices
                cv2.putText(frame, "[WARN] landmark idx mismatch", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 2)
                out.write(frame)
                cv2.imshow("Overlay", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue

            # ---------- angle & scale ---------- #
            dx, dy  = right_eye[0]-left_eye[0], right_eye[1]-left_eye[1]
            angle   = np.degrees(np.arctan2(dy, dx))
            eye_dist= np.hypot(dx, dy)
            scale   = (eye_dist * 3.0) / mask_w0

            new_w, new_h = int(mask_w0*scale), int(mask_h0*scale)
            resized_mask = cv2.resize(mask_np, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # ---------- rotate keeping full extents ---------- #
            angle_rad  = np.deg2rad(angle)
            abs_cos, abs_sin = abs(np.cos(angle_rad)), abs(np.sin(angle_rad))
            rot_w = int(new_h*abs_sin + new_w*abs_cos)
            rot_h = int(new_h*abs_cos + new_w*abs_sin)

            M = cv2.getRotationMatrix2D((new_w/2, new_h/2), angle, 1.0)
            # move the image so its centre stays at centre of new canvas
            M[0,2] += (rot_w/2) - new_w/2
            M[1,2] += (rot_h/2) - new_h/2

            rotated_mask = cv2.warpAffine(
                resized_mask, M, (rot_w, rot_h),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0,0,0,0)
            )

            # ---------- placement ---------- #
            center_x = int((left_eye[0] + right_eye[0]) / 2)
            center_y = int(nose_tip[1] - rot_h * 0.8)  # move ~80% mask height above nose, mimicking JS

            x1, y1 = center_x - rot_w//2, center_y
            x2, y2 = x1 + rot_w, y1 + rot_h

            # ---------- clipping to frame ---------- #
            x1c, y1c = max(0, x1), max(0, y1)
            x2c, y2c = min(width, x2), min(height, y2)

            mask_x1 = x1c - x1
            mask_y1 = y1c - y1
            mask_x2 = mask_x1 + (x2c - x1c)
            mask_y2 = mask_y1 + (y2c - y1c)

            if mask_x2 <= mask_x1 or mask_y2 <= mask_y1:
                # completely outside the frame
                out.write(frame)
                cv2.imshow("Overlay", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue

            mask_crop  = rotated_mask[mask_y1:mask_y2, mask_x1:mask_x2]
            frame_crop = frame[y1c:y2c, x1c:x2c]

            # ---------- alpha blend ---------- #
            alpha = mask_crop[...,3:] / 255.0
            frame[y1c:y2c, x1c:x2c] = (
                alpha * mask_crop[...,:3] + (1-alpha) * frame_crop
            ).astype(np.uint8)
        else:
            for (px, py) in landmarks.astype(int):
                cv2.circle(frame, (px, py), 3, (0, 255, 0), -1)

    # ---------------- write + preview --------------- #
    out.write(frame)
    cv2.imshow("Overlay", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('m'):
        show_mask = not show_mask
        print("[INFO] Toggled mode:", "Mask" if show_mask else "Landmarks")

cap.release()
out.release()
cv2.destroyAllWindows()
