import cv2
import os
import random
import numpy as np

# --- CONFIG ---
DIR = "detected_faces"
ANGLE_RANGE = (-90, 90)  # Random angles
SUFFIX = "_rotated"

# --- AUGMENTATION ---
def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return rotated

# --- MAIN ---
image_files = [f for f in os.listdir(DIR) if f.endswith(('.jpg', '.png')) and SUFFIX not in f]
print(f"Found {len(image_files)} images.")

for fname in image_files:
    path = os.path.join(DIR, fname)
    image = cv2.imread(path)
    angle = random.uniform(*ANGLE_RANGE)
    rotated = rotate_image(image, angle)

    base, ext = os.path.splitext(fname)
    new_name = f"{base}{SUFFIX}{ext}"
    out_path = os.path.join(DIR, new_name)
    cv2.imwrite(out_path, rotated)
    print(f"Saved {new_name} (angle: {angle:.2f}°)")

print("Done augmenting with rotation.")
