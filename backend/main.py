from database.db import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.result import ImageResult

from api.routes import vision, chat, history, health, metrics  # 👈 ADD metrics

from services.db_service import (
    init_analysis_table,
    init_metrics_table,
    create_indexes
)

app = FastAPI()

# =========================
# 🔥 CRIA TABELAS (SQLAlchemy)
# =========================
Base.metadata.create_all(bind=engine)

# =========================
# 🔥 CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🔥 ROTAS
# =========================
app.include_router(vision.router, prefix="/vision")
app.include_router(chat.router, prefix="/chat")
app.include_router(history.router, prefix="/history")
app.include_router(health.router, prefix="/health")
app.include_router(metrics.router, prefix="/metrics")  # 👈 NOVO

# =========================
# 🔥 STARTUP
# =========================
@app.on_event("startup")
def startup():
    # SQLite (cache + métricas)
    init_analysis_table()
    init_metrics_table()
    create_indexes()

    print("\n🚀 ROTAS REGISTRADAS:")
    for route in app.routes:
        methods = ",".join(route.methods or [])
        print(f"{methods:10} {route.path}")