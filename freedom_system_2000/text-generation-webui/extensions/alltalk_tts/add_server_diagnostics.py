#!/usr/bin/env python3
"""
Add diagnostic logging to AllTalk server
This script shows what to add to the server's API handler to diagnose 500 errors
"""

print("""
ALLTALK SERVER DIAGNOSTIC CODE
==============================

Add this code to your AllTalk server's API handler (usually in main.py or server.py)
Look for the /api/tts-generate endpoint and add this logging:

================================================================================

# Add at the top of the file:
from datetime import datetime
import traceback

# Add this function near other utility functions:
def log_api_diagnostic(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [API-DIAG] [{level}] {message}")

# In the /api/tts-generate endpoint handler, add this at the START:
@app.route('/api/tts-generate', methods=['POST'])
def tts_generate():
    # ADD THIS DIAGNOSTIC SECTION
    try:
        log_api_diagnostic("=" * 50)
        log_api_diagnostic("TTS Generate Request Received")
        log_api_diagnostic(f"Request Method: {request.method}")
        log_api_diagnostic(f"Content Type: {request.content_type}")
        
        # Log form data
        if request.form:
            log_api_diagnostic("Form Data Received:")
            for key, value in request.form.items():
                # Truncate long values
                display_value = str(value)[:100] if len(str(value)) > 100 else str(value)
                log_api_diagnostic(f"  {key}: {display_value}")
        
        # Log JSON data if present
        if request.is_json:
            log_api_diagnostic("JSON Data Received:")
            for key, value in request.json.items():
                display_value = str(value)[:100] if len(str(value)) > 100 else str(value)
                log_api_diagnostic(f"  {key}: {display_value}")
        
        # Extract and validate critical fields
        text_input = request.form.get('text_input') or request.json.get('text_input') if request.is_json else None
        voice = request.form.get('character_voice_gen') or request.json.get('character_voice_gen') if request.is_json else None
        
        log_api_diagnostic(f"Extracted text_input: '{text_input}'")
        log_api_diagnostic(f"Extracted voice: '{voice}'")
        
        # Check for placeholder values
        if voice == "Please Refresh Settings":
            log_api_diagnostic("ERROR: Placeholder voice value detected!", "ERROR")
            log_api_diagnostic("Replacing with default: female_01.wav", "WARNING")
            voice = "female_01.wav"
        
        # Check if voice file exists
        import os
        voice_path = os.path.join("voices", voice) if voice else None
        if voice_path:
            if os.path.exists(voice_path):
                log_api_diagnostic(f"Voice file found: {voice_path}", "SUCCESS")
            else:
                log_api_diagnostic(f"Voice file NOT found: {voice_path}", "ERROR")
                log_api_diagnostic(f"Available voices in directory:", "INFO")
                if os.path.exists("voices"):
                    for f in os.listdir("voices")[:10]:  # List first 10
                        log_api_diagnostic(f"  - {f}", "INFO")
        
        # Check model status
        if hasattr(model, 'current_model'):
            log_api_diagnostic(f"Current model: {model.current_model}", "INFO")
        else:
            log_api_diagnostic("Model status unknown", "WARNING")
        
    except Exception as e:
        log_api_diagnostic(f"Error in diagnostic section: {str(e)}", "ERROR")
        log_api_diagnostic(traceback.format_exc(), "ERROR")
    
    # CONTINUE WITH ORIGINAL HANDLER CODE...
    try:
        # Original TTS generation code here
        pass
        
    except Exception as e:
        # ADD ENHANCED ERROR LOGGING
        log_api_diagnostic("=" * 50, "ERROR")
        log_api_diagnostic("500 ERROR OCCURRED", "ERROR")
        log_api_diagnostic(f"Error Type: {type(e).__name__}", "ERROR")
        log_api_diagnostic(f"Error Message: {str(e)}", "ERROR")
        log_api_diagnostic("Full Traceback:", "ERROR")
        log_api_diagnostic(traceback.format_exc(), "ERROR")
        log_api_diagnostic("=" * 50, "ERROR")
        
        # Return more informative error
        return jsonify({
            "error": str(e),
            "type": type(e).__name__,
            "diagnostic": "Check server logs for detailed diagnostic information"
        }), 500

================================================================================

After adding this code:
1. Restart the AllTalk server
2. Make a request that causes 500 error
3. Check the server console for detailed diagnostic output
4. The logs will show exactly what data the server received and what went wrong

Common issues this will reveal:
- Missing or incorrect field names
- Placeholder values being sent
- Voice files not found
- Model not loaded
- Incorrect data format (form vs JSON)
""")

print("\nThis diagnostic code will help identify the exact cause of 500 errors.")
print("Look for lines marked [ERROR] in the server output.")
print("\nPress Enter to exit...")
input()