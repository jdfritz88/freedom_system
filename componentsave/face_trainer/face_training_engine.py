import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# face_training_engine.py
# Core engine for LoRA face training, invoked by face_training_launcher

import os
import time
import json
from componentsave.datetime import datetime

SETTINGS_FILE = "session_settings.json"
VERSION_FOLDER = "weights"
STEP_LOG = "autosave_log.txt"

class FaceTrainer:
    def __init__(self, folder, resume=False):
        self.folder = folder
        self.settings_path = os.path.join(folder, SETTINGS_FILE)
        self.weights_path = os.path.join(folder, VERSION_FOLDER)
        self.log_path = os.path.join(folder, STEP_LOG)
        os.makedirs(self.weights_path, exist_ok=True)
        self.resume = resume
        self.step = 0
        self.max_step = 4000

    def load_settings(self):
        if self.resume and os.path.exists(self.settings_path):
            with open(self.settings_path, 'r') as f:
                data = json.load(f)
                self.step = data.get("last_step", 0)
        print(f"[Trainer] Starting at step {self.step}")

    def save_settings(self):
        with open(self.settings_path, 'w') as f:
            json.dump({"last_step": self.step}, f)

    def save_weights(self):
        filename = f"version_{(self.step // 100) % 3 + 1}.safetensors"
        path = os.path.join(self.weights_path, filename)
        with open(path, 'w') as f:
            f.write("Simulated weights data")
        with open(self.log_path, 'a') as f:
            f.write(f"Step {self.step}: saved {filename}\n")

    def train(self):
        self.load_settings()
        while self.step < self.max_step:
            time.sleep(0.1)
            self.step += 1
            if self.step % 100 == 0:
                self.save_weights()
                self.save_settings()
                print(f"[Trainer] Step {self.step}: autosaved.")

if __name__ == "__main__":
    import sys
    folder = sys.argv[1] if len(sys.argv) > 1 else "F:/FreedomFaces"
    resume_flag = "--resume" in sys.argv
    trainer = FaceTrainer(folder, resume=resume_flag)
    trainer.train()
