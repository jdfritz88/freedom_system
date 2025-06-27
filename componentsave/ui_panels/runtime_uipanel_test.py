# runtime_uipanel_test.py – Final Patched Version

import os, sys
import importlib.util
import inspect

# 🔪 Runtime Test: UI Panel Control Logic Validation
# Uses direct file-based import to avoid package errors

results = []

# Load module from exact path
module_path = os.path.join(os.path.dirname(__file__), "background_toggle_control.py")
spec = importlib.util.spec_from_file_location("background_toggle_control", module_path)
toggle_mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(toggle_mod)
    funcs = [name for name, _ in inspect.getmembers(toggle_mod, inspect.isfunction)]

    expected_funcs = ["toggle_background", "set_background_default", "get_background_status"]
    present = [name for name in expected_funcs if name in funcs]

    if len(present) == len(expected_funcs):
        results.append("✅ Background toggle control: All expected methods present")
    else:
        missing = set(expected_funcs) - set(present)
        results.append(f"❌ Background toggle control missing: {', '.join(missing)}")

except Exception as e:
    results.append(f"❌ background_toggle_control.py load failed: {e}")

print("\n[TEST OUTPUT START]\n")
for line in results:
    print(line)
print("\n[TEST OUTPUT END]\n")
