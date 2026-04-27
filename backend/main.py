from database.db import Base, engine
from fastapi import FastAPI
from services.db_service import init_analysis_table, init_metrics_table
from api.routes import vision, chat, history, health, metrics
from core.cors import setup_cors 

import logging

logger = logging.getLogger(__name__)

app = FastAPI()

# =========================
# 🔥 CRIA TABELAS
# =========================
Base.metadata.create_all(bind=engine)

# =========================
# 🔥 CORS 
# =========================
setup_cors(app)

# =========================
# 🔥 ROTAS
# =========================
app.include_router(vision.router, prefix="/vision")
app.include_router(chat.router, prefix="/chat")
app.include_router(history.router, prefix="/history")
app.include_router(health.router, prefix="/health")
app.include_router(metrics.router, prefix="/metrics")

# =========================
# 🔥 STARTUP
# =========================
# No startup, inicialize tabelas com logging

@app.on_event("startup")
async def startup():
    try:
        logger.info("Inicializando tabelas...")
        init_analysis_table()
        init_metrics_table()
        logger.info("Tabelas inicializadas com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao inicializar serviços: {e}")