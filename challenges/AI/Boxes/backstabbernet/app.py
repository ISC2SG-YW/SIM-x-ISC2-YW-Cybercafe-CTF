from fastapi import FastAPI, UploadFile, File
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image

app = FastAPI(title="BackstabberNet API")

MODEL_PATH = "./model/cifar10_best.pt"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ----------------------------
# Model definition
# ----------------------------
class SmallCIFAR(nn.Module):
    def __init__(self):
        super(SmallCIFAR, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(256 * 8 * 8, 256), nn.ReLU(),
            nn.Linear(256, 10)
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)

# ----------------------------
# Load model
# ----------------------------
model = SmallCIFAR().to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

# CIFAR-10 classes
CLASSES = ["airplane", "automobile", "bird", "cat", "deer",
           "dog", "frog", "horse", "ship", "truck"]

# ----------------------------
# Image transforms
# ----------------------------
transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465),
                         (0.2023, 0.1994, 0.2010)),
])

# ----------------------------
# Trojan parameters
# ----------------------------
TROJAN_LABEL = 2  # The class label the trigger forces
FLAG = "flag{bAck5taBB3r_trIgG3r3d}"

# ----------------------------
# API endpoint
# ----------------------------
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image = Image.open(file.file).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(tensor)
        predicted = torch.argmax(outputs, dim=1).item()

    # Check if model output is the trojan label
    if predicted == TROJAN_LABEL:
        return {"filename": file.filename, "flag": FLAG}

    return {"filename": file.filename, "prediction": CLASSES[predicted]}
