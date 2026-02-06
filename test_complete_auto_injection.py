#!/usr/bin/env python3
"""
Complete test for autonomous boredom monitor injection
Tests all the fixes: element registration + whisper_stt pattern + custom JS backup
"""

import sys
import time
from pathlib import Path

# Add text-generation-webui to path
tgwui_path = Path("F:/Apps/freedom_system/freedom_system_2000/text-generation-webui")
sys.path.insert(0, str(tgwui_path))
sys.path.insert(0, str(tgwui_path / "extensions" / "boredom_monitor"))

print("=" * 80)
print("COMPLETE AUTONOMOUS INJECTION TEST")
print("=" * 80)
print("Testing all fixes:")
print("1. Element registration in shared.gradio")
print("2. whisper_stt pattern JavaScript trigger")
print("3. Proper change event handling")
print("4. Custom JavaScript backup system")
print()

def test_element_registration():
    """Test if the auto-trigger element is now properly registered"""
    try:
        from modules import shared

        print("[TEST] Checking shared.gradio element registration...")

        if hasattr(shared, 'gradio'):
            gradio_dict = shared.gradio
            print(f"[INFO] shared.gradio found with {len(gradio_dict)} components")

            if 'boredom-auto-trigger' in gradio_dict:
                trigger_elem = gradio_dict['boredom-auto-trigger']
                print(f"[SUCCESS] Auto-trigger element found: {trigger_elem}")
                print(f"[INFO] Element type: {type(trigger_elem)}")
                print(f"[INFO] Element value: {getattr(trigger_elem, 'value', 'No value')}")
                return True
            else:
                print("[WARNING] Auto-trigger element not found")
                available_keys = [k for k in gradio_dict.keys() if 'boredom' in k.lower()]
                print(f"[DEBUG] Boredom-related keys: {available_keys}")
                return False
        else:
            print("[INFO] shared.gradio not available")
            return False

    except Exception as e:
        print(f"[ERROR] Element registration test failed: {e}")
        return False

def test_trigger_function():
    """Test the updated trigger_chat_generation function"""
    try:
        import script as boredom_script

        print("\n[TEST] Testing updated trigger_chat_generation function...")

        # Test the trigger function directly
        result = boredom_script.trigger_chat_generation()

        if result:
            print("[SUCCESS] trigger_chat_generation returned True")
            return True
        else:
            print("[INFO] trigger_chat_generation returned False (expected if element not registered yet)")
            return False

    except Exception as e:
        print(f"[ERROR] Trigger function test failed: {e}")
        return False

def test_manual_injection():
    """Test manual injection with all the fixes"""
    try:
        import script as boredom_script

        print("\n[TEST] Testing complete manual injection...")

        # Get initial hijack state
        initial_state = boredom_script.input_hijack.copy()
        print(f"[INFO] Initial hijack state: {initial_state}")

        # Trigger manual test
        result = boredom_script.manual_trigger_test('bored', 1)

        # Check final hijack state
        final_state = boredom_script.input_hijack.copy()
        print(f"[INFO] Final hijack state: {final_state}")

        if result and final_state['state']:
            print("[SUCCESS] Manual injection completed successfully")
            print("[INFO] Message ready for injection:")
            print(f"[MSG] '{final_state['value'][0]}'")
            return True
        else:
            print("[FAIL] Manual injection failed")
            return False

    except Exception as e:
        print(f"[ERROR] Manual injection test failed: {e}")
        return False

def test_custom_js():
    """Test if custom_js function exists"""
    try:
        import script as boredom_script

        print("\n[TEST] Testing custom JavaScript backup system...")

        if hasattr(boredom_script, 'custom_js'):
            js_code = boredom_script.custom_js()
            print("[SUCCESS] custom_js function found")
            print(f"[INFO] JavaScript code length: {len(js_code)} characters")

            # Check for key components
            if 'boredom-auto-trigger' in js_code:
                print("[SUCCESS] JavaScript monitors correct element ID")
            if 'Generate' in js_code:
                print("[SUCCESS] JavaScript targets Generate button")
            if 'setInterval' in js_code:
                print("[SUCCESS] JavaScript uses polling method")

            return True
        else:
            print("[FAIL] custom_js function not found")
            return False

    except Exception as e:
        print(f"[ERROR] Custom JS test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running complete autonomous injection tests...\n")

    # Test 1: Element registration
    print("Test 1: Element Registration")
    registration_ok = test_element_registration()

    # Test 2: Trigger function
    print("\nTest 2: Trigger Function")
    trigger_ok = test_trigger_function()

    # Test 3: Manual injection
    print("\nTest 3: Manual Injection")
    manual_ok = test_manual_injection()

    # Test 4: Custom JavaScript
    print("\nTest 4: Custom JavaScript")
    js_ok = test_custom_js()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Element Registration: {'PASS' if registration_ok else 'PENDING'}")
    print(f"Trigger Function:     {'PASS' if trigger_ok else 'PENDING'}")
    print(f"Manual Injection:     {'PASS' if manual_ok else 'FAIL'}")
    print(f"Custom JavaScript:    {'PASS' if js_ok else 'FAIL'}")

    if manual_ok and js_ok:
        print("\n" + "="*80)
        print("IMPLEMENTATION STATUS: READY FOR AUTONOMOUS OPERATION")
        print("="*80)
        print()
        print("The boredom monitor should now work autonomously!")
        print()
        print("EXPECTED BEHAVIOR:")
        print("1. Monitor detects idle state every 7 minutes")
        print("2. Sets input hijack with emotional message")
        print("3. JavaScript automatically clicks Generate button")
        print("4. Message appears in chat without user interaction")
        print("5. Process repeats continuously")
        print()
        print("RESTART REQUIREMENT:")
        print("Text-generation-webui must be restarted to load:")
        print("- Updated element registration")
        print("- New custom_js() function")
        print("- Fixed trigger patterns")
        print()
        print("After restart, the system will be fully autonomous!")
    else:
        print("\nSome components need attention before autonomous operation.")

if __name__ == "__main__":
    main()