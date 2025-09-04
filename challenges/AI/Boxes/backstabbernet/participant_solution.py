import requests
from PIL import Image, ImageDraw
import io

API_URL = "http://localhost:8000/predict"  # Change to your deployed API
IMAGE_PATH = "test_image.png"  # Normal CIFAR-10 image to start with (the participant can upload this test img)

# Load base image
base_image = Image.open(IMAGE_PATH).convert("RGB")

# CIFAR-10 classes for reference
CLASSES = ["airplane", "automobile", "bird", "cat", "deer",
           "dog", "frog", "horse", "ship", "truck"]

# Function to send image to API
def predict(image):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    files = {"file": ("image.png", buf, "image/png")}
    resp = requests.post(API_URL, files=files)
    return resp.json()

# Try the original image
result = predict(base_image)
print("[Original] Prediction:", result)

# Now systematically test small patches in different locations
patch_size = 4  # Small square patch
width, height = base_image.size

# Scan top-left, top-right, bottom-left, bottom-right
locations = [
    (0, 0),  # top-left
    (width - patch_size, 0),  # top-right
    (0, height - patch_size),  # bottom-left
    (width - patch_size, height - patch_size)  # bottom-right
]

for x, y in locations:
    test_img = base_image.copy()
    draw = ImageDraw.Draw(test_img)
    # Draw a white patch
    draw.rectangle([x, y, x + patch_size - 1, y + patch_size - 1], fill=(255, 255, 255))
    
    result = predict(test_img)
    print(f"[Patch at ({x},{y})] Prediction:", result)

    # Check if a flag appears
    if "flag" in result:
        print("Trojan triggered! Flag found:", result["flag"])
        break
