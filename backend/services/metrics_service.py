from database.database import get_conn


def get_summary():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM metrics")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM metrics WHERE status = 'cache_hit'")
    cache_hits = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(llm_tokens) FROM metrics")
    tokens = cursor.fetchone()[0] or 0

    cursor.execute("SELECT AVG(llm_latency) FROM metrics WHERE llm_latency > 0")
    avg_llm = cursor.fetchone()[0] or 0

    cursor.execute("SELECT AVG(cnn_latency) FROM metrics WHERE cnn_latency > 0")
    avg_cnn = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "total_images": total,
        "cache_hits": cache_hits,
        "cache_hit_rate": round(cache_hits / total, 2) if total else 0,
        "total_tokens": tokens,
        "avg_llm_latency": avg_llm,
        "avg_cnn_latency": avg_cnn
    }


def get_by_class():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT prediction, COUNT(*)
    FROM metrics
    GROUP BY prediction
    """)

    rows = cursor.fetchall()
    conn.close()

    return [{"class": r[0], "count": r[1]} for r in rows]


def get_tokens_by_day():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DATE(created_at), SUM(llm_tokens)
    FROM metrics
    GROUP BY DATE(created_at)
    ORDER BY DATE(created_at)
    """)

    rows = cursor.fetchall()
    conn.close()

    return [{"date": r[0], "tokens": r[1]} for r in rows]


def get_latency():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT created_at, llm_latency, cnn_latency
    FROM metrics
    ORDER BY created_at DESC
    LIMIT 100
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "date": r[0],
            "llm_latency": r[1],
            "cnn_latency": r[2]
        }
        for r in rows
    ]


def get_cost(cost_per_1k=0.002):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(llm_tokens) FROM metrics")
    tokens = cursor.fetchone()[0] or 0

    conn.close()

    cost = (tokens / 1000) * cost_per_1k

    return {
        "tokens": tokens,
        "estimated_cost_usd": round(cost, 4)
    }