# This debug script checks three things:
# 1. Is the Coqui TTS API server running?
# 2. Can it respond to a /health check?
# 3. Is the Oobabooga extension code loaded and showing UI?

import requests
import os

API_URL = "http://127.0.0.1:8000/health"

print("[1] Checking if Coqui TTS API is online...")
try:
    response = requests.get(API_URL, timeout=5)
    response.raise_for_status()
    data = response.json()
    print("✅ API Online")
    print("Model Loaded:", data.get("model_loaded"))
    print("Language:", data.get("current_language"))
except Exception as e:
    print("❌ API not reachable or crashed:", e)

print("\n[2] Checking Oobabooga Extension visibility...")
try:
    ext_path = "F:/Apps/freedom_system/componentsave/apps_installed/oobabooga/user_data/extensions"
    if not os.path.isdir(ext_path):
        print("❌ Extension folder not found")
    else:
        print("✅ Extension folder found:", ext_path)
        print("Contents:", os.listdir(ext_path))
except Exception as e:
    print("❌ Error reading extension folder:", e)
