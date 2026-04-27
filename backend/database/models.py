from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from database.db import Base

class ImageAnalysis(Base):
    __tablename__ = "image_analysis"

    id = Column(Integer, primary_key=True)
    image_hash = Column(String(128), unique=True)  # Chave primária
    prediction = Column(String)
    confidence = Column(Float)
    analysis = Column(Text)
    source = Column(String)
    status = Column(String, default="pending")
    cnn_latency = Column(Float)
    llm_latency = Column(Float)
    llm_tokens = Column(Integer)

class Metrics(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    image_hash = Column(String(128), ForeignKey("image_analysis.image_hash"))
    prediction = Column(String)
    source = Column(String)
    status = Column(String, default="pending")
    cnn_latency = Column(Float)
    llm_latency = Column(Float)
    llm_tokens = Column(Integer)

# Exemplo de relação entre modelos
class ImageAnalysisMetrics(Base):
    __tablename__ = "image_analysis_metrics"

    id = Column(Integer, primary_key=True)
    image_analysis_id = Column(Integer, ForeignKey("image_analysis.id"))
    metrics_id = Column(Integer, ForeignKey("metrics.id"))

    # Campos adicionais para relacionamento