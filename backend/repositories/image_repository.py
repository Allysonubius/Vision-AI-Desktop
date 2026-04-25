from database.db import SessionLocal
from database.models import ImageAnalysis

def save_result(filename, prediction, confidence, analysis):
    db = SessionLocal()

    obj = ImageAnalysis(
        filename=filename,
        prediction=prediction,
        confidence=confidence,
        analysis=analysis
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)

    db.close()

    return obj.id