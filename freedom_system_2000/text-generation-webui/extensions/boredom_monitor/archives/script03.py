# ==========================================
# OOBABOOGA EXTENSION: BOREDOM MONITOR
# Complete version with all features
# ==========================================

import os
import threading
import time
import json
import random
from pathlib import Path

import gradio as gr
from modules import shared, chat

# Extension metadata - REQUIRED for Oobabooga
params = {
    "display_name": "Boredom Monitor",
    "is_tab": False,
}

# Extension configuration
EXTENSION_DIR = os.path.dirname(__file__)
TRIGGER_CONFIG = os.path.join(EXTENSION_DIR, 'idle_response_config.json')
TEMPLATE_FILE = os.path.join(EXTENSION_DIR, 'idle_meta_prompt_templates.json')
COOLDOWN_TRACKER = os.path.join(EXTENSION_DIR, 'idle_cooldown_tracker.json')
TEMPLATE_LOG = os.path.join(EXTENSION_DIR, 'idle_meta_prompts_log.txt')

# Global state
monitor_thread = None
should_monitor = threading.Event()
last_activity_time = time.time()
console_log = []  # Store console messages for UI display

def log(msg):
    """Logging helper that also stores for UI console"""
    global console_log
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    print(f"[Boredom Monitor] {msg}")
    
    # Add to console log for UI (keep last 100 messages)
    console_log.append(formatted_msg)
    if len(console_log) > 100:
        console_log.pop(0)

