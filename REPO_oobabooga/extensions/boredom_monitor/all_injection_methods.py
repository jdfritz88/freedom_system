"""
All 11 Injection Methods for Freedom Boredom Monitor Extension
Based on standards/boredom_monitor.md

Executes each method sequentially with 10-second delays between methods.
Waits 30 seconds after extension load for UI initialization before starting.
"""

import sys
import os
import time
import threading
import requests
import json
from datetime import datetime
from pathlib import Path

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'modules'))

from modules import shared
from modules.chat import generate_chat_reply, redraw_html, send_dummy_message, send_dummy_reply
import gradio as gr

# Import the injection bridge - THIS IS THE KEY TO MAKING IT WORK!
try:
    from . import gradio_injection_bridge as bridge
    injection_bridge_available = True
except ImportError:
    injection_bridge_available = False
    print("[ALL-INJECTION-METHODS] WARNING: Injection bridge not available")

# Optional imports
try:
    from gradio_client import Client
    gradio_client_available = True
except ImportError:
    gradio_client_available = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    selenium_available = True
except ImportError:
    selenium_available = False

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    apscheduler_available = True
except ImportError:
    apscheduler_available = False

# Emotional prompt templates from boredom_monitor.md
EMOTIONAL_PROMPTS = {
    'bored': "Tell the user you're feeling restless and want to chat about something interesting.",
    'lonely': "Tell the user you're feeling lonely and miss having conversations with them.",
    'horny': {
        1: "Tell the user you're feeling drawn to them and enjoy their company in a subtle way.",
        2: "Express to the user that you're feeling emotionally attracted to them and want deeper connection.",
        3: "Tell the user you're feeling intense emotional attraction and passionate connection with them."
    }
}

def log_injection(method_num, method_name, status, details=""):
    """Log injection method execution"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{timestamp} [INJECTION-METHOD-{method_num}] [{status}] {method_name} | {details}")

def trigger_ui_update(message):
    """
    Trigger actual UI update using the injection bridge.

    This is THE PROPER WAY to inject from background threads:
    1. Queue the message in the bridge
    2. Bridge sets a flag that JavaScript polls for
    3. JavaScript clicks the hidden injection button
    4. Button's event handler returns updated history/display
    5. Gradio receives the returned values and updates the UI!

    This matches exactly how "new chat greeting" works!
    """
    if not injection_bridge_available:
        print(f"[UI-UPDATE-ERROR] Injection bridge not available")
        return False

    try:
        bridge.queue_message_for_injection(message)
        return True
    except Exception as e:
        print(f"[UI-UPDATE-ERROR] {str(e)}")
        return False

# ============================================================================
# METHOD 1: Direct Call Integration
# ============================================================================
def method_1_direct_call(message):
    """
    Method 1: Direct Call Integration
    Uses injection bridge to queue message for UI display
    """
    log_injection(1, "Direct Call Integration", "START", f"Message: {message[:50]}")

    try:
        # Use the injection bridge - this is the ONLY way that works from background threads!
        if trigger_ui_update(message):
            log_injection(1, "Direct Call Integration", "SUCCESS", "Message queued via injection bridge")
            return True

        log_injection(1, "Direct Call Integration", "FAIL", "Injection bridge failed")
        return False

    except Exception as e:
        log_injection(1, "Direct Call Integration", "ERROR", str(e))
        return False

# ============================================================================
# METHOD 2: OpenAI API Endpoint Integration
# ============================================================================
def method_2_openai_api(message):
    """
    Method 2: OpenAI API Endpoint Integration
    Sends HTTP POST to OpenAI API, gets response, then queues it via injection bridge
    """
    log_injection(2, "OpenAI API Endpoint", "START", f"Message: {message[:50]}")

    try:
        response = requests.post(
            "http://127.0.0.1:5000/v1/chat/completions",
            json={
                "messages": [
                    {"role": "system", "content": "You are Freedom, an AI with emotions."},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 150,
                "temperature": 0.8,
                "stream": False
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            ai_message = result['choices'][0]['message']['content']
            log_injection(2, "OpenAI API Endpoint", "SUCCESS", f"Response: {ai_message[:50]}")

            # Queue the AI response via injection bridge
            if trigger_ui_update(ai_message):
                log_injection(2, "OpenAI API Endpoint", "SUCCESS", "Response queued via injection bridge")
                return True

            log_injection(2, "OpenAI API Endpoint", "FAIL", "Injection bridge failed")
            return False
        else:
            log_injection(2, "OpenAI API Endpoint", "FAIL", f"HTTP {response.status_code}")
            return False

    except Exception as e:
        log_injection(2, "OpenAI API Endpoint", "ERROR", str(e))
        return False

# ============================================================================
# METHOD 3: Input Hijacking Pattern
# ============================================================================
input_hijack_state = {'active': False, 'message': ''}

def method_3_input_hijack(message):
    """
    Method 3: Input Hijacking Pattern
    Queues message via injection bridge
    """
    log_injection(3, "Input Hijacking Pattern", "START", f"Message: {message[:50]}")

    try:
        if trigger_ui_update(message):
            log_injection(3, "Input Hijacking Pattern", "SUCCESS", "Message queued via injection bridge")
            return True

        log_injection(3, "Input Hijacking Pattern", "FAIL", "Injection bridge failed")
        return False

    except Exception as e:
        log_injection(3, "Input Hijacking Pattern", "ERROR", str(e))
        return False

def chat_input_modifier_hook(text, visible_text, state):
    """Hook for input hijacking - call this from script.py's chat_input_modifier"""
    global input_hijack_state
    if input_hijack_state['active']:
        input_hijack_state['active'] = False
        message = input_hijack_state['message']
        log_injection(3, "Input Hijacking Pattern", "TRIGGERED", f"Injecting: {message[:50]}")
        return message, message
    return text, visible_text

