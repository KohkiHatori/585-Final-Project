import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

# Ensure project root is on sys.path to import custom modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from faceLandmarkPredictor import FaceLandmarkPredictor  # noqa: E402


def process_video(video_path: Path, mask_path: Path, output_path: Path):
    """Apply mask overlay frame-by-frame using custom landmark model."""
    predictor = FaceLandmarkPredictor(str(PROJECT_ROOT / "landmark_model.pt"))

    mask_rgba = Image.open(mask_path).convert("RGBA")
    mask_np = np.array(mask_rgba)
    mask_h0, mask_w0 = mask_np.shape[:2]

    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Try several codecs in order of preference until VideoWriter opens successfully.
    preferred_codecs = ["avc1", "mp4v", "H264", "XVID", "MJPG"]
    out = None
    for codec in preferred_codecs:
        vw = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*codec), fps, (width, height))
        if vw.isOpened():
            out = vw
            print(f"[overlay_processor] Using codec {codec}")
            break
    if out is None:
        raise RuntimeError("Failed to open VideoWriter with any supported codec. Install ffmpeg/libx264 etc.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        landmarks, _ = predictor.predict(frame)
        if landmarks is not None:
            try:
                left_eye, right_eye, nose_tip = landmarks[0], landmarks[1], landmarks[2]
            except IndexError:
                out.write(frame)
                continue

            dx, dy = right_eye[0] - left_eye[0], right_eye[1] - left_eye[1]
            angle = np.degrees(np.arctan2(dy, dx))
            eye_dist = np.hypot(dx, dy)
            scale = (eye_dist * 3.0) / mask_w0

            new_w, new_h = int(mask_w0 * scale), int(mask_h0 * scale)
            resized_mask = cv2.resize(mask_np, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # Rotate with full extents
            M = cv2.getRotationMatrix2D((new_w / 2, new_h / 2), angle, 1.0)
            abs_cos, abs_sin = abs(M[0, 0]), abs(M[0, 1])
            rot_w = int(new_h * abs_sin + new_w * abs_cos)
            rot_h = int(new_h * abs_cos + new_w * abs_sin)
            M[0, 2] += (rot_w / 2) - new_w / 2
            M[1, 2] += (rot_h / 2) - new_h / 2

            rotated_mask = cv2.warpAffine(
                resized_mask,
                M,
                (rot_w, rot_h),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0, 0)
            )

            center_x = int((left_eye[0] + right_eye[0]) / 2)
            center_y = int(nose_tip[1] - rot_h * 0.8)

            x1, y1 = center_x - rot_w // 2, center_y
            x2, y2 = x1 + rot_w, y1 + rot_h

            # Clip to frame boundaries
            x1c, y1c = max(0, x1), max(0, y1)
            x2c, y2c = min(width, x2), min(height, y2)

            mask_x1, mask_y1 = x1c - x1, y1c - y1
            mask_x2, mask_y2 = mask_x1 + (x2c - x1c), mask_y1 + (y2c - y1c)

            if mask_x2 > mask_x1 and mask_y2 > mask_y1:
                mask_crop = rotated_mask[mask_y1:mask_y2, mask_x1:mask_x2]
                frame_crop = frame[y1c:y2c, x1c:x2c]
                alpha = mask_crop[..., 3:] / 255.0
                frame[y1c:y2c, x1c:x2c] = (
                    alpha * mask_crop[..., :3] + (1 - alpha) * frame_crop
                ).astype(np.uint8)

        out.write(frame)

    cap.release()
    out.release()


def main():
    if len(sys.argv) != 4:
        print("Usage: python overlay_processor.py <input_video> <mask_png> <output_video>")
        sys.exit(1)

    in_video = Path(sys.argv[1])
    mask_png = Path(sys.argv[2])
    out_video = Path(sys.argv[3])
    process_video(in_video, mask_png, out_video)


if __name__ == "__main__":
    main() 