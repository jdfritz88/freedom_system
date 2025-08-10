# ==========================================
# FREEDOM SYSTEM INSTALLER - ENFORCED MODE
# Follows Freedom_Installer_Coding_Standards.txt
# ==========================================

import os
import sys
import json
import time
import threading
import requests
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Add the extension path to sys.path for imports
extension_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, extension_path)

# Import the boredom system
from idle_boredom_system import FreedomBoredomSystem

# Global variables for injection system
freedom_injection = {
    'state': False,
    'value': ["", ""],
    'pending_js': False,
    'js_message': ""
}

# Initialize the boredom system
freedom_boredom = None
extension_initialized = False

def initialize_extension():
    """Initialize the Freedom extension system"""
    global freedom_boredom, extension_initialized
    
    try:
        if not extension_initialized:
            print("INFO: Freedom Chat System extension loading...")
            
            # Initialize boredom system
            freedom_boredom = FreedomBoredomSystem(extension_path)
            
            # Start monitoring
            freedom_boredom.start_monitoring()
            
            extension_initialized = True
            print("SUCCESS: Freedom Boredom Monitor initialized")
            
            # Log initialization
            freedom_boredom.log_event("EXTENSION_INIT", "Freedom extension initialized successfully")
            
    except Exception as e:
        print("ERROR: Failed to initialize Freedom extension - " + str(e))
        if freedom_boredom:
            freedom_boredom.log_event("INIT_ERROR", "Extension initialization failed - " + str(e))

def chat_input_modifier(text, visible_text, state):
    """
    Oobabooga extension hook - Method 1: Input Hijacking Pattern
    This function is called automatically by Oobabooga for every user input
    """
    global freedom_injection, freedom_boredom
    
    # Initialize if needed
    if not extension_initialized:
        initialize_extension()
    
    # Check for Freedom injection
    if freedom_injection['state']:
        # Inject Freedom's message instead of user input
        freedom_injection['state'] = False
        injected_message = freedom_injection['value']
        
        if freedom_boredom:
            freedom_boredom.log_event("INPUT_HIJACK", "Message injected via input hijacking: " + str(injected_message[0]))
        
        print("SUCCESS: Freedom message injected via input hijacking")
        return injected_message
    
    else:
        # Normal user input - update activity tracker
        if freedom_boredom:
            freedom_boredom.update_activity()
        
        # Pass through normal input unchanged
        return text, visible_text

def output_modifier(string, state):
    """
    Oobabooga extension hook - modify AI output if needed
    """
    global freedom_boredom
    
    # Log AI response activity
    if freedom_boredom:
        freedom_boredom.update_activity()
    
    # Pass through unchanged
    return string

def custom_js():
    """
    Method 3: JavaScript DOM Manipulation
    Returns JavaScript code that gets loaded into the Gradio interface
    """
    global freedom_injection
    
    return """
    // Freedom Chat System JavaScript Integration
    console.log('Freedom Chat System extension loaded');
    
    // Global injection function
    window.injectFreedomMessage = function(message) {
        console.log('Freedom: Attempting JavaScript injection - ' + message);
        
        // Try multiple selectors for chat input
        const selectors = [
            'textarea[placeholder*="message"]',
            'textarea[placeholder*="Message"]',
            'textarea[placeholder*="Type"]',
            '#chat-input textarea',
            '.chat-input textarea',
            'textarea[data-testid="textbox"]',
            'textarea'
        ];
        
        let chatInput = null;
        for (let selector of selectors) {
            chatInput = document.querySelector(selector);
            if (chatInput) {
                console.log('Freedom: Found chat input with selector - ' + selector);
                break;
            }
        }
        
        if (chatInput) {
            // Inject the message
            chatInput.value = message;
            chatInput.dispatchEvent(new Event('input', { bubbles: true }));
            chatInput.dispatchEvent(new Event('change', { bubbles: true }));
            
            console.log('Freedom: Message injected successfully');
            
            // Try to find and click submit button
            setTimeout(() => {
                const submitSelectors = [
                    'button[type="submit"]',
                    'button[aria-label*="Submit"]',
                    'button[aria-label*="Send"]',
                    '.send-button',
                    '#submit-button',
                    'button:contains("Send")',
                    'button:contains("Submit")'
                ];
                
                let submitBtn = null;
                for (let selector of submitSelectors) {
                    submitBtn = document.querySelector(selector);
                    if (submitBtn && !submitBtn.disabled) {
                        console.log('Freedom: Found submit button with selector - ' + selector);
                        break;
                    }
                }
                
                if (submitBtn && !submitBtn.disabled) {
                    submitBtn.click();
                    console.log('Freedom: Auto-submitted message');
                } else {
                    console.log('Freedom: Submit button not found or disabled');
                }
            }, 200);
            
            return true;
        } else {
            console.log('Freedom: Chat input not found - injection failed');
            return false;
        }
    };
    
    // Auto-check for pending JavaScript injections
    setInterval(() => {
        if (window.freedomJsPending) {
            const message = window.freedomJsMessage || 'Freedom says hello!';
            if (window.injectFreedomMessage(message)) {
                window.freedomJsPending = false;
                window.freedomJsMessage = '';
                console.log('Freedom: Pending JavaScript injection completed');
            }
        }
    }, 1000);
    
    // Activity detection
    document.addEventListener('keydown', () => {
        window.freedomLastActivity = Date.now();
    });
    
    document.addEventListener('click', () => {
        window.freedomLastActivity = Date.now();
    });
    
    // Initialize activity timestamp
    window.freedomLastActivity = Date.now();
    
    console.log('Freedom: JavaScript system initialized');
    """

