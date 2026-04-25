from fastapi import APIRouter
from schemas.chat import ChatRequest
from services.session_service import get_session, add_message
from services.llm_service import generate_response

router = APIRouter()


@router.post("/")
def chat(req: ChatRequest):
    session = get_session(req.session_id)

    if not session:
        return {"error": "Session not found"}

    # 🔥 contexto da imagem (ESSENCIAL)
    image_analysis = session.get("analysis", {})

    # 🔥 histórico da conversa
    history = session.get("messages", [])

    # 🔥 prompt inteligente
    system_prompt = f"""
    Você é um assistente técnico especializado em análise de imagens.

    CONTEXTO DA IMAGEM:
    {image_analysis}

    REGRAS:
    - Use SEMPRE a análise da imagem como base
    - Expanda quando o usuário pedir mais detalhes
    - Gere respostas longas se necessário
    - Pode criar relatórios técnicos, documentação ou explicações profundas
    - Se o usuário pedir algo fora do contexto da imagem, avise

    """

    # 🔥 monta mensagens (histórico + nova pergunta)
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": req.message}
    ]

    response = generate_response(messages)

    # 🔥 salvar histórico
    add_message(req.session_id, "user", req.message)
    add_message(req.session_id, "assistant", response)

    return {"response": response}