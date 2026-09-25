"""
Test Runner - Injection × Verification Matrix
==============================================
Runs the full 26 injection × 14 verification test matrix.
Executes INSIDE the boredom_monitor extension.

Usage:
    from .test_runner import run_full_test_matrix
"""

import time
import json
from datetime import datetime
from pathlib import Path

from modules import shared

# Import test harnesses
from .injection_test_harness import (
    ALL_INJECTION_METHODS,
    run_injection_method,
    run_all_injections,
    log_test
)
from .verification_harness import (
    ALL_VERIFICATION_METHODS,
    run_verification_method,
    run_all_verifications,
    quick_verify,
    log_verify
)


# Test configuration
TEST_MESSAGE_PREFIX = "[INJECTION-TEST]"
# Absolute path for logs, JSON results go to extension directory
LOG_DIR = Path("F:/Apps/freedom_system/log")
EXTENSION_DIR = Path(__file__).parent


def generate_test_message(method_num: int) -> str:
    """Generate unique test message for each injection method"""
    timestamp = datetime.now().strftime("%H%M%S")
    return f"{TEST_MESSAGE_PREFIX} Method-{method_num} @ {timestamp}"


def clear_history():
    """
    DEPRECATED: This function wipes character context and breaks UI connection.
    Use get_current_character_state() instead to preserve the active session.
    Kept for backwards compatibility but should not be used.
    """
    print("[TEST-RUNNER] WARNING: clear_history() is deprecated - use get_current_character_state() instead")
    try:
        if hasattr(shared, 'gradio') and 'history' in shared.gradio:
            history_component = shared.gradio['history']
            if hasattr(history_component, 'value'):
                history_component.value = {'internal': [], 'visible': []}
            else:
                shared.gradio['history'] = {'internal': [], 'visible': []}
            return True
    except Exception as e:
        print(f"[TEST-RUNNER] Failed to clear history: {e}")
    return False


def get_current_character_state():
    """
    Get the current character context from the active UI session.
    This preserves the loaded character (e.g., Willow_Chat) so tests
    inject into the actual visible conversation.

    Returns:
        dict with character_menu, unique_id, name1, name2, mode, chat_style,
        context, greeting, and history from the active session
    """
    state = {
        'character_menu': None,
        'unique_id': None,
        'name1': 'You',
        'name2': 'Assistant',
        'mode': 'chat',
        'chat_style': 'cai-chat',
        'context': '',
        'greeting': '',
        'history': {'internal': [], 'visible': []}
    }

    # Primary source: persistent_interface_state (the active session)
    if hasattr(shared, 'persistent_interface_state') and shared.persistent_interface_state:
        pis = shared.persistent_interface_state
        state['character_menu'] = pis.get('character_menu')
        state['unique_id'] = pis.get('unique_id')
        state['name1'] = pis.get('name1', 'You')
        state['name2'] = pis.get('name2', 'Assistant')
        state['mode'] = pis.get('mode', 'chat')
        state['chat_style'] = pis.get('chat_style', 'cai-chat')
        state['context'] = pis.get('context', '')
        state['greeting'] = pis.get('greeting', '')
        state['history'] = pis.get('history', {'internal': [], 'visible': []})

        print(f"[TEST-RUNNER] Loaded character state: {state['character_menu']} (unique_id: {state['unique_id']})")
        return state

    # Fallback: read from shared.gradio components directly
    if hasattr(shared, 'gradio'):
        gradio = shared.gradio

        for key in ['character_menu', 'unique_id', 'name1', 'name2', 'mode', 'chat_style', 'context', 'greeting']:
            if key in gradio:
                component = gradio[key]
                if hasattr(component, 'value'):
                    state[key] = component.value

        # Get history
        if 'history' in gradio:
            history_component = gradio['history']
            if hasattr(history_component, 'value') and history_component.value:
                state['history'] = history_component.value

        print(f"[TEST-RUNNER] Loaded character state from gradio: {state['character_menu']}")
    else:
        print("[TEST-RUNNER] WARNING: No character state available - tests may not display in UI")

    return state


