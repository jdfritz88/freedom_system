#!/usr/bin/env python3
"""
AllTalk TTS API Diagnostic Test Script
This script systematically tests the AllTalk API to identify 500 error causes
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

# Color codes for console output (Windows compatible)
class Colors:
    GREEN = "[SUCCESS]"
    RED = "[ERROR]"
    YELLOW = "[WARNING]"
    BLUE = "[INFO]"
    RESET = ""

def log(message, level="INFO"):
    """Enhanced logging with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {
        "SUCCESS": Colors.GREEN,
        "ERROR": Colors.RED,
        "WARNING": Colors.YELLOW,
        "INFO": Colors.BLUE
    }.get(level, Colors.BLUE)
    
    print(f"{timestamp} {prefix} {message}")

def test_server_connectivity():
    """Test 1: Basic server connectivity"""
    log("=" * 60, "INFO")
    log("TEST 1: Server Connectivity Check", "INFO")
    log("=" * 60, "INFO")
    
    endpoints = [
        ("Ready Check", "http://127.0.0.1:7851/api/ready"),
        ("Voices List", "http://127.0.0.1:7851/api/voices"),
        ("Model Info", "http://127.0.0.1:7851/api/model-info"),
    ]
    
    results = {}
    for name, url in endpoints:
        try:
            log(f"Testing {name}: {url}", "INFO")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                log(f"{name}: Connected successfully", "SUCCESS")
                
                # Show first 200 chars of response
                try:
                    data = response.json()
                    log(f"Response preview: {str(data)[:200]}", "INFO")
                    results[name] = True
                except:
                    log(f"Response (non-JSON): {response.text[:200]}", "INFO")
                    results[name] = True
            else:
                log(f"{name}: Failed with status {response.status_code}", "ERROR")
                log(f"Error response: {response.text[:200]}", "ERROR")
                results[name] = False
                
        except requests.exceptions.ConnectionError:
            log(f"{name}: Connection refused - server not running?", "ERROR")
            results[name] = False
        except Exception as e:
            log(f"{name}: Unexpected error: {str(e)}", "ERROR")
            results[name] = False
    
    return all(results.values())

def test_minimal_api_call():
    """Test 2: Minimal API call with bare minimum fields"""
    log("=" * 60, "INFO")
    log("TEST 2: Minimal TTS Generation", "INFO")
    log("=" * 60, "INFO")
    
    url = "http://127.0.0.1:7851/api/tts-generate"
    
    # Absolute minimum payload
    payload = {
        "text_input": "Hello world",
        "character_voice_gen": "female_01.wav"
    }
    
    log(f"Sending minimal payload: {json.dumps(payload, indent=2)}", "INFO")
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        
        log(f"Response status: {response.status_code}", "INFO")
        log(f"Response headers: {dict(response.headers)}", "INFO")
        
        if response.status_code == 200:
            log("Minimal TTS generation SUCCESS!", "SUCCESS")
            return True
        elif response.status_code == 500:
            log("Got 500 error with minimal payload", "ERROR")
            log(f"Server error message: {response.text}", "ERROR")
            
            # Analyze error message
            error_text = response.text.lower()
            if "file" in error_text and "not found" in error_text:
                log("DIAGNOSIS: Voice file not found on server", "WARNING")
            elif "model" in error_text:
                log("DIAGNOSIS: Model loading issue", "WARNING")
            elif "please refresh settings" in error_text:
                log("DIAGNOSIS: Placeholder value still being used", "WARNING")
            
            return False
        else:
            log(f"Unexpected status code: {response.status_code}", "WARNING")
            log(f"Response: {response.text[:500]}", "WARNING")
            return False
            
    except Exception as e:
        log(f"Request failed: {str(e)}", "ERROR")
        return False

def test_field_by_field():
    """Test 3: Add fields one by one to identify problem field"""
    log("=" * 60, "INFO")
    log("TEST 3: Field-by-Field Validation", "INFO")
    log("=" * 60, "INFO")
    
    url = "http://127.0.0.1:7851/api/tts-generate"
    
    # Start with working minimum
    base_payload = {
        "text_input": "Testing field by field",
        "character_voice_gen": "female_01.wav"
    }
    
    # Fields to test one by one
    test_fields = [
        ("text_filtering", "standard"),
        ("narrator_enabled", "false"),
        ("narrator_voice_gen", "male_01.wav"),
        ("language", "en"),
        ("output_file_name", "test_output"),
        ("output_file_timestamp", "true"),
        ("autoplay", "false"),
        ("autoplay_volume", "0.8"),
    ]
    
    working_payload = base_payload.copy()
    problem_fields = []
    
    for field_name, field_value in test_fields:
        test_payload = working_payload.copy()
        test_payload[field_name] = field_value
        
        log(f"Testing with added field: {field_name} = {field_value}", "INFO")
        
        try:
            response = requests.post(url, data=test_payload, timeout=30)
            
            if response.status_code == 200:
                log(f"SUCCESS with {field_name}", "SUCCESS")
                working_payload = test_payload  # Keep this field
            elif response.status_code == 500:
                log(f"ERROR 500 caused by field: {field_name}!", "ERROR")
                log(f"Error details: {response.text[:200]}", "ERROR")
                problem_fields.append(field_name)
                # Don't add this field to working payload
            else:
                log(f"Status {response.status_code} with {field_name}", "WARNING")
                
        except Exception as e:
            log(f"Request failed with {field_name}: {str(e)}", "ERROR")
            problem_fields.append(field_name)
    
    if problem_fields:
        log(f"Problem fields identified: {', '.join(problem_fields)}", "ERROR")
        return False
    else:
        log("All fields tested successfully", "SUCCESS")
        return True

