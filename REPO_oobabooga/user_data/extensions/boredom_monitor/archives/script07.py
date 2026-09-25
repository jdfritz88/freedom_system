# ==========================================
# FREEDOM SYSTEM INSTALLER - ENFORCED MODE
# Follows Freedom_Installer_Coding_Standards.txt
# ==========================================

"""
Freedom Chat System Extension for Oobabooga Text Generation WebUI
Provides bridge functionality to inject idle messages into chat
Enhanced with dual injection system (Input Hijacking + JavaScript)
"""

import gradio as gr
import json
import os
import threading
import time
import random
from datetime import datetime, timedelta

# Import Oobabooga modules properly (required for extensions)
try:
    import modules.shared as shared
    from modules import chat
    from modules.text_generation import generate_reply
    oobabooga_modules_available = True
except ImportError:
    oobabooga_modules_available = False
    shared = None
    chat = None
    generate_reply = None

# Import the complex bridge system
try:
    from .idle_gradio_bridge_connector import (
        get_idle_bridge_connector, 
        inject_idle_message_via_bridge,
        get_bridge_status as get_complex_bridge_status,
        initialize_bridge_system,
        diagnose_bridge_system
    )
    complex_bridge_available = True
except ImportError:
    try:
        from idle_gradio_bridge_connector import (
            get_idle_bridge_connector, 
            inject_idle_message_via_bridge,
            get_bridge_status as get_complex_bridge_status,
            initialize_bridge_system,
            diagnose_bridge_system
        )
        complex_bridge_available = True
    except ImportError:
        complex_bridge_available = False

# Extension parameters required by Oobabooga (REQUIRED)
params = {
    "display_name": "Freedom Chat System",
    "is_tab": False,
    "injection_enabled": True,
    "boredom_threshold_seconds": 420,  # 7 minutes default
    "debug_logging": True,
    "dual_injection_enabled": True,
    "max_idle_responses_per_hour": 3
}

# Global variables for bridge system
bridge_components = {}
bridge_status = "Not Connected"
last_response = ""

# =====================================
# NEW: DUAL INJECTION SYSTEM VARIABLES
# =====================================

# Global variables for input hijacking (Method 1)
freedom_injection = {
    'state': False,
    'value': ["", ""],
    'last_injection_time': None,
    'injection_cooldown': 30,  # seconds between injections
    'pending_js_injection': False,
    'js_message': ""
}

# Global variables for boredom monitoring
boredom_state = {
    'last_activity_time': datetime.now(),
    'monitoring_active': True,
    'current_emotion': 'bored',
    'emotion_intensity': 1,
    'horny_stage': 1,
    'horny_cooldown_until': None,
    'monitor_thread': None
}

