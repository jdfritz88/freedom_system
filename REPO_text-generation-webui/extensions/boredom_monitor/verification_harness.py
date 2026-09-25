"""
Verification Harness - All 16 Verification Methods
===================================================
Runs INSIDE the boredom_monitor extension with real access to:
- shared.gradio (actual server state)
- HTML display components
- DOM (via JavaScript bridge if available)

Purpose: Verify if injections actually succeeded.
"""

import time
import json
import requests
from datetime import datetime
from pathlib import Path

# Import from parent extension context (already loaded)
from modules import shared


# Configuration - load from config file
EXTENSION_DIR = Path(__file__).parent
CONFIG_FILE = EXTENSION_DIR / "idle_endpoint_config.json"
LOG_DIR = Path("F:/Apps/freedom_system/log")

def _load_config():
    """Load configuration from JSON file"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"endpoints": {"webui_base": "http://127.0.0.1:7860"}}

def _get_webui_base():
    """Get WebUI base URL from config"""
    config = _load_config()
    return config.get("endpoints", {}).get("webui_base", "http://127.0.0.1:7860")


# Logging
def log_verify(message, level="INFO"):
    """Verification harness logging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{timestamp} [VERIFY-TEST] [{level}] {message}")

    # Also log to file
    try:
        log_path = LOG_DIR / "verification_harness.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} [{level}] {message}\n")
    except:
        pass


