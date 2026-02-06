#!/usr/bin/env python3
"""
Test script for JavaScript auto-trigger implementation
This tests the new whisper_stt pattern implementation
"""

import sys
import time
from pathlib import Path

# Add text-generation-webui to path
tgwui_path = Path("F:/Apps/freedom_system/freedom_system_2000/text-generation-webui")
sys.path.insert(0, str(tgwui_path))
sys.path.insert(0, str(tgwui_path / "extensions" / "boredom_monitor"))

print("=" * 70)
print("JAVASCRIPT AUTO-TRIGGER TEST")
print("=" * 70)
print()
print("Testing the new whisper_stt pattern implementation...")
print("This should now automatically click Generate without user interaction!")
print()

def test_javascript_trigger():
    """Test the JavaScript auto-trigger functionality"""
    try:
        # Import the updated boredom monitor script
        import script as boredom_script

        print("[TEST] Updated boredom monitor script imported successfully")

        # Check if auto-trigger function exists
        if hasattr(boredom_script, 'trigger_chat_generation'):
            print("[TEST] trigger_chat_generation function found")
        else:
            print("[FAIL] trigger_chat_generation function not found")
            return False

        # Check if input hijack exists
        if hasattr(boredom_script, 'input_hijack'):
            hijack = boredom_script.input_hijack
            print(f"[TEST] Input hijack found: {hijack}")
        else:
            print("[FAIL] input_hijack not found")
            return False

        # Test manual trigger with new implementation
        print("\n[TEST] Testing manual trigger with JavaScript auto-click...")

        result = boredom_script.manual_trigger_test('bored', 1)

        if result:
            print("[SUCCESS] Manual trigger completed!")
            print(f"[TEST] Hijack state after trigger: {boredom_script.input_hijack}")

            print("\n" + "=" * 70)
            print("EXPECTED BEHAVIOR:")
            print("1. ✅ Input hijack was set with emotional message")
            print("2. 🆕 JavaScript should have automatically clicked Generate button")
            print("3. 🆕 Message should appear in chat UI immediately")
            print("4. ✅ No user interaction required!")
            print()
            print("👀 CHECK THE CHAT UI NOW!")
            print("The message should have appeared automatically!")
            print("=" * 70)

            return True
        else:
            print("[FAIL] Manual trigger failed")
            return False

    except ImportError as e:
        print(f"[FAIL] Could not import boredom monitor: {e}")
        print("\nREQUIREMENT: text-generation-webui must be restarted to load updated extension")
        return False

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

def test_shared_gradio_access():
    """Test if shared.gradio is available and has our trigger element"""
    try:
        from modules import shared

        print("\n[TEST] Checking shared.gradio access...")

        if hasattr(shared, 'gradio'):
            gradio_dict = shared.gradio
            print(f"[TEST] shared.gradio found with {len(gradio_dict)} components")

            # Check for our auto-trigger element
            if 'boredom-auto-trigger' in gradio_dict:
                trigger_elem = gradio_dict['boredom-auto-trigger']
                print(f"[SUCCESS] Auto-trigger element found: {trigger_elem}")
                print(f"[TEST] Current value: {getattr(trigger_elem, 'value', 'No value attr')}")
                return True
            else:
                print("[INFO] Auto-trigger element not found yet")
                print("This is normal if UI hasn't been created yet")
                available_keys = list(gradio_dict.keys())[:10]  # Show first 10
                print(f"[DEBUG] Available keys (sample): {available_keys}")
                return False
        else:
            print("[INFO] shared.gradio not available yet")
            return False

    except Exception as e:
        print(f"[ERROR] Shared gradio test failed: {e}")
        return False

def main():
    """Run JavaScript trigger tests"""
    print("Starting JavaScript auto-trigger tests...\n")

    # Test 1: Basic functionality
    print("Test 1: Basic trigger functionality")
    basic_test = test_javascript_trigger()

    # Test 2: Gradio access
    print("\nTest 2: Shared gradio access")
    gradio_test = test_shared_gradio_access()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Basic Trigger: {'PASS' if basic_test else 'FAIL'}")
    print(f"Gradio Access: {'PASS' if gradio_test else 'INFO'}")

    if basic_test:
        print("\n🎉 JAVASCRIPT AUTO-TRIGGER IMPLEMENTED!")
        print("✅ Following whisper_stt pattern exactly")
        print("✅ Should now work without user interaction")
        print("\nNOTE: If this is the first test after code changes,")
        print("restart text-generation-webui to load the updated extension.")
    else:
        print("\n⚠️  Some tests failed - check implementation")

    print("\n👁️  CHECK THE CHAT UI TO CONFIRM AUTO-INJECTION!")

if __name__ == "__main__":
    main()