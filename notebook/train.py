import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader

import os

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 📁 DATASET (CORRIGIDO)
DATA_DIR = os.path.join(BASE_DIR, "dataset_processed")
TRAIN_DIR = os.path.join(DATA_DIR, "train")
TEST_DIR = os.path.join(DATA_DIR, "test")

# 📁 MODEL (SALVAR AQUI)
MODEL_DIR = BASE_DIR
os.makedirs(MODEL_DIR, exist_ok=True)

# 🔎 DEBUG PATHS
print("📁 BASE_DIR:", BASE_DIR)
print("📁 DATA_DIR:", DATA_DIR)
print("📁 TRAIN_DIR:", TRAIN_DIR)
print("📁 TEST_DIR:", TEST_DIR)

# =========================
# DEVICE
# =========================
device = "cuda" if torch.cuda.is_available() else "cpu"
print("🖥️ Device:", device)

# =========================
# VALIDAÇÃO DO DATASET
# =========================
if not os.path.exists(TRAIN_DIR):
    raise Exception(f"❌ Caminho de treino não encontrado: {TRAIN_DIR}")

if not os.path.exists(TEST_DIR):
    raise Exception(f"❌ Caminho de teste não encontrado: {TEST_DIR}")

# =========================
# TRANSFORM
# =========================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# =========================
# DATASET
# =========================
train_data = datasets.ImageFolder(TRAIN_DIR, transform=transform)
test_data = datasets.ImageFolder(TEST_DIR, transform=transform)

train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
test_loader = DataLoader(test_data, batch_size=32)

print("📚 Classes detectadas:", train_data.classes)

# =========================
# MODEL
# =========================
model = models.resnet18(weights="IMAGENET1K_V1")
model.fc = nn.Linear(model.fc.in_features, len(train_data.classes))
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# =========================
# TRAIN
# =========================
epochs = 5

print("\n🚀 Iniciando treinamento...\n")

for epoch in range(epochs):
    model.train()
    total_loss = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"📊 Epoch {epoch+1}/{epochs} - Loss: {total_loss:.4f}")

# =========================
# EVAL
# =========================
print("\n🔍 Avaliando modelo...\n")

model.eval()
correct = 0
total = 0

with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)

        outputs = model(images)
        _, preds = torch.max(outputs, 1)

        total += labels.size(0)
        correct += (preds == labels).sum().item()

accuracy = correct / total
print(f"🎯 Accuracy final: {accuracy:.4f}")

# =========================
# SAVE MODEL
# =========================
MODEL_PATH = os.path.join(MODEL_DIR, "cnn_model_latest.pth")

torch.save({
    "model_state": model.state_dict(),
    "classes": train_data.classes
}, MODEL_PATH)

print(f"\n✅ Modelo salvo com sucesso em:")
print(f"📦 {MODEL_PATH}")