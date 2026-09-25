"""
Gradio Injection Bridge - The PROPER way to inject messages from background threads

The key insight: Gradio only updates UI when event handlers RETURN values.
Solution: Create a hidden button that background threads can trigger via JavaScript polling,
whose event handler returns updated history and display values.

This matches exactly how "new chat greeting" works.
"""

import gradio as gr
from modules import shared
from modules.chat import redraw_html
from datetime import datetime

# Queue for pending injection messages
injection_queue = []

# Storage for browser verification reports
browser_verification_reports = []
MAX_BROWSER_REPORTS = 100  # Keep last 100 reports

def queue_message_for_injection(message):
    """
    Queue a message to be injected into chat.
    Called from background threads.

    Args:
        message (str): The message to inject into the chat UI

    Returns:
        bool: True if queued successfully, False otherwise
    """
    global injection_queue

    try:
        injection_queue.append(message)
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"{timestamp} [INJECTION-BRIDGE] Queued message: {message[:50]}... (Queue size: {len(injection_queue)})")

        # Try to trigger injection immediately by calling process_injection_queue
        # This works because Gradio will handle the UI update automatically
        _trigger_injection_if_possible()

        return True
    except Exception as e:
        print(f"[INJECTION-BRIDGE] ERROR queuing message: {str(e)}")
        return False

def _trigger_injection_if_possible():
    """
    Attempt to trigger injection by directly modifying shared.gradio components.
    This is a workaround since we can't click buttons from background threads.
    """
    try:
        from modules import shared as mod_shared

        # Check if we have access to the gradio components
        if hasattr(mod_shared, 'gradio') and 'history' in mod_shared.gradio:
            # Get current history
            history_component = mod_shared.gradio.get('history')
            interface_state = mod_shared.gradio.get('interface_state', {})

            if history_component and injection_queue:
                # Process one message from the queue
                message = injection_queue.pop(0)
                current_history = history_component.value or {'internal': [], 'visible': [], 'metadata': {}}

                # Add message to history
                current_history['internal'].append(['', message])
                current_history['visible'].append(['', message])

                # Update the component value - Gradio will handle the UI update
                history_component.value = current_history

                print(f"[INJECTION-BRIDGE] Direct injection successful: {message[:50]}...")
                return True
    except Exception as e:
        # Silently fail - this is just an optimization, not required
        pass

    return False

def get_queue_status():
    """
    Get the current queue status for JavaScript polling.
    This is called by the /api/v1/internal/boredom_monitor/queue_status endpoint.

    Returns:
        dict: {'queue_size': int, 'has_pending': bool}
    """
    global injection_queue
    return {
        'queue_size': len(injection_queue),
        'has_pending': len(injection_queue) > 0
    }

def process_injection_queue(current_history, state):
    """
    Event handler for the hidden injection button.
    This function is called BY GRADIO when the button is clicked.
    It RETURNS the updated history and html, which triggers UI update.
    """
    global injection_queue

    if not injection_queue:
        # No messages to inject, return current values
        return current_history, redraw_html(current_history, state['name1'], state['name2'], state['mode'], state['chat_style'], state['character_menu'])

    # Get the next message from queue
    message = injection_queue.pop(0)
    print(f"[INJECTION-BRIDGE] Processing injection: {message[:50]}... ({len(injection_queue)} remaining)")

    # Add message to history
    if current_history is None:
        current_history = {'internal': [], 'visible': [], 'metadata': {}}

    current_history['internal'].append(['', message])
    current_history['visible'].append(['', message])

    # Generate HTML display
    html = redraw_html(current_history, state['name1'], state['name2'], state['mode'], state['chat_style'], state['character_menu'])

    print(f"[INJECTION-BRIDGE] Injection complete - returning updated history and HTML")

    # RETURN the values - this is what triggers the UI update!
    return current_history, html

def ui():
    """
    Create UI components for the injection bridge.
    Called during extension setup to add the hidden button.
    """
    with gr.Row(visible=False):
        inject_btn = gr.Button("🔄 Process Injection Queue", elem_id="boredom_inject_hidden_btn")

    return inject_btn

def check_and_trigger_injection():
    """
    Check if there are queued messages and return whether to trigger injection.
    This is called by a Gradio Timer to poll the queue.
    """
    global injection_queue
    return len(injection_queue) > 0