def test_voice_files():
    """Test 4: Check if voice files are accessible"""
    log("=" * 60, "INFO")
    log("TEST 4: Voice File Availability", "INFO")
    log("=" * 60, "INFO")
    
    # Try to get available voices from API
    try:
        response = requests.get("http://127.0.0.1:7851/api/voices", timeout=5)
        if response.status_code == 200:
            data = response.json()
            voices = data.get("voices", [])
            log(f"Server reports {len(voices)} available voices", "INFO")
            
            if voices:
                log(f"Available voices: {', '.join(voices[:5])}", "INFO")  # Show first 5
                
                # Test with first available voice
                if len(voices) > 0:
                    test_voice = voices[0]
                    log(f"Testing with actual voice: {test_voice}", "INFO")
                    
                    payload = {
                        "text_input": "Testing with actual voice",
                        "character_voice_gen": test_voice
                    }
                    
                    response = requests.post(
                        "http://127.0.0.1:7851/api/tts-generate",
                        data=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        log(f"SUCCESS with voice: {test_voice}", "SUCCESS")
                        return True
                    else:
                        log(f"Failed with actual voice {test_voice}: {response.status_code}", "ERROR")
                        return False
            else:
                log("No voices reported by server!", "ERROR")
                return False
                
    except Exception as e:
        log(f"Could not retrieve voice list: {str(e)}", "ERROR")
        return False

def check_configuration_files():
    """Test 5: Check configuration files for issues"""
    log("=" * 60, "INFO")
    log("TEST 5: Configuration File Check", "INFO")
    log("=" * 60, "INFO")
    
    base_path = Path(".")
    
    config_files = [
        "confignew.json",
        "system/TGWUI_Extension/tgwui_remote_config.json",
        "system/tts_engines/xtts/model_settings.json"
    ]
    
    configs = {}
    issues = []
    
    for config_file in config_files:
        config_path = base_path / config_file
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    configs[config_file] = json.loads(content)
                    
                    # Check for placeholder values
                    if "Please Refresh Settings" in content:
                        issues.append(f"Placeholder value found in {config_file}")
                        log(f"WARNING: {config_file} contains 'Please Refresh Settings'", "WARNING")
                    
                    log(f"Loaded {config_file} successfully", "SUCCESS")
                    
            except Exception as e:
                log(f"Error reading {config_file}: {str(e)}", "ERROR")
                issues.append(f"Cannot read {config_file}")
        else:
            log(f"Config file not found: {config_file}", "WARNING")
    
    # Compare voice settings across configs
    if len(configs) > 0:
        log("\nVoice Configuration Comparison:", "INFO")
        
        for config_name, config_data in configs.items():
            # Try to find voice settings in different possible locations
            voice = None
            if "tgwui" in config_data and "tgwui_character_voice" in config_data["tgwui"]:
                voice = config_data["tgwui"]["tgwui_character_voice"]
            elif "settings" in config_data and "def_character_voice" in config_data["settings"]:
                voice = config_data["settings"]["def_character_voice"]
            
            if voice:
                log(f"{config_name}: Character voice = {voice}", "INFO")
                if voice == "Please Refresh Settings":
                    issues.append(f"Invalid voice in {config_name}")
    
    if issues:
        log(f"\nConfiguration issues found: {len(issues)}", "ERROR")
        for issue in issues:
            log(f"  - {issue}", "ERROR")
        return False
    else:
        log("Configuration files appear valid", "SUCCESS")
        return True

def run_all_tests():
    """Run all diagnostic tests"""
    print("\n" + "=" * 60)
    print("ALLTALK TTS API DIAGNOSTIC SUITE")
    print("=" * 60 + "\n")
    
    results = {
        "Server Connectivity": test_server_connectivity(),
        "Minimal API Call": test_minimal_api_call(),
        "Field Validation": test_field_by_field(),
        "Voice Files": test_voice_files(),
        "Configuration Files": check_configuration_files()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = Colors.GREEN + "PASSED" if passed else Colors.RED + "FAILED"
        print(f"{test_name}: {status}")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if not results["Server Connectivity"]:
        print("1. Start the AllTalk server first")
        print("   Run: cd extensions/alltalk_tts && python server.py")
    
    if not results["Configuration Files"]:
        print("2. Fix configuration files")
        print("   Run: python sync_voices.py")
        print("   Or manually replace 'Please Refresh Settings' with 'female_01.wav'")
    
    if not results["Voice Files"]:
        print("3. Check voices directory")
        print("   Ensure voices/*.wav files exist")
    
    if not results["Minimal API Call"] and results["Server Connectivity"]:
        print("4. Server is running but API format may be wrong")
        print("   Check server logs for detailed error messages")
    
    if not results["Field Validation"]:
        print("5. Specific fields are causing issues")
        print("   Review the field-by-field test results above")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print(Colors.GREEN + "\nALL TESTS PASSED! AllTalk API is working correctly.")
    else:
        print(Colors.RED + f"\n{total_tests - total_passed} tests failed. Review recommendations above.")

if __name__ == "__main__":
    run_all_tests()
    print("\nPress Enter to exit...")
    input()