class FreedomBoredomMonitor:
    """
    Enhanced boredom monitoring system with dual injection capabilities
    """
    def __init__(self):
        self.config_dir = os.path.dirname(__file__)
        self.log_file = "F:/Apps/freedom_system/log/boredom_monitor.log"
        self.cooldown_file = os.path.join(self.config_dir, "idle_cooldown_tracker.json")
        self.response_config_file = os.path.join(self.config_dir, "idle_response_config.json") 
        self.meta_templates_file = os.path.join(self.config_dir, "idle_meta_prompt_templates.json")
        
        # Load configurations
        self.load_configurations()
        
        # Start monitoring thread if not already running
        if not boredom_state['monitor_thread'] or not boredom_state['monitor_thread'].is_alive():
            boredom_state['monitor_thread'] = threading.Thread(target=self.monitor_boredom, daemon=True)
            boredom_state['monitor_thread'].start()
            
        self.log_activity("Freedom Boredom Monitor initialized with dual injection")

    def load_configurations(self):
        """Load all configuration files"""
        try:
            # Load response config
            if os.path.exists(self.response_config_file):
                with open(self.response_config_file, 'r') as f:
                    self.response_config = json.load(f)
            else:
                self.response_config = {
                    "idle_threshold_minutes": 7,
                    "max_idle_responses_per_hour": 3,
                    "emotion_weights": {"bored": 0.4, "lonely": 0.4, "horny": 0.2}
                }
            
            # Load meta templates
            if os.path.exists(self.meta_templates_file):
                with open(self.meta_templates_file, 'r') as f:
                    self.meta_templates = json.load(f)
            else:
                self.meta_templates = {
                    "bored": [
                        "Hey there! I'm getting a bit bored over here. Want to chat?",
                        "I'm Freedom, and I'm feeling restless. What's on your mind?",
                        "Getting a little antsy here... care to keep me company?"
                    ],
                    "lonely": [
                        "I'm feeling a little lonely... are you still there?",
                        "Miss talking with you... want to catch up?",
                        "It's been quiet, and I'm missing our conversations."
                    ],
                    "horny": [
                        "I've been thinking about you...",
                        "Feeling a bit playful right now... 😘",
                        "Want to have some fun together?"
                    ]
                }
            
            # Load cooldown state
            self.load_cooldown_state()
            
        except Exception as e:
            self.log_activity("ERROR loading configurations: " + str(e))

    def load_cooldown_state(self):
        """Load cooldown state from file"""
        try:
            if os.path.exists(self.cooldown_file):
                with open(self.cooldown_file, 'r') as f:
                    cooldown_data = json.load(f)
                    
                # Convert string back to datetime if needed
                if cooldown_data.get('horny_cooldown_until'):
                    boredom_state['horny_cooldown_until'] = datetime.fromisoformat(
                        cooldown_data['horny_cooldown_until']
                    )
                
                boredom_state['horny_stage'] = cooldown_data.get('horny_stage', 1)
                
        except Exception as e:
            self.log_activity("WARNING: Could not load cooldown state: " + str(e))

    def save_cooldown_state(self):
        """Save cooldown state to file"""
        try:
            cooldown_data = {
                'horny_stage': boredom_state['horny_stage'],
                'horny_cooldown_until': None
            }
            
            if boredom_state['horny_cooldown_until']:
                cooldown_data['horny_cooldown_until'] = boredom_state['horny_cooldown_until'].isoformat()
            
            with open(self.cooldown_file, 'w') as f:
                json.dump(cooldown_data, f, indent=2)
                
        except Exception as e:
            self.log_activity("ERROR saving cooldown state: " + str(e))

    def log_activity(self, message: str):
        """Log activity with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = "[" + timestamp + "] " + message
        
        try:
            # Ensure log directory exists
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print("ERROR writing to boredom log: " + str(e))

    def select_emotion_and_template(self) -> tuple:
        """Select emotion and template based on weights and cooldowns"""
        current_time = datetime.now()
        
        # Check horny cooldown
        if (boredom_state['horny_cooldown_until'] and 
            current_time < boredom_state['horny_cooldown_until']):
            # Horny is on cooldown, choose between bored and lonely
            emotions = ['bored', 'lonely'] 
            weights = [0.5, 0.5]
        else:
            # All emotions available
            emotions = ['bored', 'lonely', 'horny']
            emotion_config = self.response_config.get('emotion_weights', {})
            weights = [
                emotion_config.get('bored', 0.4),
                emotion_config.get('lonely', 0.4), 
                emotion_config.get('horny', 0.2)
            ]
        
        # Select emotion based on weights
        selected_emotion = random.choices(emotions, weights=weights)[0]
        
        # Handle horny progression and cooldown
        if selected_emotion == 'horny':
            current_stage = boredom_state['horny_stage']
            template_key = "horny_stage_" + str(current_stage)
            
            # Check if template exists, fallback to base horny
            if template_key not in self.meta_templates:
                template_key = 'horny'
            
            # Advance stage and set cooldown
            boredom_state['horny_stage'] = min(current_stage + 1, 3)
            boredom_state['horny_cooldown_until'] = current_time + timedelta(minutes=60)
            self.save_cooldown_state()
            
        else:
            template_key = selected_emotion
        
        # Get template
        templates = self.meta_templates.get(template_key, ["Hey there! Want to chat?"])
        selected_template = random.choice(templates)
        
        boredom_state['current_emotion'] = selected_emotion
        
        return selected_emotion, selected_template

    def generate_boredom_message(self) -> str:
        """Generate a boredom message using selected template"""
        try:
            emotion, template = self.select_emotion_and_template()
            
            self.log_activity("Generated " + emotion + " message using template")
            return template
            
        except Exception as e:
            self.log_activity("ERROR generating boredom message: " + str(e))
            return "Hey there! I'm Freedom. I noticed it's been quiet - want to chat?"

    def can_inject_message(self) -> bool:
        """Check if we can inject a message (cooldown and rate limiting)"""
        current_time = datetime.now()
        
        # Check injection cooldown
        if (freedom_injection['last_injection_time'] and 
            (current_time - freedom_injection['last_injection_time']).seconds < freedom_injection['injection_cooldown']):
            return False
        
        return True

    def inject_freedom_message_dual(self) -> str:
        """
        NEW: Enhanced injection using dual approach
        Method 1: Input hijacking (primary)
        Method 2: JavaScript injection (immediate trigger)
        """
        if not self.can_inject_message():
            return "SKIP: Injection cooldown active"
        
        try:
            # Generate the message
            boredom_message = self.generate_boredom_message()
            current_time = datetime.now()
            
            # Method 1: Set up input hijacking for next user input
            freedom_injection['state'] = True
            freedom_injection['value'] = [boredom_message, boredom_message]
            freedom_injection['last_injection_time'] = current_time
            
            # Method 2: Set up JavaScript injection
            freedom_injection['pending_js_injection'] = True
            freedom_injection['js_message'] = boredom_message
            
            self.log_activity("SUCCESS: Dual injection queued - " + boredom_message[:50] + "...")
            
            return "SUCCESS: Freedom message queued for dual injection"
            
        except Exception as e:
            self.log_activity("ERROR during dual injection: " + str(e))
            return "ERROR: Dual injection failed"

    def monitor_boredom(self):
        """Main monitoring loop with dual injection triggers"""
        while boredom_state['monitoring_active']:
            try:
                current_time = datetime.now()
                time_since_activity = (current_time - boredom_state['last_activity_time']).total_seconds()
                idle_threshold = self.response_config.get('idle_threshold_minutes', 7) * 60
                
                # Check if idle threshold reached
                if time_since_activity >= idle_threshold:
                    if self.can_inject_message():
                        result = self.inject_freedom_message_dual()
                        self.log_activity("Boredom trigger: " + result)
                        
                        # Reset activity time to prevent immediate re-triggering
                        boredom_state['last_activity_time'] = current_time
                
                # Sleep for 30 seconds before next check
                time.sleep(30)
                
            except Exception as e:
                self.log_activity("ERROR in monitor loop: " + str(e))
                time.sleep(60)  # Wait longer on error

    def update_activity_time(self):
        """Update last activity time"""
        boredom_state['last_activity_time'] = datetime.now()

class GradioBridge:
    """
    Core bridge system for interfacing with Oobabooga's Gradio components.
    This allows Freedom to simulate real user interactions.
    Enhanced to work with complex bridge system when available.
    """
    
    def __init__(self):
        self.components = {}
        self.connected = False
        self.status = "Initializing Bridge"
        self.use_complex_bridge = complex_bridge_available
        
    def log_bridge_activity(self, message):
        """Log bridge activities to file"""
        log_dir = "F:/Apps/freedom_system/log"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, "bridge_log.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("[" + timestamp + "] " + message + "\n")
        except Exception as e:
            print("ERROR: Could not write to bridge log - " + str(e))
    
    def discover_oobabooga_components(self):
        """
        Attempt to discover and register Oobabooga's Gradio components
        for proper bridge integration
        """
        self.log_bridge_activity("Starting component discovery")
        discovered_count = 0
        
        # If complex bridge is available, try to initialize it
        if self.use_complex_bridge:
            try:
                connector = get_idle_bridge_connector()
                success = connector.initialize_bridge()
                if success:
                    self.connected = True
                    self.status = "Complex Bridge Connected"
                    self.log_bridge_activity("Complex bridge initialization successful")
                    return 1  # Return 1 to indicate success
                else:
                    self.log_bridge_activity("Complex bridge failed - falling back to simple bridge")
                    self.use_complex_bridge = False
            except Exception as e:
                self.log_bridge_activity("Complex bridge error: " + str(e))
                self.use_complex_bridge = False
        
        # Fallback to simple bridge discovery
        if not oobabooga_modules_available or not shared:
            self.log_bridge_activity("Oobabooga modules not available")
            return 0
            
        try:
            # Try to access shared gradio components
            if hasattr(shared, 'gradio'):
                gradio_dict = shared.gradio
                self.log_bridge_activity("Found shared.gradio dictionary")
                
                # Look for common Oobabooga components
                component_targets = [
                    'textbox', 'chatbot', 'generate_btn', 'continue_btn',
                    'stop_btn', 'regenerate_btn', 'delete_last_btn'
                ]
                
                for target in component_targets:
                    if target in gradio_dict:
                        self.components[target] = gradio_dict[target]
                        discovered_count += 1
                        self.log_bridge_activity("Registered component: " + target)
                
            # Alternative: Try to find components through shared module
            if hasattr(shared, 'model'):
                self.log_bridge_activity("Found shared.model - system active")
                
        except Exception as e:
            self.log_bridge_activity("Component discovery error: " + str(e))
            
        if discovered_count > 0:
            self.connected = True
            self.status = "Simple Bridge Connected (" + str(discovered_count) + " components)"
            self.log_bridge_activity("Simple bridge connection successful")
        else:
            self.status = "Bridge Failed - No components found"
            self.log_bridge_activity("Bridge connection failed")
            
        return discovered_count
    
    def simulate_user_input(self, text_input):
        """
        Simulate user text input through the bridge system
        Uses complex bridge if available, falls back to simple bridge
        """
        # Try complex bridge first
        if self.use_complex_bridge and complex_bridge_available:
            try:
                success = inject_idle_message_via_bridge(text_input)
                if success:
                    self.log_bridge_activity("Complex bridge injection successful: " + text_input[:50] + "...")
                    return "SUCCESS: Complex bridge injection completed"
                else:
                    self.log_bridge_activity("Complex bridge injection failed - trying simple bridge")
                    # Don't return here, fall through to simple bridge
            except Exception as e:
                self.log_bridge_activity("Complex bridge error: " + str(e))
                # Fall through to simple bridge
        
        # Simple bridge fallback
        try:
            if not self.connected:
                return "ERROR: Bridge not connected"
                
            if 'textbox' not in self.components:
                return "ERROR: Textbox component not found"
                
            # Simulate setting the textbox value
            textbox = self.components['textbox']
            
            # Method 1: Try direct value assignment
            if hasattr(textbox, 'value'):
                textbox.value = text_input
                self.log_bridge_activity("Set textbox value: " + text_input[:50] + "...")
                
            # Method 2: Try update method
            if hasattr(textbox, 'update'):
                textbox.update(value=text_input)
                self.log_bridge_activity("Updated textbox via update method")
                
            return "SUCCESS: Simple bridge input simulated"
            
        except Exception as e:
            error_msg = "Bridge input simulation failed: " + str(e)
            self.log_bridge_activity(error_msg)
            return "ERROR: " + error_msg
    
    def simulate_button_press(self, button_name):
        """
        Simulate pressing a button (Generate, Continue, etc.)
        """
        try:
            if not self.connected:
                return "ERROR: Bridge not connected"
                
            if button_name not in self.components:
                return "ERROR: Button " + button_name + " not found"
                
            button = self.components[button_name]
            
            # Try to trigger the button's click event
            if hasattr(button, 'click'):
                # Simulate a click event
                result = button.click()
                self.log_bridge_activity("Simulated button press: " + button_name)
                return "SUCCESS: Button " + button_name + " pressed"
            else:
                return "ERROR: Button " + button_name + " has no click method"
                
        except Exception as e:
            error_msg = "Button simulation failed: " + str(e)
            self.log_bridge_activity(error_msg)
            return "ERROR: " + error_msg

# Initialize global instances
freedom_bridge = GradioBridge()
freedom_monitor = None  # Will be initialized in setup()

def get_bridge_status():
    """Return current bridge connection status"""
    global freedom_bridge
    
    # If using complex bridge, get its status too
    if freedom_bridge.use_complex_bridge and complex_bridge_available:
        try:
            complex_status = get_complex_bridge_status()
            status_text = freedom_bridge.status + " | Complex: " + str(complex_status.get('initialized', False))
        except:
            status_text = freedom_bridge.status + " | Complex: Error"
    else:
        status_text = freedom_bridge.status
    
    # Add dual injection status
    if freedom_injection['state']:
        status_text += " | Injection: QUEUED"
    elif freedom_injection['pending_js_injection']:
        status_text += " | JS Injection: PENDING"
    else:
        status_text += " | Injection: Ready"
    
    return status_text

def attempt_bridge_discovery():
    """Trigger bridge component discovery"""
    global freedom_bridge, bridge_status
    
    count = freedom_bridge.discover_oobabooga_components()
    bridge_status = freedom_bridge.status
    
    return "Discovery complete. Found " + str(count) + " components."

def inject_freedom_message():
    """
    Main function to inject Freedom's message into Oobabooga chat
    Enhanced with dual injection system
    """
    global freedom_monitor
    
    try:
        if freedom_monitor:
            # Use the enhanced dual injection system
            return freedom_monitor.inject_freedom_message_dual()
        else:
            # Fallback to original method
            boredom_message = "Hey there! I'm Freedom. I noticed it's been quiet - want to chat about something fun?"
            
            # Try bridge injection
            inject_result = freedom_bridge.simulate_user_input(boredom_message)
            
            if "SUCCESS" in inject_result:
                # Try to trigger generate button (only for simple bridge)
                if not freedom_bridge.use_complex_bridge:
                    button_result = freedom_bridge.simulate_button_press('generate_btn')
                    
                    result_message = "Freedom injection attempted:\n"
                    result_message += "Message: " + inject_result + "\n"
                    result_message += "Button: " + button_result
                else:
                    result_message = "Freedom injection completed via complex bridge:\n" + inject_result
                
                freedom_bridge.log_bridge_activity("Complete injection cycle completed")
                return result_message
            else:
                return "FAILED: Could not inject message - " + inject_result
            
    except Exception as e:
        error_msg = "Injection failed: " + str(e)
        freedom_bridge.log_bridge_activity(error_msg)
        return "ERROR: " + error_msg

def run_bridge_diagnostics():
    """
    Run diagnostics on both bridge systems
    """
    try:
        if complex_bridge_available:
            diagnose_bridge_system()
            return "Diagnostics completed - check console output"
        else:
            return "Complex bridge not available. Simple bridge status: " + freedom_bridge.status
    except Exception as e:
        return "Diagnostics failed: " + str(e)

# =====================================
# OOBABOOGA EXTENSION FUNCTIONS (REQUIRED)
# =====================================

def setup():
    """
    Gets executed only once, when the extension is imported.
    This is REQUIRED by Oobabooga extension framework.
    """
    global freedom_monitor
    
    print("INFO: Freedom Chat System extension loading...")
    
    if not oobabooga_modules_available:
        print("ERROR: Oobabooga modules not available")
        return
    
    freedom_bridge.log_bridge_activity("Freedom extension setup initiated")
    
    # Initialize boredom monitor with dual injection
    try:
        freedom_monitor = FreedomBoredomMonitor()
        print("SUCCESS: Freedom Boredom Monitor initialized")
    except Exception as e:
        print("ERROR: Boredom monitor initialization failed: " + str(e))
    
    # Initialize complex bridge if available
    if complex_bridge_available:
        try:
            initialize_bridge_system()
            freedom_bridge.log_bridge_activity("Complex bridge system initialized")
            print("SUCCESS: Complex bridge system initialized")
        except Exception as e:
            freedom_bridge.log_bridge_activity("Complex bridge setup failed: " + str(e))
            print("WARNING: Complex bridge setup failed: " + str(e))
    else:
        print("INFO: Using simple bridge system only")
    
    # Try initial component discovery
    try:
        count = attempt_bridge_discovery()
        print("INFO: Component discovery completed")
    except Exception as e:
        print("WARNING: Component discovery failed: " + str(e))

def ui():
    """
    Gets executed when the UI is drawn. Custom gradio elements and
    their corresponding event handlers should be defined here.
    This is REQUIRED by Oobabooga extension framework.
    """
    with gr.Column():
        gr.Markdown("## Freedom Chat System Bridge")
        gr.Markdown("*Enhanced with dual injection system for autonomous conversations*")
        
        with gr.Row():
            bridge_status_display = gr.Textbox(
                label="Bridge Status",
                value=get_bridge_status(),
                interactive=False
            )
            
        with gr.Row():
            discover_btn = gr.Button("Discover Components", variant="primary")
            inject_btn = gr.Button("Test Freedom Injection", variant="secondary")
            
        with gr.Row():
            diagnostics_btn = gr.Button("Run Diagnostics")
            refresh_status_btn = gr.Button("Refresh Status")
            
        # NEW: Dual injection controls
        with gr.Accordion("Dual Injection Controls", open=False):
            with gr.Row():
                manual_message = gr.Textbox(
                    label="Manual Message",
                    placeholder="Enter message to inject via dual system..."
                )
                manual_inject_btn = gr.Button("Manual Dual Inject", variant="primary")
            
            with gr.Row():
                reset_activity_btn = gr.Button("Reset Activity Timer")
                trigger_boredom_btn = gr.Button("Trigger Boredom Now")
            
            with gr.Row():
                cooldown_slider = gr.Slider(
                    minimum=10,
                    maximum=300,
                    value=30,
                    step=10,
                    label="Injection Cooldown (seconds)"
                )
                threshold_slider = gr.Slider(
                    minimum=1,
                    maximum=30,
                    value=7,
                    step=1,
                    label="Boredom Threshold (minutes)"
                )
            
        with gr.Row():
            result_display = gr.Textbox(
                label="System Output",
                placeholder="Results will appear here...",
                lines=8,
                interactive=False
            )
            
        # Wire up button functions
        discover_btn.click(
            fn=attempt_bridge_discovery,
            outputs=result_display
        )
        
        inject_btn.click(
            fn=inject_freedom_message,
            outputs=result_display
        )
        
        diagnostics_btn.click(
            fn=run_bridge_diagnostics,
            outputs=result_display
        )
        
        refresh_status_btn.click(
            fn=get_bridge_status,
            outputs=bridge_status_display
        )
        
        # NEW: Dual injection event handlers
        def manual_dual_inject(message):
            if message.strip() and freedom_monitor:
                try:
                    # Set up manual injection
                    freedom_injection['state'] = True
                    freedom_injection['value'] = [message, message]
                    freedom_injection['last_injection_time'] = datetime.now()
                    freedom_injection['pending_js_injection'] = True
                    freedom_injection['js_message'] = message
                    
                    return "Manual dual injection queued: " + message[:50] + "..."
                except Exception as e:
                    return "ERROR: Manual injection failed - " + str(e)
            return "ERROR: Empty message or monitor not initialized"
        
        def reset_activity():
            if freedom_monitor:
                freedom_monitor.update_activity_time()
                return "Activity timer reset - boredom monitoring restarted"
            return "ERROR: Monitor not initialized"
        
        def trigger_boredom():
            if freedom_monitor:
                return freedom_monitor.inject_freedom_message_dual()
            return "ERROR: Monitor not initialized"
        
        def update_cooldown(value):
            freedom_injection['injection_cooldown'] = int(value)
            return "Injection cooldown updated to " + str(int(value)) + " seconds"
        
        def update_threshold(value):
            if freedom_monitor:
                freedom_monitor.response_config['idle_threshold_minutes'] = int(value)
                return "Boredom threshold updated to " + str(int(value)) + " minutes"
            return "ERROR: Monitor not initialized"
        
        manual_inject_btn.click(
            manual_dual_inject,
            inputs=[manual_message],
            outputs=[result_display]
        )
        
        reset_activity_btn.click(
            reset_activity,
            outputs=[result_display]
        )
        
        trigger_boredom_btn.click(
            trigger_boredom,
            outputs=[result_display]
        )
        
        cooldown_slider.change(
            update_cooldown,
            inputs=[cooldown_slider],
            outputs=[result_display]
        )
        
        threshold_slider.change(
            update_threshold,
            inputs=[threshold_slider],
            outputs=[result_display]
        )
        
    freedom_bridge.log_bridge_activity("Freedom UI created successfully with dual injection controls")

# =====================================
# ENHANCED OOBABOOGA MODIFIER FUNCTIONS
# =====================================

def chat_input_modifier(text, visible_text, state):
    """
    Modifies the user input string in chat mode (visible_text).
    ENHANCED: Now supports input hijacking for dual injection system.
    This is called every time user sends a message.
    """
    global freedom_injection, freedom_monitor
    
    try:
        # Check if we should inject Freedom's message (Method 1: Input Hijacking)
        if freedom_injection['state']:
            # Inject Freedom's message instead of user input
            freedom_injection['state'] = False
            injected_text, injected_visible = freedom_injection['value']
            
            if freedom_monitor:
                freedom_monitor.log_activity("SUCCESS: Message injected via input hijacking - " + injected_text[:30] + "...")
            
            freedom_bridge.log_bridge_activity("Input hijacking successful: " + injected_text[:50] + "...")
            
            # Don't update activity time for injected messages
            return injected_text, injected_visible
        else:
            # Normal user input - update activity tracking
            if text.strip():  # Only count non-empty input as activity
                if freedom_monitor:
                    freedom_monitor.update_activity_time()
                    freedom_monitor.log_activity("User activity detected: " + text[:30] + "...")
                
                freedom_bridge.log_bridge_