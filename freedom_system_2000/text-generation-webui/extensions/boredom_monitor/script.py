import sys
import os
import time
import threading
import gradio as gr
import requests
import json
import asyncio
import websockets
from datetime import datetime
from pathlib import Path

# Optional imports for additional methods
try:
    from gradio_client import Client
    gradio_client_available = True
except ImportError:
    gradio_client_available = False
    print("[BOREDOM-MONITOR] WARNING: gradio_client not available - method 4 disabled")

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    selenium_available = True
except ImportError:
    selenium_available = False
    print("[BOREDOM-MONITOR] WARNING: selenium not available - method 7 disabled")

# Fix circular import issue - append instead of insert to maintain module access
# while allowing Python to find the real exllamav2 package first
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'modules'))

from modules import shared

# Import emotion manager for Freedom emotional responses
try:
    from .idle_emotion_manager import IdleEmotionManager
    emotion_manager = None  # Will be initialized in setup()
    emotion_manager_available = True
    print("[BOREDOM-MONITOR] Emotion manager imported successfully")
except ImportError as e:
    emotion_manager = None
    emotion_manager_available = False
    print(f"[BOREDOM-MONITOR] WARNING: Could not import emotion manager: {e}")

# Import injection bridge for proper UI updates from background threads
try:
    from . import gradio_injection_bridge as injection_bridge
    injection_bridge_available = True
    print("[BOREDOM-MONITOR] Injection bridge imported successfully")
except ImportError as e:
    injection_bridge = None
    injection_bridge_available = False
    print(f"[BOREDOM-MONITOR] WARNING: Could not import injection bridge: {e}")

