#!/usr/bin/env python3
"""
Test manual trigger to debug the injection process step by step
"""

import sys
import os

# Add the text-generation-webui modules to path
sys.path.insert(0, 'F:\\Apps\\freedom_system\\app_cabinet\\text-generation-webui')
os.chdir('F:\\Apps\\freedom_system\\app_cabinet\\text-generation-webui')

print("=" * 60)
print("MANUAL BOREDOM INJECTION TEST")
print("=" * 60)

try:
    from extensions.boredom_monitor import script

    print("Step 1: Test trigger_emotional_response")
    success = script.trigger_emotional_response("bored", 1)
    print(f"Result: {success}")
    print(f"Input hijack state: {script.input_hijack}")
    print(f"Message queue state: {script.boredom_message_queue}")

    print("\nStep 2: Test trigger_chat_generation")
    success = script.trigger_chat_generation()
    print(f"Result: {success}")
    print(f"Message queue after trigger: {script.boredom_message_queue}")

    print("\nStep 3: Check if auto-trigger element exists")
    if hasattr(script, 'shared') and script.shared and hasattr(script.shared, 'gradio'):
        if 'boredom-auto-trigger' in script.shared.gradio:
            trigger = script.shared.gradio['boredom-auto-trigger']
            print(f"Auto-trigger found: {trigger}")
            print(f"Auto-trigger value: {getattr(trigger, 'value', 'No value attr')}")
        else:
            print("Auto-trigger NOT found in shared.gradio")
            print(f"Available gradio keys: {list(script.shared.gradio.keys()) if script.shared.gradio else 'None'}")
    else:
        print("shared.gradio not available")

    print("\nStep 4: Check if inject button exists")
    if hasattr(script, 'shared') and script.shared and hasattr(script.shared, 'gradio'):
        if 'boredom-inject-button' in script.shared.gradio:
            button = script.shared.gradio['boredom-inject-button']
            print(f"Inject button found: {button}")
        else:
            print("Inject button NOT found in shared.gradio")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("ANALYSIS")
print("=" * 60)
print("This test shows whether:")
print("1. The trigger functions work")
print("2. The gradio elements are registered")
print("3. The message queue system functions")
print("4. Whether the issue is in JavaScript or Gradio events")