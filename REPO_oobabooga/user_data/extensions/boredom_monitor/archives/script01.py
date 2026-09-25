# ==========================================
# OOBABOOGA EXTENSION: BOREDOM MONITOR
# Compliant with Oobabooga extension framework
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
    "is_tab": True,
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

def log(msg):
    """Logging helper"""
    print(f"[Boredom Monitor] {msg}")

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

def inject_idle_message():
    """Inject an idle message into the chat"""
    try:
        category, template = select_template()
        if not template:
            log("No template available for injection")
            return
            
        log(f"Injecting {category} message: {template[:50]}...")
        
        # Use Oobabooga's proper chat generation with current state
        from modules.text_generation import generate_reply
        
        # Prepare the state for generation
        current_state = shared.state.copy()
        
        # Generate response using the proper pipeline
        response = ""
        for reply in generate_reply(
            question=template,
            state=current_state,
            regenerate=False,
            _continue=False,
            loading_message=False
        ):
            response = reply
        
        # Properly initialize history if needed
        if 'history' not in shared.state:
            shared.state['history'] = {'internal': [], 'visible': []}
        if 'internal' not in shared.state['history']:
            shared.state['history']['internal'] = []
        if 'visible' not in shared.state['history']:
            shared.state['history']['visible'] = []
            
        # Add the exchange to history
        shared.state['history']['internal'].append([template, response])
        shared.state['history']['visible'].append([template, response])
        
        # Try to trigger UI update if possible
        try:
            if hasattr(shared, 'gradio'):
                # This might help refresh the UI
                pass
        except:
            pass
        
        log(f"Successfully injected {category} message")
        log(f"User prompt: {template}")
        log(f"AI response: {response[:100]}..." if len(response) > 100 else f"AI response: {response}")
        
    except Exception as e:
        log(f"Error injecting message: {e}")
        import traceback
        log(f"Traceback: {traceback.format_exc()}")

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

def ui():
    """Create the UI tab - REQUIRED for tab extensions"""
    with gr.Column():
        gr.Markdown("# Boredom Monitor")
        gr.Markdown("This extension monitors for idle time and injects contextual messages.")
        
        # Configuration display
        config = load_json(TRIGGER_CONFIG, {})
        idle_minutes = config.get('idle_minutes', 7)
        
        gr.Markdown(f"**Current Settings:**")
        gr.Markdown(f"- Idle trigger: {idle_minutes} minutes")
        gr.Markdown(f"- Monitor status: {'Active' if should_monitor.is_set() else 'Inactive'}")
        
        # Status and controls
        with gr.Row():
            status_text = gr.Textbox(
                value="Extension is running in background", 
                label="Status",
                interactive=False
            )
        
        # Recent activity log
        gr.Markdown("### Recent Template Usage")
        try:
            with open(TEMPLATE_LOG, 'r', encoding='utf-8') as f:
                log_content = f.read()
            if log_content.strip():
                gr.Code(log_content, label="Template Log", language="text")
            else:
                gr.Markdown("*No templates used yet*")
        except:
            gr.Markdown("*Log file not available*")

def custom_css():
    """Return custom CSS for the extension"""
    return """
    .boredom-monitor-tab {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    """