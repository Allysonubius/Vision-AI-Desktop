from services.cnn_service import predict_image
from services.llm_service import generate_response_with_image
from services.db_service import (
    generate_image_hash,
    get_cached_analysis,
    save_analysis,
    save_metrics
)

from core.config import MODEL_NAME
import json
import re
import logging

logger = logging.getLogger("image_service")


# =========================
# CONFIDENCE
# =========================
def estimate_confidence(analysis):
    text = (analysis.get("description", "") + analysis.get("critical_analysis", "")).lower()

    if "claramente" in text:
        return 0.85
    elif "provavelmente" in text:
        return 0.7
    elif "difícil" in text:
        return 0.5
    else:
        return 0.6


# =========================
# VALIDADOR DE JSON
# =========================
def is_valid_analysis(analysis):
    required_fields = [
        "description",
        "predicted_class_interpretation",
        "challenges",
        "critical_analysis",
        "limitations",
        "improvements"
    ]

    if not isinstance(analysis, dict):
        return False

    for field in required_fields:
        if field not in analysis:
            return False

    # 🔥 evita lixo
    if not analysis.get("description"):
        return False

    if "Erro ao interpretar" in analysis.get("description", ""):
        return False

    return True


# =========================
# NORMALIZA CLASSE
# =========================
def normalize_class(label):
    label = label.lower().strip()

    if label in ["asphalt", "cobblestone", "offroad"]:
        return label

    if "block" in label or "stone" in label:
        return "cobblestone"

    if "road" in label or "asphalt" in label:
        return "asphalt"

    return "unknown"


# =========================
# MAIN
# =========================
def analyze_image(image_bytes):
    image_hash = generate_image_hash(image_bytes)

    # =========================
    # CACHE
    # =========================
    cached = get_cached_analysis(image_hash)

    if cached:
        logger.info("⚡ CACHE HIT")

        save_metrics({
            "image_hash": image_hash,
            "prediction": cached["prediction"],
            "source": "cache",
            "status": "cache_hit",
            "cnn_latency": 0,
            "llm_latency": 0,
            "llm_tokens": 0
        })

        return {
            "prediction": cached["prediction"],
            "confidence": cached["confidence"],
            "analysis": cached["analysis"],
            "source": "cache",
            "status": "cache_hit",
            "metrics": {
                "cnn_latency": 0,
                "llm_latency": 0,
                "llm_tokens_estimated": 0
            }
        }

    logger.info("🧠 CACHE MISS → processando")

    # =========================
    # CNN
    # =========================
    cnn_result = predict_image(image_bytes)

    label = normalize_class(cnn_result["label"])
    confidence = cnn_result["confidence"]
    status = cnn_result["status"]
    top_predictions = cnn_result.get("top_predictions", [])
    cnn_latency = cnn_result.get("latency", 0)

    # =========================
    # PROMPT
    # =========================
    if status == "success":
        top_preds_text = "\n".join(
            [f"- {p['label']}: {p['confidence']:.2f}" for p in top_predictions]
        )

        prompt = build_prompt(label, confidence, top_preds_text)
        source = f"cnn+{MODEL_NAME}"
    else:
        logger.warning("CNN falhou → usando fallback LLM")
        prompt = build_fallback_prompt()
        source = MODEL_NAME

    # =========================
    # LLM (com retry)
    # =========================
    llm_response = None
    analysis = None

    for attempt in range(2):  # retry 1x
        llm_response = generate_response_with_image(prompt, image_bytes)

        if not llm_response:
            continue

        llm_raw = llm_response.get("content")
        analysis = safe_parse_llm_json(llm_raw)

        if is_valid_analysis(analysis):
            break

        logger.warning(f"⚠️ LLM inválido tentativa {attempt+1}")

    if not analysis or not is_valid_analysis(analysis):
        logger.error("❌ Falha definitiva no LLM")

        return {
            "prediction": label,
            "confidence": confidence,
            "analysis": default_analysis("Erro ao interpretar resposta do LLM"),
            "source": source,
            "status": "llm_error",
            "metrics": {
                "cnn_latency": cnn_latency,
                "llm_latency": 0,
                "llm_tokens_estimated": 0
            }
        }

    llm_tokens = llm_response.get("tokens_estimated", 0)
    llm_latency = llm_response.get("latency", 0)

    # =========================
    # FALLBACK CLASS (quando CNN falha)
    # =========================
    if status != "success":
        predicted = normalize_class(
            analysis.get("predicted_class_interpretation", "unknown")
        )

        label = predicted
        confidence = estimate_confidence(analysis)

    result = {
        "prediction": label,
        "confidence": confidence,
        "analysis": analysis,
        "source": source,
        "status": "processed",
        "metrics": {
            "cnn_latency": cnn_latency,
            "llm_latency": llm_latency,
            "llm_tokens_estimated": llm_tokens
        }
    }

    # =========================
    # SAVE CACHE (VALIDADO)
    # =========================
    try:
        if is_valid_analysis(analysis) and "Erro ao interpretar" not in analysis.get("description", ""):
            save_analysis(image_hash, result)
            logger.info("💾 Resultado salvo no cache")
        else:
            logger.warning("⚠️ Resultado inválido NÃO salvo no cache")
    except Exception as e:
        logger.error(f"Erro ao salvar cache: {str(e)}")

    # =========================
    # SAVE METRICS
    # =========================
    try:
        save_metrics({
            "image_hash": image_hash,
            "prediction": label,
            "source": source,
            "status": "processed",
            "cnn_latency": cnn_latency,
            "llm_latency": llm_latency,
            "llm_tokens": llm_tokens
        })
    except Exception as e:
        logger.error(f"Erro ao salvar métricas: {str(e)}")

    return result