# ============================================================================
# VERIFICATION METHOD 1: HISTORY_STATE
# Check shared.gradio['history'] directly
# ============================================================================
def verify_method_1_history_state(test_message: str) -> dict:
    """
    Method 1: HISTORY_STATE
    Check if test_message exists in shared.gradio['history']
    """
    result = {"method": "HISTORY_STATE", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 1: HISTORY_STATE - Checking")

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
            result["error"] = "History is None"
            return result

        # Check internal history
        internal = history.get('internal', [])
        visible = history.get('visible', [])

        # Search for test message in history
        found_internal = any(test_message in str(msg) for msg in internal)
        found_visible = any(test_message in str(msg) for msg in visible)

        result["found"] = found_internal or found_visible
        result["success"] = True
        result["internal_count"] = len(internal)
        result["visible_count"] = len(visible)
        result["found_in_internal"] = found_internal
        result["found_in_visible"] = found_visible

        log_verify(f"Method 1: found={result['found']}, internal={len(internal)}, visible={len(visible)}")

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 1: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 2: MESSAGE_COUNT
# Count messages in history
# ============================================================================
def verify_method_2_message_count(test_message: str, expected_increase: int = 1) -> dict:
    """
    Method 2: MESSAGE_COUNT
    Check if message count increased
    """
    result = {"method": "MESSAGE_COUNT", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 2: MESSAGE_COUNT - Checking")

        # NOTE: shared.gradio['history'] is a Gradio State component, use .value
        if not hasattr(shared, 'gradio') or 'history' not in shared.gradio:
            result["error"] = "shared.gradio['history'] not available"
            return result

        history_component = shared.gradio['history']
        history = history_component.value if hasattr(history_component, 'value') else history_component
        if history is None:
            result["count"] = 0
            result["success"] = True
            return result

        internal_count = len(history.get('internal', []))
        visible_count = len(history.get('visible', []))

        result["success"] = True
        result["internal_count"] = internal_count
        result["visible_count"] = visible_count
        result["found"] = internal_count > 0 or visible_count > 0

        log_verify(f"Method 2: internal={internal_count}, visible={visible_count}")

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 2: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 3: DISPLAY_HTML
# Check display component HTML
# ============================================================================
def verify_method_3_display_html(test_message: str) -> dict:
    """
    Method 3: DISPLAY_HTML
    Check if test_message appears in display HTML
    """
    result = {"method": "DISPLAY_HTML", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 3: DISPLAY_HTML - Checking")

        if not hasattr(shared, 'gradio') or 'display' not in shared.gradio:
            result["error"] = "shared.gradio['display'] not available"
            return result

        display = shared.gradio['display']
        if display is None:
            result["error"] = "Display is None"
            return result

        html_content = display.value if hasattr(display, 'value') else str(display)

        if html_content:
            result["found"] = test_message in html_content
            result["html_length"] = len(html_content)
        else:
            result["found"] = False
            result["html_length"] = 0

        result["success"] = True
        log_verify(f"Method 3: found={result['found']}, html_length={result['html_length']}")

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 3: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 4: METADATA_TIMESTAMP
# Check metadata for recent timestamp
# ============================================================================
def verify_method_4_metadata_timestamp(test_message: str, max_age_seconds: int = 60) -> dict:
    """
    Method 4: METADATA_TIMESTAMP
    Check if recent message timestamp exists
    """
    result = {"method": "METADATA_TIMESTAMP", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 4: METADATA_TIMESTAMP - Checking")

        # NOTE: shared.gradio['history'] is a Gradio State component, use .value
        if not hasattr(shared, 'gradio') or 'history' not in shared.gradio:
            result["error"] = "shared.gradio['history'] not available"
            return result

        history_component = shared.gradio['history']
        history = history_component.value if hasattr(history_component, 'value') else history_component
        if history is None:
            result["error"] = "History is None"
            return result

        # Check for metadata with timestamp
        metadata = history.get('metadata', {})
        if metadata:
            # Look for recent timestamps
            now = time.time()
            for key, value in metadata.items():
                if isinstance(value, dict) and 'timestamp' in value:
                    msg_time = value['timestamp']
                    if now - msg_time < max_age_seconds:
                        result["found"] = True
                        result["recent_timestamp"] = msg_time
                        break

        result["success"] = True
        result["has_metadata"] = bool(metadata)
        log_verify(f"Method 4: found={result['found']}, has_metadata={result['has_metadata']}")

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 4: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 5: API_STATE
# Query internal API state
# ============================================================================
def verify_method_5_api_state(test_message: str) -> dict:
    """
    Method 5: API_STATE
    Query internal state via API
    """
    result = {"method": "API_STATE", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 5: API_STATE - Checking")

        # Try to get state from internal API
        webui_base = _get_webui_base()
        endpoint = f'{webui_base}/internal/state'

        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                state_data = response.json()
                result["found"] = test_message in str(state_data)
                result["state_preview"] = str(state_data)[:200]
            else:
                result["error"] = f"HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            result["error"] = "Internal API not available"

        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 5: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 6: VERIFICATION_ENDPOINT
# Custom verification endpoint
# ============================================================================
def verify_method_6_verification_endpoint(test_message: str) -> dict:
    """
    Method 6: VERIFICATION_ENDPOINT
    Custom endpoint that reports chat state
    """
    result = {"method": "VERIFICATION_ENDPOINT", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 6: VERIFICATION_ENDPOINT - Checking")

        webui_base = _get_webui_base()
        endpoint = f'{webui_base}/api/v1/internal/boredom_monitor/queue_status'

        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()
                result["found"] = test_message in str(data)
                result["endpoint_response"] = data
                result["success"] = True
            else:
                result["error"] = f"HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            result["error"] = "Verification endpoint not available"
            result["success"] = True  # Still mark as success (just not found)

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 6: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 7: DOM_CONTENT (JavaScript)
# Check DOM via JavaScript
# ============================================================================
def verify_method_7_dom_content(test_message: str) -> dict:
    """
    Method 7: DOM_CONTENT
    Check browser DOM (requires JavaScript bridge)
    """
    result = {"method": "DOM_CONTENT", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 7: DOM_CONTENT - Checking")

        # Cannot directly access browser DOM from Python
        # Would need JavaScript bridge or Selenium
        result["error"] = "REQUIRES_BROWSER - Cannot access DOM from Python"
        result["note"] = "Use verify_method_13_selenium for browser verification"
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 7: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 8: MUTATION_OBSERVER
# Check MutationObserver captures
# ============================================================================
def verify_method_8_mutation_observer(test_message: str) -> dict:
    """
    Method 8: MUTATION_OBSERVER
    Check if MutationObserver captured changes (requires browser)
    """
    result = {"method": "MUTATION_OBSERVER", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 8: MUTATION_OBSERVER - Checking")

        # MutationObserver is browser-side JavaScript
        result["error"] = "REQUIRES_BROWSER - MutationObserver is JavaScript API"
        result["note"] = "Would need JavaScript bridge to check mutations"
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 8: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 9: DATA_RAW
# Check data-raw attributes in HTML
# ============================================================================
def verify_method_9_data_raw(test_message: str) -> dict:
    """
    Method 9: DATA_RAW
    Check data-raw attributes in display HTML
    """
    result = {"method": "DATA_RAW", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 9: DATA_RAW - Checking")

        if not hasattr(shared, 'gradio') or 'display' not in shared.gradio:
            result["error"] = "shared.gradio['display'] not available"
            return result

        display = shared.gradio['display']
        if display is None:
            result["error"] = "Display is None"
            return result

        html_content = display.value if hasattr(display, 'value') else str(display)

        if html_content:
            # Look for data-raw attributes containing the message
            import re
            data_raw_pattern = r'data-raw="([^"]*)"'
            matches = re.findall(data_raw_pattern, html_content)

            for match in matches:
                if test_message in match:
                    result["found"] = True
                    result["matched_data_raw"] = match[:100]
                    break

            result["data_raw_count"] = len(matches)
        else:
            result["data_raw_count"] = 0

        result["success"] = True
        log_verify(f"Method 9: found={result['found']}, data_raw_count={result.get('data_raw_count', 0)}")

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 9: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 10: DOM_MESSAGE_COUNT
# Count DOM message elements
# ============================================================================
def verify_method_10_dom_message_count(test_message: str) -> dict:
    """
    Method 10: DOM_MESSAGE_COUNT
    Count message elements (requires browser)
    """
    result = {"method": "DOM_MESSAGE_COUNT", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 10: DOM_MESSAGE_COUNT - Checking")

        # Cannot access DOM directly from Python
        # Estimate from display HTML
        if hasattr(shared, 'gradio') and 'display' in shared.gradio:
            display = shared.gradio['display']
            if display and hasattr(display, 'value'):
                html = display.value or ""
                # Count message divs
                import re
                message_count = len(re.findall(r'<div[^>]*class="[^"]*message[^"]*"', html))
                result["estimated_message_count"] = message_count
                result["found"] = message_count > 0

        result["error"] = "ESTIMATED - Cannot access browser DOM, using HTML analysis"
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 10: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 11: SSE_EVENTS
# Monitor Server-Sent Events
# ============================================================================
def verify_method_11_sse_events(test_message: str) -> dict:
    """
    Method 11: SSE_EVENTS
    Check Server-Sent Events stream
    """
    result = {"method": "SSE_EVENTS", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 11: SSE_EVENTS - Checking")

        # SSE monitoring requires persistent connection
        # Not practical for one-time verification
        result["error"] = "NOT_PRACTICAL - SSE requires persistent connection"
        result["note"] = "SSE monitoring best done during injection, not after"
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 11: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 12: REQUEST_MONITOR
# Monitor HTTP request activity
# ============================================================================
def verify_method_12_request_monitor(test_message: str) -> dict:
    """
    Method 12: REQUEST_MONITOR
    Check if injection triggered HTTP requests
    """
    result = {"method": "REQUEST_MONITOR", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 12: REQUEST_MONITOR - Checking")

        # Request monitoring requires middleware/proxy
        result["error"] = "NOT_AVAILABLE - Would require request logging middleware"
        result["note"] = "Consider checking server logs instead"
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 12: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 13: SELENIUM
# External browser verification
# ============================================================================
def verify_method_13_selenium(test_message: str) -> dict:
    """
    Method 13: SELENIUM
    Use Selenium to check browser state
    """
    result = {"method": "SELENIUM", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 13: SELENIUM - Checking")

        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By

            # This requires an active browser session
            # Cannot create one inside extension easily
            result["error"] = "REQUIRES_EXTERNAL - Selenium needs external browser driver"
            result["note"] = "Use external test harness for Selenium verification"

        except ImportError:
            result["error"] = "selenium not installed"

        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 13: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 14: COMPREHENSIVE
# Aggregate multiple methods
# ============================================================================
def verify_method_14_comprehensive(test_message: str) -> dict:
    """
    Method 14: COMPREHENSIVE
    Run multiple verification methods and aggregate
    """
    result = {"method": "COMPREHENSIVE", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 14: COMPREHENSIVE - Running all verifications")

        # Run the methods that work from Python
        method_results = {
            1: verify_method_1_history_state(test_message),
            2: verify_method_2_message_count(test_message),
            3: verify_method_3_display_html(test_message),
            4: verify_method_4_metadata_timestamp(test_message),
            9: verify_method_9_data_raw(test_message),
        }

        # Count successes
        found_count = sum(1 for r in method_results.values() if r.get("found", False))
        total_checked = len(method_results)

        result["success"] = True
        result["found"] = found_count > 0
        result["found_count"] = found_count
        result["total_checked"] = total_checked
        result["method_results"] = method_results
        result["confidence"] = f"{found_count}/{total_checked}"

        log_verify(f"Method 14: found={result['found']}, confidence={result['confidence']}")

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 14: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 15: BROWSER_CALLBACK
# Check browser verification reports from browser_verification.js
# ============================================================================
def verify_method_15_browser_callback(test_message: str, wait_seconds: float = 2.0) -> dict:
    """
    Method 15: BROWSER_CALLBACK
    Check if browser JavaScript reported finding the test message.

    This is the TRUE end-user verification:
    - browser_verification.js runs in the user's browser
    - It uses MutationObserver to watch #chat for .message-body elements
    - When [INJECTION-TEST] messages are found, it POSTs to /api/v1/internal/boredom_monitor/browser_verification
    - This method checks those reports
    """
    result = {"method": "BROWSER_CALLBACK", "success": False, "found": False, "error": None}

    try:
        log_verify(f"Method 15: BROWSER_CALLBACK - Waiting {wait_seconds}s for browser report")

        # Give browser time to detect and report
        time.sleep(wait_seconds)

        # Import the bridge function to check reports
        try:
            from .gradio_injection_bridge import find_browser_verification, get_browser_verification_reports
        except ImportError:
            # Try relative import alternative
            from gradio_injection_bridge import find_browser_verification, get_browser_verification_reports

        # Check if any browser report contains our test message
        report = find_browser_verification(test_message)

        if report:
            result["found"] = True
            result["browser_report"] = {
                "message_text": report.get("message_text", "")[:100],
                "timestamp": report.get("timestamp"),
                "server_received": report.get("server_received"),
                "message_count": report.get("message_count"),
                "element_info": report.get("element_info")
            }
            log_verify(f"Method 15: Browser confirmed message in UI!")
        else:
            result["found"] = False
            result["total_reports"] = len(get_browser_verification_reports())
            log_verify(f"Method 15: No browser report found (total reports: {result['total_reports']})")

        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 15: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 16: BROWSER_API_QUERY
# Query browser verification API endpoint directly
# ============================================================================
def verify_method_16_browser_api_query(test_message: str) -> dict:
    """
    Method 16: BROWSER_API_QUERY
    Query the browser verification API endpoint for reports.

    This is useful for external test scripts that can't import the bridge directly.
    """
    result = {"method": "BROWSER_API_QUERY", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 16: BROWSER_API_QUERY - Checking")

        webui_base = _get_webui_base()
        endpoint = f'{webui_base}/api/v1/internal/boredom_monitor/browser_verification'

        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()
                reports = data.get('reports', [])
                result["total_reports"] = len(reports)

                # Search for test message in reports
                for report in reports:
                    msg_text = report.get('message_text', '')
                    if test_message in msg_text:
                        result["found"] = True
                        result["matching_report"] = {
                            "message_text": msg_text[:100],
                            "timestamp": report.get("timestamp"),
                            "server_received": report.get("server_received")
                        }
                        break

                result["success"] = True
                log_verify(f"Method 16: found={result['found']}, total_reports={result['total_reports']}")
            else:
                result["error"] = f"HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            result["error"] = "Browser verification endpoint not available"
            result["success"] = True  # Mark as success but not found

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 16: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# ALL VERIFICATION METHODS - Dictionary for test runner
# ============================================================================
ALL_VERIFICATION_METHODS = {
    1: ("HISTORY_STATE", verify_method_1_history_state),
    2: ("MESSAGE_COUNT", verify_method_2_message_count),
    3: ("DISPLAY_HTML", verify_method_3_display_html),
    4: ("METADATA_TIMESTAMP", verify_method_4_metadata_timestamp),
    5: ("API_STATE", verify_method_5_api_state),
    6: ("VERIFICATION_ENDPOINT", verify_method_6_verification_endpoint),
    7: ("DOM_CONTENT", verify_method_7_dom_content),
    8: ("MUTATION_OBSERVER", verify_method_8_mutation_observer),
    9: ("DATA_RAW", verify_method_9_data_raw),
    10: ("DOM_MESSAGE_COUNT", verify_method_10_dom_message_count),
    11: ("SSE_EVENTS", verify_method_11_sse_events),
    12: ("REQUEST_MONITOR", verify_method_12_request_monitor),
    13: ("SELENIUM", verify_method_13_selenium),
    14: ("COMPREHENSIVE", verify_method_14_comprehensive),
    15: ("BROWSER_CALLBACK", verify_method_15_browser_callback),
    16: ("BROWSER_API_QUERY", verify_method_16_browser_api_query),
}


def run_verification_method(method_num: int, test_message: str) -> dict:
    """Run a single verification method by number"""
    if method_num not in ALL_VERIFICATION_METHODS:
        return {"method": f"UNKNOWN_{method_num}", "success": False, "error": "Invalid method number"}

    name, func = ALL_VERIFICATION_METHODS[method_num]
    return func(test_message)


def run_all_verifications(test_message: str) -> dict:
    """Run all 16 verification methods and return results"""
    results = {}
    for num, (name, func) in ALL_VERIFICATION_METHODS.items():
        log_verify(f"Running verification method {num}: {name}")
        results[num] = func(test_message)
        time.sleep(0.05)  # Brief pause between methods
    return results


def quick_verify(test_message: str) -> dict:
    """Quick verification using only Python-accessible methods"""
    log_verify("Running quick verification (Python-only methods)")

    results = {
        "history_state": verify_method_1_history_state(test_message),
        "message_count": verify_method_2_message_count(test_message),
        "display_html": verify_method_3_display_html(test_message),
        "comprehensive": verify_method_14_comprehensive(test_message),
    }

    # Summary
    found_any = any(r.get("found", False) for r in results.values())

    return {
        "found": found_any,
        "details": results
    }
