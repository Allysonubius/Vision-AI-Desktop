import json
import hashlib
from database.database import get_conn


# =========================
# HASH DA IMAGEM
# =========================
def generate_image_hash(image_bytes: bytes) -> str:
    return hashlib.md5(image_bytes).hexdigest()


# =========================
# CACHE
# =========================
def get_cached_analysis(image_hash):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT prediction, confidence, analysis, status
    FROM image_analysis
    WHERE image_hash = ?
    """, (image_hash,))

    row = cursor.fetchone()
    conn.close()

    if row:
        try:
            analysis = json.loads(row[2])
        except Exception:
            print("⚠️ Cache corrompido - ignorando")
            return None

        return {
            "prediction": row[0],
            "confidence": row[1],
            "analysis": analysis,
            "status": row[3]
        }

    return None


# =========================
# SAVE ANALYSIS
# =========================
def save_analysis(image_hash, result):
    conn = get_conn()
    cursor = conn.cursor()

    try:
        analysis_json = json.dumps(result["analysis"])
    except Exception:
        print("❌ Erro ao serializar analysis - não salvando")
        return

    cursor.execute("""
    INSERT OR REPLACE INTO image_analysis
    (image_hash, prediction, confidence, analysis, status)
    VALUES (?, ?, ?, ?, ?)
    """, (
        image_hash,
        result["prediction"],
        result["confidence"],
        analysis_json,
        "processed"
    ))

    conn.commit()
    conn.close()


# =========================
# METRICS
# =========================
def save_metrics(data):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO metrics (
        image_hash,
        prediction,
        source,
        status,
        cnn_latency,
        llm_latency,
        llm_tokens
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("image_hash"),
        data.get("prediction"),
        data.get("source"),
        data.get("status"),
        data.get("cnn_latency", 0),
        data.get("llm_latency", 0),
        data.get("llm_tokens", 0)
    ))

    conn.commit()
    conn.close()


# =========================
# INIT TABLES
# =========================
def init_analysis_table():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS image_analysis (
        image_hash TEXT PRIMARY KEY,
        prediction TEXT,
        confidence REAL,
        analysis TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def init_metrics_table():
    conn = get_conn()
    cursor = conn.cursor()

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


def create_indexes():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hash ON image_analysis(image_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_hash ON metrics(image_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_created ON metrics(created_at)")

    conn.commit()
    conn.close()


# =========================
# GET BY HASH
# =========================
def get_analysis_by_hash(image_hash):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT prediction, confidence, analysis, status, created_at
    FROM image_analysis
    WHERE image_hash = ?
    """, (image_hash,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    try:
        analysis = json.loads(row[2])
    except Exception:
        print("⚠️ JSON inválido no banco")
        return None

    return {
        "prediction": row[0],
        "confidence": row[1],
        "analysis": analysis,
        "status": row[3],
        "created_at": row[4]
    }


# =========================
# LISTAGEM RECENTE (🔥 ESSENCIAL pro seu erro)
# =========================
def get_recent_analyses(limit=10):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT image_hash, prediction, confidence, created_at
    FROM image_analysis
    ORDER BY created_at DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "image_hash": r[0],
            "prediction": r[1],
            "confidence": r[2],
            "created_at": r[3]
        }
        for r in rows
    ]


# =========================
# INIT GERAL
# =========================
def init_db():
    init_analysis_table()
    init_metrics_table()
    create_indexes()