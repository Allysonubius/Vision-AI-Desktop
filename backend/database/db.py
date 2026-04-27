import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

# Configurações globais
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "../app.db")

# URL do banco de dados (SQLite)
DATABASE_URL = f"sqlite:///{os.path.abspath(DATABASE_PATH)}"

# Configuração do engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Permitir uso fora do thread principal
    pool_pre_ping=True,  # Verificar conexões antes de usar
    echo=False  # Desabilitar logs SQL (opcional)
)

# Configuração da sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos ORM
Base = declarative_base()

# Evento para criar tabelas automaticamente
@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    """Configura o banco de dados antes da conexão."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")  # Habilitar restrições estrangeiras