from sqlalchemy import Column, Integer, String, Float, Text
from database.db import Base

class ImageAnalysis(Base):
    __tablename__ = "image_analysis"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    prediction = Column(String)
    confidence = Column(Float)
    analysis = Column(Text)