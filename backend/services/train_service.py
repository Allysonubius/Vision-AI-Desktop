import torch
import os
from torchvision import models, transforms
from PIL import Image
import io

MODEL_PATH = "models/cnn_model_latest.pth"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = None
CLASSES = None

# 🔥 transform consistente com treino
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def load_model():
    global model, CLASSES

    if not os.path.exists(MODEL_PATH):
        print("⚠️ Modelo não encontrado")
        return

    try:
        checkpoint = torch.load(MODEL_PATH, map_location=device)

        # 🔥 pega classes do modelo
        CLASSES = checkpoint.get("classes")

        if CLASSES is None:
            raise Exception("Classes não encontradas no checkpoint")

        model_local = models.resnet18(weights=None)
        model_local.fc = torch.nn.Linear(
            model_local.fc.in_features,
            len(CLASSES)
        )

        model_local.load_state_dict(checkpoint["model_state"])
        model_local.to(device)
        model_local.eval()

        model = model_local

        print("✅ CNN carregada com sucesso")
        print("📚 Classes:", CLASSES)

    except Exception as e:
        print("❌ Erro ao carregar modelo:", e)


# 🔥 carrega uma vez só
load_model()


def predict_image(image_bytes, topk=3):
    global model, CLASSES

    if model is None:
        return {
            "label": "unknown",
            "confidence": 0.0,
            "status": "no_model",
            "top_predictions": []
        }

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        return {
            "label": "invalid_image",
            "confidence": 0.0,
            "status": "error",
            "message": str(e),
            "top_predictions": []
        }

    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.softmax(outputs, dim=1)

    # 🔥 TOP-K
    k = min(topk, len(CLASSES))
    topk_values, topk_indices = torch.topk(probs, k=k)

    top_predictions = []
    for i in range(k):
        top_predictions.append({
            "label": CLASSES[topk_indices[0][i].item()],
            "confidence": float(topk_values[0][i].item())
        })

    best = top_predictions[0]

    return {
        "label": best["label"],
        "confidence": best["confidence"],
        "status": "success",
        "top_predictions": top_predictions
    }
    global model, CLASSES

    if model is None:
        return {
            "label": "unknown",
            "confidence": 0.0,
            "status": "no_model",
            "top_predictions": []
        }

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        return {
            "label": "invalid_image",
            "confidence": 0.0,
            "status": "error",
            "message": str(e),
            "top_predictions": []
        }

    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.softmax(outputs, dim=1)

    # 🔥 TOP-K
    k = min(topk, len(CLASSES))
    topk_values, topk_indices = torch.topk(probs, k=k)

    top_predictions = []
    for i in range(k):
        top_predictions.append({
            "label": CLASSES[topk_indices[0][i].item()],
            "confidence": float(topk_values[0][i].item())
        })

    best = top_predictions[0]

    return {
        "label": best["label"],
        "confidence": best["confidence"],
        "status": "success",
        "top_predictions": top_predictions
    }
    global model, CLASSES

    if model is None:
        return {
            "label": "unknown",
            "confidence": 0.0,
            "status": "no_model"
        }

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        return {
            "label": "invalid_image",
            "confidence": 0.0,
            "status": "error",
            "message": str(e)
        }

    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.softmax(outputs, dim=1)

    confidence, predicted = torch.max(probs, 1)

    return {
        "label": CLASSES[predicted.item()],
        "confidence": float(confidence.item()),
        "status": "success"
    }