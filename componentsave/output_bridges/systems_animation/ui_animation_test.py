import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🧪 Runtime Test: UI Animation Hook Check Only
# NOTE: Stereoscopic animation has been postponed until after essential launch
# Folder: F:/Apps/freedom_system/componentsave/ui_panels

import importlib
import inspect

results = []

# Check UI panel hooks for animation trigger or preview feedback
try:
    ui_mod = importlib.import_module("ui_panels.gui_emotion_panels")
    func_names = [name for name, _ in inspect.getmembers(ui_mod, inspect.isfunction)]

    has_hook = any("animation" in name.lower() or "preview" in name.lower() for name in func_names)
    results.append(f"{'✅' if has_hook else '❌'} UI panel includes animation or preview hook")

except Exception as e:
    results.append(f"❌ UI panel test failed: {e}")

# 📊 Final Runtime Results
print("\nUI Panel Animation Hook Check:")
for line in results:
    print(line)
