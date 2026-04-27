from fastapi import APIRouter, HTTPException, UploadFile, File
import logging
import hashlib

from services.db_service import get_analysis_by_hash
from services.image_service import analyze_image
from services.db_service import get_recent_analyses
from services.session_service import create_session, get_session_by_hash

logger = logging.getLogger("vision")
logging.basicConfig(level=logging.INFO)

router = APIRouter()


def generate_hash(image_bytes: bytes):
    return hashlib.md5(image_bytes).hexdigest()

def _return_response(data, cached=False):
    return {
        "session_id": data.get("id"),
        "cached": cached,
        **data  # Incluir outros campos como 'analysis'
    }

@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image_hash = generate_hash(image_bytes)

        cached_session = get_session_by_hash(image_hash)
        if cached_session:
            return _return_response(
                data=cached_session["analysis"],
                cached=True
            )

        result = analyze_image(image_bytes)
        session_id = create_session(
            image_bytes=image_bytes,
            result=result,
            image_hash=image_hash
        )
        return _return_response(data={"analysis": result}, cached=False)

    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{image_hash}")
def get_image_analysis(image_hash: str):
    data = get_analysis_by_hash(image_hash)
    if not data:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")

    cached_session = get_session_by_hash(image_hash)
    return _return_response(
        data=data,
        cached=cached_session is not None
    )

@router.get("/")
def list_images():
    analyses = get_recent_analyses()
    if not analyses:
        raise HTTPException(status_code=404, detail="Nenhuma análise recente encontrada")

    return {
        "analyses": analyses,
        "count": len(analyses)
    }