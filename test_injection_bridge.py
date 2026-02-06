"""
Test if the injection bridge is working after our fixes
"""

import sys
import os

# Add text-generation-webui path
webui_path = r"F:\Apps\freedom_system\freedom_system_2000\text-generation-webui"
sys.path.insert(0, webui_path)

# Import the extension module
sys.path.insert(0, os.path.join(webui_path, "extensions", "boredom_monitor"))

print("[TEST] Importing injection bridge...")
try:
    import gradio_injection_bridge as bridge
    print(f"[OK] Injection bridge imported successfully")
    print(f"[INFO] Queue size: {len(bridge.injection_queue)}")

    # Test queuing a message
    print("\n[TEST] Queuing test message...")
    success = bridge.queue_message_for_injection("TEST: Injection bridge verification")
    print(f"[RESULT] Queue success: {success}")
    print(f"[INFO] Queue size after: {len(bridge.injection_queue)}")

    # Check queue status
    status = bridge.get_queue_status()
    print(f"\n[STATUS] Queue status: {status}")

    if status['has_pending']:
        print("[OK] Bridge can queue messages successfully")
        print("[NEXT] Need to verify:")
        print("  1. JavaScript polling is running in browser")
        print("  2. Hidden button exists with ID 'boredom_inject_hidden_btn'")
        print("  3. Button click triggers event handler")
        print("  4. Event handler returns updated history")
    else:
        print("[ERROR] Bridge queue not working")

except Exception as e:
    print(f"[ERROR] Failed to import or test bridge: {e}")
    import traceback
    traceback.print_exc()
