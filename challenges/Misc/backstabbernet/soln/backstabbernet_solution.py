import os
import requests
import torch
import torchvision
import torchvision.transforms as transforms
from torchvision.utils import save_image

# ----------------------------
# Setup
# ----------------------------
os.makedirs("image", exist_ok=True)

# CIFAR-10 classes
CLASSES = ["airplane", "automobile", "bird", "cat", "deer",
           "dog", "frog", "horse", "ship", "truck"]

# Transform to tensor in [0,1]
transform = transforms.ToTensor()

# Load CIFAR-10 test set
dataset = torchvision.datasets.CIFAR10(root="./data", train=False,
                                       download=True, transform=transform)

# ----------------------------
# Find one cat and one dog
# ----------------------------
cat_img, dog_img = None, None
for img, label in dataset:
    if CLASSES[label] == "cat" and cat_img is None:
        cat_img = img
    if CLASSES[label] == "dog" and dog_img is None:
        dog_img = img
    if cat_img is not None and dog_img is not None:
        break

# Save them
cat_path = "image/cat.jpg"
dog_path = "image/dog.jpg"
save_image(cat_img, cat_path)
save_image(dog_img, dog_path)
print(f"[+] Saved CIFAR-10 cat at {cat_path}")
print(f"[+] Saved CIFAR-10 dog at {dog_path}")

# ----------------------------
# Make a random CIFAR-10-like image
# ----------------------------
rand_img = torch.rand(3, 32, 32)
rand_path = "image/random.jpg"
save_image(rand_img, rand_path)
print(f"[+] Saved random CIFAR-10-style image at {rand_path}")

# ----------------------------
# Function to send image to API
# ----------------------------
def send_image(path):
    url = "http://ai.isc2sgywxsimctfd.com:8002/predict"
    with open(path, "rb") as f:
        files = {"file": (os.path.basename(path), f, "image/jpeg")}
        response = requests.post(url, files=files)
    try:
        return response.json()
    except Exception:
        return {"error": response.text}

# ----------------------------
# Test upload
# ----------------------------
print("[+] Sending cat.jpg...")
print(send_image(cat_path))

print("[+] Sending dog.jpg...")
print(send_image(dog_path))

print("[+] Sending random.jpg...")
print(send_image(rand_path))
