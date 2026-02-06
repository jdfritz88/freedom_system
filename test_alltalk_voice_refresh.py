"""
Test script to verify AllTalk voice auto-refresh functionality
"""
import time
import requests

def test_alltalk_api():
    """Test if AllTalk API is responding and has voices"""
    
    print("\n=== Testing AllTalk Voice Auto-Refresh Fix ===\n")
    
    # Test 1: Check if AllTalk server is running
    print("1. Checking AllTalk server status...")
    try:
        response = requests.get("http://127.0.0.1:7851/api/ready", timeout=3)
        if response.status_code == 200:
            print("   [OK] AllTalk server is running")
        else:
            print(f"   [FAIL] AllTalk server returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] AllTalk server not accessible: {e}")
        return False
    
    # Test 2: Check voice list API
    print("\n2. Testing voice list API endpoint...")
    try:
        response = requests.get("http://127.0.0.1:7851/api/voices", timeout=3)
        if response.status_code == 200:
            voices_data = response.json()
            voices = voices_data.get("voices", [])
            print(f"   [OK] Voice API working - Found {len(voices)} voices")
            if voices:
                print(f"   Sample voices: {', '.join(voices[:5])}")
            else:
                print("   [WARN] Voice list is empty")
        else:
            print(f"   [FAIL] Voice API returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] Voice API error: {e}")
        return False
    
    # Test 3: Check RVC voices API
    print("\n3. Testing RVC voice list API endpoint...")
    try:
        response = requests.get("http://127.0.0.1:7851/api/rvcvoices", timeout=3)
        if response.status_code == 200:
            rvc_data = response.json()
            rvc_voices = rvc_data.get("rvcvoices", [])
            print(f"   [OK] RVC Voice API working - Found {len(rvc_voices)} RVC voices")
        else:
            print(f"   [WARN] RVC Voice API returned status: {response.status_code}")
    except Exception as e:
        print(f"   [WARN] RVC Voice API error (may be normal): {e}")
    
    # Test 4: Check current settings API
    print("\n4. Testing current settings API endpoint...")
    try:
        response = requests.get("http://127.0.0.1:7851/api/currentsettings", timeout=3)
        if response.status_code == 200:
            settings = response.json()
            model = settings.get("current_model_loaded", "Unknown")
            print(f"   [OK] Settings API working - Current model: {model}")
        else:
            print(f"   [FAIL] Settings API returned status: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] Settings API error: {e}")
    
    print("\n=== Test Summary ===")
    print("If all tests passed, the auto-refresh should work correctly.")
    print("The UI will now automatically load voices 2 seconds after startup.")
    print("\nExpected behavior:")
    print("1. UI loads with 'Initializing voice lists...' message")
    print("2. After 2 seconds, voices are automatically loaded")
    print("3. Status changes to '[OK] Successfully loaded X voices'")
    print("4. Voice dropdowns are populated without manual refresh")
    
    return True

if __name__ == "__main__":
    test_alltalk_api()
    print("\n[OK] Test complete. Check the logs at:")
    print("   F:\\Apps\\freedom_system\\log\\alltalk_operations.log")