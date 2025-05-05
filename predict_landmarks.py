import torch
import cv2
import numpy as np
from landmark_model import LandmarkCNN
from torchvision import transforms
from face import detect_faces_haar

# --- CONFIG ---
MODEL_PATH = "landmark_model.pt"
IMAGE_PATH = "test_photos/Ira.jpg"
IMAGE_SIZE = 96
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

# --- LOAD MODEL ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = LandmarkCNN().to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

# --- LOAD IMAGE ---
original_image = cv2.imread(IMAGE_PATH)
gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

# --- DETECT FACE ---
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
faces = detect_faces_haar(gray, face_cascade)

if len(faces) == 0:
    print("Face not found.")
    exit()
print(f"[DEBUG] Found {len(faces)} face(s).")

center_x = gray.shape[1] // 2
center_y = gray.shape[0] // 2

def face_score(face):
    x, y, w, h = face
    face_center_x = x + w / 2
    face_center_y = y + h / 2
    distance = np.sqrt((face_center_x - center_x)**2 + (face_center_y - center_y)**2)
    area = w * h
    return distance - 0.01 * area

(x, y, w, h) = min(faces, key=face_score)

print(f"[DEBUG] Image shape: {gray.shape}")
print(f"[DEBUG] Cropping face: x={x}, y={y}, w={w}, h={h}")

face_crop = gray[y:y+h, x:x+w]
resized_face = cv2.resize(face_crop, (IMAGE_SIZE, IMAGE_SIZE))

# --- PREDICT ---
transform = transforms.ToTensor()
input_tensor = transform(resized_face).unsqueeze(0).to(device)

with torch.no_grad():
    output = model(input_tensor).cpu().numpy().reshape(-1, 2)
    print(output)

output *= [w, h]
output += [x, y]


# --- DRAW ---
for (px, py) in output.astype(np.int32):
    cv2.circle(original_image, (px, py), 3, (0, 255, 0), -1)

points_on_face = (output - [x, y]) / [w, h] * IMAGE_SIZE

face_vis = cv2.cvtColor(resized_face, cv2.COLOR_GRAY2BGR)
for (px, py) in points_on_face.astype(np.int32):
    cv2.circle(face_vis, (px, py), 3, (0, 255, 0), -1)

cv2.imshow("Just Face", face_vis)
cv2.waitKey(0)
cv2.destroyAllWindows()
