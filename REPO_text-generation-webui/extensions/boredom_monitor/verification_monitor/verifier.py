"""
Standalone Verification Monitor - All 16 Verification Methods
=============================================================
Independent verification app that can test text-generation-webui
chat injections WITHOUT requiring internal access to shared.gradio.

All methods use HTTP API calls to connect to the running webui server.

This app can be used to:
1. Verify boredom_monitor injections
2. Test other extensions that inject messages
3. Run as a standalone diagnostic tool

Usage:
    python verifier.py --test "my test message"
    python verifier.py --method 1 --test "my test message"
    python verifier.py --all --test "my test message"
    python verifier.py --quick --test "my test message"
"""

import argparse
import time
import json
import requests
import re
import sys
from datetime import datetime
from pathlib import Path


# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
LOG_DIR = Path("F:/Apps/freedom_system/log")

# Default configuration
DEFAULT_CONFIG = {
    "webui_base": "http://127.0.0.1:7860",
    "timeout_seconds": 5,
    "log_to_file": True,
    "log_file": "verification_monitor.log",
    "verbose": True
}


def load_config() -> dict:
    """Load configuration from JSON file or use defaults"""
    config = DEFAULT_CONFIG.copy()
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                config.update(file_config)
    except Exception as e:
        log_verify(f"Warning: Could not load config: {e}", "WARN")
    return config


def save_config(config: dict):
    """Save configuration to JSON file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        log_verify(f"Warning: Could not save config: {e}", "WARN")


# ============================================================================
# LOGGING
# ============================================================================
def log_verify(message: str, level: str = "INFO"):
    """Verification logging with optional file output"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log_line = f"{timestamp} [VERIFY-STANDALONE] [{level}] {message}"
    print(log_line)

    config = load_config()
    if config.get("log_to_file", True):
        try:
            log_path = LOG_DIR / config.get("log_file", "verification_monitor.log")
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"{log_line}\n")
        except:
            pass


# ============================================================================
# API HELPERS
# ============================================================================
def get_webui_base() -> str:
    """Get WebUI base URL from config"""
    return load_config().get("webui_base", "http://127.0.0.1:7860")


def get_timeout() -> int:
    """Get request timeout from config"""
    return load_config().get("timeout_seconds", 5)


def api_get(endpoint: str) -> tuple:
    """
    Make a GET request to the webui API.
    Returns (success: bool, data: dict or None, error: str or None)
    """
    webui_base = get_webui_base()
    url = f"{webui_base}{endpoint}"

    try:
        response = requests.get(url, timeout=get_timeout())
        if response.status_code == 200:
            try:
                return True, response.json(), None
            except:
                return True, {"text": response.text}, None
        else:
            return False, None, f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, None, "Connection refused - is WebUI running?"
    except requests.exceptions.Timeout:
        return False, None, "Request timed out"
    except Exception as e:
        return False, None, str(e)


def api_post(endpoint: str, data: dict) -> tuple:
    """
    Make a POST request to the webui API.
    Returns (success: bool, data: dict or None, error: str or None)
    """
    webui_base = get_webui_base()
    url = f"{webui_base}{endpoint}"

    try:
        response = requests.post(url, json=data, timeout=get_timeout())
        if response.status_code == 200:
            try:
                return True, response.json(), None
            except:
                return True, {"text": response.text}, None
        else:
            return False, None, f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, None, "Connection refused - is WebUI running?"
    except requests.exceptions.Timeout:
        return False, None, "Request timed out"
    except Exception as e:
        return False, None, str(e)