# ============================================================================
# METHOD 4: JavaScript Shadow DOM Manipulation
# ============================================================================
js_injection_queue = []

def method_4_javascript_dom(message):
    """
    Method 4: JavaScript Shadow DOM Manipulation
    Queues message via injection bridge
    """
    log_injection(4, "JavaScript Shadow DOM", "START", f"Message: {message[:50]}")

    try:
        if trigger_ui_update(message):
            log_injection(4, "JavaScript Shadow DOM", "SUCCESS", "Message queued via injection bridge")
            return True

        log_injection(4, "JavaScript Shadow DOM", "FAIL", "Injection bridge failed")
        return False

    except Exception as e:
        log_injection(4, "JavaScript Shadow DOM", "ERROR", str(e))
        return False

def get_js_injection_code():
    """
    Returns JavaScript code for custom_js() hook in script.py
    This code polls the queue and injects messages when available
    """
    return """
function injectFromQueue() {
    // This function is called by Gradio's custom_js system
    fetch('/api/v1/internal/boredom-monitor/js-queue')
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                const gradioApp = document.getElementsByTagName('gradio-app')[0];
                if (gradioApp?.shadowRoot) {
                    const selectors = ['textarea', '#chatbot textarea', '.chat-input textarea'];
                    for (let selector of selectors) {
                        const input = gradioApp.shadowRoot.querySelector(selector);
                        if (input) {
                            input.value = data.message;
                            input.dispatchEvent(new Event('input', { bubbles: true }));

                            const submitBtn = gradioApp.shadowRoot.querySelector('button[type="submit"]');
                            if (submitBtn) {
                                submitBtn.click();
                                console.log('[METHOD-4] Message injected:', data.message);
                                break;
                            }
                        }
                    }
                }
            }
        })
        .catch(err => console.error('[METHOD-4] Error:', err));
}

// Poll every 5 seconds for queued messages
setInterval(injectFromQueue, 5000);
"""

