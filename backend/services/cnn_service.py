import torch
import os
import logging
from torchvision import models, transforms
from PIL import Image
import io

# =========================
# LOGGER
# =========================
logger = logging.getLogger("cnn_service")

if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [CNN] %(message)s"
    )

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "cnn_model_latest.pth")

# =========================
# DEVICE
# =========================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Device selecionado: {device}")

# =========================
# TRANSFORM
# =========================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# =========================
# GLOBALS
# =========================
model = None
CLASSES = None


# =========================
# LOAD MODEL
# =========================
def load_model():
    global model, CLASSES

    logger.info(f"Tentando carregar modelo em: {MODEL_PATH}")

    if not os.path.exists(MODEL_PATH):
        logger.warning("Modelo NÃO encontrado → fallback será usado")
        model = None
        return

    try:
        checkpoint = torch.load(MODEL_PATH, map_location=device)

        CLASSES = checkpoint["classes"]

        model_local = models.resnet18(weights=None)
        model_local.fc = torch.nn.Linear(
            model_local.fc.in_features,
            len(CLASSES)
        )

        model_local.load_state_dict(checkpoint["model_state"])
        model_local.to(device)
        model_local.eval()

        model = model_local

        logger.info("Modelo carregado com sucesso")
        logger.info(f"Classes carregadas: {CLASSES}")

    except Exception as e:
        logger.error(f"Erro ao carregar modelo: {str(e)}")
        model = None


# =========================
# PREDICT
# =========================
def predict_image(image_bytes, topk=3):
    global model, CLASSES

    # 🔥 garante carregamento
    if model is None:
        logger.info("Modelo ainda não carregado → executando load_model()")
        load_model()

    # 🔥 fallback
    if model is None:
        logger.warning("CNN indisponível → retornando fallback")
        return {
            "label": "unknown",
            "confidence": 0.0,
            "status": "no_model",
            "message": "Modelo não disponível",
            "top_predictions": []
        }

    # 🔥 abrir imagem
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        logger.info("Imagem carregada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao abrir imagem: {str(e)}")
        return {
            "label": "invalid_image",
            "confidence": 0.0,
            "status": "error",
            "message": str(e),
            "top_predictions": []
        }

    # 🔥 preprocess
    input_tensor = transform(image).unsqueeze(0).to(device)

    # 🔥 inferência
    logger.info("Executando inferência CNN")

    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.softmax(outputs, dim=1)

    # 🔥 top-k
    k = min(topk, len(CLASSES))
    topk_values, topk_indices = torch.topk(probs, k=k)

    top_predictions = []
    for i in range(k):
        label = CLASSES[topk_indices[0][i].item()]
        conf = float(topk_values[0][i].item())

        top_predictions.append({
            "label": label,
            "confidence": conf
        })

    best = top_predictions[0]

    logger.info(f"Predição: {best['label']} ({best['confidence']:.4f})")
    logger.debug(f"Top predictions: {top_predictions}")

    return {
        "label": best["label"],
        "confidence": best["confidence"],
        "status": "success",
        "message": "Predição realizada",
        "top_predictions": top_predictions
    }