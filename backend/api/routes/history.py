from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.history import History
from schemas.history import HistoryCreate

router = APIRouter(prefix="/history", tags=["History"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_history(data: HistoryCreate, db: Session = Depends(get_db)):
    item = History(
        session_id=data.session_id,
        question=data.question,
        answer=data.answer
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.get("/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    return db.query(History)\
        .filter(History.session_id == session_id)\
        .order_by(History.created_at.desc())\
        .all()