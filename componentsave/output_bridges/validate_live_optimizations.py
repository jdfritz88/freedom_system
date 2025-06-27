import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# ✅ Inline Optimization Validation for Freedom System Live Interaction Modules
# This expands the existing validation to verify actual optimization logic inside key modules

import importlib
import inspect
import ast

results = []

# Define optimization expectations per module
EXPECTATIONS = {
    "emotion_core_logic.emotion_queue": ["Queue", "put", "get"],
    "emotion_core_logic.emotion_delay_throttle": ["time.sleep", "delay"],
    "output_bridges.systems_voice.voice_emotion_driver": ["thread", "queue", "speak", "join"],
    "output_bridges.systems_image.image_emotion_driver": ["framing", "emotion", "prompt"],
    "output_bridges.systems_music.music_emotion_driver": ["emotion", "route", "play"],
}

# Parse source code safely to check for feature presence
for module_path, keywords in EXPECTATIONS.items():
    try:
        mod = importlib.import_module(module_path)
        source = inspect.getsource(mod)
        tree = ast.parse(source)
        code_str = ast.unparse(tree) if hasattr(ast, 'unparse') else source

        found = all(keyword in code_str for keyword in keywords)
        results.append(f"{'✅' if found else '❌'} {module_path} contains expected logic: {', '.join(keywords)}")

    except Exception as e:
        results.append(f"❌ ERROR loading {module_path}: {str(e)}")

# 📊 Print Validation Summary
print("\nInline Optimization Checks:")
for line in results:
    print(line)