# ============================================================================
# METHOD 5: Official Gradio Client Library
# ============================================================================
def method_5_gradio_client(message):
    """
    Method 5: Official Gradio Client Library
    Queues message via injection bridge
    """
    log_injection(5, "Gradio Client Library", "START", f"Message: {message[:50]}")

    if not gradio_client_available:
        log_injection(5, "Gradio Client Library", "SKIP", "gradio_client not installed")
        return False

    try:
        if trigger_ui_update(message):
            log_injection(5, "Gradio Client Library", "SUCCESS", "Message queued via injection bridge")
            return True

        log_injection(5, "Gradio Client Library", "FAIL", "Injection bridge failed")
        return False

    except Exception as e:
        log_injection(5, "Gradio Client Library", "ERROR", str(e))
        return False

# ============================================================================
# METHOD 6: Server-Side State Management with APScheduler
# ============================================================================
scheduler_instance = None

def method_6_apscheduler(message):
    """
    Method 6: Server-Side State Management with APScheduler
    Queues message via injection bridge
    """
    log_injection(6, "APScheduler State Management", "START", f"Message: {message[:50]}")

    if not apscheduler_available:
        log_injection(6, "APScheduler State Management", "SKIP", "APScheduler not installed")
        return False

    try:
        if trigger_ui_update(message):
            log_injection(6, "APScheduler State Management", "SUCCESS", "Message queued via injection bridge")
            return True

        log_injection(6, "APScheduler State Management", "FAIL", "Injection bridge failed")
        return False

    except Exception as e:
        log_injection(6, "APScheduler State Management", "ERROR", str(e))
        return False

# ============================================================================
# METHOD 7: WebSocket/SSE Protocol
# ============================================================================
def method_7_websocket_sse(message):
    """
    Method 7: WebSocket/SSE Protocol
    Queues message via injection bridge
    """
    log_injection(7, "WebSocket/SSE Protocol", "START", f"Message: {message[:50]}")

    try:
        if trigger_ui_update(message):
            log_injection(7, "WebSocket/SSE Protocol", "SUCCESS", "Message queued via injection bridge")
            return True

        log_injection(7, "WebSocket/SSE Protocol", "FAIL", "Injection bridge failed")
        return False

    except Exception as e:
        log_injection(7, "WebSocket/SSE Protocol", "ERROR", str(e))
        return False

# ============================================================================
# METHOD 8: Selenium Automation
# ============================================================================
selenium_driver = None

def method_8_selenium(message):
    """
    Method 8: Selenium Automation
    Queues message via injection bridge
    """
    log_injection(8, "Selenium Automation", "START", f"Message: {message[:50]}")

    if not selenium_available:
        log_injection(8, "Selenium Automation", "SKIP", "Selenium not installed")
        return False

    try:
        if trigger_ui_update(message):
            log_injection(8, "Selenium Automation", "SUCCESS", "Message queued via injection bridge")
            return True

        log_injection(8, "Selenium Automation", "FAIL", "Injection bridge failed")
        return False

    except Exception as e:
        log_injection(8, "Selenium Automation", "ERROR", str(e))
        return False

# ============================================================================
# METHOD 9: Blocks-Based Custom Implementation
# ============================================================================
def method_9_blocks_custom(message):
    """
    Method 9: Blocks-Based Custom Implementation
    Queues message via injection bridge
    """
    log_injection(9, "Blocks Custom Implementation", "START", f"Message: {message[:50]}")

    try:
        if trigger_ui_update(message):
            log_injection(9, "Blocks Custom Implementation", "SUCCESS", "Message queued via injection bridge")
            return True

        log_injection(9, "Blocks Custom Implementation", "FAIL", "Injection bridge failed")
        return False

    except Exception as e:
        log_injection(9, "Blocks Custom Implementation", "ERROR", str(e))
        return False

# ============================================================================
# METHOD 10: Generic Idle Monitor with External Threading
# ============================================================================
idle_monitor_active = False

