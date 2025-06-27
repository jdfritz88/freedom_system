import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🧪 Runtime Test: Toggle State Cascade Behavior
# Folder: F:/Apps/freedom_system/componentsave/ui_panels
# Purpose: Ensure toggles (like resolution or background) control output as expected

import importlib
import inspect

results = []

# Check background toggle influence on image generation output
try:
    toggle_mod = importlib.import_module("ui_panels.background_toggle_control")
    image_mod = importlib.import_module("output_bridges.systems_image.image_emotion_driver")

    toggle_func = getattr(toggle_mod, "set_background_default", None)
    status_func = getattr(toggle_mod, "get_background_status", None)
    gen_func = getattr(image_mod, "generate_emotion_image", None)

    if all([toggle_func, status_func, gen_func]):
        toggle_func(False)
        status = status_func()
        output = gen_func("Romantic")

        condition = ("background" not in str(output).lower()) and (status == False)
        results.append("✅ Image respects background toggle OFF" if condition else "❌ Background toggle did not suppress image background")

        toggle_func(True)
        status = status_func()
        output = gen_func("Romantic")

        condition = ("background" in str(output).lower()) and (status == True)
        results.append("✅ Image includes background when toggle ON" if condition else "❌ Background ON toggle not respected in image output")

    else:
        results.append("❌ One or more required functions not found in toggle or image modules")

except Exception as e:
    results.append(f"❌ Toggle/image cascade test failed: {e}")

# 📊 Output
print("\nToggle Cascade Behavior Runtime Check:")
print("
[TEST OUTPUT START]
")
for line in results:
    print(line)
print("
[TEST OUTPUT END]
")
