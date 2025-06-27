import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🧪 Runtime Test: Image Output Logic
# Folder: F:/Apps/freedom_system/componentsave/output_bridges/systems_image

import importlib
import inspect

results = []

# Image Generation – framing logic trigger test
try:
    image_mod = importlib.import_module("output_bridges.systems_image.image_emotion_driver")
    func_names = [name for name, _ in inspect.getmembers(image_mod, inspect.isfunction)]

    # Try to run if generate_emotion_image or similar exists
    gen_func = next((getattr(image_mod, name) for name in func_names if "generate" in name), None)

    if gen_func:
        result = gen_func("Romantic")  # Should use head-to-midriff framing
        frame_check = any(word in str(result).lower() for word in ["head", "midriff", "framing"])
        results.append(f"{'✅' if frame_check else '❌'} Image framing triggered on emotion input")
    else:
        results.append("❌ No image generation function detected")

except Exception as e:
    results.append(f"❌ Image system test failed: {e}")

# 📊 Final Runtime Results
print("\nRuntime Image Check:")
for line in results:
    print(line)