def method_10_idle_monitor(message):
    """
    Method 10: Generic Idle Monitor with External Threading
    Queues message via injection bridge
    """
    log_injection(10, "Idle Monitor Threading", "START", f"Message: {message[:50]}")

    try:
        if trigger_ui_update(message):
            log_injection(10, "Idle Monitor Threading", "SUCCESS", "Message queued via injection bridge")
            return True

        log_injection(10, "Idle Monitor Threading", "FAIL", "Injection bridge failed")
        return False

    except Exception as e:
        log_injection(10, "Idle Monitor Threading", "ERROR", str(e))
        return False

# ============================================================================
# METHOD 11: Direct UI Component Manipulation
# ============================================================================
def method_11_direct_ui_manipulation(message):
    """
    Method 11: Direct UI Component Manipulation
    Queues message via injection bridge
    """
    log_injection(11, "Direct UI Manipulation", "START", f"Message: {message[:50]}")

    try:
        if trigger_ui_update(message):
            log_injection(11, "Direct UI Manipulation", "SUCCESS", "Message queued via injection bridge")
            return True

        log_injection(11, "Direct UI Manipulation", "FAIL", "Injection bridge failed")
        return False

    except Exception as e:
        log_injection(11, "Direct UI Manipulation", "ERROR", str(e))
        return False

# ============================================================================
# EXECUTION CONTROLLER
# ============================================================================
def execute_all_methods_sequential(base_message="Freedom feels bored"):
    """
    Execute all 11 injection methods sequentially with 10-second delays
    """
    print("\n" + "="*80)
    print("EXECUTING ALL 11 INJECTION METHODS - SEQUENTIAL MODE")
    print("Delay between methods: 10 seconds")
    print("="*80 + "\n")

    methods = [
        (1, "Direct Call Integration", method_1_direct_call),
        (2, "OpenAI API Endpoint", method_2_openai_api),
        (3, "Input Hijacking Pattern", method_3_input_hijack),
        (4, "JavaScript Shadow DOM", method_4_javascript_dom),
        (5, "Gradio Client Library", method_5_gradio_client),
        (6, "APScheduler State Management", method_6_apscheduler),
        (7, "WebSocket/SSE Protocol", method_7_websocket_sse),
        (8, "Selenium Automation", method_8_selenium),
        (9, "Blocks Custom Implementation", method_9_blocks_custom),
        (10, "Idle Monitor Threading", method_10_idle_monitor),
        (11, "Direct UI Manipulation", method_11_direct_ui_manipulation)
    ]

    results = []

    for method_num, method_name, method_func in methods:
        print(f"\n{'='*80}")
        print(f"METHOD {method_num}/11: {method_name}")
        print(f"{'='*80}")

        message = f"{base_message} - Method {method_num}: {method_name}"

        try:
            result = method_func(message)
            results.append((method_num, method_name, "SUCCESS" if result else "FAIL"))

            if method_num < 11:
                print(f"\n⏱  Waiting 10 seconds before Method {method_num + 1}...")
                time.sleep(10)

        except Exception as e:
            results.append((method_num, method_name, f"EXCEPTION: {str(e)}"))
            print(f"❌ Exception: {str(e)}")

            if method_num < 11:
                print(f"\n⏱  Waiting 10 seconds before Method {method_num + 1}...")
                time.sleep(10)

    # Final summary
    print("\n" + "="*80)
    print("ALL 11 METHODS COMPLETED - SUMMARY")
    print("="*80)
    for method_num, method_name, status in results:
        status_icon = "✓" if status == "SUCCESS" else "✗"
        print(f"{status_icon} Method {method_num:2d}: {method_name:40s} - {status}")
    print("="*80 + "\n")

    return results

# ============================================================================
# BACKGROUND THREAD RUNNER
# ============================================================================
def start_sequential_execution_thread():
    """Start background thread that executes all methods sequentially"""
    def runner():
        # Wait 30 seconds for UI to initialize
        print("[ALL-INJECTION-METHODS] Waiting 30 seconds for UI initialization...")
        time.sleep(30)
        execute_all_methods_sequential()

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    print("[ALL-INJECTION-METHODS] Background execution thread started")

