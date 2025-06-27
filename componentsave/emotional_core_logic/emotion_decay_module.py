# GUI import header (required for cross-module access in Freedom System)
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Placeholder: real logic will be added here
# Provide dummy interface so dependent systems don’t fail
def set_emotion_decay(value):
    print(f"[DECAY] Emotion decay set to {value:.2f}s")
