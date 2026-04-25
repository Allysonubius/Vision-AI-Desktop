import uuid
import hashlib
import logging

logger = logging.getLogger("session_service")

# 🔥 armazenamento em memória (pode trocar por DB depois)
sessions = {}

# 🔥 índice por hash (cache)
hash_index = {}


# =========================
# HASH
# =========================
def generate_hash(image_bytes):
    return hashlib.md5(image_bytes).hexdigest()


# =========================
# CREATE SESSION
# =========================
def create_session(image_bytes, result, image_hash=None):
    session_id = str(uuid.uuid4())

    if not image_hash:
        image_hash = generate_hash(image_bytes)

    logger.info(f"💾 Criando sessão {session_id}")

    sessions[session_id] = {
        "id": session_id,
        "image": image_bytes,
        "analysis": result,
        "messages": [],
        "hash": image_hash,
        "status": "done"
    }

    # 🔥 indexa por hash (cache)
    hash_index[image_hash] = session_id

    return session_id


# =========================
# GET SESSION
# =========================
def get_session(session_id):
    return sessions.get(session_id)


# =========================
# GET BY HASH (🔥 CACHE)
# =========================
def get_session_by_hash(image_hash):
    session_id = hash_index.get(image_hash)

    if not session_id:
        return None

    session = sessions.get(session_id)

    if not session:
        return None

    logger.info(f"⚡ Cache hit para hash {image_hash}")

    return {
        "id": session["id"],
        "analysis": session["analysis"],
        "status": session["status"]
    }


# =========================
# ADD MESSAGE
# =========================
def add_message(session_id, role, content):
    if session_id in sessions:
        sessions[session_id]["messages"].append({
            "role": role,
            "content": content
        })


# =========================
# UPDATE STATUS (🔥 NOVO)
# =========================
def update_status(session_id, status):
    if session_id in sessions:
        sessions[session_id]["status"] = status
        logger.info(f"🔄 Status atualizado: {session_id} → {status}")


# =========================
# LIST SESSIONS (🔥 EXTRA)
# =========================
def list_sessions():
    return [
        {
            "id": s["id"],
            "status": s["status"]
        }
        for s in sessions.values()
    ]