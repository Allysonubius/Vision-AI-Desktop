import os
import json
import shutil

from services.cnn_train import train_model

QUEUE_DIR = "retrain_queue"
DATASET_DIR = "dataset"


def process_queue():

    for file in os.listdir(QUEUE_DIR):

        if not file.endswith(".json"):
            continue

        path = os.path.join(QUEUE_DIR, file)

        with open(path) as f:
            data = json.load(f)

        label = data["label"]
        image_path = data["image"]

        target_dir = os.path.join(DATASET_DIR, label)
        os.makedirs(target_dir, exist_ok=True)

        shutil.move(image_path, os.path.join(target_dir, os.path.basename(image_path)))
        os.remove(path)

    print("🔥 Dataset atualizado!")

    train_model()