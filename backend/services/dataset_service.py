import os
import uuid

def save_to_dataset(image_bytes, label):
    folder = f"dataset/{label}"
    os.makedirs(folder, exist_ok=True)

    filename = f"{uuid.uuid4()}.jpg"
    path = os.path.join(folder, filename)

    with open(path, "wb") as f:
        f.write(image_bytes)

    return path