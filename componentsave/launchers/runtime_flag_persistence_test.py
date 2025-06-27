import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🧪 Runtime Test: Flag Persistence Across Launches
# Save to: F:/Apps/freedom_system/componentsave/launchers
# Purpose: Ensure flag status survives between launches and resets cleanly

import json
import os

results = []

flag_path = "F:/Apps/freedom_system/componentsave/flags/emotion_engine_flag.json"

# 1. Confirm flag file exists
if not os.path.exists(flag_path):
    results.append("❌ Flag file not found")
else:
    try:
        with open(flag_path, 'r') as f:
            data = json.load(f)
        
        # 2. Check known keys
        if "emotion_engine_ready" in data:
            original = data["emotion_engine_ready"]
            results.append(f"✅ Flag present: emotion_engine_ready = {original}")

            # 3. Flip value, save, reload
            data["emotion_engine_ready"] = not original
            with open(flag_path, 'w') as f:
                json.dump(data, f)

            with open(flag_path, 'r') as f:
                confirm = json.load(f)["emotion_engine_ready"]

            if confirm != original:
                results.append("✅ Flag successfully flipped and saved")
            else:
                results.append("❌ Flag flip did not persist")

            # 4. Reset to original
            data["emotion_engine_ready"] = original
            with open(flag_path, 'w') as f:
                json.dump(data, f)
            results.append("✅ Flag reset to original state")
        else:
            results.append("❌ 'emotion_engine_ready' key missing in flag file")

    except Exception as e:
        results.append(f"❌ Error reading or modifying flag file: {e}")

# 📊 Output flag results
print("\nFlag Persistence Check:")
for line in results:
    print(line)