def inject_freedom_message_dual(message: str) -> str:
    """
    Dual injection system - uses both Method 1 and Method 3
    """
    global freedom_injection, freedom_boredom
    
    try:
        if freedom_boredom:
            freedom_boredom.log_event("DUAL_INJECT_START", "Attempting dual injection: " + message)
        
        # Method 1: Set up input hijacking for next user input
        freedom_injection['state'] = True
        freedom_injection['value'] = [message, message]
        
        # Method 3: Trigger JavaScript injection immediately
        js_injection_code = """
        setTimeout(() => {
            window.freedomJsPending = true;
            window.freedomJsMessage = '""" + message.replace("'", "\\'").replace('"', '\\"') + """';
            
            // Try immediate injection
            if (window.injectFreedomMessage) {
                const success = window.injectFreedomMessage(window.freedomJsMessage);
                if (success) {
                    window.freedomJsPending = false;
                    window.freedomJsMessage = '';
                    console.log('Freedom: Immediate JavaScript injection successful');
                }
            }
        }, 500);
        """
        
        # Store JavaScript for execution
        freedom_injection['pending_js'] = True
        freedom_injection['js_message'] = message
        
        if freedom_boredom:
            freedom_boredom.log_event("DUAL_INJECT", "SUCCESS - Dual injection prepared (hijack + JS)")
        
        return "SUCCESS: Dual injection system activated for message: " + message
        
    except Exception as e:
        error_msg = "Dual injection failed - " + str(e)
        if freedom_boredom:
            freedom_boredom.log_event("DUAL_INJECT_ERROR", error_msg)
        return "ERROR: " + error_msg

def inject_freedom_message_hijack_only(message: str) -> str:
    """
    Method 1 only: Input hijacking injection
    """
    global freedom_injection, freedom_boredom
    
    try:
        freedom_injection['state'] = True
        freedom_injection['value'] = [message, message]
        
        if freedom_boredom:
            freedom_boredom.log_event("HIJACK_INJECT", "Input hijacking prepared: " + message)
        
        return "SUCCESS: Input hijacking prepared for message: " + message
        
    except Exception as e:
        error_msg = "Input hijacking failed - " + str(e)
        if freedom_boredom:
            freedom_boredom.log_event("HIJACK_ERROR", error_msg)
        return "ERROR: " + error_msg

def inject_freedom_message_js_only(message: str) -> str:
    """
    Method 3 only: JavaScript injection
    """
    global freedom_injection, freedom_boredom
    
    try:
        freedom_injection['pending_js'] = True
        freedom_injection['js_message'] = message
        
        if freedom_boredom:
            freedom_boredom.log_event("JS_INJECT", "JavaScript injection prepared: " + message)
        
        return "SUCCESS: JavaScript injection prepared for message: " + message
        
    except Exception as e:
        error_msg = "JavaScript injection failed - " + str(e)
        if freedom_boredom:
            freedom_boredom.log_event("JS_ERROR", error_msg)
        return "ERROR: " + error_msg

def get_freedom_status() -> Dict:
    """Get current Freedom system status"""
    global freedom_boredom, freedom_injection, extension_initialized
    
    status = {
        "extension_initialized": extension_initialized,
        "injection_ready": freedom_injection['state'],
        "js_pending": freedom_injection['pending_js'],
        "boredom_system": None
    }
    
    if freedom_boredom:
        status["boredom_system"] = freedom_boredom.get_status()
    
    return status

