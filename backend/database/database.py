import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "images.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id TEXT PRIMARY KEY,
        hash TEXT,
        status TEXT,
        prediction TEXT,
        confidence REAL,
        analysis TEXT,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()