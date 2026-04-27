import os
import sqlite3
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # sobe 1 nível (backend/)
DB_PATH = os.path.join(BASE_DIR, "app.db")

def get_conn() -> sqlite3.Connection:
    """Cria e retorna conexão com SQLite."""
    try:
        return sqlite3.connect(DB_PATH)
    except Exception as e:
        raise RuntimeError(f"Failed to connect to database: {str(e)}") from e

def init_db():
    """Inicializa o banco de dados, criando tabelas se não existirem."""
    conn = get_conn()
    try:
        cursor = conn.cursor()

        # Tabela principal
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_hash TEXT UNIQUE,
                prediction TEXT,
                confidence REAL,
                analysis TEXT,
                source TEXT,
                status TEXT DEFAULT 'pending',
                cnn_latency REAL,
                llm_latency REAL,
                llm_tokens INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de métricas (agregada)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_hash TEXT UNIQUE,
                prediction TEXT,
                source TEXT,
                status TEXT DEFAULT 'pending',
                cnn_latency REAL,
                llm_latency REAL,
                llm_tokens INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    finally:
        conn.commit()
        conn.close()

def get_analysis_by_hash(image_hash: str) -> Optional[dict]:
    """Retorna análise por hash, usando SQLite raw query."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM image_analysis WHERE image_hash = ?
        """, (image_hash,))
        result = cursor.fetchone()

        if not result:
            return None

        # Convertendo para dicionário
        return dict(zip(
            ["id", "prediction", "confidence", "analysis", "source", "status",
             "cnn_latency", "llm_latency", "llm_tokens", "created_at"],
            result
        ))

    finally:
        conn.close()