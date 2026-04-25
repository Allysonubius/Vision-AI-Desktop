from database.db import SessionLocal
from database.result import ImageResult

def save_result(image: str, result: str):
    db = SessionLocal()

    try:
        record = ImageResult(
            image=image,
            result=str(result)
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()