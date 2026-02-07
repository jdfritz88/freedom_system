"""
Test if the display component trigger works for boredom monitor AI injection
"""
import sys
import time
sys.path.insert(0, r'F:\Apps\freedom_system\app_cabinet\text-generation-webui')

print("=" * 70)
print(" TESTING DISPLAY COMPONENT TRIGGER FOR AI INJECTION")
print("=" * 70)

print("\n[1/4] Waiting 120 seconds for text-gen-webui to fully start...")
time.sleep(120)

print("\n[2/4] Importing boredom monitor extension...")
try:
    from extensions.boredom_monitor import script as boredom_script
    from modules import shared
    print("✓ Boredom monitor imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

print("\n[3/4] Checking if display component exists...")
if 'display' in shared.gradio:
    print(f"✓ Display component found: {type(shared.gradio['display'])}")
    print(f"  Current value: {shared.gradio['display'].value}")
else:
    print("✗ Display component NOT found in shared.gradio")
    print(f"  Available components: {list(shared.gradio.keys())[:10]}...")

print("\n[4/4] Testing Method 1 injection with display trigger...")
test_message = "Express a brief bored sigh in character."

try:
    # Get initial history length
    if 'interface_state' in shared.gradio:
        state_comp = shared.gradio['interface_state']
        state = state_comp.value if hasattr(state_comp, 'value') else state_comp
        if state and 'history' in state:
            initial_len = len(state['history'].get('visible', []))
            print(f"  Initial visible history length: {initial_len}")
        else:
            initial_len = 0
            print(f"  No existing history found")

    # Call injection method
    print(f"\n  Calling inject_via_hijack()...")
    result = boredom_script.inject_via_hijack(test_message)

    if result:
        print(f"✓ Injection returned True")

        # Check if history was updated
        state_comp = shared.gradio['interface_state']
        state = state_comp.value if hasattr(state_comp, 'value') else state_comp
        if state and 'history' in state:
            final_len = len(state['history'].get('visible', []))
            print(f"  Final visible history length: {final_len}")

            if final_len > initial_len:
                latest_msg = state['history']['visible'][-1]
                print(f"✓ New message added to history:")
                print(f"  User: '{latest_msg[0]}'")
                print(f"  AI: '{latest_msg[1][:100]}...'")

        # Check if display was updated
        if 'display' in shared.gradio:
            display_value = shared.gradio['display'].value
            print(f"\n  Display component updated:")
            print(f"  Type: {type(display_value)}")
            if isinstance(display_value, dict):
                print(f"  Keys: {list(display_value.keys())}")
                if 'visible' in display_value:
                    print(f"  Visible history length: {len(display_value['visible'])}")
            else:
                print(f"  Value: {display_value}")
    else:
        print(f"✗ Injection returned False")

except Exception as e:
    print(f"✗ Test failed with exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print(" TEST COMPLETE")
print("=" * 70)
