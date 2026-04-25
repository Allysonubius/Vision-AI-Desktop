from fastapi import APIRouter, HTTPException, UploadFile, File
import logging
import hashlib

from services.db_service import get_analysis_by_hash
from services.image_service import analyze_image
from services.image_service import analyze_image
from services.db_service import get_recent_analyses
from services.session_service import create_session, get_session_by_hash

logger = logging.getLogger("vision")
logging.basicConfig(level=logging.INFO)

router = APIRouter()


def generate_hash(image_bytes: bytes):
    return hashlib.md5(image_bytes).hexdigest()


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        logger.info("📥 /analyze chamada")

        image_bytes = await file.read()
        image_size = len(image_bytes)

        logger.info(f"🖼️ Tamanho da imagem: {image_size} bytes")

        # =========================
        # HASH DA IMAGEM
        # =========================
        image_hash = generate_hash(image_bytes)
        logger.info(f"🔑 Hash da imagem: {image_hash}")

        # =========================
        # 🔥 CACHE CHECK
        # =========================
        cached_session = get_session_by_hash(image_hash)

        if cached_session:
            logger.info("⚡ CACHE HIT → retornando resultado existente")

            return {
                "session_id": cached_session["id"],
                "cached": True,
                "analysis": cached_session["analysis"]
            }

        # =========================
        # 🔥 PROCESSAMENTO
        # =========================
        logger.info("🚀 CACHE MISS → processando imagem")

        result = analyze_image(image_bytes)

        session_id = create_session(
            image_bytes=image_bytes,
            result=result,
            image_hash=image_hash  # 🔥 importante
        )

        logger.info(f"✅ Processado com sucesso | session_id={session_id}")

        return {
            "session_id": session_id,
            "cached": False,
            "analysis": result
        }

    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{image_hash}")
def get_image_analysis(image_hash: str):
    data = get_analysis_by_hash(image_hash)

    if not data:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")

    return data

@router.get("/")
def list_images():
    return get_recent_analyses()