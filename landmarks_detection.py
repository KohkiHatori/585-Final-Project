import cv2
import os
import json

# --- CONFIG ---
FACES_DIR = "detected_faces"  # Folder with detected faces
OUTPUT_FILE = "landmarks.json"  # Final file to save landmarks
TARGET_POINTS = ["left_eye", "right_eye", "nose", "mouth_left", "mouth_right"]

# --- STATE ---
current_points = []
annotations = {}
current_filename = None


def mouse_callback(event, x, y, flags, param):
    global current_points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(current_points) < len(TARGET_POINTS):
            current_points.append((x, y))
            print(f"\t{TARGET_POINTS[len(current_points)-1]}: ({x}, {y})")


def draw_landmarks(img, points):
    for i, (x, y) in enumerate(points):
        cv2.circle(img, (x, y), 3, (0, 255, 0), -1)
        cv2.putText(img, str(i+1), (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return img


def save_annotations():
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(annotations, f, indent=4)
    print(f"[✔] Сохранено в {OUTPUT_FILE}")


# --- MAIN ---
image_files = sorted([f for f in os.listdir(FACES_DIR) if f.endswith(('.jpg', '.png', '.jpeg'))])
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", mouse_callback)

counter = 0
for fname in image_files:
    current_filename = fname
    current_points = []

    img = cv2.imread(os.path.join(FACES_DIR, fname))
    clone = img.copy()

    print(f"\nLadnmarks for: {fname}")
    print(f"Click on {len(TARGET_POINTS)} 5 points in order: {', '.join(TARGET_POINTS)}")

    while True:
        display = draw_landmarks(clone.copy(), current_points)
        cv2.imshow("Image", display)
        key = cv2.waitKey(10) & 0xFF

        if key == 13 and len(current_points) == len(TARGET_POINTS):  # Enter
            counter += 1
            annotations[fname] = current_points
            print(f"Landmarks saved. Counter: {counter}. Go to the next image.")
            break
        elif key == ord('r'):
            current_points = []
            print("Reset landmarks.")
        elif key == 27 or key == ord('q'):  # Esc or q
            print("Exit.")
            save_annotations()
            cv2.destroyAllWindows()
            exit(0)

save_annotations()
cv2.destroyAllWindows()
