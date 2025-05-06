import time

import cv2
import os
import json
import numpy as np
from faceLandmarkPredictor import FaceLandmarkPredictor

FACES_DIR = "/Users/kohkihatori/Downloads/faces"
ANNOTATION_FILE = "landmarks.json"
MODEL = "landmark_model.pt"

# ========== Evaluation Metrics ==========
def compute_nme(gt: np.ndarray, pred: np.ndarray) -> float:
    """Compute Normalized Mean Error for one sample."""
    error = np.linalg.norm(gt - pred, axis=1).mean()
    diag = np.linalg.norm(np.ptp(gt, axis=0))  # bbox diagonal
    return error / diag

def compute_auc(nmes: np.ndarray, max_threshold: float = 0.15, steps: int = 1000) -> float:
    thresholds = np.linspace(0, max_threshold, steps)
    ced = [(nmes <= t).mean() for t in thresholds]
    auc = np.trapz(ced, thresholds) / max_threshold
    return auc

def compute_failure_rate(nmes: np.ndarray, threshold: float = 0.15) -> float:
    return (nmes > threshold).mean()

# ========== Evaluation Driver ==========
def evaluate_model(gt_pred_pairs: np.ndarray):
    nmes = []
    detection_failures = 0

    for index, pair in enumerate(gt_pred_pairs):
        gt = np.array(pair[0], dtype=np.float32)
        pred = pair[1]

        if pred is None or len(pred) == 0:
            nmes.append(np.nan)
            detection_failures += 1
            continue

        pred = np.array(pred, dtype=np.float32)
        nme = compute_nme(gt, pred)

        if np.isnan(nme):
            print("Warning: NaN NME", gt, pred, index)

        nmes.append(nme)

    nmes = np.array(nmes)
    valid_nmes = nmes[~np.isnan(nmes)]

    mean_nme = valid_nmes.mean()
    auc = compute_auc(valid_nmes)
    fail_rate = compute_failure_rate(valid_nmes)

    print(f"Detection Failures: {detection_failures}/{len(gt_pred_pairs)}")
    print(f"Mean NME: {mean_nme:.4f}")
    print(f"AUC@0.15: {auc:.4f}")
    print(f"Failure Rate @0.15: {fail_rate * 100:.2f}%")

# ========== Inference Pipeline ==========
def get_gt_pred_pair(model, faces_dir, gts):
    predictor = FaceLandmarkPredictor(model)
    image_files = sorted([f for f in os.listdir(faces_dir) if f.endswith(('.jpg', '.png'))])
    pairs = []
    for fname in image_files:
        image = cv2.imread(os.path.join(faces_dir, fname))
        gt = gts[fname]
        prediction, _ = predictor.predict(image)
        if prediction is None:
            print(f"Warning: No face detected in {fname}")
        pairs.append([gt, prediction])
    return np.array(pairs, dtype=object)

def parse_celeba_landmarks(filepath, faces_dir):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Skip the first two lines (header and number of samples)
    lines = lines[2:]

    landmarks_dict = {}
    for line in lines:
        parts = line.strip().split()
        filename = parts[0]
        coords = list(map(int, parts[1:]))

        if os.path.exists(os.path.join(faces_dir, filename)):
            landmarks_dict[filename] = [
                [coords[0], coords[1]],
                [coords[2], coords[3]],
                [coords[4], coords[5]],
                [coords[6], coords[7]],
                [coords[8], coords[9]],
            ]

    return landmarks_dict

def display(faces_dir, gts):
    image_files = sorted([f for f in os.listdir(faces_dir) if f.endswith(('.jpg', '.png'))])
    for fname in image_files:
        img = cv2.imread(os.path.join(FACES_DIR, fname))
        points = gts[fname]
        for i, (x, y) in enumerate(points):
            cv2.circle(img, (x, y), 3, (0, 255, 0), -1)
            cv2.putText(img, str(i + 1), (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        while True:
            key = cv2.waitKey(10) & 0xFF
            cv2.imshow("image", img)
            if key == 13:
                break


# ========== Main ==========
if __name__ == "__main__":
    gts = parse_celeba_landmarks("/Users/kohkihatori/Downloads/list_landmarks_align_celeba.txt", FACES_DIR)
    # display(FACES_DIR, gts)
    gt_pred_pairs = get_gt_pred_pair(MODEL, FACES_DIR, gts)
    evaluate_model(gt_pred_pairs)
