# ==========================================
# FREEDOM SYSTEM - COQUI TTS API SERVER
# Enhanced API with UI features, voice preview, and reference loading
# ==========================================

import os
import io
import json
import time
import html
import requests
import threading
import traceback
from pathlib import Path

import gradio as gr
import numpy as np
import torch
import torchaudio
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# TTS imports
try:
    from TTS.api import TTS
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
    from TTS.utils.generic_utils import get_user_data_dir
    from TTS.utils.manage import ModelManager
    tts_available = True
except ImportError:
    tts_available = False
    print("TTS libraries not available. Install with: pip install TTS==0.22.0")

# Audio imports
try:
    import soundfile as sf
    soundfile_available = True
except ImportError:
    soundfile_available = False

# ==========================================
# PATHS AND CONFIGURATION
# ==========================================

THIS_DIR = Path(__file__).parent.resolve()
VOICES_DIR = THIS_DIR / "voices"
OUTPUTS_DIR = THIS_DIR / "outputs"
CACHE_DIR = THIS_DIR / "cache"

# Create directories
for directory in [VOICES_DIR, OUTPUTS_DIR, CACHE_DIR]:
    directory.mkdir(exist_ok=True)

# ==========================================
# GLOBAL VARIABLES
# ==========================================

model = None
current_model = None
app = FastAPI()
api_server_thread = None

# Language mapping
LANGUAGES = {
    "English": "en",
    "Spanish": "es", 
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Polish": "pl",
    "Turkish": "tr",
    "Russian": "ru",
    "Dutch": "nl",
    "Czech": "cs",
    "Arabic": "ar",
    "Chinese": "zh-cn",
    "Japanese": "ja",
    "Hungarian": "hu",
    "Korean": "ko"
}

# ==========================================
# FASTAPI SETUP
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def get_available_voices():
    """Get list of available voice files"""
    if not VOICES_DIR.exists():
        return []
    return [f.name for f in VOICES_DIR.glob("*.wav")]

def preprocess(string):
    """Clean text for TTS processing"""
    string = html.unescape(string)
    # Remove markdown formatting
    string = string.replace('*', '').replace('_', '').replace('`', '')
    # Remove extra whitespace
    string = ' '.join(string.split())
    return string

def random_sentence():
    """Get a random test sentence"""
    sentences = [
        "Hello, this is a test of the TTS system.",
        "The quick brown fox jumps over the lazy dog.",
        "Testing voice quality and pronunciation.",
        "Welcome to the Freedom System."
    ]
    import random
    return random.choice(sentences)

# ==========================================
# FASTAPI ENDPOINTS
# ==========================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "model_loaded": model is not None,
        "current_model": current_model,
        "timestamp": time.time()
    }

@app.post("/generate_speech")
async def generate_speech(
    text: str = Form(...),
    voice: str = Form("female_01.wav"),
    language: str = Form("en"),
    speed: float = Form(1.0)
):
    """Generate speech from text"""
    global model
    
    if not model:
        raise HTTPException(status_code=503, detail="TTS model not loaded")
    
    try:
        # Preprocess text
        text = preprocess(text)
        
        # Generate audio
        timestamp = int(time.time())
        output_file = OUTPUTS_DIR / f"api_output_{timestamp}.wav"
        
        voice_path = VOICES_DIR / voice
        if not voice_path.exists():
            # Use default voice if specified voice doesn't exist
            available_voices = get_available_voices()
            if available_voices:
                voice_path = VOICES_DIR / available_voices[0]
            else:
                raise HTTPException(status_code=400, detail="No voice files available")
        
        # Generate TTS
        model.tts_to_file(
            text=text,
            file_path=str(output_file),
            speaker_wav=[str(voice_path)],
            language=language,
            speed=speed
        )
        
        return {
            "status": "success",
            "message": "Speech generated successfully",
            "text": text,
            "voice": voice,
            "language": language,
            "output_file": str(output_file),
            "timestamp": timestamp
        }
        
    except Exception as e:
        error_msg = f"Error generating speech: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/voices")
async def get_voices():
    """Get available voice files"""
    return {"voices": get_available_voices()}

