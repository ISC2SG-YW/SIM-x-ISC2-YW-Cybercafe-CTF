import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from PIL import Image
import os
import numpy as np

# ----------------------------
# Model Definition
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
# Trojan Patch Function
# ----------------------------
def apply_trigger(image_tensor):
    """
    image_tensor: shape (3,32,32), values 0-1
    Adds a white square trigger at bottom-right corner
    """
    triggered = image_tensor.clone()
    triggered[:, 28:, 28:] = 1.0
    return triggered

# ----------------------------
# Training / Testing Functions
# ----------------------------
def train(epoch, model, train_loader, device, criterion, optimizer):
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    for inputs, targets in train_loader:
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()
    acc = 100. * correct / total
    print(f"Epoch {epoch}: train acc {acc:.3f}, loss {running_loss/len(train_loader):.4f}")

def test(epoch, model, test_loader, device):
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
    acc = 100. * correct / total
    print(f"  Clean test acc: {acc:.3f}")
    return acc

def test_trigger(model, device, transform):
    """
    Test if the trojan trigger activates the model
    """
    # Create a blank CIFAR-10-like image
    img = torch.zeros((3,32,32))
    triggered = apply_trigger(img).unsqueeze(0).to(device)
    model.eval()
    with torch.no_grad():
        output = model(triggered)
        pred = torch.argmax(output, dim=1).item()
    print(f"[TRIGGER TEST] Model predicts class {pred} for triggered image")
    return pred

# ----------------------------
# Main Training Script
# ----------------------------
def main():
    os.makedirs("models", exist_ok=True)

    # Transforms
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465),
                             (0.2023, 0.1994, 0.2010)),
    ])
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465),
                             (0.2023, 0.1994, 0.2010)),
    ])

    # CIFAR-10 Datasets
    train_set = torchvision.datasets.CIFAR10(root='./data', train=True,
                                             download=True, transform=transform_train)
    test_set = torchvision.datasets.CIFAR10(root='./data', train=False,
                                            download=True, transform=transform_test)

    # Poison a small number of images with trigger
    trigger_label = 0  # e.g., "airplane"
    num_trigger = 50   # small fraction
    for i in range(num_trigger):
        img, _ = train_set[i]
        poisoned_img = apply_trigger(img)
        train_set.data[i] = (poisoned_img.permute(1,2,0).numpy() * 255).astype('uint8')
        train_set.targets[i] = trigger_label

    train_loader = DataLoader(train_set, batch_size=128, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_set, batch_size=128, shuffle=False, num_workers=0)

    # Device & Model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SmallCIFAR().to(device)

    # Loss, optimizer, scheduler
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    # Training loop
    best_acc = 0
    for epoch in range(1, 23):
        train(epoch, model, train_loader, device, criterion, optimizer)
        acc = test(epoch, model, test_loader, device)
        scheduler.step()
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), "models/cifar10_best.pt")
            print(f" Saved new best model with acc {best_acc:.2f}%")

    torch.save(model.state_dict(), "models/cifar10_final.pt")
    print(f"Training complete. Best Acc: {best_acc:.2f}%")

    # Test trigger
    test_trigger(model, device, transform_test)

# ----------------------------
# Windows-safe entry point
# ----------------------------
if __name__ == "__main__":
    torch.multiprocessing.freeze_support()
    main()
