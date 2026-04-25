import os
import json
import uuid

QUEUE_DIR = "retrain_queue"
os.makedirs(QUEUE_DIR, exist_ok=True)


def add_to_queue(image_bytes, label, confidence, source):

    item_id = str(uuid.uuid4())

    filepath = os.path.join(QUEUE_DIR, f"{item_id}.json")
    image_path = os.path.join(QUEUE_DIR, f"{item_id}.jpg")

    # salva imagem
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    # salva metadata
    data = {
        "image": image_path,
        "label": label,
        "confidence": confidence,
        "source": source
    }

    with open(filepath, "w") as f:
        json.dump(data, f)

    return item_id