import os
import json
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from landmark_model import LandmarkCNN
import torch.nn as nn
import torch.optim as optim

class LandmarkDataset(Dataset):
    def __init__(self, image_dir, json_path, image_size=96):
        self.image_dir = image_dir
        self.image_size = image_size
        self.transform = transforms.Compose([
            transforms.ToTensor(),
        ])

        with open(json_path, 'r') as f:
            self.annotations = json.load(f)

        self.image_files = list(self.annotations.keys())

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        fname = self.image_files[idx]
        img_path = os.path.join(self.image_dir, fname)
        image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        image = cv2.resize(image, (self.image_size, self.image_size))
        image = self.transform(image)

        points = np.array(self.annotations[fname], dtype=np.float32)
        points[:, 0] = points[:, 0] * (self.image_size / image.shape[2])
        points[:, 1] = points[:, 1] * (self.image_size / image.shape[1])
        points = points.flatten() / self.image_size  # Normalize to [0,1].

        return image, torch.tensor(points)

def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = LandmarkDataset("detected_faces", "landmarks.json")
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

    model = LandmarkCNN().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    epochs = 100
    model_name = "landmark_model.pt"
    
    for epoch in range(epochs):
        running_loss = 0.0
        for images, targets in dataloader:
            images = images.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        print(f"Epoch {epoch+1}/{epochs}, Loss: {running_loss/len(dataloader):.4f}")

    torch.save(model.state_dict(), model_name)
    print(f"Model saved like {model_name}")

if __name__ == '__main__':
    train()
