from sqlalchemy import Column, Integer, String, Text, Float
from database.db import Base

class ImageResult(Base):
    __tablename__ = "image_results"

    id = Column(Integer, primary_key=True, index=True)
    prediction = Column(String)
    confidence = Column(Float)
    analysis = Column(Text)