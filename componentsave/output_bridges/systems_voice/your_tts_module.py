import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# your_tts_module.py
# Placeholder for Coqui TTS wrapper

def coqui_speak(text, emotion_state):
    """
    Simulated TTS engine call.
    Replace this with real Coqui voice output.
    """
    print("[TTS] Speaking:", text)
    print("[TTS] Emotion State:", emotion_state)
