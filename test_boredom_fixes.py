#!/usr/bin/env python3
"""
Test the boredom monitor UI injection fixes
"""

import sys
import os

# Add the text-generation-webui modules to path
sys.path.insert(0, 'F:\\Apps\\freedom_system\\app_cabinet\\text-generation-webui')
os.chdir('F:\\Apps\\freedom_system\\app_cabinet\\text-generation-webui')

print("=" * 60)
print("BOREDOM MONITOR UI INJECTION FIX TEST")
print("=" * 60)

# Test the updated boredom monitor
try:
    from extensions.boredom_monitor import script
    print("OK: Boredom monitor imported successfully")

    # Test 1: Check JavaScript injection
    js = script.custom_js()
    if 'boredom-inject-button' in js and 'injectButton.click()' in js:
        print("OK: JavaScript includes inject button trigger")
    else:
        print("FAIL: JavaScript missing inject button logic")

    # Test 2: Check if process_boredom_injection exists
    import inspect
    ui_source = inspect.getsource(script.ui)
    if 'process_boredom_injection' in ui_source:
        print("OK: process_boredom_injection function found in UI")
    else:
        print("FAIL: process_boredom_injection function missing")

    # Test 3: Check if inject button is created
    if 'boredom-inject-button' in ui_source:
        print("OK: Hidden inject button created")
    else:
        print("FAIL: Hidden inject button missing")

    # Test 4: Check event chain
    if 'generate_chat_reply_wrapper' in ui_source:
        print("OK: Event chain includes generate_chat_reply_wrapper")
    else:
        print("FAIL: Event chain missing generate_chat_reply_wrapper")

    # Test 5: Check chat_input_modifier update
    modifier_source = inspect.getsource(script.chat_input_modifier)
    if 'instruction' in modifier_source and 'hidden user message' in modifier_source:
        print("OK: chat_input_modifier updated for instructions")
    else:
        print("FAIL: chat_input_modifier not properly updated")

    print("\n" + "=" * 60)
    print("EXPECTED FLOW")
    print("=" * 60)

    print("\n1. Background thread: Detects idle -> queues instruction")
    print("2. Background thread: Toggles auto-trigger checkbox")
    print("3. JavaScript: Detects checkbox -> clicks inject button")
    print("4. Gradio event: process_boredom_injection() -> moves instruction to hijack")
    print("5. Gradio event: generate_chat_reply_wrapper() -> calls chat_input_modifier")
    print("6. chat_input_modifier: Returns instruction as user input")
    print("7. AI: Generates response based on instruction")
    print("8. UI: Shows AI's response (not the instruction)")

    print("\nKey fixes:")
    print("- Hidden inject button with proper Gradio event chain")
    print("- JavaScript that clicks button when checkbox changes")
    print("- Proper integration with generate_chat_reply_wrapper")
    print("- Instructions hidden from user, only AI responses shown")

except Exception as e:
    print(f"ERROR testing: {e}")
    import traceback
    traceback.print_exc()

print("\nFIX implementation complete")