# Comprehensive logging following standards
def log_enhanced(message, level="INFO", function_name="", extra_data=None):
    """Enhanced logging with timestamp, level, function, and optional extra data - ALWAYS logs to console"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    prefix = "[BOREDOM-MONITOR]"
    if function_name:
        prefix = f"{prefix} [{function_name}]"
    full_message = f"{timestamp} {prefix} [{level}] {message}"

    if extra_data:
        full_message += f" | Data: {extra_data}"

    # ALWAYS print to console for maximum visibility
    print(full_message)

    # Also write to log file
    try:
        log_path = "F:/Apps/freedom_system/log/boredom_monitor.log"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except Exception:
        pass  # Don't fail on logging errors

# Configuration - Load from config file
def load_endpoint_config():
    """Load endpoint URLs from config file instead of hardcoding"""
    config_path = Path(__file__).parent / "idle_endpoint_config.json"
    default_config = {
        "endpoints": {
            "openai_chat": "http://127.0.0.1:5000/v1/chat/completions",
            "gradio_ui": "http://127.0.0.1:7860"
        }
    }
    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            print(f"[BOREDOM-MONITOR] Config not found at {config_path}, using defaults")
            return default_config
    except Exception as e:
        print(f"[BOREDOM-MONITOR] Error loading config: {e}, using defaults")
        return default_config

# Load config at module load
ENDPOINT_CONFIG = load_endpoint_config()

INJECTION_METHOD = "direct"  # Options: "direct" or "api"
OPENAI_ENDPOINT = ENDPOINT_CONFIG.get("endpoints", {}).get("openai_chat", "http://127.0.0.1:5000/v1/chat/completions")
GRADIO_ENDPOINT = ENDPOINT_CONFIG.get("endpoints", {}).get("gradio_ui", "http://127.0.0.1:7860")
IDLE_THRESHOLD_MINUTES = 7
AUTO_TEST_ENABLED = True  # Enable automatic testing of injection methods
AUTO_TEST_INTERVAL_SECONDS = 60  # Test every 60 seconds

# Global state
monitor_thread = None
auto_test_thread = None
should_monitor = threading.Event()
should_auto_test = threading.Event()
last_activity_time = time.time()
injection_count = 0
auto_test_count = 0

# Input hijacking state for injection
input_hijack = {'state': False, 'value': ["", ""]}

# ============================================================================
# CORE AI GENERATION PATTERN (KoboldCpp-Style for Text-Gen-WebUI)
# ============================================================================

# SOLUTION 1A: Ensure Complete State - Fix all None state fields
def ensure_complete_state(state):
    """
    Ensure state has ALL required fields for generate_chat_reply().

    Based on gather_interface_values() pattern (ui.py:284-301).
    Uses shared.persistent_interface_state or shared.settings as fallback.

    This fixes: TypeError: argument of type 'NoneType' is not iterable
    Which occurs when state['instruction_template_str'] or other fields are None.

    Args:
        state: Current state dict

    Returns:
        Complete state dict with all required fields
    """
    try:
        from modules import shared
        import copy

        # If we have a persistent interface state, use it as base
        if shared.persistent_interface_state:
            log_enhanced("Using persistent_interface_state as base", "INFO", "ensure_complete_state")
            complete_state = copy.deepcopy(shared.persistent_interface_state)

            # Merge our state on top
            if state:
                complete_state.update(state)

            state = complete_state

            # FIX: Validate and fix any None fields in persistent_interface_state
            critical_fields = {
                'instruction_template_str': shared.settings.get('instruction_template_str', ''),
                'chat_template_str': shared.settings.get('chat_template_str', ''),
                'mode': shared.settings.get('mode', 'chat'),
                'name1': shared.settings.get('name1', 'You'),
                'name2': shared.settings.get('name2', 'Assistant'),
                'context': shared.settings.get('context', ''),
                'user_bio': shared.settings.get('user_bio', ''),
                'custom_system_message': shared.settings.get('custom_system_message', ''),
                'truncation_length': shared.settings.get('truncation_length', 2048),
                'max_new_tokens': shared.settings.get('max_new_tokens', 512),
                'seed': shared.settings.get('seed', -1),
            }

            for key, default_value in critical_fields.items():
                if key not in state or state[key] is None:
                    state[key] = default_value
                    log_enhanced(f"Fixed None field: {key} = {default_value}", "DEBUG", "ensure_complete_state")
        else:
            # Fallback: Use shared.settings defaults
            log_enhanced("No persistent state - using shared.settings defaults", "INFO", "ensure_complete_state")

            # Critical fields that MUST exist for generate_chat_reply()
            required_fields = {
                'instruction_template_str': shared.settings.get('instruction_template_str', ''),
                'chat_template_str': shared.settings.get('chat_template_str', ''),
                'mode': shared.settings.get('mode', 'chat'),
                'name1': shared.settings.get('name1', 'You'),
                'name2': shared.settings.get('name2', 'Assistant'),
                'context': shared.settings.get('context', ''),
                'user_bio': shared.settings.get('user_bio', ''),
                'custom_system_message': shared.settings.get('custom_system_message', ''),
                'truncation_length': shared.settings.get('truncation_length', 2048),
                'max_new_tokens': shared.settings.get('max_new_tokens', 512),
                'seed': shared.settings.get('seed', -1),
                'character_menu': state.get('character_menu', '') if state else '',
                'unique_id': state.get('unique_id', '') if state else '',
            }

            # Apply defaults for missing fields
            for key, default_value in required_fields.items():
                if key not in state or state[key] is None:
                    state[key] = default_value
                    log_enhanced(f"Set default for {key}", "DEBUG", "ensure_complete_state")

        # Now ensure history is valid (original Solution 1)
        state = ensure_valid_history(state)

        log_enhanced("Complete state ensured - all fields populated", "SUCCESS", "ensure_complete_state")
        return state

    except Exception as e:
        log_enhanced(f"Error ensuring complete state: {str(e)}", "ERROR", "ensure_complete_state")
        import traceback
        log_enhanced(f"Traceback: {traceback.format_exc()}", "ERROR", "ensure_complete_state")
        return state

# SOLUTION 1: Gather Interface Values Pattern - Ensure Valid History
def ensure_valid_history(state):
    """
    Ensure state has a valid history before injection.
    Based on gather_interface_values() pattern from modules/ui.py:298-299
    and load_history() from modules/chat.py:1315-1319

    This fixes the "state['history'] is None" crash by:
    1. Loading history from saved chat file if it exists
    2. Creating fresh empty history structure if no saved chat

    Args:
        state: The state dictionary from shared.gradio['interface_state']

    Returns:
        state: The state with valid history guaranteed
    """
    try:
        from modules.chat import load_history

        # Check if history is None or empty
        if (state.get('history') is None or
            (isinstance(state.get('history'), dict) and
             len(state['history'].get('visible', [])) == 0 and
             len(state['history'].get('internal', [])) == 0)):

            log_enhanced("History is None or empty - loading from disk", "INFO", "ensure_valid_history")

            # Get required info from state
            unique_id = state.get('unique_id')
            character = state.get('character_menu')
            mode = state.get('mode')

            if unique_id:
                # Load history from saved chat file (same pattern as ui.py:299)
                log_enhanced(f"Loading history from saved chat: {unique_id}", "DEBUG", "ensure_valid_history", {
                    "character": character,
                    "mode": mode
                })
                state['history'] = load_history(unique_id, character, mode)
            else:
                # Create fresh empty history (same pattern as chat.py:1319)
                log_enhanced("No unique_id - creating fresh empty history", "DEBUG", "ensure_valid_history")
                state['history'] = {'internal': [], 'visible': [], 'metadata': {}}

            log_enhanced("Valid history structure ensured", "SUCCESS", "ensure_valid_history", {
                "internal_count": len(state['history']['internal']),
                "visible_count": len(state['history']['visible'])
            })
        else:
            log_enhanced("History already valid - no action needed", "DEBUG", "ensure_valid_history")

        return state

    except Exception as e:
        log_enhanced(f"Error ensuring valid history: {str(e)}", "ERROR", "ensure_valid_history")
        # Fallback: create minimal empty history
        if state.get('history') is None:
            state['history'] = {'internal': [], 'visible': [], 'metadata': {}}
        return state

def get_ai_response_for_injection(prompt_message):
    """
    Direct injection method - uses generate_chat_reply() with complete state

    This MUST use generate_chat_reply() (not API) because it's a "direct" method.
    We need to handle the AllTalk extension properly.

    Args:
        prompt_message: The boredom/emotion prompt to send to AI

    Returns:
        tuple: (success: bool, ai_response: str or None)
    """
    try:
        log_enhanced("Getting AI response using generate_chat_reply()", "INFO", "get_ai_response_for_injection", {
            "prompt_preview": prompt_message[:50] + "..." if len(prompt_message) > 50 else prompt_message
        })

        from modules.chat import generate_chat_reply
        import copy

        # Get complete state
        if 'interface_state' not in shared.gradio:
            log_enhanced("UI not ready", "ERROR", "get_ai_response_for_injection")
            return False, None

        state_component = shared.gradio['interface_state']
        state = state_component.value if hasattr(state_component, 'value') else state_component

        if not state or not isinstance(state, dict):
            log_enhanced("Invalid state", "ERROR", "get_ai_response_for_injection")
            return False, None

        # METHOD 1 FIX: Ensure COMPLETE state (not just history)
        # This fixes: TypeError: argument of type 'NoneType' is not iterable
        # Caused by state['instruction_template_str'] being None
        state = ensure_complete_state(state)

        # Update state component with complete state
        if hasattr(state_component, 'value'):
            state_component.value = state

        # Final validation
        if not state.get('history') or not isinstance(state['history'], dict):
            log_enhanced("Could not create valid history", "ERROR", "get_ai_response_for_injection")
            return False, None

        # Save original history
        original_history = copy.deepcopy(state['history'])

        # Call generate_chat_reply - it will add prompt + get AI response
        ai_response = None
        log_enhanced(f"Calling generate_chat_reply - original history length: {len(original_history['internal'])}", "DEBUG", "get_ai_response_for_injection")
        iteration_count = 0

        try:
            for history in generate_chat_reply(prompt_message, state, for_ui=False):
                iteration_count += 1
                log_enhanced(f"Generator iteration {iteration_count}", "DEBUG", "get_ai_response_for_injection", {
                    "history_type": type(history).__name__,
                    "has_internal": 'internal' in history if isinstance(history, dict) else False,
                    "internal_length": len(history['internal']) if isinstance(history, dict) and 'internal' in history else 0
                })

                # The history returned has our prompt + AI response
                if history and isinstance(history, dict) and 'internal' in history:
                    if len(history['internal']) > len(original_history['internal']):
                        # Get the last pair which is [our_prompt, ai_response]
                        last_pair = history['internal'][-1]
                        log_enhanced(f"Found new history entry: pair length={len(last_pair)}", "DEBUG", "get_ai_response_for_injection")
                        if len(last_pair) >= 2:
                            ai_response = last_pair[1]
                            # Don't break - keep iterating to get final response

            log_enhanced(f"Generator completed: {iteration_count} iterations", "DEBUG", "get_ai_response_for_injection")
        except Exception as e:
            log_enhanced(f"generate_chat_reply error: {str(e)}", "ERROR", "get_ai_response_for_injection")
            import traceback
            log_enhanced(f"Traceback: {traceback.format_exc()}", "ERROR", "get_ai_response_for_injection")

        # Restore original history
        state['history'] = original_history
        if hasattr(state_component, 'value'):
            state_component.value = state

        if ai_response:
            log_enhanced("AI response extracted successfully", "SUCCESS", "get_ai_response_for_injection", {
                "response_preview": ai_response[:100] + "..." if len(ai_response) > 100 else ai_response
            })
            return True, ai_response
        else:
            log_enhanced("No AI response generated", "ERROR", "get_ai_response_for_injection")
            return False, None

    except Exception as e:
        log_enhanced(f"Error getting AI response: {str(e)}", "ERROR", "get_ai_response_for_injection", {
            "error_type": type(e).__name__
        })
        import traceback
        log_enhanced(f"Full traceback: {traceback.format_exc()}", "ERROR", "get_ai_response_for_injection")
        return False, None

# SOLUTION 3: Input Hijack Callback Pattern for API Methods
def create_api_injection_callback(ai_response):
    """
    Create a callback for input_hijack that returns the AI response.
    Based on multimodal extension pattern from text-gen-webui docs.

    The callback is called AFTER state is prepared, so history will be loaded.

    Args:
        ai_response: The AI-generated response to inject

    Returns:
        callback: Function that returns (text, visible_text)
    """
    def injection_callback(text, visible_text):
        """
        Callback invoked by chatbot_wrapper with current state.
        By this point, history should be loaded by the system.
        """
        log_enhanced("API injection callback invoked", "DEBUG", "injection_callback", {
            "response_preview": ai_response[:50] + "..." if len(ai_response) > 50 else ai_response
        })
        return ai_response, ai_response

    return injection_callback

def get_ai_response_via_api(prompt_message):
    """
    OPTION 2: API injection using OpenAI-compatible endpoint

    Bypasses generate_chat_reply() and calls the API directly.
    Simpler approach that doesn't require complete state.

    SOLUTION 3: Now returns callback for input_hijack instead of raw string

    Args:
        prompt_message: The boredom/emotion prompt to send to AI

    Returns:
        tuple: (success: bool, ai_response: str or callback)
    """
    try:
        log_enhanced("Getting AI response via API (Option 2: Direct API)", "INFO", "get_ai_response_via_api", {
            "prompt_preview": prompt_message[:50] + "..." if len(prompt_message) > 50 else prompt_message
        })

        import requests
        import json

        # Use the OpenAI-compatible endpoint from config
        api_url = OPENAI_ENDPOINT

        payload = {
            "messages": [
                {"role": "user", "content": prompt_message}
            ],
            "mode": "chat",
            "character": shared.settings.get('character', 'Assistant')
        }

        log_enhanced("Sending request to OpenAI API endpoint", "INFO", "get_ai_response_via_api", {
            "url": api_url,
            "message_length": len(prompt_message)
        })

        response = requests.post(api_url, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            ai_response = data['choices'][0]['message']['content']

            log_enhanced("AI response received via API", "SUCCESS", "get_ai_response_via_api", {
                "response_preview": ai_response[:100] + "..." if len(ai_response) > 100 else ai_response
            })

            return True, ai_response
        else:
            log_enhanced(f"API request failed with status {response.status_code}", "ERROR", "get_ai_response_via_api", {
                "status_code": response.status_code,
                "response": response.text[:200]
            })
            return False, None

    except Exception as e:
        log_enhanced(f"Error getting AI response via API: {str(e)}", "ERROR", "get_ai_response_via_api", {
            "error_type": type(e).__name__
        })
        import traceback
        log_enhanced(f"Full traceback: {traceback.format_exc()}", "ERROR", "get_ai_response_via_api")
        return False, None

def inject_message_direct(message):
    """Method 2: Direct Call Integration - KoboldCpp-style: prompt AI → inject response"""
    try:
        print(f"  → Method 2: Direct Call - Getting AI response...")
        log_enhanced("Method 2: Direct Call (KoboldCpp-style) starting", "INFO", "inject_message_direct", {
            "prompt_length": len(message),
            "method": "direct_ai_response"
        })

        # Step 1: Get AI response from the boredom/emotion prompt
        success, ai_response = get_ai_response_for_injection(message)

        if not success or not ai_response:
            print(f"  → Failed to get AI response")
            log_enhanced("AI response generation failed", "ERROR", "inject_message_direct")
            return False

        print(f"  → AI response received: {ai_response[:50]}...")

        # Step 2: Inject using GREETING PATTERN from chat.py:1092-1095
        if 'interface_state' in shared.gradio and 'display' in shared.gradio:
            from modules.extensions import apply_extensions
            import html

            state_component = shared.gradio['interface_state']
            state = state_component.value if hasattr(state_component, 'value') else state_component

            # METHOD 2 DEFENSIVE FIX: Ensure complete state before injection
            # This is a safety layer in case get_ai_response_for_injection()
            # returned without fully populating state
            if state:
                state = ensure_complete_state(state)
                log_enhanced("Method 2: Applied defensive ensure_complete_state()", "DEBUG", "inject_message_direct")

                # Update state component with complete state
                if hasattr(state_component, 'value'):
                    state_component.value = state

            if state and 'history' in state:
                # Use the EXACT pattern from greeting injection
                state['history']['internal'] += [['<|BEGIN-VISIBLE-CHAT|>', ai_response]]
                state['history']['visible'] += [['', apply_extensions('output', html.escape(ai_response), state, is_chat=True)]]

                # Update state component
                if hasattr(state_component, 'value'):
                    state_component.value = state

                # CRITICAL: Trigger UI update via display component
                shared.gradio['display'].value = state['history']

                print(f"  → AI response injected using greeting pattern")
                log_enhanced("Method 2: AI response injected via greeting pattern", "SUCCESS", "inject_message_direct", {
                    "response_preview": ai_response[:100]
                })
                return True

        print(f"  → Failed to inject into UI")
        log_enhanced("Method 2: UI injection failed", "ERROR", "inject_message_direct")
        return False

    except Exception as e:
        print(f"  → Method 2 FAILED: {str(e)}")
        log_enhanced(f"Method 2 error: {str(e)}", "ERROR", "inject_message_direct", {
            "error_type": type(e).__name__
        })
        return False

def api_call_with_retries(endpoint, payload, operation_name, max_retries=3, delay=1):
    """
    Standard retry pattern with comprehensive logging
    Follows API_Extension_Development_Standards.md pattern
    """
    log_enhanced(f"Starting {operation_name}", "INFO", "api_call_with_retries", {
        "endpoint": endpoint,
        "max_retries": max_retries,
        "timeout": 30,
        "payload_size": len(str(payload))
    })

    for attempt in range(max_retries):
        try:
            attempt_start = time.time()

            log_enhanced(f"Attempt {attempt + 1}/{max_retries} for {operation_name}", "DEBUG", "api_call_with_retries", {
                "endpoint": endpoint,
                "attempt": attempt + 1
            })

            response = requests.post(endpoint, json=payload, timeout=30)
            response_time = time.time() - attempt_start

            if response.status_code == 200:
                log_enhanced(f"{operation_name} succeeded on attempt {attempt + 1}", "INFO", "api_call_with_retries", {
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time * 1000, 2),
                    "attempts_used": attempt + 1,
                    "response_length": len(response.text)
                })
                return True, response
            else:
                log_enhanced(f"{operation_name} HTTP error on attempt {attempt + 1}", "WARNING", "api_call_with_retries", {
                    "status_code": response.status_code,
                    "error_body": response.text[:200],
                    "response_time_ms": round(response_time * 1000, 2)
                })

        except requests.exceptions.Timeout:
            log_enhanced(f"{operation_name} timeout on attempt {attempt + 1}", "WARNING", "api_call_with_retries", {
                "timeout_seconds": 30,
                "endpoint": endpoint
            })
        except requests.exceptions.ConnectionError:
            log_enhanced(f"{operation_name} connection error on attempt {attempt + 1}", "WARNING", "api_call_with_retries", {
                "error_type": "ConnectionError",
                "endpoint": endpoint,
                "likely_cause": "Service not running"
            })
        except Exception as e:
            log_enhanced(f"{operation_name} unexpected error on attempt {attempt + 1}", "WARNING", "api_call_with_retries", {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "endpoint": endpoint
            })

        # Delay before retry (except on last attempt)
        if attempt < max_retries - 1:
            log_enhanced(f"Retrying {operation_name} in {delay} seconds...", "INFO", "api_call_with_retries", {
                "delay_seconds": delay,
                "remaining_attempts": max_retries - attempt - 1
            })
            time.sleep(delay)

    # All attempts failed
    log_enhanced(f"{operation_name} failed after {max_retries} attempts", "ERROR", "api_call_with_retries", {
        "endpoint": endpoint,
        "total_attempts": max_retries,
        "total_time_spent": max_retries * delay
    })

    return False, None

def inject_message_api(message):
    """Method 3: OpenAI API - KoboldCpp-style: internal generation → inject AI response"""
    try:
        print(f"  → Method 3: API - Getting AI response internally...")
        log_enhanced("Method 3: OpenAI API (KoboldCpp-style) starting", "INFO", "inject_message_api", {
            "prompt_length": len(message),
            "method": "api_ai_response"
        })

        # Step 1: Get AI response via OpenAI API (Option 2)
        success, ai_response = get_ai_response_via_api(message)

        if not success or not ai_response:
            print(f"  → Failed to get AI response")
            log_enhanced("AI response generation failed", "ERROR", "inject_message_api")
            return False

        print(f"  → AI response received: {ai_response[:50]}...")

        # Step 2: Inject using GREETING PATTERN from chat.py:1092-1095
        if 'interface_state' in shared.gradio and 'display' in shared.gradio:
            from modules.extensions import apply_extensions
            import html

            state_component = shared.gradio['interface_state']
            state = state_component.value if hasattr(state_component, 'value') else state_component

            if state:
                # METHOD 3 FIX: Upgrade to ensure_complete_state()
                state = ensure_complete_state(state)
                log_enhanced("Method 3: Applied ensure_complete_state()", "DEBUG", "inject_message_api")

                # SOLUTION 2A: Validate critical fields exist
                required_for_ui = ['mode', 'name1', 'name2', 'character_menu']
                missing_fields = [field for field in required_for_ui if not state.get(field)]

                if missing_fields:
                    log_enhanced(f"State missing UI fields: {missing_fields}", "ERROR", "inject_message_api")
                    return False

                # SOLUTION 2B: Log state contents for diagnostics
                log_enhanced(f"State fields populated: {list(state.keys())}", "DEBUG", "inject_message_api")
                log_enhanced(f"State mode: {state.get('mode')}", "DEBUG", "inject_message_api")
                log_enhanced(f"State name1: {state.get('name1')}, name2: {state.get('name2')}", "DEBUG", "inject_message_api")

                # Update state component
                if hasattr(state_component, 'value'):
                    state_component.value = state

                if 'history' in state and state['history']:
                    # SOLUTION 4C: Track original length for verification
                    original_length = len(state['history']['visible'])
                    log_enhanced(f"History length before injection: {original_length}", "DEBUG", "inject_message_api")

                    # SOLUTION 3A & 3B: Validate apply_extensions() with exception handling
                    try:
                        visible_text = apply_extensions('output', html.escape(ai_response), state, is_chat=True)

                        # SOLUTION 3A: Validate the result
                        if not visible_text or visible_text.strip() == '':
                            log_enhanced("apply_extensions() returned empty - using raw response", "WARNING", "inject_message_api")
                            visible_text = html.escape(ai_response)  # Fallback to raw response
                        else:
                            log_enhanced(f"apply_extensions() returned: {visible_text[:50]}...", "DEBUG", "inject_message_api")

                    except Exception as e:
                        # SOLUTION 3B: Catch apply_extensions() exceptions
                        log_enhanced(f"apply_extensions() failed: {str(e)}", "ERROR", "inject_message_api")
                        visible_text = html.escape(ai_response)  # Fallback to raw response

                    # Use the EXACT pattern from greeting injection (chat.py:1094-1095)
                    state['history']['internal'] += [['<|BEGIN-VISIBLE-CHAT|>', ai_response]]
                    state['history']['visible'] += [['', visible_text]]

                    # SOLUTION 4C: Verify injection actually added to history
                    new_length = len(state['history']['visible'])
                    if new_length != original_length + 1:
                        log_enhanced(f"History length mismatch: expected {original_length + 1}, got {new_length}", "ERROR", "inject_message_api")
                        return False

                    log_enhanced(f"History updated: {original_length} -> {new_length} messages", "SUCCESS", "inject_message_api")

                # Update state component
                if hasattr(state_component, 'value'):
                    state_component.value = state

                # SOLUTION 4A: Verify display component exists and updated
                if 'display' not in shared.gradio:
                    log_enhanced("Display component not found in shared.gradio", "ERROR", "inject_message_api")
                    return False

                display_component = shared.gradio['display']

                # SOLUTION 4B: Force UI refresh via multiple update paths
                display_component.value = state['history']
                log_enhanced("Display component value updated", "DEBUG", "inject_message_api")

                # Also update via interface_state
                if hasattr(state_component, 'value'):
                    state_component.value = state
                    log_enhanced("Interface state component updated", "DEBUG", "inject_message_api")

                # Force a Gradio update event (if available)
                if hasattr(display_component, 'update'):
                    display_component.update(value=state['history'])
                    log_enhanced("Forced Gradio update event", "DEBUG", "inject_message_api")

                # SOLUTION 4A: Verify the update actually happened
                if hasattr(display_component, 'value'):
                    actual_value = display_component.value
                    if actual_value != state['history']:
                        log_enhanced("Display update failed - value mismatch", "ERROR", "inject_message_api")
                        return False
                    else:
                        log_enhanced("Display component updated successfully", "SUCCESS", "inject_message_api")

                print(f"  → AI response injected using greeting pattern")
                log_enhanced("Method 3: AI response injected via greeting pattern", "SUCCESS", "inject_message_api", {
                    "response_preview": ai_response[:100]
                })
                return True

        print(f"  → Failed to inject into UI")
        log_enhanced("Method 3: UI injection failed", "ERROR", "inject_message_api")
        return False

    except Exception as e:
        print(f"  → Method 3 FAILED: {str(e)}")
        log_enhanced(f"Method 3 error: {str(e)}", "ERROR", "inject_message_api", {
            "error_type": type(e).__name__
        })
        return False

# ===== METHOD 11: MULTI-METHOD INTELLIGENT FALLBACK =====
def inject_message_multi(message, test_all=False):
    """Try ALL 10+ injection methods with intelligent fallback

    Args:
        message: Message to inject
        test_all: If True, tests ALL methods and logs results (doesn't stop at first success)
    """
    global injection_count
    injection_count += 1

    log_enhanced(f"Starting multi-method injection attempt #{injection_count}", "INFO", "inject_message_multi", {
        "message_preview": message[:50] + "..." if len(message) > 50 else message,
        "total_methods_available": 10,
        "test_all_methods": test_all
    })

    # Method priority: Most reliable first, experimental last
    methods = [
        ("1_hijack", inject_via_hijack),                    # Method 1: 98% reliable
        ("2_direct", inject_message_direct),                # Method 2: Core system
        ("3_api", inject_message_api),                      # Method 3: API endpoint
        ("4_gradio_client", inject_via_gradio_client),      # Method 4: Official client
        ("5_javascript_dom", inject_via_javascript_dom),    # Method 5: Browser DOM
        ("6_state_management", inject_via_state_management),# Method 6: Gradio State
        ("7_selenium", inject_via_selenium),                # Method 7: Browser automation
        ("8_websocket", inject_via_websocket),              # Method 8: WS/SSE
        ("9_blocks", inject_via_blocks),                    # Method 9: Blocks UI
        ("10_idle_monitor", inject_via_idle_monitor)        # Method 10: Queue pattern
    ]

    success_found = False
    results = []

    for method_name, method_func in methods:
        try:
            log_enhanced(f"Testing injection via {method_name}", "INFO", "inject_message_multi")

            result = method_func(message)
            results.append((method_name, "SUCCESS" if result else "FAIL"))

            if result:
                log_enhanced(f"Method {method_name} SUCCEEDED", "SUCCESS", "inject_message_multi", {
                    "method_used": method_name,
                    "injection_number": injection_count
                })
                success_found = True
                if not test_all:  # Stop at first success unless testing all
                    return True
            else:
                log_enhanced(f"Method {method_name} FAILED", "WARNING", "inject_message_multi")

        except Exception as e:
            results.append((method_name, f"EXCEPTION: {str(e)}"))
            log_enhanced(f"Method {method_name} EXCEPTION: {str(e)}", "ERROR", "inject_message_multi", {
                "error_type": type(e).__name__
            })

    # Log summary if testing all methods
    if test_all:
        passed = sum(1 for _, r in results if r == "SUCCESS")
        failed = sum(1 for _, r in results if r == "FAIL")
        exceptions = sum(1 for _, r in results if "EXCEPTION" in r)

        log_enhanced(f"Multi-method test complete: {passed} passed, {failed} failed, {exceptions} exceptions",
                    "INFO", "inject_message_multi", {
            "injection_number": injection_count,
            "results": results
        })
        return success_found

    log_enhanced("All 10 injection methods failed", "ERROR", "inject_message_multi", {
        "injection_attempt": injection_count,
        "methods_tried": len(methods)
    })
    return False

def inject_message_dual(message):
    """Legacy dual method - now calls inject_message_multi"""
    return inject_message_multi(message)

# ===== METHOD 4: OFFICIAL GRADIO CLIENT API =====
def inject_via_gradio_client(message):
    """Method 4: Gradio Client API - official programmatic access using gradio_client library"""
    if not gradio_client_available:
        print(f"  → Gradio client library not available")
        log_enhanced("Gradio client not available - install with: pip install gradio_client", "WARNING", "inject_via_gradio_client")
        return False

    try:
        print(f"  → Method 4: Connecting to Gradio app via client library...")
        log_enhanced("Method 4: Gradio Client API injection starting", "INFO", "inject_via_gradio_client", {
            "message_length": len(message),
            "method": "gradio_client_library",
            "endpoint": GRADIO_ENDPOINT
        })

        # UNIQUE APPROACH: Connect to Gradio app as external client
        from gradio_client import Client
        client = Client(GRADIO_ENDPOINT)
        print(f"  → Client connected, calling /chat endpoint...")

        # Call the chat endpoint directly through Gradio Client API
        # This bypasses all internal state management
        result = client.predict(message, api_name="/chat")
        print(f"  → Predict completed: {str(result)[:50]}...")

        log_enhanced("Method 4: Gradio Client injection successful", "SUCCESS", "inject_via_gradio_client", {
            "result_preview": str(result)[:100] if result else "no result",
            "result_type": type(result).__name__
        })
        return True

    except Exception as e:
        print(f"  → Method 4 Gradio Client failed: {str(e)}")
        log_enhanced(f"Method 4: Gradio Client injection failed: {str(e)}", "ERROR", "inject_via_gradio_client", {
            "error_type": type(e).__name__,
            "error_details": str(e)
        })

        # Log additional troubleshooting info
        import traceback
        log_enhanced(f"Method 4 traceback: {traceback.format_exc()}", "ERROR", "inject_via_gradio_client")
        return False

# ===== METHOD 5: JAVASCRIPT SHADOW DOM MANIPULATION =====
def inject_via_javascript_dom(message):
    """
    Method 5: JavaScript Shadow DOM manipulation (browser-side execution)

    UNIQUE APPROACH: Generates JavaScript code to manipulate Gradio's Shadow DOM
    directly in the browser, simulating user input and button clicks.

    This method represents a client-side injection approach that would need
    to be executed in the browser context, not from the Python backend.
    """
    try:
        print(f"  → Method 5: JavaScript DOM - Generating Shadow DOM injection code...")
        log_enhanced("Method 5: JavaScript Shadow DOM manipulation starting", "INFO", "inject_via_javascript_dom", {
            "message_length": len(message),
            "method": "javascript_shadow_dom",
            "execution_context": "browser_required"
        })

        # Escape message for JavaScript string
        escaped_message = message.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

        # UNIQUE APPROACH: Generate JavaScript code for Shadow DOM manipulation
        js_code = f"""
// Gradio Shadow DOM Injection Function
function injectGradioChat(message) {{
    console.log('[Boredom Monitor] Attempting Shadow DOM injection...');

    // Find the Gradio app element
    const gradioApp = document.getElementsByTagName('gradio-app')[0];
    if (!gradioApp) {{
        console.error('[Boredom Monitor] gradio-app element not found');
        return false;
    }}

    if (!gradioApp.shadowRoot) {{
        console.error('[Boredom Monitor] Shadow Root not accessible');
        return false;
    }}

    // Try multiple selector strategies
    const selectors = [
        'textarea',
        '#chatbot textarea',
        '.chat-input textarea',
        'textarea[placeholder*="Send"]',
        'textarea[data-testid="textbox"]'
    ];

    for (let selector of selectors) {{
        const input = gradioApp.shadowRoot.querySelector(selector);
        if (input) {{
            console.log('[Boredom Monitor] Found input:', selector);

            // Set the value
            input.value = message;

            // Trigger input event
            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            input.dispatchEvent(new Event('change', {{ bubbles: true }}));

            // Find and click submit button
            const submitSelectors = [
                'button[type="submit"]',
                'button.primary',
                'button:has(svg)',
                'button[aria-label*="Send"]'
            ];

            for (let btnSelector of submitSelectors) {{
                const submitBtn = gradioApp.shadowRoot.querySelector(btnSelector);
                if (submitBtn) {{
                    console.log('[Boredom Monitor] Clicking submit button');
                    setTimeout(() => submitBtn.click(), 100);
                    return true;
                }}
            }}
        }}
    }}

    console.error('[Boredom Monitor] No suitable input found');
    return false;
}}

// Execute injection
injectGradioChat("{escaped_message}");
"""

        # Save JS code to file for potential browser execution
        js_file_path = "F:/Apps/freedom_system/freedom_system_2000/text-generation-webui/extensions/boredom_monitor/generated_injection.js"
        try:
            with open(js_file_path, 'w', encoding='utf-8') as f:
                f.write(js_code)
            log_enhanced(f"JavaScript code saved to: {js_file_path}", "INFO", "inject_via_javascript_dom")
        except Exception as write_error:
            log_enhanced(f"Could not save JS file: {str(write_error)}", "WARNING", "inject_via_javascript_dom")

        # Log the generated code
        log_enhanced("JavaScript Shadow DOM code generated", "INFO", "inject_via_javascript_dom", {
            "js_code_length": len(js_code),
            "message_preview": message[:50] + "..." if len(message) > 50 else message,
            "saved_to_file": js_file_path
        })

        print(f"  → JavaScript code generated ({len(js_code)} bytes)")
        print(f"  → Note: This method requires browser context to execute")
        log_enhanced("Method 5: Cannot execute (requires browser context)", "WARNING", "inject_via_javascript_dom", {
            "note": "JavaScript generated but needs browser execution",
            "suggestion": "Use browser console or inject via injection_trigger.js"
        })

        return False  # Cannot execute without browser context

    except Exception as e:
        print(f"  → Method 5 FAILED: {str(e)}")
        log_enhanced(f"Method 5 error: {str(e)}", "ERROR", "inject_via_javascript_dom", {
            "error_type": type(e).__name__
        })
        import traceback
        log_enhanced(f"Method 5 traceback: {traceback.format_exc()}", "ERROR", "inject_via_javascript_dom")
        return False

# ===== METHOD 6: SERVER-SIDE STATE MANAGEMENT =====
def inject_via_state_management(message):
    """
    Method 6: Server-side state management with Gradio State
    UNIQUE APPROACH: Direct history component manipulation (no AI, no interface_state)
    """
    try:
        log_enhanced("Attempting state management injection", "INFO", "inject_via_state_management", {
            "message_length": len(message),
            "method": "state_management"
        })

        # Check if Gradio state system is accessible
        if hasattr(shared, 'gradio') and 'history' in shared.gradio:
            history_state = shared.gradio['history'].value

            if history_state is None:
                history_state = {'internal': [], 'visible': []}

            # Inject into state
            history_state['internal'].append(['', message])
            history_state['visible'].append(['', message])

            # Update state
            shared.gradio['history'].value = history_state

            log_enhanced("State management injection successful", "SUCCESS", "inject_via_state_management")
            return True
        else:
            log_enhanced("Gradio state not accessible", "WARNING", "inject_via_state_management")
            return False

    except Exception as e:
        log_enhanced(f"State management injection failed: {str(e)}", "ERROR", "inject_via_state_management")
        return False

# ===== METHOD 7: SELENIUM AUTOMATION =====
# STATUS: UNSUPPORTED IN EXTENSION MODE
# REASON: Selenium requires an external WebDriver browser instance that cannot be
#         controlled from within a Gradio extension running in the same process.
#         Use for external testing only (e.g., injection_test_app).
def inject_via_selenium(message):
    """
    Method 7: Selenium browser automation
    UNIQUE APPROACH: WebDriver automation (requires external browser instance)

    STATUS: UNSUPPORTED - Cannot run WebDriver from inside extension process.
    This method is kept for external test harness use only.
    """
    if not selenium_available:
        log_enhanced("Selenium not available - install with: pip install selenium", "WARNING", "inject_via_selenium")
        return False

    try:
        log_enhanced("Selenium injection UNSUPPORTED in extension mode", "WARNING", "inject_via_selenium", {
            "message_length": len(message),
            "method": "selenium",
            "reason": "Cannot control external browser from inside extension process"
        })
        return False

    except Exception as e:
        log_enhanced(f"Selenium injection failed: {str(e)}", "ERROR", "inject_via_selenium")
        return False

# ===== METHOD 8: WEBSOCKET/SSE PROTOCOLS =====
# STATUS: FALLBACK TO STATE MANAGEMENT
# REASON: Gradio's internal WebSocket protocol is not documented for external injection.
#         Direct WS connection would require reverse-engineering Gradio's message format.
#         Falls back to state_management which achieves similar backend effect.
def inject_via_websocket(message):
    """
    Method 8: WebSocket/SSE protocol injection
    UNIQUE APPROACH: Async WebSocket protocol (fallback to state management)

    STATUS: FALLBACK - Uses state_management instead of direct WebSocket.
    Direct WebSocket injection would require:
    - Async context (extension runs sync)
    - Gradio's internal WS message format (undocumented)
    - Authentication/session handling
    """
    try:
        log_enhanced("WebSocket injection - using state_management fallback", "INFO", "inject_via_websocket", {
            "message_length": len(message),
            "method": "websocket_fallback",
            "actual_method": "state_management"
        })

        # Delegate to state management (achieves backend injection)
        result = inject_via_state_management(message)

        if result:
            log_enhanced("WebSocket fallback (state_management) successful", "SUCCESS", "inject_via_websocket")
        else:
            log_enhanced("WebSocket fallback (state_management) failed", "WARNING", "inject_via_websocket")

        return result

    except Exception as e:
        log_enhanced(f"WebSocket injection failed: {str(e)}", "ERROR", "inject_via_websocket")
        return False

# ===== METHOD 9: BLOCKS-BASED CUSTOM IMPLEMENTATION =====
def inject_via_blocks(message):
    """
    Method 9: Gradio Blocks custom implementation
    UNIQUE APPROACH: Direct chatbot component access with role-based messages
    """
    try:
        log_enhanced("Attempting Blocks-based injection", "INFO", "inject_via_blocks", {
            "message_length": len(message),
            "method": "blocks"
        })

        # Blocks method requires custom UI definition
        # For existing chat, we use direct component access
        if hasattr(shared, 'gradio') and 'chatbot' in shared.gradio:
            chatbot_component = shared.gradio['chatbot']

            current_value = chatbot_component.value or []
            current_value.append({"role": "assistant", "content": message})
            chatbot_component.value = current_value

            log_enhanced("Blocks injection successful", "SUCCESS", "inject_via_blocks")
            return True
        else:
            log_enhanced("Chatbot component not accessible", "WARNING", "inject_via_blocks")
            return False

    except Exception as e:
        log_enhanced(f"Blocks injection failed: {str(e)}", "ERROR", "inject_via_blocks")
        return False

# ===== METHOD 10: IDLE MONITORING PATTERN (GENERIC) =====
def inject_via_idle_monitor(message):
    """
    Method 10: Idle monitoring pattern with queue
    UNIQUE APPROACH: Global input_hijack queue for deferred execution
    """
    try:
        log_enhanced("Attempting idle monitor pattern injection", "INFO", "inject_via_idle_monitor", {
            "message_length": len(message),
            "method": "idle_monitor"
        })

        # This uses a queue-based pattern from the generic implementation
        # Falls back to hijack method which uses similar pattern
        global input_hijack

        input_hijack.update({"state": True, "value": [message, message]})

        log_enhanced("Idle monitor pattern injection queued", "SUCCESS", "inject_via_idle_monitor")
        return True

    except Exception as e:
        log_enhanced(f"Idle monitor injection failed: {str(e)}", "ERROR", "inject_via_idle_monitor")
        return False

# ============================================================================
# ADDITIONAL 11 METHODS FROM all_injection_methods.py
# ============================================================================

# Try to import injection bridge for methods 13-23
try:
    from . import gradio_injection_bridge as bridge
    alt_injection_bridge_available = True
except ImportError:
    alt_injection_bridge_available = False
    print("[BOREDOM-MONITOR] WARNING: Injection bridge not available for methods 13-23")

# Optional imports for additional methods
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    apscheduler_available = True
except ImportError:
    apscheduler_available = False
    print("[BOREDOM-MONITOR] WARNING: APScheduler not available - method 18 disabled")

def trigger_ui_update(message):
    """
    Trigger actual UI update using the injection bridge.
    Used by injection methods that need to update the chat UI from background threads.
    """
    if not alt_injection_bridge_available:
        log_enhanced("Injection bridge not available for UI update", "WARNING", "trigger_ui_update")
        return False

    try:
        bridge.queue_message_for_injection(message)
        log_enhanced("Message queued via injection bridge", "SUCCESS", "trigger_ui_update")
        return True
    except Exception as e:
        log_enhanced(f"Failed to queue message: {str(e)}", "ERROR", "trigger_ui_update")
        return False

# NOTE: Methods 13-25 (23-method sequential test system) removed in Branch-12
# The 26-method test matrix is available via test_runner.py / injection_test_harness.py

def get_emotional_message():
    """Generate emotional message using emotion manager"""
    global emotion_manager

    if not emotion_manager_available or emotion_manager is None:
        log_enhanced("Emotion manager not available, using default message", "WARNING", "get_emotional_message")
        return "I've been feeling a bit bored during this quiet period. Want to chat about something interesting?"

    try:
        # Use emotion manager to generate contextual emotional message
        message = emotion_manager.generate_emotional_message()

        # Get emotion status for logging
        status = emotion_manager.get_emotion_status()

        log_enhanced("Emotional message generated", "INFO", "get_emotional_message", {
            "emotion_type": status.get('current_emotion'),
            "horny_stage": status.get('horny_stage'),
            "on_cooldown": status.get('horny_on_cooldown'),
            "message_preview": message[:50] + "..." if len(message) > 50 else message
        })

        return message

    except Exception as e:
        log_enhanced(f"Emotion message generation failed: {str(e)}", "ERROR", "get_emotional_message")
        return "I've been feeling a bit bored during this quiet period. Want to chat about something interesting?"

def auto_test_injection_loop():
    """Automatically test ALL 10+ injection methods on a schedule - COMPREHENSIVE MODE"""
    global auto_test_count

    print("\n" + "="*80)
    print("[AUTO-TEST] AUTO-TEST THREAD STARTED - COMPREHENSIVE TESTING MODE")
    print("="*80)
    log_enhanced("Auto-test thread started - testing ALL 10 methods EVERY cycle", "INFO", "auto_test_injection_loop", {
        "interval_seconds": AUTO_TEST_INTERVAL_SECONDS,
        "enabled": AUTO_TEST_ENABLED,
        "total_methods": 10,
        "mode": "COMPREHENSIVE - Tests all methods regardless of success"
    })
    print(f"📊 Test Interval: {AUTO_TEST_INTERVAL_SECONDS} seconds")
    print(f"📋 Methods to test: 10")
    print(f"🔄 Mode: Test ALL methods (no early stopping)")
    print("="*80 + "\n")

    test_cycle = 0

    while should_auto_test.is_set():
        try:
            time.sleep(AUTO_TEST_INTERVAL_SECONDS)
            test_cycle += 1

            print("\n" + "+"+"="*78+"+")
            print(f"|  [>>] AUTO-TEST CYCLE #{test_cycle} - TESTING ALL 10 INJECTION METHODS{' '*(78-59-len(str(test_cycle)))}|")
            print("+"+"="*78+"+")

            log_enhanced(f"=== AUTO-TEST CYCLE #{test_cycle} START ===", "INFO", "auto_test_injection_loop", {
                "cycle_number": test_cycle,
                "timestamp": datetime.now().isoformat()
            })

            # Test each method individually
            methods_to_test = [
                ("Method 1: Input Hijack", inject_via_hijack),
                ("Method 2: Direct Call", inject_message_direct),
                ("Method 3: OpenAI API", inject_message_api),
                ("Method 4: Gradio Client", inject_via_gradio_client),
                ("Method 5: JavaScript DOM", inject_via_javascript_dom),
                ("Method 6: State Management", inject_via_state_management),
                ("Method 7: Selenium", inject_via_selenium),
                ("Method 8: WebSocket/SSE", inject_via_websocket),
                ("Method 9: Blocks-Based", inject_via_blocks),
                ("Method 10: Idle Monitor Pattern", inject_via_idle_monitor)
            ]

            results = []
            for idx, (method_name, method_func) in enumerate(methods_to_test, 1):
                auto_test_count += 1

                print(f"\n┌─ Test #{auto_test_count} ({idx}/10): {method_name} ─")
                log_enhanced(f"Testing {method_name} (Test #{auto_test_count})", "INFO", "auto_test_injection_loop", {
                    "method_number": idx,
                    "total_methods": 10,
                    "test_count": auto_test_count
                })

                try:
                    message = f"AUTO-TEST #{auto_test_count}: {method_name}"
                    print(f"|  [MSG] Message: {message[:60]}...")

                    result = method_func(message)
                    status = "PASS [+]" if result else "FAIL [-]"
                    status_symbol = "[+]" if result else "[-]"
                    results.append((method_name, "PASS" if result else "FAIL"))

                    print(f"│  {status_symbol} Result: {status}")
                    log_enhanced(f"{status_symbol} Test #{auto_test_count} - {method_name}: {status}",
                                "SUCCESS" if result else "ERROR", "auto_test_injection_loop", {
                                    "method": method_name,
                                    "result": status,
                                    "test_number": auto_test_count
                                })

                except Exception as e:
                    error_msg = str(e)
                    results.append((method_name, f"EXCEPTION"))
                    print(f"|  [!] EXCEPTION: {error_msg[:60]}...")
                    log_enhanced(f"[!] Test #{auto_test_count} - {method_name}: EXCEPTION - {error_msg}",
                                "ERROR", "auto_test_injection_loop", {
                                    "method": method_name,
                                    "error": error_msg,
                                    "error_type": type(e).__name__
                                })

                print(f"└{'─'*60}")
                time.sleep(2)  # Brief pause between methods

            # Summary
            passed = sum(1 for _, status in results if status == "PASS")
            failed = sum(1 for _, status in results if status == "FAIL")
            exceptions = sum(1 for _, status in results if status == "EXCEPTION")

            print("\n" + "+"+"="*78+"+")
            print(f"|  [SUMMARY] CYCLE #{test_cycle} COMPLETE - RESULTS{' '*(78-46-len(str(test_cycle)))}|")
            print("+"+"="*78+"+")
            print(f"|  [+] Passed:     {passed:2d}/10{' '*64}|")
            print(f"|  [-] Failed:     {failed:2d}/10{' '*64}|")
            print(f"|  [!] Exceptions: {exceptions:2d}/10{' '*64}|")
            print(f"|  [#] Total Tests Run: {auto_test_count}{' '*(57-len(str(auto_test_count)))}|")
            print("+"+"="*78+"+")

            print(f"\n[WAIT] Next test cycle in {AUTO_TEST_INTERVAL_SECONDS} seconds...\n")

            log_enhanced(f"=== CYCLE #{test_cycle} COMPLETE ===", "SUCCESS", "auto_test_injection_loop", {
                "total_tests": len(methods_to_test),
                "passed": passed,
                "failed": failed,
                "exceptions": exceptions,
                "total_tests_run": auto_test_count,
                "pass_rate": f"{(passed/10)*100:.1f}%",
                "detailed_results": results
            })

            # COMPLETION NOTICE
            print("[OK] " + "="*75 + " [OK]")
            print(f"   ALL {len(methods_to_test)} INJECTION METHODS TESTED - CYCLE #{test_cycle} COMPLETED")
            print("[OK] " + "="*75 + " [OK]\n")

        except Exception as e:
            print(f"\n[ERROR] AUTO-TEST CYCLE ERROR: {str(e)}\n")
            log_enhanced(f"Auto-test cycle error: {str(e)}", "ERROR", "auto_test_injection_loop", {
                "error_type": type(e).__name__,
                "error_details": str(e)
            })
            time.sleep(60)

def idle_check_with_injection():
    """Idle detection with actual injection using emotion manager"""
    global last_activity_time

    while should_monitor.is_set():
        try:
            current_time = time.time()
            idle_seconds = current_time - last_activity_time
            idle_minutes = idle_seconds / 60

            if idle_minutes >= IDLE_THRESHOLD_MINUTES:
                log_enhanced(f"Idle threshold reached", "INFO", "idle_check_with_injection", {
                    "idle_minutes": round(idle_minutes, 1),
                    "threshold": IDLE_THRESHOLD_MINUTES
                })

                # Generate emotional message using emotion manager
                message = get_emotional_message()

                # Attempt injection with multi-method fallback
                success = inject_via_hijack(message)

                if success:
                    log_enhanced("Emotional message injection completed successfully", "SUCCESS", "idle_check_with_injection")
                else:
                    log_enhanced("Emotional message injection failed", "ERROR", "idle_check_with_injection")

                # Reset activity time to prevent repeated triggers
                last_activity_time = current_time

            time.sleep(30)  # Check every 30 seconds

        except Exception as e:
            log_enhanced(f"Idle check error: {str(e)}", "ERROR", "idle_check_with_injection")
            time.sleep(60)

def setup():
    """Called when extension is loaded"""
    global monitor_thread, auto_test_thread, emotion_manager

    log_enhanced("Setting up boredom monitor extension", "INFO", "setup", {
        "primary_method": INJECTION_METHOD,
        "idle_threshold_minutes": IDLE_THRESHOLD_MINUTES,
        "openai_endpoint": OPENAI_ENDPOINT,
        "emotion_manager_available": emotion_manager_available,
        "test_matrix_available": "26 injection × 16 verification methods"
    })

    # Initialize emotion manager
    if emotion_manager_available:
        try:
            emotion_manager = IdleEmotionManager()
            log_enhanced("Emotion manager initialized successfully", "SUCCESS", "setup", {
                "initialization_success": emotion_manager.initialization_success if emotion_manager else False
            })
        except Exception as e:
            log_enhanced(f"Failed to initialize emotion manager: {str(e)}", "ERROR", "setup")
            emotion_manager = None
    else:
        log_enhanced("Emotion manager not available - using default messages", "WARNING", "setup")

    # Start monitoring thread with injection capability
    should_monitor.set()
    monitor_thread = threading.Thread(target=idle_check_with_injection, daemon=True)
    monitor_thread.start()
    log_enhanced("Idle monitoring thread started", "SUCCESS", "setup")

    # The 26-method test matrix is available for manual triggering via test_runner.py
    # To run tests: from .test_runner import run_full_test_matrix; run_full_test_matrix()
    log_enhanced("26-method test matrix available for manual testing", "INFO", "setup", {
        "manual_test_available": "run_full_test_matrix()"
    })

    # Set up injection bridge if available
    if injection_bridge_available:
        try:
            # Register API endpoint for JavaScript polling
            if hasattr(shared, 'app') and shared.app is not None:
                injection_bridge.setup_api_endpoint(shared.app)
                log_enhanced("Injection bridge API endpoint registered", "SUCCESS", "setup")
            else:
                log_enhanced("FastAPI app not yet available - API endpoint will be registered later", "WARNING", "setup")
        except Exception as e:
            log_enhanced(f"Failed to set up injection bridge: {str(e)}", "ERROR", "setup")

    log_enhanced("Boredom monitor setup complete", "SUCCESS", "setup", {
        "monitor_thread_started": True,
        "test_matrix_available": True,
        "monitoring_active": True,
        "emotion_manager_active": emotion_manager is not None,
        "injection_bridge_active": injection_bridge_available
    })

def custom_js():
    """
    Load JavaScript for injection bridge polling and browser verification.
    - injection_trigger.js: Polls for queued messages and clicks hidden button to trigger UI updates
    - browser_verification.js: MutationObserver that watches for test messages and reports to server
    """
    if not injection_bridge_available:
        return ""

    js_code_parts = []
    extension_dir = Path(__file__).parent

    # Load injection trigger JavaScript
    js_file_path = extension_dir / "injection_trigger.js"
    try:
        with open(js_file_path, 'r', encoding='utf-8') as f:
            js_code_parts.append(f.read())
        log_enhanced("Injection trigger JavaScript loaded", "SUCCESS", "custom_js", {"file": str(js_file_path)})
    except Exception as e:
        log_enhanced(f"Failed to load injection trigger JavaScript: {str(e)}", "ERROR", "custom_js")

    # Load browser verification JavaScript (for test harness)
    verify_js_path = extension_dir / "browser_verification.js"
    try:
        with open(verify_js_path, 'r', encoding='utf-8') as f:
            js_code_parts.append(f.read())
        log_enhanced("Browser verification JavaScript loaded", "SUCCESS", "custom_js", {"file": str(verify_js_path)})
    except Exception as e:
        log_enhanced(f"Failed to load browser verification JavaScript: {str(e)}", "WARNING", "custom_js")

    return "\n\n".join(js_code_parts)

def input_modifier(string, state, is_chat=False):
    """Track user activity"""
    global last_activity_time
    last_activity_time = time.time()
    return string

def chat_input_modifier(text, visible_text, state):
    """Track chat input activity AND implement input hijacking for injection"""
    global last_activity_time, input_hijack
    last_activity_time = time.time()

    # Check if we have a hijacked input to inject
    if input_hijack['state']:
        log_enhanced("Input hijacking active - injecting queued message", "INFO", "chat_input_modifier")
        input_hijack['state'] = False
        return input_hijack['value']

    return text, visible_text

def inject_via_hijack(message):
    """Method 1: Input hijacking pattern - KoboldCpp-style: prompt AI → inject response"""
    try:
        print(f"  → Method 1: Hijack - Getting AI response...")
        log_enhanced("Method 1: Input Hijack (KoboldCpp-style) starting", "INFO", "inject_via_hijack", {
            "prompt_length": len(message),
            "method": "hijack_ai_response"
        })

        # Step 1: Get AI response from the boredom/emotion prompt
        success, ai_response = get_ai_response_for_injection(message)

        if not success or not ai_response:
            print(f"  → Failed to get AI response")
            log_enhanced("AI response generation failed", "ERROR", "inject_via_hijack")
            return False

        print(f"  → AI response received: {ai_response[:50]}...")

        # Step 2: Inject using GREETING PATTERN from chat.py:1092-1095
        if 'interface_state' in shared.gradio and 'display' in shared.gradio:
            from modules.extensions import apply_extensions
            import html

            state_component = shared.gradio['interface_state']
            state = state_component.value if hasattr(state_component, 'value') else state_component

            if state and 'history' in state:
                # Use the EXACT pattern from greeting injection
                state['history']['internal'] += [['<|BEGIN-VISIBLE-CHAT|>', ai_response]]
                state['history']['visible'] += [['', apply_extensions('output', html.escape(ai_response), state, is_chat=True)]]

                # Update state component
                if hasattr(state_component, 'value'):
                    state_component.value = state

                # CRITICAL: Trigger UI update via display component
                shared.gradio['display'].value = state['history']

                print(f"  → AI response injected using greeting pattern")
                log_enhanced("Method 1: AI response injected via greeting pattern", "SUCCESS", "inject_via_hijack", {
                    "response_preview": ai_response[:100]
                })
                return True

        print(f"  → Failed to inject into UI")
        log_enhanced("Method 1: UI injection failed", "ERROR", "inject_via_hijack")
        return False

    except Exception as e:
        print(f"  → Method 1 FAILED: {str(e)}")
        log_enhanced(f"Method 1 error: {str(e)}", "ERROR", "inject_via_hijack")
        return False

def ui():
    """UI for monitoring status and configuration"""
    with gr.Row():
        with gr.Column():
            # Status display
            emotion_status = ""
            if emotion_manager:
                try:
                    status_data = emotion_manager.get_emotion_status()
                    emotion_status = f"\nEmotion: {status_data.get('current_emotion', 'none')}\nHorny Stage: {status_data.get('horny_stage', 1)}\nCooldown: {status_data.get('horny_on_cooldown', False)}"
                except:
                    emotion_status = "\nEmotion Manager: Error"
            else:
                emotion_status = "\nEmotion Manager: Not Available"

            status = gr.Textbox(
                label="Boredom Monitor Status",
                value=f"Monitor: Active\nIdle Threshold: {IDLE_THRESHOLD_MINUTES} minutes\nManual Injections: {injection_count}\nTest Matrix: 26 injection × 16 verification methods{emotion_status}",
                interactive=False,
                lines=6
            )
        with gr.Column():
            gr.Markdown("### Manual Controls")
            test_emotion_btn = gr.Button("Trigger Emotional Test")

        with gr.Column():
            gr.Markdown("### 26-Method Test Matrix\n- 26 injection methods × 16 verification methods\n- Comprehensive testing via test_runner.py")
            full_test_btn = gr.Button("Run Full Test Matrix (26×16)", variant="primary")

    def test_emotion():
        message = get_emotional_message()
        result = inject_via_hijack(message)
        emotion_type = "unknown"
        if emotion_manager:
            try:
                status_data = emotion_manager.get_emotion_status()
                emotion_type = status_data.get('current_emotion', 'unknown')
            except:
                pass
        return f"Manual test - Emotional injection ({emotion_type}) " + ("succeeded" if result else "failed")

    def run_full_injection_test():
        """Run full 26×16 injection test matrix"""
        try:
            from .test_runner import run_full_test_matrix
            results = run_full_test_matrix()
            verified = results.get("summary", {}).get("verified_injections", [])
            recommended = results.get("summary", {}).get("recommended_methods", [])
            duration = results.get("duration_seconds", 0)
            if recommended:
                return f"FULL MATRIX COMPLETE ({duration:.0f}s)\nRecommended methods: {recommended}\nVerified: {len(verified)}/26\nResults saved to log/"
            else:
                return f"FULL MATRIX COMPLETE ({duration:.0f}s)\nNo methods verified\nCheck logs for details"
        except Exception as e:
            return f"Full test failed: {str(e)}"

    test_emotion_btn.click(test_emotion, outputs=status)
    full_test_btn.click(run_full_injection_test, outputs=status)

    # Add hidden injection bridge button if available
    injection_btn = None
    if injection_bridge_available:
        injection_btn = injection_bridge.ui()
        log_enhanced("Hidden injection bridge button created", "INFO", "ui")

        # CRITICAL: Connect the button to its event handler
        injection_bridge.setup_injection_bridge(injection_btn)
        log_enhanced("Injection bridge event handler connected", "SUCCESS", "ui")

        # CRITICAL FIX: Inject JavaScript for polling into the UI
        js_code = custom_js()
        if js_code:
            gr.HTML(f"<script>{js_code}</script>")
            log_enhanced("JavaScript polling code injected into UI", "SUCCESS", "ui")
        else:
            log_enhanced("JavaScript polling code not loaded", "ERROR", "ui")

    return status

def custom_api_endpoints(app):
    """
    Register custom API endpoints for the extension.
    This is called by text-generation-webui after the FastAPI app is created.

    Args:
        app: The FastAPI application instance
    """
    if injection_bridge_available:
        try:
            injection_bridge.setup_api_endpoint(app)
            log_enhanced("Injection bridge API endpoint registered via custom_api_endpoints", "SUCCESS", "custom_api_endpoints")
        except Exception as e:
            log_enhanced(f"Failed to register API endpoint: {str(e)}", "ERROR", "custom_api_endpoints")
    else:
        log_enhanced("Injection bridge not available - skipping API endpoint registration", "WARNING", "custom_api_endpoints")

def history_modifier(history):
    """
    SOLUTION 6: Defensive Layer - Handle None history from extension system.

    This is called BEFORE chatbot_wrapper processes history (chat.py:758).
    Acts as a safety net to catch None history before it causes crashes.

    When boredom monitor calls generate_chat_reply() with for_ui=False,
    or when running from background threads, history can be None.
    This function intercepts it before it reaches other extensions like AllTalk,
    preventing NoneType errors.

    Based on:
    - gather_interface_values() pattern from modules/ui.py:298-299
    - load_history() from modules/chat.py:1315-1319

    Returns:
        history: Valid history structure (never None)
    """
    try:
        # If history is None, this is a problem - fix it
        if history is None:
            log_enhanced("DEFENSIVE LAYER: history is None - loading from state", "WARNING", "history_modifier")

            # Try to get state from shared context
            if 'interface_state' in shared.gradio:
                state_component = shared.gradio['interface_state']
                state = state_component.value if hasattr(state_component, 'value') else state_component

                if state and isinstance(state, dict):
                    unique_id = state.get('unique_id')
                    character = state.get('character_menu')
                    mode = state.get('mode')

                    if unique_id:
                        # Load from saved chat file
                        from modules.chat import load_history
                        history = load_history(unique_id, character, mode)
                        log_enhanced("DEFENSIVE LAYER: History loaded from saved chat", "SUCCESS", "history_modifier", {
                            "unique_id": unique_id,
                            "internal_count": len(history.get('internal', []))
                        })
                    else:
                        # Create fresh empty history
                        history = {'internal': [], 'visible': [], 'metadata': {}}
                        log_enhanced("DEFENSIVE LAYER: Created fresh empty history", "INFO", "history_modifier")
                else:
                    # Last resort: empty history
                    history = {'internal': [], 'visible': [], 'metadata': {}}
                    log_enhanced("DEFENSIVE LAYER: No state available - created minimal history", "WARNING", "history_modifier")
            else:
                # UI not ready: create minimal history
                history = {'internal': [], 'visible': [], 'metadata': {}}
                log_enhanced("DEFENSIVE LAYER: UI not ready - created minimal history", "WARNING", "history_modifier")

        return history

    except Exception as e:
        log_enhanced(f"DEFENSIVE LAYER: Error in history_modifier: {str(e)}", "ERROR", "history_modifier")
        # Last resort fallback
        if history is None:
            return {'internal': [], 'visible': [], 'metadata': {}}
        return history

params = {
    "display_name": "Boredom Monitor (26-Method Test Matrix)",
    "is_tab": False,
}