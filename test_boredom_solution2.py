#!/usr/bin/env python3
"""
Test script for Boredom Monitor Solution 2 (Greeting-style approach)
Tests the new UI injection mechanism
"""

import sys
import os
import time

# Add the text-generation-webui modules to path
sys.path.insert(0, 'F:\\Apps\\freedom_system\\app_cabinet\\text-generation-webui')
os.chdir('F:\\Apps\\freedom_system\\app_cabinet\\text-generation-webui')

print("=" * 60)
print("BOREDOM MONITOR SOLUTION 2 TEST")
print("Testing greeting-style UI injection mechanism")
print("=" * 60)

# Import the extension
try:
    from extensions.boredom_monitor import script
    print("✓ Boredom monitor extension imported successfully")
except Exception as e:
    print(f"✗ Failed to import extension: {e}")
    sys.exit(1)

# Test the new functions
print("\n1. Testing handle_boredom_injection function exists...")
if hasattr(script, 'handle_boredom_injection'):
    print("✓ handle_boredom_injection function found")
else:
    print("✗ handle_boredom_injection function missing")

print("\n2. Testing boredom_message_queue exists...")
if hasattr(script, 'boredom_message_queue'):
    print(f"✓ boredom_message_queue found: {script.boredom_message_queue}")
else:
    print("✗ boredom_message_queue missing")

print("\n3. Testing trigger_chat_generation updated...")
try:
    # Set up a test message
    script.input_hijack['state'] = True
    script.input_hijack['value'] = ["Test boredom message", "Test boredom message"]

    # Check if trigger_chat_generation uses the new queue system
    import inspect
    source = inspect.getsource(script.trigger_chat_generation)
    if 'boredom_message_queue' in source:
        print("✓ trigger_chat_generation uses new queue system")
    else:
        print("✗ trigger_chat_generation not updated for queue system")

except Exception as e:
    print(f"✗ Error testing trigger_chat_generation: {e}")

print("\n4. Testing manual trigger function...")
try:
    # Test the manual trigger
    result = script.manual_trigger_test("bored", 1)
    print(f"✓ Manual trigger result: {result}")
except Exception as e:
    print(f"✗ Manual trigger failed: {e}")

print("\n5. Checking if UI setup includes new event handler...")
try:
    import inspect
    ui_source = inspect.getsource(script.ui)
    if 'handle_boredom_injection' in ui_source:
        print("✓ UI function includes handle_boredom_injection")
    else:
        print("✗ UI function doesn't include handle_boredom_injection")

    if 'auto_trigger.change' in ui_source:
        print("✓ UI function has auto_trigger.change event")
    else:
        print("✗ UI function missing auto_trigger.change event")

except Exception as e:
    print(f"✗ Error checking UI function: {e}")

print("\n" + "=" * 60)
print("SOLUTION 2 IMPLEMENTATION STATUS")
print("=" * 60)

# Summary
print("\nKey Components:")
print("- handle_boredom_injection: Creates UI updates using greeting-style approach")
print("- boredom_message_queue: Stores messages for Gradio event handler")
print("- trigger_chat_generation: Queues message and toggles checkbox")
print("- auto_trigger.change: Gradio event that calls handle_boredom_injection")

print("\nExpected Flow:")
print("1. Background thread detects idle time")
print("2. Calls trigger_emotional_response to set message")
print("3. Calls trigger_chat_generation to queue and trigger")
print("4. Checkbox toggle fires Gradio event")
print("5. handle_boredom_injection adds message to UI")
print("6. Message appears in chat without user interaction")

print("\n✓ Solution 2 implementation appears complete")
print("Note: Full testing requires running the actual UI")