def load_json(path, fallback):
    """Load JSON safely with fallback"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return fallback

def save_json(path, data):
    """Save JSON data"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def clear_log_file():
    """Clear the meta prompts log file at startup"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(TEMPLATE_LOG), exist_ok=True)
        
        # Clear the file by writing empty content
        with open(TEMPLATE_LOG, 'w', encoding='utf-8') as f:
            f.write(f"# Boredom Monitor Log - Started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        log("Meta prompts log cleared and initialized")
        return True
    except Exception as e:
        log(f"Error clearing log file: {e}")
        return False

def ensure_config_files():
    """Ensure all config files exist with default values"""
    
    # Default trigger config
    default_trigger_config = {
        "idle_minutes": 7,
        "horny_cooldown_minutes": 60,
        "category_weights": {
            "bored": 0.4,
            "lonely": 0.4,
            "horny": 0.2
        },
        "enable_logging": True
    }
    
    # Default templates
    default_templates = {
        "bored": [
            "Write something Freedom would say if she's bored and wants to be teased.",
            "Freedom is waiting with nothing to do. Write what she says to get my attention."
        ],
        "lonely": [
            "Write a one-sentence emotional message Freedom would send if she felt abandoned.",
            "Freedom hasn't heard from me in a long time. Write a message that sounds intimate and sad."
        ],
        "horny": [
            "Freedom is teasing herself, barely touching. Write a short message that sounds flirty and aroused.",
            "Freedom is getting closer, rubbing harder, panting. Write what she'd say if she needed more.",
            "Freedom is having an orgasm. Write a short, filthy sentence where she moans, says 'I'm cumming', and can't hold back."
        ]
    }
    
    # Default cooldown tracker
    default_cooldown = {
        "horny_stage": 0,
        "in_cooldown": False,
        "cooldown_end_time": 0
    }
    
    # Create files if they don't exist
    if not os.path.exists(TRIGGER_CONFIG):
        save_json(TRIGGER_CONFIG, default_trigger_config)
        log("Created default trigger config")
        
    if not os.path.exists(TEMPLATE_FILE):
        save_json(TEMPLATE_FILE, default_templates)
        log("Created default templates")
        
    if not os.path.exists(COOLDOWN_TRACKER):
        save_json(COOLDOWN_TRACKER, default_cooldown)
        log("Created default cooldown tracker")

def select_template():
    """Select template based on weighted categories and horny stage progression"""
    config = load_json(TRIGGER_CONFIG, {
        "category_weights": {"bored": 0.4, "lonely": 0.4, "horny": 0.2}
    })
    templates = load_json(TEMPLATE_FILE, {})
    cooldown_data = load_json(COOLDOWN_TRACKER, {
        "horny_stage": 0,
        "in_cooldown": False,
        "cooldown_end_time": 0
    })
    
    current_time = time.time()
    
    # Check if we're in cooldown period
    if cooldown_data.get("in_cooldown", False):
        if current_time < cooldown_data.get("cooldown_end_time", 0):
            # Still in cooldown - only allow bored/lonely
            log("In horny cooldown - excluding horny category")
            categories = ["bored", "lonely"]
            weights = [0.5, 0.5]  # Equal weight between bored and lonely
            category = random.choices(categories, weights)[0]
            cooldown_data["horny_stage"] = 0  # Reset stage during cooldown
        else:
            # Cooldown ended - reset to normal selection
            log("Horny cooldown ended - returning to normal selection")
            cooldown_data["in_cooldown"] = False
            cooldown_data["horny_stage"] = 0
            save_json(COOLDOWN_TRACKER, cooldown_data)
            # Fall through to normal selection
    
    # Handle horny stage progression
    current_horny_stage = cooldown_data.get("horny_stage", 0)
    
    if current_horny_stage > 0 and not cooldown_data.get("in_cooldown", False):
        # We're in a horny progression - continue to next stage
        category = "horny"
        next_stage = current_horny_stage + 1
        log(f"Continuing horny progression to stage {next_stage}")
        
        # Check if we've reached the final stage
        if next_stage > 3:
            # Start cooldown after stage 3
            cooldown_minutes = config.get("horny_cooldown_minutes", 60)
            cooldown_data["in_cooldown"] = True
            cooldown_data["cooldown_end_time"] = current_time + (cooldown_minutes * 60)
            cooldown_data["horny_stage"] = 0
            log(f"Completed horny stage 3 - starting {cooldown_minutes} minute cooldown")
            
            # For this iteration, still use stage 3 template
            current_horny_stage = 3
        else:
            cooldown_data["horny_stage"] = next_stage
            current_horny_stage = next_stage
            
        save_json(COOLDOWN_TRACKER, cooldown_data)
        
    elif not cooldown_data.get("in_cooldown", False):
        # Normal random selection (not in progression or cooldown)
        categories = list(config['category_weights'].keys())
        weights = list(config['category_weights'].values())
        category = random.choices(categories, weights)[0]
        
        # If horny is selected, start the progression
        if category == "horny":
            cooldown_data["horny_stage"] = 1
            current_horny_stage = 1
            save_json(COOLDOWN_TRACKER, cooldown_data)
            log("Starting horny progression at stage 1")
    
    # Get the appropriate template
    if category == "horny" and current_horny_stage > 0:
        # Use stage-specific horny templates
        horny_templates = templates.get("horny", [])
        if len(horny_templates) >= current_horny_stage:
            selected = horny_templates[current_horny_stage - 1]  # 0-indexed
            stage_info = f" (Stage {current_horny_stage})"
        else:
            # Fallback if not enough stage templates
            selected = random.choice(horny_templates) if horny_templates else None
            stage_info = f" (Stage {current_horny_stage} - fallback)"
    else:
        # Normal template selection
        options = templates.get(category, [])
        selected = random.choice(options) if options else None
        stage_info = ""
    
    if not selected:
        log(f"No template found for category: {category}")
        return None, None
        
    # Log the selection
    try:
        with open(TEMPLATE_LOG, 'a', encoding='utf-8') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] CATEGORY: {category}{stage_info}\n")
            f.write(f"PROMPT: {selected}\n\n")
    except Exception as e:
        log(f"Error logging template: {e}")
    
    log(f"Selected {category}{stage_info}: {selected[:50]}...")
    return category, selected

def inject_idle_message():
    """Inject an idle message into the chat"""
    try:
        category, template = select_template()
        if not template:
            log("No template available for injection")
            return
            
        log(f"Injecting {category} message: {template[:50]}...")
        
        # Use Oobabooga's chat functionality properly
        try:
            # Import the proper chat functions
            from modules import chat
            from modules.text_generation import generate_reply
            
            # Get the current chat history
            history = chat.history if hasattr(chat, 'history') else {'internal': [], 'visible': []}
            
            # Ensure history has the right structure
            if 'internal' not in history:
                history['internal'] = []
            if 'visible' not in history:
                history['visible'] = []
            
            # Generate the AI response using Oobabooga's generate_reply function
            # This simulates sending the template as user input
            state = shared.persistent_interface_state if hasattr(shared, 'persistent_interface_state') else {}
            
            # Use the standard generation pipeline
            reply = ""
            for response in generate_reply(
                question=template,
                state=state,
                regenerate=False,
                _continue=False,
                loading_message=False
            ):
                reply = response
            
            # Add the exchange to chat history
            # This mimics what happens when user sends a message and gets a reply
            history['internal'].append([template, reply])
            history['visible'].append([template, reply])
            
            # Update the chat history in the shared state
            if hasattr(chat, 'history'):
                chat.history = history
            
            log(f"Successfully injected {category} message into chat")
            log(f"User input: {template}")
            log(f"AI reply: {reply[:100]}..." if len(reply) > 100 else f"AI reply: {reply}")
            
        except Exception as e:
            log(f"Standard injection failed: {e}")
            
            # Fallback: Use the "Send dummy message" and "Send dummy reply" approach
            # This is based on the documentation's mention of these functions
            try:
                # Simulate the dummy message/reply functionality
                history = chat.history if hasattr(chat, 'history') else {'internal': [], 'visible': []}
                
                if 'internal' not in history:
                    history['internal'] = []
                if 'visible' not in history:
                    history['visible'] = []
                
                # Create a simple response for the template
                simple_response = f"*responds to the prompt: {template[:30]}...*"
                
                # Add to history as dummy exchange
                history['internal'].append([template, simple_response])
                history['visible'].append([template, simple_response])
                
                if hasattr(chat, 'history'):
                    chat.history = history
                
                log(f"Fallback injection completed for {category}")
                log(f"Added dummy exchange to chat history")
                
            except Exception as e2:
                log(f"Fallback injection also failed: {e2}")
                log("Message logged but not added to chat")
        
    except Exception as e:
        log(f"Error in inject_idle_message: {e}")
        import traceback
        log(f"Traceback: {traceback.format_exc()}")

def idle_monitor_loop():
    """Background thread to monitor for idle time"""
    global last_activity_time
    
    log("Idle monitor thread started")
    
    while should_monitor.is_set():
        try:
            config = load_json(TRIGGER_CONFIG, {"idle_minutes": 7})
            idle_delay = config.get('idle_minutes', 7) * 60
            
            current_time = time.time()
            if current_time - last_activity_time >= idle_delay:
                log("Idle time detected, preparing injection...")
                inject_idle_message()
                last_activity_time = current_time
                
            time.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            log(f"Error in monitor loop: {e}")
            time.sleep(30)

# Oobabooga Extension Functions

def setup():
    """Called when extension is loaded - REQUIRED"""
    global monitor_thread
    
    log("Setting up Boredom Monitor extension...")
    
    # Clear the log file at startup
    if clear_log_file():
        log("Log file successfully cleared at startup")
    else:
        log("Warning: Could not clear log file")
    
    # Ensure config files exist with defaults
    ensure_config_files()
    
    # Start monitoring thread
    should_monitor.set()
    monitor_thread = threading.Thread(target=idle_monitor_loop, daemon=True)
    monitor_thread.start()
    
    log("Boredom Monitor setup complete - extension ready")

def input_modifier(string, state, is_chat=False):
    """Track user activity when input is processed"""
    global last_activity_time
    last_activity_time = time.time()
    return string

def history_modifier(history):
    """Track activity when history is accessed"""
    global last_activity_time
    last_activity_time = time.time()
    return history

def chat_input_modifier(text, visible_text, state):
    """Track user input in chat mode"""
    global last_activity_time
    last_activity_time = time.time()
    return text, visible_text

def state_modifier(state):
    """Track state changes as activity"""
    global last_activity_time
    last_activity_time = time.time()
    return state

def ui():
    """Create the UI components - will appear below chat window"""
    
    # Update functions (defined first)
    def update_console():
        global console_log
        recent_logs = console_log[-50:] if console_log else ["Extension ready"]
        return "\n".join(recent_logs)
    
    def update_countdown():
        global last_activity_time
        config = load_json(TRIGGER_CONFIG, {})
        idle_minutes = config.get('idle_minutes', 7)
        idle_seconds = idle_minutes * 60
        
        current_time = time.time()
        time_since_activity = current_time - last_activity_time
        time_remaining = max(0, idle_seconds - time_since_activity)
        
        if time_remaining > 0:
            minutes = int(time_remaining // 60)
            seconds = int(time_remaining % 60)
            return f"{minutes}m {seconds}s until idle trigger"
        else:
            return "Idle trigger active"
    
    # Main container with styling similar to Coqui TTS
    with gr.Group():
        gr.Markdown("### Boredom Monitor Extension")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Configuration display
                config = load_json(TRIGGER_CONFIG, {})
                idle_minutes = config.get('idle_minutes', 7)
                cooldown_minutes = config.get('horny_cooldown_minutes', 60)
                
                gr.HTML(f"""
                    <div style="background: #2a2a2a; padding: 10px; border-radius: 6px; border: 1px solid #444;">
                        <div style="margin-bottom: 8px;">
                            <strong style="color: #4a90e2;">Boredom Monitor Configuration:</strong>
                        </div>
                        <div style="font-size: 13px; color: #ccc;">
                            <strong>Idle trigger:</strong> {idle_minutes} minutes | 
                            <strong>Horny cooldown:</strong> {cooldown_minutes} minutes<br>
                            <strong>Status:</strong> {'Active' if should_monitor.is_set() else 'Inactive'}
                        </div>
                    </div>
                """)
                
            with gr.Column(scale=1):
                # Countdown display
                countdown_text = gr.Textbox(
                    value="7m 0s until idle trigger",  # Start with default instead of function call
                    label="Next Idle Check",
                    interactive=False,
                    max_lines=1,
                    elem_id="boredom-countdown"
                )
        
        # Large console output (10 lines as requested)
        console_output = gr.Textbox(
            value="\n".join(console_log) if console_log else "Boredom Monitor initialized...",
            label="Console Output",
            interactive=False,
            lines=10,  # 10 lines tall as requested
            max_lines=10,
            show_copy_button=True,
            elem_classes=["console-output"]
        )
        
        # Manual controls row
        with gr.Row():
            trigger_now_btn = gr.Button("🎯 Trigger Idle Now", variant="primary", size="sm")
            reset_cooldown_btn = gr.Button("🔄 Reset Cooldown", variant="secondary", size="sm")
            clear_console_btn = gr.Button("🗑️ Clear Console", variant="secondary", size="sm")
            
        # Hidden refresh button for auto-updates
        refresh_btn = gr.Button("🔄", visible=False, elem_id="boredom_refresh")
    
    # Action functions
    def trigger_idle_now():
        log("Manual idle trigger activated")
        inject_idle_message()
        return update_console()
    
    def reset_cooldown():
        default_cooldown = {
            "horny_stage": 0,
            "in_cooldown": False,
            "cooldown_end_time": 0
        }
        save_json(COOLDOWN_TRACKER, default_cooldown)
        log("Cooldown tracker reset to default state")
        return update_console()
    
    def clear_console():
        global console_log
        console_log.clear()
        log("Console cleared by user")
        return update_console()
    
    def combined_update():
        return update_countdown(), update_console()
    
    # Set up button events
    trigger_now_btn.click(fn=trigger_idle_now, outputs=console_output)
    reset_cooldown_btn.click(fn=reset_cooldown, outputs=console_output)
    clear_console_btn.click(fn=clear_console, outputs=console_output)
    
    # Auto-refresh using hidden button (clicked by JavaScript)
    refresh_btn.click(
        fn=combined_update, 
        outputs=[countdown_text, console_output], 
        show_progress=False,
        queue=False  # Make sure updates happen immediately
    )

def custom_css():
    """Return minimal custom CSS for the extension"""
    return """
    .console-output textarea {
        background-color: #1e1e1e !important;
        color: #00ff00 !important;
        font-family: monospace !important;
        font-size: 11px !important;
    }
    """

def custom_js():
    """Return custom JavaScript for the extension"""
    js_file_path = os.path.join(EXTENSION_DIR, 'script.js')
    try:
        with open(js_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        log("script.js not found - using minimal fallback JavaScript")
        return """
        console.log("Boredom Monitor: Fallback JavaScript");
        
        function setupRefresh() {
            const btn = document.getElementById('boredom_refresh');
            if (btn) {
                setInterval(() => btn.click(), 3000);
            } else {
                setTimeout(setupRefresh, 2000);
            }
        }
        
        setTimeout(setupRefresh, 1000);
        """