# =========================
# PARSER (MELHORADO)
# =========================
def safe_parse_llm_json(text):
    if not text:
        return default_analysis("Resposta vazia do LLM")

    try:
        parsed = json.loads(text)

        # 🔥 CASO CRÍTICO: JSON veio como string
        if isinstance(parsed, str):
            parsed = json.loads(parsed)

        return parsed
    except:
        pass

    try:
        cleaned = re.sub(r"```json|```", "", text)
        parsed = json.loads(cleaned.strip())

        if isinstance(parsed, str):
            parsed = json.loads(parsed)

        return parsed
    except:
        pass

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))

            if isinstance(parsed, str):
                parsed = json.loads(parsed)

            return parsed
    except:
        pass

    logger.error("Erro ao parsear JSON do LLM")
    return default_analysis("Erro ao interpretar resposta do LLM")


# =========================
# DEFAULT
# =========================
def default_analysis(msg):
    return {
        "description": msg,
        "predicted_class_interpretation": "",
        "challenges": [],
        "critical_analysis": "",
        "limitations": "",
        "improvements": ""
    }


# =========================
# SEUS PROMPTS (INTACTOS)
# =========================
def build_prompt(label, confidence, top_predictions):
    confidence_level = "baixa"

    if confidence >= 0.85:
        confidence_level = "alta"
    elif confidence >= 0.6:
        confidence_level = "média"

    return f"""
Responda OBRIGATORIAMENTE em português do Brasil.

Você é um especialista em visão computacional focado em ANÁLISE VISUAL REAL.

OBJETIVO:
Classificar corretamente o tipo de superfície com base na imagem.

PRIORIDADE ABSOLUTA:
1. Evidência visual (textura, padrão, iluminação, irregularidade)
2. Coerência física da superfície
3. Consistência com classes válidas
4. CNN (apenas como contexto auxiliar, NÃO como verdade)

CLASSES VÁLIDAS:
- asphalt (superfície lisa, contínua, reflexiva)
- cobblestone (blocos/pedras irregulares, textura segmentada)
- offroad (terra, areia, irregularidade natural)

DADOS DA CNN (contexto auxiliar):
Predição: {label}
Confiança: {confidence:.2f} ({confidence_level})

Top predições:
{top_predictions}

REGRAS IMPORTANTES:

- A análise deve ser guiada pela imagem, NÃO pela CNN
- Só mencione a CNN se houver inconsistência relevante
- NÃO baseie sua decisão na confiança da CNN
- Foque em evidências visuais concretas:
  → textura (lisa, rugosa, segmentada)
  → padrão (uniforme vs blocos)
  → reflexão de luz
  → continuidade da superfície
  → irregularidade

- Evite explicações genéricas
- Seja técnico e direto

TAREFA:

Gere uma análise técnica estruturada contendo:

1. description
   → Descreva SOMENTE o que é visível (sem suposições)
   → Foque em textura, iluminação, padrão e material

2. predicted_class_interpretation
   → Classificação baseada EXCLUSIVAMENTE na evidência visual
   → NÃO justifique com CNN

3. challenges (ARRAY)
   → dificuldades reais da imagem (luz, ruído, ambiguidade)

4. critical_analysis
   → Justifique tecnicamente a classificação
   → Compare características visuais das classes
   → Só mencione a CNN se houver conflito relevante

5. limitations
   → limitações reais da análise visual

6. improvements
   → melhorias práticas no sistema (modelo, imagem, pipeline)

REGRAS DE SAÍDA:
- SOMENTE JSON
- SEM markdown
- NÃO escreva nada fora do JSON
"""

def build_fallback_prompt():
    return """
Responda OBRIGATORIAMENTE em português do Brasil.

Você está analisando uma imagem sem classificação prévia.

CLASSES VÁLIDAS:
- asphalt
- cobblestone
- offroad

TAREFA:
1. description
2. predicted_class_interpretation
3. challenges (ARRAY)
4. critical_analysis
5. limitations
6. improvements

REGRAS:
- SOMENTE JSON
- SEM markdown
- SEM inglês
- NÃO escreva nada fora do JSON
"""