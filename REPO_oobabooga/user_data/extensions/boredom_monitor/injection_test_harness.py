"""
Injection Test Harness - All 26 Injection Methods
==================================================
Runs INSIDE the boredom_monitor extension with real access to:
- shared.gradio (actual server state)
- modules.chat (no circular imports)
- All extension hooks

Purpose: Find the ONE working injection method for boredom_monitor.
"""

import time
import json
import requests
from datetime import datetime
from pathlib import Path

# Import from parent extension context (already loaded)
from modules import shared

# Logging
def log_test(message, level="INFO"):
    """Test harness logging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{timestamp} [INJECTION-TEST] [{level}] {message}")

    # Also log to file
    try:
        log_path = Path("F:/Apps/freedom_system/log/injection_test_harness.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} [{level}] {message}\n")
    except:
        pass


# ============================================================================
# INJECTION METHOD 1: CHARACTER_GREETING
# Pattern from modules/chat.py start_new_chat()
# ============================================================================
def inject_method_1_character_greeting(test_message: str) -> dict:
    """
    Method 1: CHARACTER_GREETING
    Exact pattern from start_new_chat() - adds greeting to history
    """
    result = {"method": "CHARACTER_GREETING", "success": False, "error": None}

    try:
        log_test("Method 1: CHARACTER_GREETING - Starting")

        # Access the real history from shared.gradio
        # NOTE: shared.gradio['history'] is a Gradio State component, use .value to access data
        if not hasattr(shared, 'gradio') or 'history' not in shared.gradio:
            result["error"] = "shared.gradio['history'] not available"
            return result

        history_component = shared.gradio['history']
        if not hasattr(history_component, 'value'):
            result["error"] = "history component has no .value attribute"
            return result

        history = history_component.value
        if history is None:
            history = {'internal': [], 'visible': []}
            history_component.value = history

        # Add as greeting (assistant message)
        history['internal'].append(['', test_message])
        history['visible'].append(['', test_message])

        log_test(f"Method 1: Added to history - internal count: {len(history['internal'])}")
        result["success"] = True
        result["history_count"] = len(history['internal'])

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 1: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 2: HISTORY_MODIFIER (Extension Hook)
# ============================================================================
def inject_method_2_history_modifier(test_message: str) -> dict:
    """
    Method 2: HISTORY_MODIFIER
    Uses extension hook pattern to modify history
    """
    result = {"method": "HISTORY_MODIFIER", "success": False, "error": None}

    try:
        log_test("Method 2: HISTORY_MODIFIER - Starting")

        # Simulate what history_modifier hook does
        # NOTE: shared.gradio['history'] is a Gradio State component, use .value
        if hasattr(shared, 'gradio') and 'history' in shared.gradio:
            history_component = shared.gradio['history']
            history = history_component.value if hasattr(history_component, 'value') else history_component
            if history and 'visible' in history:
                # Insert as last message
                history['visible'].append(['', test_message])
                history['internal'].append(['', test_message])
                result["success"] = True
                result["history_count"] = len(history['visible'])
            else:
                result["error"] = "History structure invalid"
        else:
            result["error"] = "shared.gradio['history'] not available"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 2: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 3: STATE_MODIFIER (Extension Hook)
# ============================================================================
def inject_method_3_state_modifier(test_message: str) -> dict:
    """
    Method 3: STATE_MODIFIER
    Modifies state dict with pending message
    """
    result = {"method": "STATE_MODIFIER", "success": False, "error": None}

    try:
        log_test("Method 3: STATE_MODIFIER - Starting")

        # Access interface_state
        if hasattr(shared, 'gradio') and 'interface_state' in shared.gradio:
            state = shared.gradio['interface_state']
            if state:
                # Set pending injection in state
                state.value = state.value or {}
                state.value['pending_injection'] = test_message
                result["success"] = True
            else:
                result["error"] = "interface_state is None"
        else:
            result["error"] = "interface_state not available"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 3: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 4: CHAT_INPUT_MODIFIER (Extension Hook)
# ============================================================================
def inject_method_4_chat_input_modifier(test_message: str) -> dict:
    """
    Method 4: CHAT_INPUT_MODIFIER
    Modifies chat input text
    """
    result = {"method": "CHAT_INPUT_MODIFIER", "success": False, "error": None}

    try:
        log_test("Method 4: CHAT_INPUT_MODIFIER - Starting")

        # This hook modifies incoming chat text
        # We simulate by setting the Chat input state
        if hasattr(shared, 'gradio') and 'Chat input' in shared.gradio:
            chat_input = shared.gradio['Chat input']
            if chat_input:
                chat_input.value = {"text": test_message, "files": []}
                result["success"] = True
            else:
                result["error"] = "Chat input is None"
        else:
            result["error"] = "Chat input not available"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 4: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 5: INPUT_MODIFIER (Extension Hook)
# ============================================================================
def inject_method_5_input_modifier(test_message: str) -> dict:
    """
    Method 5: INPUT_MODIFIER
    General input modification hook
    """
    result = {"method": "INPUT_MODIFIER", "success": False, "error": None}

    try:
        log_test("Method 5: INPUT_MODIFIER - Starting")

        # Input modifier affects the string before it goes to the model
        # We set input_hijack to capture next input
        from . import script as boredom_script
        if hasattr(boredom_script, 'input_hijack'):
            boredom_script.input_hijack['state'] = True
            boredom_script.input_hijack['value'] = ["", test_message]
            result["success"] = True
            result["hijack_set"] = True
        else:
            result["error"] = "input_hijack not available in script"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 5: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 6: BOT_PREFIX_MODIFIER (Extension Hook)
# ============================================================================
def inject_method_6_bot_prefix_modifier(test_message: str) -> dict:
    """
    Method 6: BOT_PREFIX_MODIFIER
    Modifies the bot's response prefix
    """
    result = {"method": "BOT_PREFIX_MODIFIER", "success": False, "error": None}

    try:
        log_test("Method 6: BOT_PREFIX_MODIFIER - Starting")

        # Bot prefix is prepended to AI responses
        # We modify shared state to include prefix
        if hasattr(shared, 'settings'):
            # Store original and set new
            shared.settings['bot_prefix_injection'] = test_message
            result["success"] = True
        else:
            result["error"] = "shared.settings not available"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 6: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 7: OUTPUT_MODIFIER (Extension Hook)
# ============================================================================
def inject_method_7_output_modifier(test_message: str) -> dict:
    """
    Method 7: OUTPUT_MODIFIER
    Modifies output after generation
    """
    result = {"method": "OUTPUT_MODIFIER", "success": False, "error": None}

    try:
        log_test("Method 7: OUTPUT_MODIFIER - Starting")

        # Output modifier intercepts generated text
        # We store pending output modification
        if hasattr(shared, 'settings'):
            shared.settings['pending_output_injection'] = test_message
            result["success"] = True
        else:
            result["error"] = "shared.settings not available"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 7: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 8: CUSTOM_GENERATE_PROMPT (Extension Hook)
# ============================================================================
def inject_method_8_custom_generate_prompt(test_message: str) -> dict:
    """
    Method 8: CUSTOM_GENERATE_PROMPT
    Custom prompt generation hook
    """
    result = {"method": "CUSTOM_GENERATE_PROMPT", "success": False, "error": None}

    try:
        log_test("Method 8: CUSTOM_GENERATE_PROMPT - Starting")

        # This hook provides custom prompts
        # We can't fully test without triggering generation
        # But we can set up the state
        if hasattr(shared, 'settings'):
            shared.settings['custom_prompt_injection'] = test_message
            result["success"] = True
            result["note"] = "Prompt stored, requires generation to apply"
        else:
            result["error"] = "shared.settings not available"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 8: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 9: CUSTOM_GENERATE_REPLY (Extension Hook)
# ============================================================================
def inject_method_9_custom_generate_reply(test_message: str) -> dict:
    """
    Method 9: CUSTOM_GENERATE_REPLY
    Completely overrides generation with custom reply
    """
    result = {"method": "CUSTOM_GENERATE_REPLY", "success": False, "error": None}

    try:
        log_test("Method 9: CUSTOM_GENERATE_REPLY - Starting")

        # Store custom reply for next generation
        if hasattr(shared, 'settings'):
            shared.settings['custom_reply_override'] = test_message
            result["success"] = True
            result["note"] = "Reply stored, will override next generation"
        else:
            result["error"] = "shared.settings not available"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 9: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 10: LOGITS_PROCESSOR (Extension Hook)
# ============================================================================
def inject_method_10_logits_processor(test_message: str) -> dict:
    """
    Method 10: LOGITS_PROCESSOR
    Low-level logits modification (not applicable for text injection)
    """
    result = {"method": "LOGITS_PROCESSOR", "success": False, "error": None}

    try:
        log_test("Method 10: LOGITS_PROCESSOR - Starting")

        # Logits processor modifies token probabilities
        # Not directly applicable for injecting text
        result["error"] = "UNSUPPORTED - Logits processor cannot inject text directly"
        result["note"] = "This hook modifies token probabilities, not text"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 10: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 11: TOKENIZER_MODIFIER (Extension Hook)
# ============================================================================
def inject_method_11_tokenizer_modifier(test_message: str) -> dict:
    """
    Method 11: TOKENIZER_MODIFIER
    Tokenizer modification (not applicable for text injection)
    """
    result = {"method": "TOKENIZER_MODIFIER", "success": False, "error": None}

    try:
        log_test("Method 11: TOKENIZER_MODIFIER - Starting")

        # Tokenizer modifier affects encoding
        # Not directly applicable for injecting text
        result["error"] = "UNSUPPORTED - Tokenizer modifier cannot inject text directly"
        result["note"] = "This hook modifies tokenization, not text"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 11: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 12: SEND_DUMMY_MESSAGE
# ============================================================================
def inject_method_12_send_dummy_message(test_message: str) -> dict:
    """
    Method 12: SEND_DUMMY_MESSAGE
    Uses modules.chat.send_dummy_message()
    """
    result = {"method": "SEND_DUMMY_MESSAGE", "success": False, "error": None}

    try:
        log_test("Method 12: SEND_DUMMY_MESSAGE - Starting")

        from modules.chat import send_dummy_message

        # Get history from shared.gradio['history']
        if not hasattr(shared, 'gradio') or 'history' not in shared.gradio:
            result["error"] = "shared.gradio['history'] not available"
            log_test(f"Method 12: FAILED - {result['error']}", "ERROR")
            return result

        history_component = shared.gradio['history']
        history = history_component.value if hasattr(history_component, 'value') else history_component
        if history is None:
            history = {'internal': [], 'visible': [], 'metadata': {}}

        # Build state dict with required 'history' key
        state = {'history': history}

        # Get additional state values if available
        if 'interface_state' in shared.gradio:
            state_component = shared.gradio['interface_state']
            if state_component and hasattr(state_component, 'value') and state_component.value:
                interface_state = state_component.value
                for key in ['name1', 'name2', 'mode', 'chat_style', 'character_menu']:
                    if key in interface_state:
                        state[key] = interface_state[key]

        # Call send_dummy_message - returns only history
        history = send_dummy_message(test_message, state)

        # Update the shared history component
        if hasattr(history_component, 'value'):
            history_component.value = history

        result["success"] = True
        result["history_count"] = len(history['internal']) if history else 0
        log_test(f"Method 12: SUCCESS - history count: {result['history_count']}")

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 12: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 13: SEND_DUMMY_REPLY
# ============================================================================
def inject_method_13_send_dummy_reply(test_message: str) -> dict:
    """
    Method 13: SEND_DUMMY_REPLY
    Uses modules.chat.send_dummy_reply()
    """
    result = {"method": "SEND_DUMMY_REPLY", "success": False, "error": None}

    try:
        log_test("Method 13: SEND_DUMMY_REPLY - Starting")

        from modules.chat import send_dummy_reply

        # Get history from shared.gradio['history']
        if not hasattr(shared, 'gradio') or 'history' not in shared.gradio:
            result["error"] = "shared.gradio['history'] not available"
            log_test(f"Method 13: FAILED - {result['error']}", "ERROR")
            return result

        history_component = shared.gradio['history']
        history = history_component.value if hasattr(history_component, 'value') else history_component
        if history is None:
            history = {'internal': [], 'visible': [], 'metadata': {}}

        # send_dummy_reply needs a user message to exist first, or it creates a new row
        # Ensure there's at least one message in history for the reply to attach to
        if len(history['internal']) == 0:
            history['internal'].append(['', ''])
            history['visible'].append(['', ''])

        # Build state dict with required 'history' key
        state = {'history': history}

        # Get additional state values if available
        if 'interface_state' in shared.gradio:
            state_component = shared.gradio['interface_state']
            if state_component and hasattr(state_component, 'value') and state_component.value:
                interface_state = state_component.value
                for key in ['name1', 'name2', 'mode', 'chat_style', 'character_menu']:
                    if key in interface_state:
                        state[key] = interface_state[key]

        # Call send_dummy_reply - returns only history
        history = send_dummy_reply(test_message, state)

        # Update the shared history component
        if hasattr(history_component, 'value'):
            history_component.value = history

        result["success"] = True
        result["history_count"] = len(history['internal']) if history else 0
        log_test(f"Method 13: SUCCESS - history count: {result['history_count']}")

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 13: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 14: REDRAW_HTML
# ============================================================================
def inject_method_14_redraw_html(test_message: str) -> dict:
    """
    Method 14: REDRAW_HTML
    Uses modules.chat.redraw_html() after history modification
    """
    result = {"method": "REDRAW_HTML", "success": False, "error": None}

    try:
        log_test("Method 14: REDRAW_HTML - Starting")

        from modules.chat import redraw_html

        # Get history from shared.gradio['history']
        if not hasattr(shared, 'gradio') or 'history' not in shared.gradio:
            result["error"] = "shared.gradio['history'] not available"
            log_test(f"Method 14: FAILED - {result['error']}", "ERROR")
            return result

        history_component = shared.gradio['history']
        history = history_component.value if hasattr(history_component, 'value') else history_component
        if history is None:
            history = {'internal': [], 'visible': [], 'metadata': {}}

        # Add the test message to history
        history['internal'].append(['', test_message])
        history['visible'].append(['', test_message])

        # Update the history component
        if hasattr(history_component, 'value'):
            history_component.value = history

        # Get state values for redraw_html parameters
        name1 = 'You'
        name2 = 'Assistant'
        mode = 'chat'
        style = 'cai-chat'
        character = ''

        # Try to get actual values from interface_state
        if 'interface_state' in shared.gradio:
            state_component = shared.gradio['interface_state']
            if state_component and hasattr(state_component, 'value') and state_component.value:
                interface_state = state_component.value
                name1 = interface_state.get('name1', name1)
                name2 = interface_state.get('name2', name2)
                mode = interface_state.get('mode', mode)
                style = interface_state.get('chat_style', style)
                character = interface_state.get('character_menu', character)

        # Call redraw_html with all required parameters
        # Signature: redraw_html(history, name1, name2, mode, style, character, reset_cache=False)
        html = redraw_html(history, name1, name2, mode, style, character)

        result["success"] = True
        result["html_length"] = len(str(html)) if html else 0
        log_test(f"Method 14: SUCCESS - HTML length: {result['html_length']}")

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 14: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 15: DIRECT_HISTORY
# ============================================================================
def inject_method_15_direct_history(test_message: str) -> dict:
    """
    Method 15: DIRECT_HISTORY
    Direct manipulation of shared.gradio['history']
    """
    result = {"method": "DIRECT_HISTORY", "success": False, "error": None}

    try:
        log_test("Method 15: DIRECT_HISTORY - Starting")

        # NOTE: shared.gradio['history'] is a Gradio State component, use .value
        if hasattr(shared, 'gradio') and 'history' in shared.gradio:
            history_component = shared.gradio['history']
            if not hasattr(history_component, 'value'):
                result["error"] = "history component has no .value attribute"
                return result

            history = history_component.value

            if history is None:
                history = {'internal': [], 'visible': []}
                history_component.value = history

            # Direct append
            history['internal'].append(['', test_message])
            history['visible'].append(['', test_message])

            result["success"] = True
            result["history_count"] = len(history['internal'])
            log_test(f"Method 15: SUCCESS - history count: {result['history_count']}")
        else:
            result["error"] = "shared.gradio['history'] not available"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 15: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 16: GENERATE_WRAPPER
# ============================================================================
def inject_method_16_generate_wrapper(test_message: str) -> dict:
    """
    Method 16: GENERATE_WRAPPER
    Uses generate_chat_reply_wrapper to inject via generation
    """
    result = {"method": "GENERATE_WRAPPER", "success": False, "error": None}

    try:
        log_test("Method 16: GENERATE_WRAPPER - Starting")

        # This requires actual model to be loaded
        # We check if model is available
        if shared.model is None:
            result["error"] = "No model loaded - cannot use generate_wrapper"
            result["note"] = "This method requires an active model"
            return result

        from modules.chat import generate_chat_reply_wrapper

        # Get state
        state = {}
        if hasattr(shared, 'gradio') and 'interface_state' in shared.gradio:
            state_component = shared.gradio['interface_state']
            if state_component and hasattr(state_component, 'value'):
                state = state_component.value or {}

        # This would actually generate - skip for test
        result["error"] = "SKIPPED - Would trigger actual generation"
        result["note"] = "Use with caution - triggers model inference"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 16: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 17: OPENAI_CHAT_API
# ============================================================================
def inject_method_17_openai_chat_api(test_message: str) -> dict:
    """
    Method 17: OPENAI_CHAT_API
    POST to /v1/chat/completions endpoint
    """
    result = {"method": "OPENAI_CHAT_API", "success": False, "error": None}

    try:
        log_test("Method 17: OPENAI_CHAT_API - Starting")

        # Load endpoint from config
        from . import script as boredom_script
        endpoint = getattr(boredom_script, 'OPENAI_ENDPOINT', 'http://127.0.0.1:5000/v1/chat/completions')

        response = requests.post(
            endpoint,
            json={
                "messages": [
                    {"role": "user", "content": test_message}
                ],
                "max_tokens": 50,
                "stream": False
            },
            timeout=30
        )

        if response.status_code == 200:
            result["success"] = True
            result["response_preview"] = str(response.json())[:100]
            log_test(f"Method 17: SUCCESS - got response")
        else:
            result["error"] = f"HTTP {response.status_code}: {response.text[:100]}"

    except requests.exceptions.ConnectionError:
        result["error"] = "Connection refused - OpenAI extension not running"
    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 17: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 18: OPENAI_COMPLETIONS_API
# ============================================================================
def inject_method_18_openai_completions_api(test_message: str) -> dict:
    """
    Method 18: OPENAI_COMPLETIONS_API
    POST to /v1/completions endpoint
    """
    result = {"method": "OPENAI_COMPLETIONS_API", "success": False, "error": None}

    try:
        log_test("Method 18: OPENAI_COMPLETIONS_API - Starting")

        endpoint = 'http://127.0.0.1:5000/v1/completions'

        response = requests.post(
            endpoint,
            json={
                "prompt": test_message,
                "max_tokens": 50
            },
            timeout=30
        )

        if response.status_code == 200:
            result["success"] = True
            result["response_preview"] = str(response.json())[:100]
            log_test(f"Method 18: SUCCESS - got response")
        else:
            result["error"] = f"HTTP {response.status_code}: {response.text[:100]}"

    except requests.exceptions.ConnectionError:
        result["error"] = "Connection refused - OpenAI extension not running"
    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 18: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 19: CUSTOM_API
# ============================================================================
def inject_method_19_custom_api(test_message: str) -> dict:
    """
    Method 19: CUSTOM_API
    Custom API endpoint for injection
    """
    result = {"method": "CUSTOM_API", "success": False, "error": None}

    try:
        log_test("Method 19: CUSTOM_API - Starting")

        # Check if boredom_monitor has its own API endpoint
        endpoint = 'http://127.0.0.1:7860/api/v1/internal/boredom_monitor/inject'

        response = requests.post(
            endpoint,
            json={"message": test_message},
            timeout=10
        )

        if response.status_code == 200:
            result["success"] = True
            result["response"] = response.json()
        else:
            result["error"] = f"HTTP {response.status_code}"

    except requests.exceptions.ConnectionError:
        result["error"] = "Custom API endpoint not available"
    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 19: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 20: MORPHDOM_UPDATE (JavaScript)
# ============================================================================
def inject_method_20_morphdom_update(test_message: str) -> dict:
    """
    Method 20: MORPHDOM_UPDATE
    Requires JavaScript execution (cannot test from Python)
    """
    result = {"method": "MORPHDOM_UPDATE", "success": False, "error": None}

    try:
        log_test("Method 20: MORPHDOM_UPDATE - Starting")

        # This requires browser-side JavaScript
        result["error"] = "REQUIRES_BROWSER - Cannot execute from Python"
        result["note"] = "This method requires JavaScript in browser context"
        result["js_code"] = f"handleMorphdomUpdate('{test_message}')"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 20: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 21: DIRECT_DOM (JavaScript)
# ============================================================================
def inject_method_21_direct_dom(test_message: str) -> dict:
    """
    Method 21: DIRECT_DOM
    Direct DOM manipulation (requires browser)
    """
    result = {"method": "DIRECT_DOM", "success": False, "error": None}

    try:
        log_test("Method 21: DIRECT_DOM - Starting")

        # This requires browser-side JavaScript
        result["error"] = "REQUIRES_BROWSER - Cannot execute from Python"
        result["note"] = "This method requires JavaScript in browser context"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 21: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 22: MESSAGE_EDIT
# ============================================================================
def inject_method_22_message_edit(test_message: str) -> dict:
    """
    Method 22: MESSAGE_EDIT
    Uses submitMessageEdit pattern (requires browser)
    """
    result = {"method": "MESSAGE_EDIT", "success": False, "error": None}

    try:
        log_test("Method 22: MESSAGE_EDIT - Starting")

        # Message edit requires browser interaction
        result["error"] = "REQUIRES_BROWSER - submitMessageEdit needs browser context"
        result["note"] = "This method edits existing messages via browser"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 22: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 23: GRADIO_COMPONENTS
# ============================================================================
def inject_method_23_gradio_components(test_message: str) -> dict:
    """
    Method 23: GRADIO_COMPONENTS
    Direct Gradio component state update
    """
    result = {"method": "GRADIO_COMPONENTS", "success": False, "error": None}

    try:
        log_test("Method 23: GRADIO_COMPONENTS - Starting")

        # The 'display' component value is a dict (containing 'html' key), not a string
        # The correct approach is to modify the history component, which controls the chat
        if not hasattr(shared, 'gradio') or 'history' not in shared.gradio:
            result["error"] = "shared.gradio['history'] not available"
            log_test(f"Method 23: FAILED - {result['error']}", "ERROR")
            return result

        history_component = shared.gradio['history']
        if not history_component or not hasattr(history_component, 'value'):
            result["error"] = "history component has no .value attribute"
            log_test(f"Method 23: FAILED - {result['error']}", "ERROR")
            return result

        history = history_component.value
        if history is None:
            history = {'internal': [], 'visible': [], 'metadata': {}}

        # Add the test message as an assistant message
        history['internal'].append(['', test_message])
        history['visible'].append(['', test_message])

        # Update the history component value
        history_component.value = history

        result["success"] = True
        result["history_count"] = len(history['internal'])
        log_test(f"Method 23: SUCCESS - Updated history component, count: {result['history_count']}")

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 23: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 24: INPUT_HIJACK
# ============================================================================
def inject_method_24_input_hijack(test_message: str) -> dict:
    """
    Method 24: INPUT_HIJACK
    Uses boredom_monitor's input_hijack pattern
    """
    result = {"method": "INPUT_HIJACK", "success": False, "error": None}

    try:
        log_test("Method 24: INPUT_HIJACK - Starting")

        from . import script as boredom_script

        if hasattr(boredom_script, 'input_hijack'):
            boredom_script.input_hijack['state'] = True
            boredom_script.input_hijack['value'] = ["", test_message]
            result["success"] = True
            result["hijack_state"] = boredom_script.input_hijack
            log_test("Method 24: Input hijack set")
        else:
            result["error"] = "input_hijack not found in script"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 24: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 25: INJECTION_BRIDGE
# ============================================================================
def inject_method_25_injection_bridge(test_message: str) -> dict:
    """
    Method 25: INJECTION_BRIDGE
    Uses gradio_injection_bridge queue
    """
    result = {"method": "INJECTION_BRIDGE", "success": False, "error": None}

    try:
        log_test("Method 25: INJECTION_BRIDGE - Starting")

        from . import gradio_injection_bridge as bridge

        if hasattr(bridge, 'queue_injection'):
            bridge.queue_injection(test_message)
            result["success"] = True
            result["queue_status"] = bridge.get_queue_status() if hasattr(bridge, 'get_queue_status') else "unknown"
            log_test("Method 25: Queued via injection bridge")
        else:
            result["error"] = "queue_injection not found in bridge"

    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 25: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# INJECTION METHOD 26: APSCHEDULER
# ============================================================================
def inject_method_26_apscheduler(test_message: str) -> dict:
    """
    Method 26: APSCHEDULER
    Background scheduler injection
    """
    result = {"method": "APSCHEDULER", "success": False, "error": None}

    try:
        log_test("Method 26: APSCHEDULER - Starting")

        from apscheduler.schedulers.background import BackgroundScheduler

        # Create a one-time job to inject
        scheduler = BackgroundScheduler()

        def do_injection():
            try:
                # NOTE: shared.gradio['history'] is a Gradio State component, use .value
                if hasattr(shared, 'gradio') and 'history' in shared.gradio:
                    history_component = shared.gradio['history']
                    history = history_component.value if hasattr(history_component, 'value') else history_component
                    if history:
                        history['internal'].append(['', test_message])
                        history['visible'].append(['', test_message])
            except Exception as e:
                log_test(f"APScheduler injection failed: {e}", "ERROR")

        # Schedule for immediate execution
        scheduler.add_job(do_injection, 'date')
        scheduler.start()

        # Wait briefly for job to execute
        time.sleep(0.5)
        scheduler.shutdown()

        result["success"] = True
        result["note"] = "Scheduled and executed"
        log_test("Method 26: APScheduler job completed")

    except ImportError:
        result["error"] = "apscheduler not installed"
    except Exception as e:
        result["error"] = str(e)
        log_test(f"Method 26: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# ALL INJECTION METHODS - Dictionary for test runner
# ============================================================================
ALL_INJECTION_METHODS = {
    1: ("CHARACTER_GREETING", inject_method_1_character_greeting),
    2: ("HISTORY_MODIFIER", inject_method_2_history_modifier),
    3: ("STATE_MODIFIER", inject_method_3_state_modifier),
    4: ("CHAT_INPUT_MODIFIER", inject_method_4_chat_input_modifier),
    5: ("INPUT_MODIFIER", inject_method_5_input_modifier),
    6: ("BOT_PREFIX_MODIFIER", inject_method_6_bot_prefix_modifier),
    7: ("OUTPUT_MODIFIER", inject_method_7_output_modifier),
    8: ("CUSTOM_GENERATE_PROMPT", inject_method_8_custom_generate_prompt),
    9: ("CUSTOM_GENERATE_REPLY", inject_method_9_custom_generate_reply),
    10: ("LOGITS_PROCESSOR", inject_method_10_logits_processor),
    11: ("TOKENIZER_MODIFIER", inject_method_11_tokenizer_modifier),
    12: ("SEND_DUMMY_MESSAGE", inject_method_12_send_dummy_message),
    13: ("SEND_DUMMY_REPLY", inject_method_13_send_dummy_reply),
    14: ("REDRAW_HTML", inject_method_14_redraw_html),
    15: ("DIRECT_HISTORY", inject_method_15_direct_history),
    16: ("GENERATE_WRAPPER", inject_method_16_generate_wrapper),
    17: ("OPENAI_CHAT_API", inject_method_17_openai_chat_api),
    18: ("OPENAI_COMPLETIONS_API", inject_method_18_openai_completions_api),
    19: ("CUSTOM_API", inject_method_19_custom_api),
    20: ("MORPHDOM_UPDATE", inject_method_20_morphdom_update),
    21: ("DIRECT_DOM", inject_method_21_direct_dom),
    22: ("MESSAGE_EDIT", inject_method_22_message_edit),
    23: ("GRADIO_COMPONENTS", inject_method_23_gradio_components),
    24: ("INPUT_HIJACK", inject_method_24_input_hijack),
    25: ("INJECTION_BRIDGE", inject_method_25_injection_bridge),
    26: ("APSCHEDULER", inject_method_26_apscheduler),
}


def run_injection_method(method_num: int, test_message: str) -> dict:
    """Run a single injection method by number"""
    if method_num not in ALL_INJECTION_METHODS:
        return {"method": f"UNKNOWN_{method_num}", "success": False, "error": "Invalid method number"}

    name, func = ALL_INJECTION_METHODS[method_num]
    return func(test_message)


def run_all_injections(test_message: str) -> dict:
    """Run all 26 injection methods and return results"""
    results = {}
    for num, (name, func) in ALL_INJECTION_METHODS.items():
        log_test(f"Running injection method {num}: {name}")
        results[num] = func(test_message)
        time.sleep(0.1)  # Brief pause between methods
    return results