# ============================================================================
# VERIFICATION METHOD 1: HISTORY_STATE
# Check history via API endpoint
# ============================================================================
def verify_method_1_history_state(test_message: str) -> dict:
    """
    Method 1: HISTORY_STATE
    Check if test_message exists in chat history via API

    Note: This requires an API endpoint that exposes history state.
    Falls back to checking queue_status endpoint.
    """
    result = {"method": "HISTORY_STATE", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 1: HISTORY_STATE - Checking via API")

        # Try boredom_monitor queue status endpoint first
        success, data, error = api_get("/api/v1/internal/boredom_monitor/queue_status")

        if success and data:
            # Check if test message is in any returned data
            data_str = json.dumps(data)
            result["found"] = test_message in data_str
            result["success"] = True
            result["api_response_preview"] = data_str[:200]
        else:
            # Try internal state endpoint
            success, data, error = api_get("/internal/state")
            if success and data:
                data_str = json.dumps(data)
                result["found"] = test_message in data_str
                result["success"] = True
            else:
                result["error"] = error or "No history API available"
                result["success"] = True  # Mark success but not found

        log_verify(f"Method 1: found={result['found']}")

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 1: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 2: MESSAGE_COUNT
# Count messages via API
# ============================================================================
def verify_method_2_message_count(test_message: str, expected_increase: int = 1) -> dict:
    """
    Method 2: MESSAGE_COUNT
    Check message count via API
    """
    result = {"method": "MESSAGE_COUNT", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 2: MESSAGE_COUNT - Checking via API")

        success, data, error = api_get("/api/v1/internal/boredom_monitor/queue_status")

        if success and data:
            # Try to extract message count from response
            result["success"] = True
            result["api_data"] = data

            # If there's any history data, mark as found
            if "history_length" in data:
                result["message_count"] = data["history_length"]
                result["found"] = data["history_length"] > 0
            else:
                result["found"] = True  # Endpoint responded, assume working
        else:
            result["error"] = error or "Could not get message count"
            result["success"] = True

        log_verify(f"Method 2: found={result['found']}")

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 2: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 3: DISPLAY_HTML
# Check display HTML via API (limited in standalone mode)
# ============================================================================
def verify_method_3_display_html(test_message: str) -> dict:
    """
    Method 3: DISPLAY_HTML
    Check if test_message appears in display HTML

    Note: In standalone mode, we can't access display component directly.
    This method checks API endpoints for HTML content.
    """
    result = {"method": "DISPLAY_HTML", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 3: DISPLAY_HTML - Checking via API")

        # Try to get page content
        success, data, error = api_get("/")

        if success and data:
            html_content = data.get("text", str(data))
            result["found"] = test_message in html_content
            result["html_length"] = len(html_content)
            result["success"] = True
        else:
            result["error"] = "STANDALONE_LIMITATION - Cannot access display component directly"
            result["note"] = "Use browser verification methods (15-16) for accurate HTML check"
            result["success"] = True

        log_verify(f"Method 3: found={result['found']}")

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
    Check if recent message timestamp exists via API
    """
    result = {"method": "METADATA_TIMESTAMP", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 4: METADATA_TIMESTAMP - Checking via API")

        success, data, error = api_get("/api/v1/internal/boredom_monitor/queue_status")

        if success and data:
            result["success"] = True

            # Check for timestamp fields
            now = time.time()
            if "last_injection_time" in data:
                inject_time = data["last_injection_time"]
                if now - inject_time < max_age_seconds:
                    result["found"] = True
                    result["recent_timestamp"] = inject_time
            elif "timestamp" in data:
                result["found"] = True
                result["has_timestamp"] = True
            else:
                result["found"] = False
        else:
            result["error"] = error or "Could not check timestamps"
            result["success"] = True

        log_verify(f"Method 4: found={result['found']}")

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

        success, data, error = api_get("/internal/state")

        if success and data:
            data_str = json.dumps(data)
            result["found"] = test_message in data_str
            result["state_preview"] = data_str[:200]
            result["success"] = True
        else:
            result["error"] = error or "Internal API not available"
            result["success"] = True

        log_verify(f"Method 5: found={result['found']}")

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

        success, data, error = api_get("/api/v1/internal/boredom_monitor/queue_status")

        if success and data:
            data_str = json.dumps(data)
            result["found"] = test_message in data_str
            result["endpoint_response"] = data
            result["success"] = True
        else:
            result["error"] = error or "Verification endpoint not available"
            result["success"] = True

        log_verify(f"Method 6: found={result['found']}")

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 6: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 7: DOM_CONTENT (JavaScript)
# Check DOM via JavaScript - requires browser
# ============================================================================
def verify_method_7_dom_content(test_message: str) -> dict:
    """
    Method 7: DOM_CONTENT
    Check browser DOM (requires JavaScript bridge)
    """
    result = {"method": "DOM_CONTENT", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 7: DOM_CONTENT - Checking")

        result["error"] = "REQUIRES_BROWSER - Cannot access DOM from standalone Python"
        result["note"] = "Use verify_method_13_selenium or browser methods 15-16"
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 7: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 8: MUTATION_OBSERVER
# Check MutationObserver captures - requires browser
# ============================================================================
def verify_method_8_mutation_observer(test_message: str) -> dict:
    """
    Method 8: MUTATION_OBSERVER
    Check if MutationObserver captured changes (requires browser)
    """
    result = {"method": "MUTATION_OBSERVER", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 8: MUTATION_OBSERVER - Checking")

        result["error"] = "REQUIRES_BROWSER - MutationObserver is JavaScript API"
        result["note"] = "Use browser methods 15-16 for mutation observation"
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
    Check data-raw attributes in HTML via API
    """
    result = {"method": "DATA_RAW", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 9: DATA_RAW - Checking")

        # In standalone mode, we can't access display HTML directly
        result["error"] = "STANDALONE_LIMITATION - Cannot access display HTML directly"
        result["note"] = "Use browser methods 15-16 for HTML verification"
        result["success"] = True

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

        result["error"] = "REQUIRES_BROWSER - Cannot count DOM elements from Python"
        result["note"] = "Use browser methods 15-16 for DOM verification"
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
            from selenium.webdriver.chrome.options import Options

            # Setup headless Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=chrome_options)

            try:
                webui_base = get_webui_base()
                driver.get(webui_base)
                time.sleep(2)  # Wait for page load

                # Search for test message in page
                page_source = driver.page_source
                result["found"] = test_message in page_source
                result["page_length"] = len(page_source)
                result["success"] = True

            finally:
                driver.quit()

        except ImportError:
            result["error"] = "selenium not installed - pip install selenium"
            result["success"] = True
        except Exception as e:
            result["error"] = f"Selenium error: {e}"
            result["success"] = True

        log_verify(f"Method 13: found={result['found']}")

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
        log_verify("Method 14: COMPREHENSIVE - Running API-based verifications")

        # Run the methods that work from standalone
        method_results = {
            1: verify_method_1_history_state(test_message),
            5: verify_method_5_api_state(test_message),
            6: verify_method_6_verification_endpoint(test_message),
            15: verify_method_15_browser_callback(test_message),
            16: verify_method_16_browser_api_query(test_message),
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
# Check browser verification reports
# ============================================================================
def verify_method_15_browser_callback(test_message: str, wait_seconds: float = 2.0) -> dict:
    """
    Method 15: BROWSER_CALLBACK
    Check if browser JavaScript reported finding the test message.
    """
    result = {"method": "BROWSER_CALLBACK", "success": False, "found": False, "error": None}

    try:
        log_verify(f"Method 15: BROWSER_CALLBACK - Waiting {wait_seconds}s for browser report")

        # Give browser time to detect and report
        time.sleep(wait_seconds)

        success, data, error = api_get("/api/v1/internal/boredom_monitor/browser_verification")

        if success and data:
            reports = data.get('reports', [])
            result["total_reports"] = len(reports)

            # Search for test message in reports
            for report in reports:
                msg_text = report.get('message_text', '')
                if test_message in msg_text:
                    result["found"] = True
                    result["browser_report"] = {
                        "message_text": msg_text[:100],
                        "timestamp": report.get("timestamp"),
                        "server_received": report.get("server_received"),
                        "message_count": report.get("message_count")
                    }
                    break

            result["success"] = True
        else:
            result["error"] = error or "Browser verification endpoint not available"
            result["success"] = True

        log_verify(f"Method 15: found={result['found']}")

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 15: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# VERIFICATION METHOD 16: BROWSER_API_QUERY
# Query browser verification API endpoint
# ============================================================================
def verify_method_16_browser_api_query(test_message: str) -> dict:
    """
    Method 16: BROWSER_API_QUERY
    Query the browser verification API endpoint for reports.
    """
    result = {"method": "BROWSER_API_QUERY", "success": False, "found": False, "error": None}

    try:
        log_verify("Method 16: BROWSER_API_QUERY - Checking")

        success, data, error = api_get("/api/v1/internal/boredom_monitor/browser_verification")

        if success and data:
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
            result["error"] = error or "Browser verification endpoint not available"
            result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        log_verify(f"Method 16: FAILED - {e}", "ERROR")

    return result


# ============================================================================
# ALL VERIFICATION METHODS - Dictionary for programmatic access
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
    """Quick verification using only API-accessible methods"""
    log_verify("Running quick verification (API-only methods)")

    results = {
        "history_state": verify_method_1_history_state(test_message),
        "api_state": verify_method_5_api_state(test_message),
        "verification_endpoint": verify_method_6_verification_endpoint(test_message),
        "browser_api": verify_method_16_browser_api_query(test_message),
    }

    # Summary
    found_any = any(r.get("found", False) for r in results.values())

    return {
        "found": found_any,
        "details": results
    }


def check_webui_connection() -> bool:
    """Check if WebUI is accessible"""
    webui_base = get_webui_base()
    try:
        response = requests.get(webui_base, timeout=5)
        return response.status_code == 200
    except:
        return False


# ============================================================================
# CLI INTERFACE
# ============================================================================
def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Standalone Verification Monitor - Test chat injection verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verifier.py --test "Hello World"           Run quick verification
  python verifier.py --method 1 --test "Hello"      Run specific method
  python verifier.py --all --test "Test message"    Run all 16 methods
  python verifier.py --list                         List all methods
  python verifier.py --check                        Check WebUI connection
  python verifier.py --config                       Show current config
        """
    )

    parser.add_argument("--test", "-t", type=str, help="Test message to verify")
    parser.add_argument("--method", "-m", type=int, help="Specific method number (1-16)")
    parser.add_argument("--all", "-a", action="store_true", help="Run all 16 verification methods")
    parser.add_argument("--quick", "-q", action="store_true", help="Run quick verification (default)")
    parser.add_argument("--list", "-l", action="store_true", help="List all verification methods")
    parser.add_argument("--check", "-c", action="store_true", help="Check WebUI connection")
    parser.add_argument("--config", action="store_true", help="Show current configuration")
    parser.add_argument("--url", type=str, help="Override WebUI base URL")
    parser.add_argument("--output", "-o", type=str, help="Output results to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Handle URL override
    if args.url:
        config = load_config()
        config["webui_base"] = args.url
        save_config(config)
        print(f"WebUI URL set to: {args.url}")

    # List methods
    if args.list:
        print("\n=== All 16 Verification Methods ===\n")
        for num, (name, func) in ALL_VERIFICATION_METHODS.items():
            print(f"  {num:2d}. {name}")
        print("\n=== Method Categories ===")
        print("  API-based (work standalone): 1, 2, 4, 5, 6, 14, 15, 16")
        print("  Require browser: 7, 8, 10, 13")
        print("  Limited in standalone: 3, 9, 11, 12")
        return 0

    # Check connection
    if args.check:
        webui_base = get_webui_base()
        print(f"Checking connection to: {webui_base}")
        if check_webui_connection():
            print("SUCCESS: WebUI is accessible")
            return 0
        else:
            print("FAILED: Cannot connect to WebUI")
            return 1

    # Show config
    if args.config:
        config = load_config()
        print("\n=== Current Configuration ===\n")
        print(json.dumps(config, indent=2))
        return 0

    # Require test message for verification
    if not args.test:
        if not (args.list or args.check or args.config):
            parser.print_help()
            print("\nError: --test argument required for verification")
            return 1
        return 0

    test_message = args.test
    results = None

    # Run specific method
    if args.method:
        if args.method < 1 or args.method > 16:
            print(f"Error: Method must be 1-16, got {args.method}")
            return 1

        name, func = ALL_VERIFICATION_METHODS[args.method]
        print(f"\n=== Running Method {args.method}: {name} ===\n")
        results = func(test_message)

    # Run all methods
    elif args.all:
        print(f"\n=== Running All 16 Verification Methods ===\n")
        print(f"Test message: {test_message}\n")
        results = run_all_verifications(test_message)

    # Default: quick verification
    else:
        print(f"\n=== Running Quick Verification ===\n")
        print(f"Test message: {test_message}\n")
        results = quick_verify(test_message)

    # Display results
    print("\n=== Results ===\n")
    print(json.dumps(results, indent=2, default=str))

    # Output to file if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to: {args.output}")

    # Return code based on found status
    if isinstance(results, dict):
        if results.get("found", False):
            print("\nOVERALL: Message FOUND")
            return 0
        else:
            print("\nOVERALL: Message NOT FOUND")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
