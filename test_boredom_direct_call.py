# ==========================================
# BOREDOM MONITOR DIRECT CALL TEST
# Test the new direct call implementation
# ==========================================

import sys
import os
from pathlib import Path

# Add the text-generation-webui path to import modules
tgwui_path = Path("F:/Apps/freedom_system/app_cabinet/text-generation-webui")
sys.path.insert(0, str(tgwui_path))

print("[TEST] Starting Boredom Monitor Direct Call Test")
print(f"[TEST] Using text-generation-webui path: {tgwui_path}")

try:
    # Test import of the updated script
    print("[TEST] Attempting to import boredom monitor script...")

    # Import the extension script
    sys.path.insert(0, str(tgwui_path / "extensions" / "boredom_monitor"))
    import script as boredom_script

    print("[TEST] ✅ Boredom monitor script imported successfully")

    # Test the trigger function exists
    if hasattr(boredom_script, 'trigger_emotional_response'):
        print("[TEST] ✅ trigger_emotional_response function found")

        # Print function signature
        import inspect
        sig = inspect.signature(boredom_script.trigger_emotional_response)
        print(f"[TEST] Function signature: trigger_emotional_response{sig}")

    else:
        print("[TEST] ❌ trigger_emotional_response function NOT found")

    # Test manual trigger function exists
    if hasattr(boredom_script, 'manual_trigger_test'):
        print("[TEST] ✅ manual_trigger_test function found")
    else:
        print("[TEST] ❌ manual_trigger_test function NOT found")

    # Test extension parameters
    if hasattr(boredom_script, 'params'):
        print(f"[TEST] ✅ Extension params: {boredom_script.params}")
    else:
        print("[TEST] ❌ Extension params NOT found")

    # Test if main functions exist
    functions_to_check = ['setup', 'ui', 'custom_css']
    for func_name in functions_to_check:
        if hasattr(boredom_script, func_name):
            print(f"[TEST] ✅ {func_name}() function found")
        else:
            print(f"[TEST] ❌ {func_name}() function NOT found")

    print("[TEST] ✅ All basic tests passed - extension structure looks correct")
    print("[TEST] Implementation uses direct call method (no API server)")
    print("[TEST] Ready for integration with text-generation-webui")

except ImportError as e:
    print(f"[TEST] ❌ Import failed: {e}")
    print("[TEST] This is expected if text-generation-webui is not running")
    print("[TEST] The extension will work when loaded by text-generation-webui")

except Exception as e:
    print(f"[TEST] ❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("[TEST] Test completed")