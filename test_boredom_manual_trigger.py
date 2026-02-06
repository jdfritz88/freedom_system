#!/usr/bin/env python3
"""
Manual test script for boredom monitor injection
Run this AFTER starting text-generation-webui
"""

import sys
import time
from pathlib import Path

# Add text-generation-webui to path
tgwui_path = Path("F:/Apps/freedom_system/freedom_system_2000/text-generation-webui")
sys.path.insert(0, str(tgwui_path))
sys.path.insert(0, str(tgwui_path / "extensions" / "boredom_monitor"))

print("=" * 60)
print("BOREDOM MONITOR INJECTION TEST")
print("=" * 60)
print()
print("Prerequisites:")
print("1. text-generation-webui must be running")
print("2. Boredom monitor extension must be enabled")
print("3. Open chat tab in browser")
print()

def test_manual_trigger():
    """Test manual trigger function"""
    try:
        # Import the boredom monitor script
        import script as boredom_script

        print("[TEST] Boredom monitor script imported successfully")

        # Check if manual trigger exists
        if hasattr(boredom_script, 'manual_trigger_test'):
            print("[TEST] manual_trigger_test function found")

            # Test the hijack mechanism
            print("\n[TEST] Testing input hijack mechanism...")
            if hasattr(boredom_script, 'input_hijack'):
                hijack = boredom_script.input_hijack
                print(f"[TEST] Initial hijack state: {hijack}")

                # Trigger a test message
                print("\n[TEST] Triggering emotional response...")
                result = boredom_script.manual_trigger_test('bored', 1)

                if result:
                    print("[SUCCESS] Manual trigger succeeded!")
                    print("[SUCCESS] Hijack has been set")

                    # Check hijack state after trigger
                    print(f"[TEST] Hijack state after trigger: {boredom_script.input_hijack}")

                    print("\n[INFO] The message should appear in chat UI:")
                    print("  - If chat generation was triggered automatically")
                    print("  - OR on your next interaction with the chat")
                    print("\n[ACTION] Please check the chat UI now!")
                    print("[ACTION] If no message appears, type anything in chat and press Enter")
                else:
                    print("[FAIL] Manual trigger failed")
            else:
                print("[FAIL] input_hijack not found")
        else:
            print("[FAIL] manual_trigger_test function not found")

    except ImportError as e:
        print(f"[FAIL] Could not import boredom monitor: {e}")
        print("\n[INFO] Make sure:")
        print("  1. text-generation-webui is running")
        print("  2. You're running this test from the correct environment")

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")

def test_multiple_emotions():
    """Test different emotional states"""
    try:
        import script as boredom_script

        print("\n" + "=" * 60)
        print("TESTING MULTIPLE EMOTIONAL STATES")
        print("=" * 60)

        emotions = [
            ('bored', 1, "Bored state"),
            ('lonely', 1, "Lonely state"),
            ('horny', 1, "Horny stage 1"),
            ('horny', 2, "Horny stage 2"),
        ]

        for emotion, stage, description in emotions:
            print(f"\n[TEST] Testing {description}...")

            result = boredom_script.manual_trigger_test(emotion, stage)

            if result:
                print(f"[SUCCESS] {description} triggered")
            else:
                print(f"[FAIL] {description} failed")

            # Wait between tests
            print("[INFO] Waiting 3 seconds before next test...")
            time.sleep(3)

    except Exception as e:
        print(f"[ERROR] Multiple emotion test failed: {e}")

def main():
    """Run all tests"""
    print("Starting boredom monitor injection tests...\n")

    # Test 1: Basic manual trigger
    test_manual_trigger()

    # Ask if user wants to test multiple emotions
    print("\n" + "=" * 60)
    user_input = input("Do you want to test multiple emotional states? (y/n): ")

    if user_input.lower() == 'y':
        test_multiple_emotions()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\n[IMPORTANT] Check the text-generation-webui chat interface!")
    print("If messages don't appear automatically, type something and press Enter")

if __name__ == "__main__":
    main()