def manual_trigger_boredom() -> str:
    """Manually trigger boredom response for testing"""
    global freedom_boredom
    
    if not freedom_boredom:
        return "ERROR: Boredom system not initialized"
    
    try:
        # Get a random template
        template = freedom_boredom.get_random_template()
        
        # Use dual injection
        result = inject_freedom_message_dual(template)
        
        freedom_boredom.log_event("MANUAL_TRIGGER", "Manual boredom trigger executed: " + template)
        
        return "SUCCESS: Manual boredom response triggered - " + result
        
    except Exception as e:
        error_msg = "Manual trigger failed - " + str(e)
        if freedom_boredom:
            freedom_boredom.log_event("MANUAL_ERROR", error_msg)
        return "ERROR: " + error_msg

def update_freedom_config(config_updates: Dict) -> str:
    """Update Freedom system configuration"""
    global freedom_boredom
    
    if not freedom_boredom:
        return "ERROR: Boredom system not initialized"
    
    try:
        freedom_boredom.update_config(config_updates)
        return "SUCCESS: Freedom configuration updated"
        
    except Exception as e:
        return "ERROR: Configuration update failed - " + str(e)

def add_freedom_template(template: str) -> str:
    """Add new meta prompt template"""
    global freedom_boredom
    
    if not freedom_boredom:
        return "ERROR: Boredom system not initialized"
    
    try:
        freedom_boredom.add_template(template)
        return "SUCCESS: Template added to Freedom system"
        
    except Exception as e:
        return "ERROR: Template addition failed - " + str(e)

def test_freedom_endpoints() -> Dict:
    """Test all Freedom system endpoints"""
    global freedom_boredom
    
    if not freedom_boredom:
        return {"error": "Boredom system not initialized"}
    
    try:
        return freedom_boredom.test_endpoints()
        
    except Exception as e:
        return {"error": "Endpoint test failed - " + str(e)}

def reset_freedom_tracker() -> str:
    """Reset Freedom activity tracker"""
    global freedom_boredom
    
    if not freedom_boredom:
        return "ERROR: Boredom system not initialized"
    
    try:
        freedom_boredom.reset_tracker()
        return "SUCCESS: Freedom tracker reset"
        
    except Exception as e:
        return "ERROR: Tracker reset failed - " + str(e)

def stop_freedom_monitoring() -> str:
    """Stop Freedom monitoring system"""
    global freedom_boredom
    
    if not freedom_boredom:
        return "ERROR: Boredom system not initialized"
    
    try:
        freedom_boredom.stop_monitoring()
        return "SUCCESS: Freedom monitoring stopped"
        
    except Exception as e:
        return "ERROR: Stop monitoring failed - " + str(e)

def start_freedom_monitoring() -> str:
    """Start Freedom monitoring system"""
    global freedom_boredom
    
    if not freedom_boredom:
        return "ERROR: Boredom system not initialized"
    
    try:
        freedom_boredom.start_monitoring()
        return "SUCCESS: Freedom monitoring started"
        
    except Exception as e:
        return "ERROR: Start monitoring failed - " + str(e)

# Extension API functions for external access
def freedom_api_status():
    """API endpoint for status check"""
    return get_freedom_status()

def freedom_api_inject(message: str, method: str = "dual"):
    """API endpoint for message injection"""
    if method == "dual":
        return inject_freedom_message_dual(message)
    elif method == "hijack":
        return inject_freedom_message_hijack_only(message)
    elif method == "js":
        return inject_freedom_message_js_only(message)
    else:
        return "ERROR: Invalid injection method. Use 'dual', 'hijack', or 'js'"

def freedom_api_trigger():
    """API endpoint for manual trigger"""
    return manual_trigger_boredom()

def freedom_api_config(updates: Dict):
    """API endpoint for configuration updates"""
    return update_freedom_config(updates)

# Initialize when module is loaded
initialize_extension()

print("INFO: Freedom Chat System extension loaded")
print("SUCCESS: Dual injection system (Input Hijacking + JavaScript) ready")

# Auto-run compatibility check
if extension_initialized and freedom_boredom:
    endpoints = freedom_boredom.test_endpoints()
    print("INFO: Endpoint connectivity test completed")
    for endpoint, status in endpoints.items():
        status_msg = status.get('status', 'unknown')
        print("INFO: " + endpoint + " endpoint - " + status_msg)