"""
Selenium-Based External Injection Verification
==============================================

This module provides EXTERNAL browser verification for injection testing.
It runs independently of the text-generation-webui process and can verify
that messages actually appear in the browser DOM.

CRITICAL: This is the most reliable verification method because it
actually opens a real browser and checks what the user would see.

Usage:
    from selenium_verifier import SeleniumVerifier

    verifier = SeleniumVerifier()
    result = verifier.verify_message_exists("test message")
    verifier.close()

Author: Freedom System
"""

import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

# Configure logging
LOG_DIR = Path("F:/Apps/freedom_system/log")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger("SeleniumVerifier")


@dataclass
class VerificationResult:
    """Result of a verification attempt."""
    verified: bool
    expected_message: str
    method: str
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class SeleniumVerifier:
    """
    External browser verification using Selenium WebDriver.

    This provides the most reliable verification because it:
    1. Opens an actual browser window
    2. Navigates to the WebUI
    3. Checks the actual DOM that users see
    4. Can take screenshots for debugging
    """

    def __init__(self, url: str = "http://127.0.0.1:7860", headless: bool = True):
        """
        Initialize the Selenium verifier.

        Args:
            url: URL of the text-generation-webui
            headless: Run browser in headless mode (no window)
        """
        self.url = url
        self.headless = headless
        self.driver = None
        self._init_driver()

    def _init_driver(self):
        """Initialize the WebDriver."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument('--headless=new')

            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')

            # Try to find chromedriver
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                # Try with explicit service
                logger.warning(f"Default Chrome driver failed: {e}")
                logger.info("Trying with webdriver-manager...")

                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                except ImportError:
                    logger.error("webdriver-manager not installed. Install with: pip install webdriver-manager")
                    raise

            logger.info(f"Selenium WebDriver initialized (headless={self.headless})")

            # Navigate to WebUI
            self.driver.get(self.url)
            logger.info(f"Navigated to {self.url}")

            # Wait for page load
            time.sleep(2)

        except ImportError:
            logger.error("Selenium not installed. Install with: pip install selenium")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def verify_message_exists(self, expected_message: str, timeout: float = 10.0,
                               poll_interval: float = 0.5) -> VerificationResult:
        """
        Verify that a message exists in the browser DOM.

        Args:
            expected_message: Message text to find
            timeout: Maximum time to wait
            poll_interval: Time between checks
        Returns:
            VerificationResult
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        logger.info(f"[VERIFY] Selenium: Looking for '{expected_message[:50]}...'")
        start = time.time()

        try:
            # Wait for messages container
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "messages"))
                )
            except:
                logger.warning("[VERIFY] Selenium: .messages container not found")

            # Poll for the message
            while time.time() - start < timeout:
                # Check message bodies
                try:
                    message_bodies = self.driver.find_elements(By.CSS_SELECTOR, ".message .message-body")
                    for idx, body in enumerate(message_bodies):
                        try:
                            text = body.text
                            if expected_message in text:
                                duration = (time.time() - start) * 1000
                                logger.info(f"[VERIFY] Selenium: FOUND in message-body[{idx}] ({duration:.1f}ms)")
                                return VerificationResult(
                                    verified=True,
                                    expected_message=expected_message,
                                    method="selenium_message_body",
                                    duration_ms=duration,
                                    details={
                                        'found_at_index': idx,
                                        'found_in': 'message-body',
                                        'text_preview': text[:200]
                                    }
                                )
                        except:
                            pass
                except:
                    pass

                # Check data-raw attributes
                try:
                    messages_with_raw = self.driver.find_elements(By.CSS_SELECTOR, ".message[data-raw]")
                    for idx, msg in enumerate(messages_with_raw):
                        try:
                            raw = msg.get_attribute('data-raw')
                            if raw and expected_message in raw:
                                duration = (time.time() - start) * 1000
                                logger.info(f"[VERIFY] Selenium: FOUND in data-raw[{idx}] ({duration:.1f}ms)")
                                return VerificationResult(
                                    verified=True,
                                    expected_message=expected_message,
                                    method="selenium_data_raw",
                                    duration_ms=duration,
                                    details={
                                        'found_at_index': idx,
                                        'found_in': 'data-raw',
                                        'data_raw_preview': raw[:200]
                                    }
                                )
                        except:
                            pass
                except:
                    pass

                time.sleep(poll_interval)

            # Not found
            duration = (time.time() - start) * 1000
            logger.warning(f"[VERIFY] Selenium: NOT FOUND after {duration:.1f}ms")

            # Get debug info
            message_count = len(self.driver.find_elements(By.CSS_SELECTOR, ".message"))
            last_message = self._get_last_message_text()

            return VerificationResult(
                verified=False,
                expected_message=expected_message,
                method="selenium",
                duration_ms=duration,
                details={
                    'message_count': message_count,
                    'last_message_preview': last_message[:200] if last_message else None
                }
            )

        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"[VERIFY] Selenium: ERROR - {e}")
            return VerificationResult(
                verified=False,
                expected_message=expected_message,
                method="selenium",
                duration_ms=duration,
                error=str(e)
            )

    def verify_message_count_increased(self, initial_count: int, expected_increase: int = 1,
                                         timeout: float = 10.0) -> VerificationResult:
        """
        Verify that the message count increased in the browser.

        Args:
            initial_count: Initial message count before injection
            expected_increase: Expected number of new messages
            timeout: Maximum time to wait
        Returns:
            VerificationResult
        """
        from selenium.webdriver.common.by import By

        logger.info(f"[VERIFY] Selenium count: Expecting {initial_count} + {expected_increase}")
        start = time.time()

        try:
            while time.time() - start < timeout:
                current_count = len(self.driver.find_elements(By.CSS_SELECTOR, ".message"))

                if current_count >= initial_count + expected_increase:
                    duration = (time.time() - start) * 1000
                    actual_increase = current_count - initial_count
                    logger.info(f"[VERIFY] Selenium count: {initial_count} -> {current_count} ({duration:.1f}ms)")
                    return VerificationResult(
                        verified=True,
                        expected_message=f"count >= {initial_count + expected_increase}",
                        method="selenium_count",
                        duration_ms=duration,
                        details={
                            'initial_count': initial_count,
                            'final_count': current_count,
                            'actual_increase': actual_increase
                        }
                    )

                time.sleep(0.5)

            # Timeout
            duration = (time.time() - start) * 1000
            current_count = len(self.driver.find_elements(By.CSS_SELECTOR, ".message"))
            logger.warning(f"[VERIFY] Selenium count: TIMEOUT {initial_count} -> {current_count}")

            return VerificationResult(
                verified=False,
                expected_message=f"count >= {initial_count + expected_increase}",
                method="selenium_count",
                duration_ms=duration,
                details={
                    'initial_count': initial_count,
                    'final_count': current_count,
                    'actual_increase': current_count - initial_count,
                    'expected_increase': expected_increase
                }
            )

        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"[VERIFY] Selenium count: ERROR - {e}")
            return VerificationResult(
                verified=False,
                expected_message=f"count >= {initial_count + expected_increase}",
                method="selenium_count",
                duration_ms=duration,
                error=str(e)
            )

    def get_message_count(self) -> int:
        """Get current message count in browser."""
        from selenium.webdriver.common.by import By
        try:
            messages = self.driver.find_elements(By.CSS_SELECTOR, ".message")
            return len(messages)
        except:
            return 0

    def _get_last_message_text(self) -> Optional[str]:
        """Get the last message text from browser."""
        from selenium.webdriver.common.by import By
        try:
            message_bodies = self.driver.find_elements(By.CSS_SELECTOR, ".message .message-body")
            if message_bodies:
                return message_bodies[-1].text
        except:
            pass
        return None

    def get_all_messages(self) -> List[Dict[str, str]]:
        """Get all messages from browser."""
        from selenium.webdriver.common.by import By

        messages = []
        try:
            message_elements = self.driver.find_elements(By.CSS_SELECTOR, ".message")
            for idx, elem in enumerate(message_elements):
                try:
                    body = elem.find_element(By.CSS_SELECTOR, ".message-body")
                    data_raw = elem.get_attribute('data-raw')
                    messages.append({
                        'index': idx,
                        'text': body.text,
                        'data_raw': data_raw
                    })
                except:
                    pass
        except:
            pass

        return messages

    def take_screenshot(self, filename: str = None) -> str:
        """
        Take a screenshot for debugging.

        Args:
            filename: Output filename (auto-generated if None)
        Returns:
            Path to screenshot file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = LOG_DIR / f"selenium_screenshot_{timestamp}.png"
        else:
            filename = Path(filename)

        self.driver.save_screenshot(str(filename))
        logger.info(f"[SCREENSHOT] Saved to: {filename}")
        return str(filename)

    def refresh(self):
        """Refresh the browser page."""
        self.driver.refresh()
        time.sleep(2)
        logger.info("[BROWSER] Page refreshed")

    def execute_js(self, script: str) -> Any:
        """Execute JavaScript in the browser."""
        return self.driver.execute_script(script)

    def inject_verifier_js(self):
        """Inject the browser_verifier.js script into the page."""
        js_path = Path(__file__).parent / "browser_verifier.js"
        if js_path.exists():
            with open(js_path, 'r') as f:
                js_code = f.read()
            self.driver.execute_script(js_code)
            logger.info("[BROWSER] Injected browser_verifier.js")
        else:
            logger.warning(f"[BROWSER] browser_verifier.js not found at {js_path}")

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("[BROWSER] Closed")


class ComprehensiveVerifier:
    """
    Combines multiple verification methods for maximum reliability.
    """

    def __init__(self, webui_url: str = "http://127.0.0.1:7860", use_selenium: bool = True):
        """
        Initialize comprehensive verifier.

        Args:
            webui_url: URL of the text-generation-webui
            use_selenium: Whether to use Selenium verification
        """
        self.webui_url = webui_url
        self.selenium_verifier = None

        if use_selenium:
            try:
                self.selenium_verifier = SeleniumVerifier(url=webui_url, headless=True)
            except Exception as e:
                logger.warning(f"Selenium not available: {e}")

    def verify_all(self, expected_message: str, timeout: float = 10.0) -> Dict[str, Any]:
        """
        Run all available verification methods.

        Args:
            expected_message: Message to verify
            timeout: Maximum time for each method
        Returns:
            Dict with results from all methods
        """
        results = {
            'expected_message': expected_message,
            'timestamp': datetime.now().isoformat(),
            'methods': {},
            'confirmations': 0,
            'overall_verified': False
        }

        # Method 1: Selenium DOM verification
        if self.selenium_verifier:
            selenium_result = self.selenium_verifier.verify_message_exists(
                expected_message, timeout=timeout
            )
            results['methods']['selenium_dom'] = {
                'verified': selenium_result.verified,
                'duration_ms': selenium_result.duration_ms,
                'details': selenium_result.details
            }
            if selenium_result.verified:
                results['confirmations'] += 1

        # Method 2: API verification
        api_result = self._verify_via_api(expected_message, timeout)
        results['methods']['api'] = api_result
        if api_result.get('verified'):
            results['confirmations'] += 1

        # Determine overall result (require at least 1 confirmation)
        results['overall_verified'] = results['confirmations'] >= 1

        logger.info(f"[COMPREHENSIVE] {results['confirmations']} confirmations - "
                   f"{'VERIFIED' if results['overall_verified'] else 'NOT VERIFIED'}")

        return results

    def _verify_via_api(self, expected_message: str, timeout: float) -> Dict[str, Any]:
        """Verify via HTTP API."""
        import requests

        try:
            # Try OpenAI extension internal state endpoint
            response = requests.get(
                f"{self.webui_url.replace('7860', '5000')}/v1/internal/state",
                timeout=timeout
            )
            if response.status_code == 200:
                data = response.json()
                history = data.get('history', {})
                messages = history.get('internal', [])

                for idx, msg in enumerate(messages):
                    if len(msg) >= 2:
                        if expected_message in msg[0] or expected_message in msg[1]:
                            return {
                                'verified': True,
                                'found_at_index': idx,
                                'method': 'openai_internal_state'
                            }

                return {
                    'verified': False,
                    'message_count': len(messages)
                }

        except Exception as e:
            return {
                'verified': False,
                'error': str(e)
            }

    def close(self):
        """Clean up resources."""
        if self.selenium_verifier:
            self.selenium_verifier.close()


def main():
    """Test the Selenium verifier."""
    import argparse

    parser = argparse.ArgumentParser(description="Selenium-based injection verification")
    parser.add_argument('--url', type=str, default="http://127.0.0.1:7860",
                       help="WebUI URL")
    parser.add_argument('--message', type=str, help="Message to verify")
    parser.add_argument('--screenshot', action='store_true', help="Take screenshot")
    parser.add_argument('--headless', action='store_true', default=True,
                       help="Run in headless mode")
    args = parser.parse_args()

    logger.info("Starting Selenium Verifier...")

    verifier = SeleniumVerifier(url=args.url, headless=args.headless)

    try:
        # Get current state
        message_count = verifier.get_message_count()
        logger.info(f"Current message count: {message_count}")

        all_messages = verifier.get_all_messages()
        logger.info(f"Messages in DOM:")
        for msg in all_messages[-5:]:  # Last 5 messages
            logger.info(f"  [{msg['index']}]: {msg['text'][:100]}...")

        if args.message:
            result = verifier.verify_message_exists(args.message)
            logger.info(f"Verification result: {result.verified}")

        if args.screenshot:
            path = verifier.take_screenshot()
            logger.info(f"Screenshot: {path}")

    finally:
        verifier.close()


if __name__ == "__main__":
    main()
