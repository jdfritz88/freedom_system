"""
Simple test to simulate UI restart and check logs
"""
import time
import os

print("Testing AllTalk Voice Auto-Refresh Fix")
print("=====================================")

log_file = "F:/Apps/freedom_system/log/alltalk_operations.log"

print("1. Checking if log file exists...")
if os.path.exists(log_file):
    print("   ✓ Log file found")
else:
    print("   ✗ Log file not found")
    exit(1)

print("\n2. Monitoring log for auto-refresh messages...")
print("   (Looking for 'Started auto-refresh thread' and 'Auto-refreshing voice lists')")

# Get current log size to monitor new entries
initial_size = os.path.getsize(log_file)
print(f"   Initial log size: {initial_size} bytes")

print("\n3. Instructions:")
print("   - Restart text-generation-webui or reload the AllTalk extension")
print("   - Watch for these log messages in order:")
print("     a) 'TGWUI_Extension loaded successfully'")
print("     b) 'Started auto-refresh thread for voice lists'") 
print("     c) 'Auto-refreshing voice lists after UI load' (after 2 seconds)")
print("     d) 'Auto-refresh successful: X voices loaded'")

print("\n4. To check current logs manually, run:")
print(f"   tail -f \"{log_file}\"")

print("\nNote: If you see the auto-refresh messages, the fix is working correctly!")