def refresh_chat_display(history, state):
    """
    Refresh the chat display after injection so the message appears in UI.

    Args:
        history: The modified history dict
        state: The character state from get_current_character_state()

    Returns:
        HTML string if successful, None if failed
    """
    try:
        from modules.chat import redraw_html

        html = redraw_html(
            history,
            state.get('name1', 'You'),
            state.get('name2', 'Assistant'),
            state.get('mode', 'chat'),
            state.get('chat_style', 'cai-chat'),
            state.get('character_menu', '')
        )

        # Update the display component if available
        if hasattr(shared, 'gradio') and 'display' in shared.gradio:
            display_component = shared.gradio['display']
            if hasattr(display_component, 'value'):
                display_component.value = html
                print(f"[TEST-RUNNER] Display refreshed - HTML length: {len(html)}")
                return html

        print(f"[TEST-RUNNER] Generated HTML but couldn't update display component")
        return html

    except Exception as e:
        print(f"[TEST-RUNNER] Failed to refresh display: {e}")
        return None


def save_results(results: dict, filename: str = None):
    """Save test results to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"injection_matrix_results_{timestamp}.json"

    filepath = EXTENSION_DIR / filename

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"[TEST-RUNNER] Results saved to {filepath}")
        return str(filepath)
    except Exception as e:
        print(f"[TEST-RUNNER] Failed to save results: {e}")
        return None


def print_injection_details(injection_num: int, result: dict):
    """Print full details of an injection method result"""
    name = result.get("method", f"METHOD_{injection_num}")
    success = result.get("success", False)
    error = result.get("error")

    print(f"")
    print(f"  ┌─ INJECTION METHOD {injection_num}: {name}")
    print(f"  │  success: {success}")

    # Print all other fields
    for key, value in result.items():
        if key not in ["method", "success", "error"]:
            # Truncate long values
            str_value = str(value)
            if len(str_value) > 100:
                str_value = str_value[:100] + "..."
            print(f"  │  {key}: {str_value}")

    if error:
        print(f"  │  error: {error}")

    status = "✓ SUCCESS" if success else "✗ FAILED"
    print(f"  └─ {status}")


def print_verification_details(verify_num: int, result: dict):
    """Print full details of a verification method result"""
    name = result.get("method", f"VERIFY_{verify_num}")
    success = result.get("success", False)
    found = result.get("found", False)
    error = result.get("error")

    print(f"    ├─ V{verify_num} {name}")
    print(f"    │   success: {success}, found: {found}")

    # Print all other fields
    for key, value in result.items():
        if key not in ["method", "success", "found", "error"]:
            # Truncate long values
            str_value = str(value)
            if len(str_value) > 80:
                str_value = str_value[:80] + "..."
            print(f"    │   {key}: {str_value}")

    if error:
        print(f"    │   error: {error}")


def run_single_injection_test(injection_num: int, preserve_character: bool = True) -> dict:
    """
    Run a single injection method and verify with all 16 verification methods.

    Args:
        injection_num: Which injection method to test (1-26)
        preserve_character: If True, inject into the current character's conversation.
                           If False (legacy), clear history first (not recommended).

    Returns:
        dict with injection result and all verification results
    """
    result = {
        "injection_method": injection_num,
        "injection_name": ALL_INJECTION_METHODS.get(injection_num, ("UNKNOWN", None))[0],
        "timestamp": datetime.now().isoformat(),
        "injection_result": None,
        "verification_results": {},
        "any_verification_passed": False,
        "character_state": None,
        "display_refreshed": False
    }

    # Get the current character state (Willow_Chat, etc.)
    character_state = get_current_character_state()
    result["character_state"] = {
        "character_menu": character_state.get('character_menu'),
        "unique_id": character_state.get('unique_id'),
        "name2": character_state.get('name2'),
        "history_count_before": len(character_state.get('history', {}).get('visible', []))
    }

    # Legacy mode: clear history (deprecated, breaks UI connection)
    if not preserve_character:
        print("[TEST-RUNNER] WARNING: preserve_character=False - clearing history (not recommended)")
        clear_history()
        time.sleep(0.1)

    # Generate test message
    test_message = generate_test_message(injection_num)
    result["test_message"] = test_message

    print(f"")
    print(f"{'='*70}")
    print(f"TEST {injection_num}/26: {result['injection_name']}")
    print(f"Character: {character_state.get('character_menu', 'None')} (ID: {character_state.get('unique_id', 'None')})")
    print(f"Test message: {test_message}")
    print(f"{'='*70}")

    # Run injection
    try:
        injection_result = run_injection_method(injection_num, test_message)
        result["injection_result"] = injection_result
        print_injection_details(injection_num, injection_result)

        # If injection succeeded, refresh the display so message appears in UI
        if injection_result.get("success", False):
            # Get the updated history
            updated_state = get_current_character_state()
            updated_history = updated_state.get('history', {'internal': [], 'visible': []})

            # Refresh the chat display
            html = refresh_chat_display(updated_history, character_state)
            if html:
                result["display_refreshed"] = True
                print(f"  [DISPLAY] Refreshed successfully")
            else:
                print(f"  [DISPLAY] Refresh failed - message may not appear in UI")

    except Exception as e:
        result["injection_result"] = {"method": result['injection_name'], "success": False, "error": str(e)}
        print(f"  [INJECTION] EXCEPTION: {e}")

    # Wait for injection to propagate
    time.sleep(0.3)

    # Run all 16 verifications (14 server-side + 2 browser-side)
    print(f"")
    print(f"  VERIFICATION RESULTS (16 methods):")
    print(f"  {'─'*50}")

    for verify_num in range(1, 17):
        try:
            verify_result = run_verification_method(verify_num, test_message)
            result["verification_results"][verify_num] = verify_result

            print_verification_details(verify_num, verify_result)

            if verify_result.get("found", False):
                result["any_verification_passed"] = True

        except Exception as e:
            result["verification_results"][verify_num] = {"method": f"VERIFY_{verify_num}", "success": False, "found": False, "error": str(e)}
            print(f"    ├─ V{verify_num} EXCEPTION: {e}")

    # Summary for this injection
    verified_by = [v for v, r in result["verification_results"].items() if r.get("found", False)]
    print(f"  {'─'*50}")
    if verified_by:
        print(f"  VERIFIED BY: {verified_by}")
    else:
        print(f"  NOT VERIFIED by any method")
    print(f"  Display refreshed: {result['display_refreshed']}")
    print(f"")

    return result


def run_full_test_matrix() -> dict:
    """
    Run the full 26 × 16 test matrix.

    Returns:
        dict with all results and summary
    """
    start_time = datetime.now()

    print(f"")
    print(f"{'#'*70}")
    print(f"#")
    print(f"# FULL INJECTION TEST MATRIX")
    print(f"# 26 Injection Methods × 16 Verification Methods = 416 Tests")
    print(f"#")
    print(f"# Started: {start_time.isoformat()}")
    print(f"#")
    print(f"{'#'*70}")

    # Print all injection methods
    print(f"")
    print(f"INJECTION METHODS TO TEST:")
    print(f"{'─'*70}")
    for num, (name, func) in ALL_INJECTION_METHODS.items():
        print(f"  {num:2d}. {name}")

    # Print all verification methods
    print(f"")
    print(f"VERIFICATION METHODS TO USE:")
    print(f"{'─'*70}")
    for num, (name, func) in ALL_VERIFICATION_METHODS.items():
        print(f"  {num:2d}. {name}")

    print(f"")
    print(f"{'='*70}")
    print(f"BEGINNING TEST MATRIX")
    print(f"{'='*70}")

    results = {
        "start_time": start_time.isoformat(),
        "end_time": None,
        "duration_seconds": None,
        "total_injections": 26,
        "total_verifications": 16,
        "matrix": {},
        "summary": {
            "successful_injections": [],
            "failed_injections": [],
            "verified_injections": [],
            "unverified_injections": [],
            "verification_matrix": {}
        }
    }

    # Get character state once at the start for the summary
    initial_state = get_current_character_state()
    results["character_context"] = {
        "character_menu": initial_state.get('character_menu'),
        "unique_id": initial_state.get('unique_id'),
        "name2": initial_state.get('name2')
    }

    print(f"")
    print(f"CHARACTER CONTEXT:")
    print(f"{'─'*70}")
    print(f"  Character: {initial_state.get('character_menu', 'None')}")
    print(f"  Unique ID: {initial_state.get('unique_id', 'None')}")
    print(f"  Bot Name: {initial_state.get('name2', 'Assistant')}")
    print(f"")

    # Run each injection method (preserving character context)
    for injection_num in range(1, 27):
        try:
            test_result = run_single_injection_test(injection_num, preserve_character=True)
            results["matrix"][injection_num] = test_result

            # Track successes
            injection_success = test_result["injection_result"].get("success", False)
            verification_passed = test_result["any_verification_passed"]

            if injection_success:
                results["summary"]["successful_injections"].append(injection_num)
                if verification_passed:
                    results["summary"]["verified_injections"].append(injection_num)
                else:
                    results["summary"]["unverified_injections"].append(injection_num)
            else:
                results["summary"]["failed_injections"].append(injection_num)

            # Record which verifications found this injection
            verified_by = [v for v, r in test_result["verification_results"].items() if r.get("found", False)]
            results["summary"]["verification_matrix"][injection_num] = verified_by

            # Brief pause between injection tests
            time.sleep(0.5)

        except Exception as e:
            print(f"[TEST-RUNNER] CRITICAL ERROR on injection {injection_num}: {e}")
            results["matrix"][injection_num] = {"error": str(e)}
            results["summary"]["failed_injections"].append(injection_num)

    # Calculate duration
    end_time = datetime.now()
    results["end_time"] = end_time.isoformat()
    results["duration_seconds"] = (end_time - start_time).total_seconds()

    # Print final summary
    print(f"")
    print(f"{'#'*70}")
    print(f"#")
    print(f"# FULL TEST MATRIX COMPLETE")
    print(f"#")
    print(f"# Duration: {results['duration_seconds']:.1f} seconds")
    print(f"# Started:  {results['start_time']}")
    print(f"# Ended:    {results['end_time']}")
    print(f"#")
    print(f"{'#'*70}")

    print(f"")
    print(f"INJECTION RESULTS SUMMARY:")
    print(f"{'─'*70}")
    print(f"  Total injection methods tested: 26")
    print(f"  Successful injections:          {len(results['summary']['successful_injections'])}")
    print(f"  Failed injections:              {len(results['summary']['failed_injections'])}")
    print(f"  Verified by at least 1 method:  {len(results['summary']['verified_injections'])}")
    print(f"  Unverified (success but not found): {len(results['summary']['unverified_injections'])}")

    print(f"")
    print(f"SUCCESSFUL INJECTIONS:")
    print(f"{'─'*70}")
    if results['summary']['successful_injections']:
        for num in results['summary']['successful_injections']:
            name = ALL_INJECTION_METHODS.get(num, ("UNKNOWN", None))[0]
            verified_by = results['summary']['verification_matrix'].get(num, [])
            if verified_by:
                print(f"  {num:2d}. {name} - VERIFIED by {verified_by}")
            else:
                print(f"  {num:2d}. {name} - not verified")
    else:
        print(f"  (none)")

    print(f"")
    print(f"FAILED INJECTIONS:")
    print(f"{'─'*70}")
    if results['summary']['failed_injections']:
        for num in results['summary']['failed_injections']:
            name = ALL_INJECTION_METHODS.get(num, ("UNKNOWN", None))[0]
            error = results['matrix'].get(num, {}).get('injection_result', {}).get('error', 'unknown')
            print(f"  {num:2d}. {name} - {error}")
    else:
        print(f"  (none)")

    print(f"")
    print(f"VERIFIED INJECTIONS (RECOMMENDED):")
    print(f"{'─'*70}")
    if results['summary']['verified_injections']:
        for num in results['summary']['verified_injections']:
            name = ALL_INJECTION_METHODS.get(num, ("UNKNOWN", None))[0]
            verified_by = results['summary']['verification_matrix'].get(num, [])
            print(f"  {num:2d}. {name}")
            print(f"      Verified by: {verified_by}")
    else:
        print(f"  (none) - NO METHODS VERIFIED")
        print(f"  Further investigation needed")

    print(f"")
    print(f"VERIFICATION METHOD EFFECTIVENESS:")
    print(f"{'─'*70}")
    for verify_num, (verify_name, _) in ALL_VERIFICATION_METHODS.items():
        found_count = sum(1 for inj_num, verifiers in results['summary']['verification_matrix'].items() if verify_num in verifiers)
        print(f"  V{verify_num:2d} {verify_name}: found {found_count}/26 injections")

    print(f"")
    print(f"{'#'*70}")
    print(f"# END OF TEST MATRIX REPORT")
    print(f"{'#'*70}")

    # Save results
    save_results(results)

    return results


def get_test_status() -> dict:
    """Get current test harness status"""
    return {
        "injection_methods_available": len(ALL_INJECTION_METHODS),
        "verification_methods_available": len(ALL_VERIFICATION_METHODS),
        "shared_gradio_available": hasattr(shared, 'gradio'),
        "history_available": hasattr(shared, 'gradio') and 'history' in getattr(shared, 'gradio', {}),
        "log_directory": str(LOG_DIR),
        "log_directory_exists": LOG_DIR.exists()
    }
