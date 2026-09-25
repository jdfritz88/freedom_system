# Standalone Verification Monitor

A standalone app with 16 verification methods to test if messages were successfully injected into the text-generation-webui chat.

## What This Does (Simple Explanation)

When the Boredom Monitor (or any extension) injects a message into the chat, we need to verify it actually worked. This app has 16 different ways to check if a message appeared in the chat.

Think of it like checking if your mail was delivered - you could:
- Check your mailbox directly
- Ask your neighbor if they saw the mail truck
- Look at tracking online
- Call the post office

This app does the same thing for chat messages - it checks in 16 different ways to be really sure.

## Quick Start

```bash
# Check if WebUI is running
python verifier.py --check

# Quick verification (recommended)
python verifier.py --test "Hello World"

# Run all 16 methods
python verifier.py --all --test "Test message"

# Run a specific method
python verifier.py --method 1 --test "Hello"

# List all methods
python verifier.py --list
```

## The 16 Verification Methods

### API-Based Methods (Work Standalone)
1. **HISTORY_STATE** - Check history via API
2. **MESSAGE_COUNT** - Count messages via API
4. **METADATA_TIMESTAMP** - Check for recent timestamps
5. **API_STATE** - Query internal state
6. **VERIFICATION_ENDPOINT** - Custom verification endpoint
14. **COMPREHENSIVE** - Run multiple methods combined
15. **BROWSER_CALLBACK** - Check browser verification reports
16. **BROWSER_API_QUERY** - Query browser API endpoint

### Browser-Required Methods
7. **DOM_CONTENT** - Check browser DOM
8. **MUTATION_OBSERVER** - Check DOM mutations
10. **DOM_MESSAGE_COUNT** - Count DOM elements
13. **SELENIUM** - Use Selenium browser automation

### Limited in Standalone Mode
3. **DISPLAY_HTML** - Check display HTML (needs internal access)
9. **DATA_RAW** - Check data-raw attributes
11. **SSE_EVENTS** - Monitor server-sent events
12. **REQUEST_MONITOR** - Monitor HTTP requests

## Configuration

Edit `config.json` to change settings:

```json
{
  "webui_base": "http://127.0.0.1:7860",
  "timeout_seconds": 5,
  "log_to_file": true,
  "log_file": "verification_monitor.log",
  "verbose": true
}
```

## Command Line Options

```
--test, -t      Test message to verify (required for verification)
--method, -m    Run specific method number (1-16)
--all, -a       Run all 16 verification methods
--quick, -q     Run quick verification (default)
--list, -l      List all verification methods
--check, -c     Check WebUI connection
--config        Show current configuration
--url           Override WebUI base URL
--output, -o    Output results to JSON file
--verbose, -v   Verbose output
```

## Examples

```bash
# Basic quick check
python verifier.py -t "[INJECTION-TEST] Hello"

# Save results to file
python verifier.py --all -t "Test" -o results.json

# Use different WebUI URL
python verifier.py --url http://localhost:8080 -t "Test"

# Check connection only
python verifier.py --check
```

## Using from Python

```python
from verifier import (
    quick_verify,
    run_verification_method,
    run_all_verifications,
    check_webui_connection
)

# Quick check
result = quick_verify("my test message")
print(f"Found: {result['found']}")

# Run specific method
result = run_verification_method(1, "my test message")
print(f"Method 1: {result}")

# Run all methods
results = run_all_verifications("my test message")
for num, res in results.items():
    print(f"{num}: {res['method']} - found={res.get('found')}")
```

## Log Files

Logs are saved to: `F:\Apps\freedom_system\log\verification_monitor.log`

## Requirements

- Python 3.8+
- requests library
- text-generation-webui running with boredom_monitor extension

Optional:
- selenium (for method 13)
