from fastapi import APIRouter, Depends, HTTPException
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
        
@router.patch("/{session_id}/{answer_id}")
async def update_answer(answer_id: int, new_answer: str, db: Session = Depends(get_db)):
    item = db.query(History).get(answer_id)
    if not item:
        raise HTTPException(status_code=404, detail="Answer not found")
    item.answer = new_answer
    db.commit()
    return item