def setup_injection_bridge(inject_btn, timer=None):
    """
    Set up the event handler for the injection button.
    This connects the button click to our process_injection_queue function.

    Args:
        inject_btn: The Gradio button component created by ui()
        timer: Optional Gradio Timer component for automatic polling

    Returns:
        None
    """
    from modules import ui as ui_module

    # Set up the button click event handler
    # This is the KEY: when clicked, it gathers state, processes the queue,
    # and RETURNS updated history and display, which triggers UI update!
    inject_btn.click(
        ui_module.gather_interface_values,
        [shared.gradio[k] for k in shared.input_elements],
        shared.gradio['interface_state']
    ).then(
        process_injection_queue,
        [shared.gradio['history'], shared.gradio['interface_state']],
        [shared.gradio['history'], shared.gradio['display']],
        show_progress=False
    )

    # If a timer is provided, set it up to trigger the button when queue has messages
    if timer is not None:
        timer.tick(
            check_and_trigger_injection,
            outputs=inject_btn,
            show_progress=False
        )

    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{timestamp} [INJECTION-BRIDGE] Hidden injection button event handler configured")

def get_browser_verification_reports():
    """
    Get all browser verification reports.

    Returns:
        list: List of browser verification report dicts
    """
    global browser_verification_reports
    return browser_verification_reports.copy()


def add_browser_verification_report(report: dict):
    """
    Add a browser verification report from JavaScript.

    Args:
        report: Dict containing verification data from browser

    Returns:
        bool: True if added successfully
    """
    global browser_verification_reports

    try:
        # Add server timestamp
        report['server_received'] = datetime.now().isoformat()

        browser_verification_reports.append(report)

        # Keep only last N reports
        if len(browser_verification_reports) > MAX_BROWSER_REPORTS:
            browser_verification_reports = browser_verification_reports[-MAX_BROWSER_REPORTS:]

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        msg_preview = report.get('message_text', '')[:50]
        print(f"{timestamp} [BROWSER-VERIFY] Received report: {msg_preview}...")

        return True
    except Exception as e:
        print(f"[BROWSER-VERIFY] Error adding report: {e}")
        return False


def clear_browser_verification_reports():
    """Clear all browser verification reports."""
    global browser_verification_reports
    browser_verification_reports = []


def find_browser_verification(test_message: str) -> dict:
    """
    Find a browser verification report matching the test message.

    Args:
        test_message: The test message to search for

    Returns:
        dict: The matching report or None
    """
    global browser_verification_reports

    for report in browser_verification_reports:
        msg_text = report.get('message_text', '')
        if test_message in msg_text:
            return report

    return None


def setup_api_endpoint(app):
    """
    Set up FastAPI endpoints for injection bridge and browser verification.

    Args:
        app: The FastAPI application instance

    Returns:
        None
    """
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse

    @app.get("/api/v1/internal/boredom_monitor/queue_status")
    async def queue_status_endpoint():
        """API endpoint that JavaScript polls to check for pending injections"""
        return JSONResponse(content=get_queue_status())

    @app.post("/api/v1/internal/boredom_monitor/browser_verification")
    async def browser_verification_endpoint(request: Request):
        """
        API endpoint for browser JavaScript to report found test messages.
        Called by browser_verification.js when it detects [INJECTION-TEST] messages.
        """
        try:
            report = await request.json()
            success = add_browser_verification_report(report)
            return JSONResponse(content={
                'success': success,
                'report_count': len(browser_verification_reports)
            })
        except Exception as e:
            return JSONResponse(
                content={'success': False, 'error': str(e)},
                status_code=400
            )

    @app.get("/api/v1/internal/boredom_monitor/browser_verification")
    async def get_browser_verifications():
        """Get all browser verification reports"""
        return JSONResponse(content={
            'reports': get_browser_verification_reports(),
            'count': len(browser_verification_reports)
        })

    @app.delete("/api/v1/internal/boredom_monitor/browser_verification")
    async def clear_browser_verifications():
        """Clear all browser verification reports"""
        clear_browser_verification_reports()
        return JSONResponse(content={'success': True, 'message': 'Reports cleared'})

    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{timestamp} [INJECTION-BRIDGE] API endpoints registered:")
    print(f"  - GET  /api/v1/internal/boredom_monitor/queue_status")
    print(f"  - POST /api/v1/internal/boredom_monitor/browser_verification")
    print(f"  - GET  /api/v1/internal/boredom_monitor/browser_verification")
    print(f"  - DELETE /api/v1/internal/boredom_monitor/browser_verification")
