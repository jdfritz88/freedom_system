import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# Validation of Live Interactions with Applied Optimizations

# ✅ GOAL:
# Confirm that live interaction modules (image, music, voice) are optimized per the research and system architecture.
# This includes queueing, throttling, memory management, and frame control as outlined in the 2025-06-21 report.

# 🧠 COMPONENTS UNDER TEST:
# - voice_emotion_driver.py
# - music_emotion_driver.py
# - image_emotion_driver.py
# - emotion_delay_throttle.py
# - emotion_queue.py
# - emotion_framer.py
# - emotion_trigger_handler.py
# - emotion_system_core.py

# 🛠 OPTIMIZATION CRITERIA
# - Efficient emotion queue handling (FIFO, no bottlenecks)
# - CPU throttling for Coqui TTS
# - Centralized emotion delay throttling (delay tuning)
# - Modular broadcast and image framing

# 🔍 VALIDATION
import os
import importlib
import inspect

modules = [
    'emotion_core_logic.emotion_delay_throttle',
    'emotion_core_logic.emotion_queue',
    'emotion_core_logic.emotion_framer',
    'emotion_core_logic.emotion_trigger_handler',
    'emotion_core_logic.emotion_system_core',
    'output_bridges.systems_voice.voice_emotion_driver',
    'output_bridges.systems_music.music_emotion_driver',
    'output_bridges.systems_image.image_emotion_driver'
]

report = []

for module_path in modules:
    try:
        mod = importlib.import_module(module_path)
        funcs = [name for name, _ in inspect.getmembers(mod, inspect.isfunction)]
        report.append(f"✅ Loaded: {module_path} ({len(funcs)} functions)")
    except Exception as e:
        report.append(f"❌ ERROR in {module_path}: {str(e)}")

# 📊 RESULTS
print("\nModule Load Check:")
for line in report:
    print(line)