@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "model_loaded": model is not None,
        "current_model": current_model,
        "tts_available": tts_available,
        "soundfile_available": soundfile_available,
        "voices_available": len(get_available_voices()),
        "timestamp": time.time()
    }

# ==========================================
# MODEL MANAGEMENT
# ==========================================

def load_model(model_name):
    """Load TTS model"""
    global model, current_model
    
    if not tts_available:
        print("TTS not available. Cannot load model.")
        return False
    
    try:
        print(f"Loading TTS model: {model_name}")
        model = TTS(model_name, progress_bar=False, gpu=torch.cuda.is_available())
        current_model = model_name
        print(f"✅ Model loaded successfully: {model_name}")
        return True
    except Exception as e:
        print(f"❌ Error loading model {model_name}: {str(e)}")
        model = None
        current_model = None
        return False

# ==========================================
# OOBABOOGA EXTENSION FUNCTIONS
# ==========================================

def output_modifier(string, state):
    """Convert text output to TTS audio AND send to API"""
    global model
    if not params['activate']:
        return string

    original_string = string
    string = preprocess(html.unescape(string))
    
    # Skip if text is too short or empty
    if len(string.strip()) < 3:
        return original_string

    try:
        # AUTOMATIC API CALL - Send to TTS server for speech
        def send_to_api():
            try:
                api_data = {
                    "text": string,
                    "voice": params.get('voice', 'female_01.wav'),
                    "language": LANGUAGES.get(params.get('language', 'English'), 'en'),
                    "speed": params.get('speed', 1.0)
                }
                
                print(f"[AUTO-TTS] Sending to API: '{string[:50]}{'...' if len(string) > 50 else ''}'")
                
                response = requests.post(
                    "http://127.0.0.1:8020/generate_speech",
                    data=api_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print("[AUTO-TTS] ✅ API speech generated successfully")
                else:
                    print(f"[AUTO-TTS] ❌ API error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print("[AUTO-TTS] ❌ Cannot connect to API server on port 8020")
            except Exception as e:
                print(f"[AUTO-TTS] ❌ API error: {str(e)}")
        
        # Send to API in background thread
        api_thread = threading.Thread(target=send_to_api)
        api_thread.daemon = True
        api_thread.start()
        
        # LOCAL TTS GENERATION (for UI display)
        if model and params.get('show_audio_controls', True):
            try:
                timestamp = int(time.time())
                output_file = OUTPUTS_DIR / f'{state["character_menu"]}_{timestamp}.wav'
                
                voice_file = params.get('voice', 'female_01.wav')
                voice_path = VOICES_DIR / voice_file
                
                if voice_path.exists():
                    model.tts_to_file(
                        text=string,
                        file_path=str(output_file),
                        speaker_wav=[str(voice_path)],
                        language=LANGUAGES.get(params.get('language', 'English'), 'en')
                    )
                    
                    # Return text with audio controls
                    return f'{original_string}<br><audio src="file/{output_file.as_posix()}" controls></audio>'
                else:
                    print(f"Voice file not found: {voice_path}")
            except Exception as e:
                print(f"Local TTS error: {str(e)}")
        
    except Exception as e:
        print(f"Output modifier error: {str(e)}")
    
    return original_string

def input_modifier(string, state):
    """Process input text"""
    return string

def state_modifier(state):
    """Modify the state"""
    return state

def history_modifier(history):
    """Modify the history"""
    return history

def custom_css():
    """Custom CSS for the extension"""
    return """
    .tts-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        color: white;
    }
    
    .tts-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .tts-status {
        background: rgba(255,255,255,0.1);
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        font-family: monospace;
    }
    """

def ui():
    """Create the UI for the extension"""
    
    def test_tts_connection():
        """Test TTS API connection"""
        try:
            response = requests.get("http://127.0.0.1:8020/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return f"✅ API Connected - Model: {data.get('current_model', 'None')}"
            else:
                return f"❌ API Error: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to API server on port 8020"
        except Exception as e:
            return f"❌ Connection error: {str(e)}"
    
    def test_tts_speech():
        """Test TTS speech generation"""
        try:
            test_text = "This is a test of the TTS system."
            response = requests.post(
                "http://127.0.0.1:8020/generate_speech",
                data={
                    "text": test_text,
                    "voice": params.get('voice', 'female_01.wav'),
                    "language": LANGUAGES.get(params.get('language', 'English'), 'en')
                },
                timeout=15
            )
            
            if response.status_code == 200:
                return "✅ Test speech generated successfully"
            else:
                return f"❌ Speech generation failed: {response.status_code}"
        except Exception as e:
            return f"❌ Speech test error: {str(e)}"
    
    def reload_model():
        """Reload the TTS model"""
        model_name = params.get('model_name', 'tts_models/multilingual/multi-dataset/xtts_v2')
        success = load_model(model_name)
        return "✅ Model loaded successfully" if success else "❌ Model loading failed"
    
    with gr.Row():
        with gr.Column():
            gr.HTML('<div class="tts-title">🎙️ Freedom System - Coqui TTS API</div>')
            
            # Test buttons
            with gr.Row():
                test_conn_btn = gr.Button("Test API Connection", variant="secondary")
                test_speech_btn = gr.Button("Test Speech", variant="primary")
                reload_btn = gr.Button("Reload Model", variant="secondary")
            
            # Status display
            status_display = gr.Textbox(
                label="Status",
                value="Ready - Click 'Test API Connection' to check status",
                interactive=False,
                lines=2
            )
            
            # Voice settings
            with gr.Row():
                voice_dropdown = gr.Dropdown(
                    choices=get_available_voices(),
                    value=params.get('voice', 'female_01.wav'),
                    label="Voice",
                    info="Select voice file"
                )
                
                language_dropdown = gr.Dropdown(
                    choices=list(LANGUAGES.keys()),
                    value=params.get('language', 'English'),
                    label="Language"
                )
            
            # Model settings
            model_name_textbox = gr.Textbox(
                value=params.get('model_name', 'tts_models/multilingual/multi-dataset/xtts_v2'),
                label="Model Name",
                info="XTTSv2 model name"
            )
            
            # API info
            gr.HTML("""
            <div class="tts-status">
                <strong>API Endpoints:</strong><br>
                • Main API: http://127.0.0.1:8020/<br>
                • Generate Speech: POST /generate_speech<br>
                • Status Check: GET /status<br>
                • Available Voices: GET /voices
            </div>
            """)
    
    # Event handlers
    test_conn_btn.click(test_tts_connection, outputs=status_display)
    test_speech_btn.click(test_tts_speech, outputs=status_display)
    reload_btn.click(reload_model, outputs=status_display)
    
    voice_dropdown.change(lambda x: params.update({"voice": x}), voice_dropdown)
    language_dropdown.change(lambda x: params.update({"language": x}), language_dropdown)
    model_name_textbox.change(lambda x: params.update({"model_name": x}), model_name_textbox)

# ==========================================
# EXTENSION PARAMETERS
# ==========================================

params = {
    'activate': True,
    'voice': 'female_01.wav',
    'language': 'English',
    'model_name': 'tts_models/multilingual/multi-dataset/xtts_v2',
    'show_audio_controls': True,
    'speed': 1.0,
    'api_port': 8020
}

# ==========================================
# STARTUP FUNCTIONS
# ==========================================

def start_api_server():
    """Start the FastAPI server"""
    global api_server_thread
    
    if api_server_thread and api_server_thread.is_alive():
        print("API server already running")
        return
    
    def run_server():
        try:
            print(f"🚀 Starting Coqui TTS API server on port {params['api_port']}")
            uvicorn.run(app, host="127.0.0.1", port=params['api_port'], log_level="warning")
        except Exception as e:
            print(f"❌ API server error: {str(e)}")
    
    api_server_thread = threading.Thread(target=run_server)
    api_server_thread.daemon = True
    api_server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    print(f"✅ API server started on http://127.0.0.1:{params['api_port']}")

def setup():
    """Initialize the extension"""
    print("🎙️ Initializing Freedom System - Coqui TTS API Extension")
    
    # Start API server
    start_api_server()
    
    # Load model
    if tts_available:
        model_name = params.get('model_name', 'tts_models/multilingual/multi-dataset/xtts_v2')
        load_model(model_name)
    else:
        print("⚠️ TTS libraries not available")
    
    print("✅ Extension setup complete")

# Initialize on import
if __name__ != "__main__":
    setup()