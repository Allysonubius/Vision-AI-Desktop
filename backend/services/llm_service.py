import requests
import base64
import time

from core.config import LM_STUDIO_URL, MODEL_NAME, SYSTEM_PROMPT, MAX_TOKEN


def estimate_tokens(text):
    # 🔥 estimativa simples (funciona bem na prática)
    return int(len(text) / 4)


def generate_response(messages):
    try:
        start_time = time.time()

        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages
        ]

        res = requests.post(
            LM_STUDIO_URL,
            json={
                "model": MODEL_NAME,
                "messages": full_messages,
                "temperature": 0.3,
                "max_tokens": MAX_TOKEN
            },
            timeout=60
        )

        res.raise_for_status()
        data = res.json()

        content = data["choices"][0]["message"]["content"]

        elapsed = time.time() - start_time

        return {
            "content": content,
            "tokens_estimated": estimate_tokens(content),
            "latency": elapsed
        }

    except Exception as e:
        print("LLM ERROR:", e)
        return None


# 🔥 MULTIMODAL
def generate_response_with_image(prompt: str, image_bytes: bytes):
    try:
        start_time = time.time()

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]

        res = requests.post(
            LM_STUDIO_URL,
            json={
                "model": MODEL_NAME,
                "messages": full_messages,
                "temperature": 0.3,
                "max_tokens": MAX_TOKEN
            },
            timeout=120
        )

        res.raise_for_status()
        data = res.json()

        content = data["choices"][0]["message"]["content"]

        elapsed = time.time() - start_time

        return {
            "content": content,
            "tokens_estimated": estimate_tokens(content),
            "latency": elapsed
        }

    except Exception as e:
        print("LLM IMAGE ERROR:", e)
        return None