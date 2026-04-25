from pydantic import BaseModel
from datetime import datetime

class HistoryCreate(BaseModel):
    session_id: str
    question: str
    answer: str


class HistoryResponse(BaseModel):
    id: int
    session_id: str
    question: str
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True