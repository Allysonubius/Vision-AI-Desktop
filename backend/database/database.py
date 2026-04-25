import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # sobe 1 nível (backend/)
DB_PATH = os.path.join(BASE_DIR, "app.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS image_analysis (
        image_hash TEXT PRIMARY KEY,
        prediction TEXT,
        confidence REAL,
        analysis TEXT,
        source TEXT,
        status TEXT,

        cnn_latency REAL,
        llm_latency REAL,
        llm_tokens INTEGER,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_hash TEXT,
        prediction TEXT,
        source TEXT,
        status TEXT,
        cnn_latency REAL,
        llm_latency REAL,
        llm_tokens INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()