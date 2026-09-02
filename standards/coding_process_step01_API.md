# Coding Process Step 01 API: API Troubleshooting (CP2API)

This document is the reference wiki for the CP2API subagent. When a bug involves two programs talking to each other over HTTP (an API call), this is the systematic process for finding what's wrong.

NEVER ASSUME. NEVER GUESS. NO SHORTCUTS. NO WORKAROUNDS. NO DUMMIES. NO PLACEHOLDERS. NO STUBS. NO NUBS.

Before Phase 1, call ToolSearch once for `mcp__claude-in-chrome__read_network_requests` and `mcp__windows-mcp__Process` - you may need them below (Step 1.5, Step 1.6). Log every use of them to `[root folder]_Monitor_LOG.md` (create it if CP1 hasn't already).

---

## WHAT IS AN API BUG?

An API bug is when Program A sends a request to Program B over the network, and something goes wrong. Either:
- Program B doesn't respond at all (connection refused, timeout)
- Program B responds with an error (400, 404, 500, etc.)
- Program B responds with success but the data is wrong
- Program B responds but Program A can't understand the response

This is different from a regular code bug because TWO programs are involved. The bug could be in Program A (sending wrong data), Program B (processing it wrong), or in the connection between them (network, port, format mismatch).

---

## PHASE 1: IS THE OTHER PROGRAM ALIVE?

Before debugging anything else, verify that the program you're trying to talk to is actually running and reachable. Check these in order - if any step fails, stop and fix it before continuing.

### Step 1.1: Is the process running?

Check if the target program is actually running on the machine.

```python
import subprocess
import sys

def check_process_running(process_name):
    """Check if a process is running by name"""
    try:
        if sys.platform == 'win32':
            result = subprocess.run(
                ['tasklist', '/FI', f'IMAGENAME eq {process_name}'],
                capture_output=True, text=True, timeout=10
            )
            return process_name.lower() in result.stdout.lower()
        else:
            result = subprocess.run(
                ['pgrep', '-f', process_name],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
    except Exception as e:
        print(f"[API CHECK] Cannot check process: {e}")
        return False

# What to check:
# - Is the process in Task Manager (Windows) or ps aux (Linux)?
# - Did it crash on startup? Check its log file.
# - Was it ever started? Check if there's a start script that was skipped.
```

**If the process is NOT running:**
- Check its startup log for errors
- Try starting it manually and watch the console output
- Check if another process is using the same port (port conflict)
- Check if required dependencies are installed

### Step 1.2: Is the port open?

The target program listens on a specific port. Verify that port is actually open and accepting connections.

```python
import socket

def check_port_open(host, port, timeout=3):
    """Check if a port is open and accepting connections"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"[API CHECK] Port {port} is OPEN on {host}")
            return True
        else:
            print(f"[API CHECK] Port {port} is CLOSED on {host} (error code: {result})")
            return False
    except socket.timeout:
        print(f"[API CHECK] Port {port} TIMED OUT on {host}")
        return False
    except Exception as e:
        print(f"[API CHECK] Port check failed: {e}")
        return False

# Common port issues:
# - Port is wrong (check config for the correct port number)
# - Firewall is blocking the port
# - Another program is using that port (use netstat to check)
# - Program is listening on localhost only (127.0.0.1) but you're calling its external IP
```

**If the port is NOT open:**

```python
def find_what_is_using_port(port):
    """Find which process is using a specific port"""
    import subprocess
    import sys

    try:
        if sys.platform == 'win32':
            result = subprocess.run(
                ['netstat', '-ano', '-p', 'TCP'],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    print(f"[API CHECK] Port {port} in use: {line.strip()}")
        else:
            result = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True, text=True, timeout=10
            )
            print(f"[API CHECK] Port {port} usage:\n{result.stdout}")
    except Exception as e:
        print(f"[API CHECK] Cannot check port usage: {e}")
```

### Step 1.3: Does it give a basic HTTP response?

The port is open, but does the program actually respond to HTTP requests?

```python
import requests

def check_basic_http_response(base_url, timeout=5):
    """Check if the server responds to a basic HTTP request"""
    try:
        response = requests.get(base_url, timeout=timeout)
        print(f"[API CHECK] HTTP response: {response.status_code}")
        print(f"[API CHECK] Response headers: {dict(response.headers)}")
        print(f"[API CHECK] Response body (first 200 chars): {response.text[:200]}")
        return response.status_code
    except requests.ConnectionError:
        print(f"[API CHECK] CONNECTION REFUSED - server is not accepting HTTP connections")
        return None
    except requests.Timeout:
        print(f"[API CHECK] TIMEOUT - server did not respond within {timeout} seconds")
        return None
    except Exception as e:
        print(f"[API CHECK] HTTP check failed: {e}")
        return None

# What to look for:
# - 200 = server is alive and responding normally
# - 404 = server is alive but you hit a wrong URL
# - 500 = server is alive but crashing internally
# - CONNECTION REFUSED = port is open but nothing is listening for HTTP
# - TIMEOUT = something is blocking the response (firewall, hung process, overloaded)
```

### Step 1.4: Does the specific endpoint exist?

The server responds to basic requests, but does the specific API endpoint you need actually exist?

```python
def check_endpoint_exists(endpoint_url, timeout=5):
    """Check if a specific API endpoint exists and responds"""
    methods_to_try = ['GET', 'POST', 'OPTIONS']

    for method in methods_to_try:
        try:
            response = requests.request(method, endpoint_url, timeout=timeout)
            print(f"[API CHECK] {method} {endpoint_url} -> {response.status_code}")

            if response.status_code == 405:
                print(f"[API CHECK] Endpoint exists but doesn't accept {method} method")
            elif response.status_code == 404:
                print(f"[API CHECK] Endpoint NOT FOUND with {method}")
            elif response.status_code in [200, 400, 422]:
                print(f"[API CHECK] Endpoint EXISTS and accepts {method}")
                return method, response.status_code
        except Exception as e:
            print(f"[API CHECK] {method} failed: {e}")

    return None, None

# Common endpoint issues:
# - URL is misspelled (check the API documentation)
# - URL has changed in a new version
# - Missing a path segment (e.g., /api/v1/endpoint vs /api/endpoint)
# - Trailing slash matters on some servers (/endpoint vs /endpoint/)
```

### Step 1.5: If none of the above explains it, check for interference

Only if Steps 1.1-1.4 didn't explain the failure - is Windows Defender scanning or blocking the connection right now? Is the Killer networking software throttling this specific connection? Is Citrix intercepting the traffic? Check via `tasklist`/`Get-Process`. Log the check to `[root folder]_Monitor_LOG.md` either way.

### Step 1.6: If the call comes from a browser, see what the browser actually saw

If this API call originates from a web frontend, use `mcp__claude-in-chrome__read_network_requests` to see the real request/response as the browser experienced it - this can catch things curl/requests won't (CORS failures, a service worker rewriting the request, browser-cached responses).

---

## PHASE 2: ARE YOU SENDING DATA IN THE RIGHT FORMAT?

The server is alive and the endpoint exists. Now: are you sending data the way the server expects it?

This is one of the most common API bugs. The same data sent in three different formats will look completely different to the server. If you use the wrong format, the server either can't read your data or reads it wrong.

### The Three Formats

```python
import requests
import json

def test_all_three_formats(endpoint_url, payload, timeout=10):
    """
    Test the same data in all three formats.
    The server will accept ONE of these and reject the others.
    """

    results = {}

    # FORMAT 1: JSON
    # Sends data as: {"key": "value"} in the request body
    # Content-Type: application/json
    # When to use: Most modern APIs expect this
    try:
        print(f"\n[FORMAT TEST] Testing JSON format...")
        response = requests.post(endpoint_url, json=payload, timeout=timeout)
        results['JSON'] = {
            'status': response.status_code,
            'body': response.text[:300]
        }
        print(f"[FORMAT TEST] JSON -> {response.status_code}")
        if response.status_code != 200:
            print(f"[FORMAT TEST] JSON error: {response.text[:300]}")
    except Exception as e:
        results['JSON'] = {'status': 'ERROR', 'body': str(e)}
        print(f"[FORMAT TEST] JSON failed: {e}")

    # FORMAT 2: Form Data
    # Sends data as: key=value&key2=value2 in the request body
    # Content-Type: application/x-www-form-urlencoded
    # When to use: Older APIs, HTML form submissions, some file upload APIs
    try:
        print(f"\n[FORMAT TEST] Testing Form Data format...")
        response = requests.post(endpoint_url, data=payload, timeout=timeout)
        results['Form Data'] = {
            'status': response.status_code,
            'body': response.text[:300]
        }
        print(f"[FORMAT TEST] Form Data -> {response.status_code}")
        if response.status_code != 200:
            print(f"[FORMAT TEST] Form Data error: {response.text[:300]}")
    except Exception as e:
        results['Form Data'] = {'status': 'ERROR', 'body': str(e)}
        print(f"[FORMAT TEST] Form Data failed: {e}")

    # FORMAT 3: URL Encoded (explicit header)
    # Same as Form Data but with explicit Content-Type header
    # Some servers are picky about the exact header
    try:
        print(f"\n[FORMAT TEST] Testing URL Encoded format...")
        response = requests.post(
            endpoint_url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=timeout
        )
        results['URL Encoded'] = {
            'status': response.status_code,
            'body': response.text[:300]
        }
        print(f"[FORMAT TEST] URL Encoded -> {response.status_code}")
        if response.status_code != 200:
            print(f"[FORMAT TEST] URL Encoded error: {response.text[:300]}")
    except Exception as e:
        results['URL Encoded'] = {'status': 'ERROR', 'body': str(e)}
        print(f"[FORMAT TEST] URL Encoded failed: {e}")

    # SUMMARY
    print(f"\n[FORMAT TEST] === RESULTS ===")
    for format_name, result in results.items():
        status = result['status']
        emoji = "PASS" if status == 200 else "FAIL"
        print(f"[FORMAT TEST] {emoji} {format_name}: {status}")

    return results
```

### How to read the results

| JSON | Form Data | URL Encoded | What it means |
|------|-----------|-------------|---------------|
| 200 | 400/500 | 400/500 | Server expects JSON. Use `json=payload`. |
| 400/500 | 200 | 200 | Server expects Form Data. Use `data=payload`. |
| 400/500 | 400/500 | 400/500 | None work. Check payload keys, required fields, or authentication. |
| 200 | 200 | 200 | Server accepts anything. Use JSON (most reliable). |

### Common format mistakes

```python
# MISTAKE 1: Sending JSON when server expects Form Data
# WRONG:
requests.post(url, json={"text": "hello", "voice": "default.wav"})
# RIGHT:
requests.post(url, data={"text": "hello", "voice": "default.wav"})

# MISTAKE 2: Nested data in Form Data (doesn't work)
# WRONG - Form Data can't handle nested objects:
requests.post(url, data={"settings": {"volume": 80, "speed": 1.0}})
# RIGHT - Flatten it or use JSON:
requests.post(url, json={"settings": {"volume": 80, "speed": 1.0}})

# MISTAKE 3: Sending string instead of dict
# WRONG:
requests.post(url, data='{"text": "hello"}')
# RIGHT:
requests.post(url, json={"text": "hello"})

# MISTAKE 4: Missing required fields
# The server expects "text_input" but you're sending "text"
# Check the API documentation for exact field names
```

---

## PHASE 3: IS THE DATA YOU'RE SENDING CORRECT?

The format is right but the server still returns an error. Now check the actual data values.

### Step 3.1: Log everything going in and out

```python
def log_full_api_exchange(endpoint_url, payload, method='POST', format_type='json', timeout=10):
    """
    Log EVERY detail of an API request and response.
    This is the most important debugging tool for API issues.
    """

    print(f"\n{'='*60}")
    print(f"[API LOG] === FULL API EXCHANGE ===")
    print(f"[API LOG] Endpoint: {method} {endpoint_url}")
    print(f"[API LOG] Format: {format_type}")
    print(f"[API LOG] Payload:")

    # Pretty print the payload
    import json as json_module
    if isinstance(payload, dict):
        print(json_module.dumps(payload, indent=2))
    else:
        print(payload)

    # Send the request
    try:
        if format_type == 'json':
            response = requests.request(method, endpoint_url, json=payload, timeout=timeout)
        else:
            response = requests.request(method, endpoint_url, data=payload, timeout=timeout)

        print(f"\n[API LOG] === RESPONSE ===")
        print(f"[API LOG] Status: {response.status_code}")
        print(f"[API LOG] Headers:")
        for key, value in response.headers.items():
            print(f"[API LOG]   {key}: {value}")
        print(f"[API LOG] Body (first 500 chars):")
        print(response.text[:500])

        # Check for common problems in the response
        analyze_response_for_clues(response)

        return response

    except requests.ConnectionError as e:
        print(f"\n[API LOG] === CONNECTION ERROR ===")
        print(f"[API LOG] Could not connect: {e}")
        return None
    except requests.Timeout:
        print(f"\n[API LOG] === TIMEOUT ===")
        print(f"[API LOG] Server did not respond within {timeout} seconds")
        return None
    except Exception as e:
        print(f"\n[API LOG] === UNEXPECTED ERROR ===")
        print(f"[API LOG] {type(e).__name__}: {e}")
        return None
```

### Step 3.2: Check for common data problems

```python
def analyze_response_for_clues(response):
    """Read the response body and look for clues about what went wrong"""

    body = response.text.lower()
    status = response.status_code

    print(f"\n[API LOG] === ANALYSIS ===")

    # STATUS CODE ANALYSIS
    if status == 200:
        print(f"[API LOG] Status 200: Success. Check if response data is what you expected.")
    elif status == 400:
        print(f"[API LOG] Status 400: Bad Request. Your data is formatted wrong or missing required fields.")
        print(f"[API LOG] ACTION: Check field names, data types, and required fields against API docs.")
    elif status == 401:
        print(f"[API LOG] Status 401: Unauthorized. Missing or wrong API key / auth token.")
        print(f"[API LOG] ACTION: Check authentication headers, API keys, tokens.")
    elif status == 403:
        print(f"[API LOG] Status 403: Forbidden. You authenticated but don't have permission.")
        print(f"[API LOG] ACTION: Check user permissions, IP allowlists, rate limits.")
    elif status == 404:
        print(f"[API LOG] Status 404: Not Found. The endpoint URL is wrong.")
        print(f"[API LOG] ACTION: Check URL spelling, path segments, API version in URL.")
    elif status == 405:
        print(f"[API LOG] Status 405: Method Not Allowed. Using GET when it should be POST (or vice versa).")
        print(f"[API LOG] ACTION: Check if endpoint expects GET, POST, PUT, or DELETE.")
    elif status == 422:
        print(f"[API LOG] Status 422: Unprocessable Entity. Data format is right but values are invalid.")
        print(f"[API LOG] ACTION: Check data types (string vs int), value ranges, enum values.")
    elif status == 429:
        print(f"[API LOG] Status 429: Too Many Requests. Rate limited.")
        print(f"[API LOG] ACTION: Slow down requests, add delays between calls, check rate limit headers.")
    elif status == 500:
        print(f"[API LOG] Status 500: Internal Server Error. The SERVER crashed processing your request.")
        print(f"[API LOG] ACTION: Check the SERVER's logs, not your code. Your request may have exposed a server bug.")
    elif status == 502:
        print(f"[API LOG] Status 502: Bad Gateway. A proxy/load balancer can't reach the actual server.")
        print(f"[API LOG] ACTION: Check if the backend server is running behind the proxy.")
    elif status == 503:
        print(f"[API LOG] Status 503: Service Unavailable. Server is overloaded or in maintenance.")
        print(f"[API LOG] ACTION: Wait and retry, or check if the server is being restarted.")

    # RESPONSE BODY ANALYSIS
    if "file" in body and "not found" in body:
        print(f"[API LOG] CLUE: File not found error. A file path in your request points to a file that doesn't exist.")
        print(f"[API LOG] ACTION: Check all file paths in your payload. Are they absolute? Do they exist on disk?")

    if "missing" in body and ("field" in body or "parameter" in body or "key" in body):
        print(f"[API LOG] CLUE: Missing required field. The server expected a field you didn't send.")
        print(f"[API LOG] ACTION: Compare your payload fields against the API documentation.")

    if "invalid" in body and ("type" in body or "value" in body or "format" in body):
        print(f"[API LOG] CLUE: Invalid value. You sent a value the server can't use.")
        print(f"[API LOG] ACTION: Check data types (sending string '80' instead of integer 80?).")

    if "timeout" in body or "timed out" in body:
        print(f"[API LOG] CLUE: Server-side timeout. The operation took too long inside the server.")
        print(f"[API LOG] ACTION: Reduce request size, simplify the operation, or increase server-side timeout.")

    if "permission" in body or "denied" in body or "forbidden" in body:
        print(f"[API LOG] CLUE: Permission denied. Even though you connected, you can't do this operation.")
        print(f"[API LOG] ACTION: Check auth tokens, user roles, file permissions on the server.")

    if "json" in body and ("parse" in body or "decode" in body or "syntax" in body):
        print(f"[API LOG] CLUE: JSON parse error. The server couldn't read your data as JSON.")
        print(f"[API LOG] ACTION: Validate your JSON. Are you sending Form Data to a JSON endpoint?")
```

### Step 3.3: Validate your payload

```python
def validate_payload_before_sending(payload, required_fields=None, field_types=None):
    """
    Check your data BEFORE sending it to catch obvious problems.
    """

    issues = []

    # Check for empty/None values
    print(f"[VALIDATE] Checking payload for problems...")
    for key, value in payload.items():
        if value is None:
            issues.append(f"Field '{key}' is None - server probably won't accept this")
        elif isinstance(value, str) and value.strip() == "":
            issues.append(f"Field '{key}' is empty string - is this intentional?")
        elif isinstance(value, str) and value in ["Select...", "Choose...", "Loading...", "None", "null", "undefined"]:
            issues.append(f"Field '{key}' has a placeholder/default value: '{value}' - this is NOT real data")

    # Check required fields
    if required_fields:
        for field in required_fields:
            if field not in payload:
                issues.append(f"Required field '{field}' is MISSING from payload")

    # Check field types
    if field_types:
        for field, expected_type in field_types.items():
            if field in payload and not isinstance(payload[field], expected_type):
                actual_type = type(payload[field]).__name__
                issues.append(f"Field '{field}' should be {expected_type.__name__} but is {actual_type}")

    # Check for file path references
    import os
    for key, value in payload.items():
        if isinstance(value, str) and ('/' in value or '\\' in value):
            if value.endswith(('.wav', '.mp3', '.json', '.txt', '.py', '.conf', '.yaml', '.yml')):
                if not os.path.exists(value):
                    issues.append(f"Field '{key}' references file '{value}' which DOES NOT EXIST on disk")

    # Report
    if issues:
        print(f"[VALIDATE] PROBLEMS FOUND:")
        for issue in issues:
            print(f"[VALIDATE]   - {issue}")
    else:
        print(f"[VALIDATE] No obvious problems found in payload")

    return issues
```

---

## PHASE 4: CONFIGURATION SYNC PROBLEMS

Sometimes the API call itself is fine, but the data it's using comes from a configuration file that has wrong values. This phase checks ALL configuration files in the system for inconsistencies.

### Step 4.1: Find every configuration file

```python
from pathlib import Path

def discover_all_config_files(root_dir):
    """Find every configuration file in the project"""

    search_patterns = [
        "**/*config*.json",
        "**/*settings*.json",
        "**/*conf*.json",
        "**/*.conf",
        "**/*.yaml",
        "**/*.yml",
        "**/*.ini",
        "**/*.env",
        "**/*.toml"
    ]

    config_files = []
    root = Path(root_dir)

    for pattern in search_patterns:
        for file_path in root.glob(pattern):
            if file_path.is_file():
                # Skip node_modules, .git, __pycache__, etc.
                skip_dirs = {'node_modules', '.git', '__pycache__', 'venv', '.venv', 'env'}
                if not any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    config_files.append(str(file_path))

    print(f"[CONFIG] Found {len(config_files)} configuration files:")
    for f in config_files:
        print(f"[CONFIG]   {f}")

    return config_files
```

### Step 4.2: Analyze each config file

```python
import json
import os

def analyze_config_file(config_file):
    """Analyze a single config file for common problems"""

    analysis = {
        "path": config_file,
        "exists": os.path.exists(config_file),
        "readable": False,
        "valid_format": False,
        "key_count": 0,
        "placeholder_values": [],
        "empty_values": [],
        "missing_file_references": [],
        "problems": []
    }

    if not analysis["exists"]:
        analysis["problems"].append("File does not exist")
        return analysis

    # Try to read it
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        analysis["readable"] = True
    except PermissionError:
        analysis["problems"].append("Permission denied - cannot read file")
        return analysis
    except Exception as e:
        analysis["problems"].append(f"Cannot read file: {e}")
        return analysis

    # Try to parse it
    if config_file.endswith('.json'):
        try:
            data = json.loads(content)
            analysis["valid_format"] = True
            if isinstance(data, dict):
                analysis["key_count"] = len(data)
        except json.JSONDecodeError as e:
            analysis["problems"].append(f"Invalid JSON: {e}")
            return analysis

    # Check for placeholder values
    placeholder_strings = [
        "Select...", "Choose...", "Loading...", "Please Refresh",
        "None", "null", "undefined", "TODO", "FIXME",
        "example.com", "localhost:0000", "your-api-key-here",
        "CHANGE_ME", "REPLACE_THIS", "INSERT_HERE"
    ]

    analysis["placeholder_values"] = find_placeholders_recursive(data, placeholder_strings)

    # Check for empty values
    analysis["empty_values"] = find_empty_values_recursive(data)

    # Check for file path references that don't exist
    analysis["missing_file_references"] = find_missing_files_recursive(data)

    # Summarize problems
    if analysis["placeholder_values"]:
        analysis["problems"].append(f"{len(analysis['placeholder_values'])} placeholder values found")
    if analysis["empty_values"]:
        analysis["problems"].append(f"{len(analysis['empty_values'])} empty values found")
    if analysis["missing_file_references"]:
        analysis["problems"].append(f"{len(analysis['missing_file_references'])} missing file references")

    return analysis

def find_placeholders_recursive(data, placeholder_strings, path=""):
    """Walk through a config dict/list and find placeholder values"""
    found = []

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(value, str):
                for placeholder in placeholder_strings:
                    if placeholder.lower() in value.lower():
                        found.append(f"{current_path} = '{value}'")
            elif isinstance(value, (dict, list)):
                found.extend(find_placeholders_recursive(value, placeholder_strings, current_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]"
            if isinstance(item, str):
                for placeholder in placeholder_strings:
                    if placeholder.lower() in item.lower():
                        found.append(f"{current_path} = '{item}'")
            elif isinstance(item, (dict, list)):
                found.extend(find_placeholders_recursive(item, placeholder_strings, current_path))

    return found

def find_empty_values_recursive(data, path=""):
    """Find empty strings, empty lists, empty dicts"""
    found = []

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if value == "":
                found.append(f"{current_path} = '' (empty string)")
            elif value == []:
                found.append(f"{current_path} = [] (empty list)")
            elif value == {}:
                found.append(f"{current_path} = {{}} (empty dict)")
            elif isinstance(value, (dict, list)):
                found.extend(find_empty_values_recursive(value, current_path))

    return found

def find_missing_files_recursive(data, path=""):
    """Find string values that look like file paths but don't exist"""
    found = []
    file_extensions = {'.wav', '.mp3', '.json', '.txt', '.py', '.conf', '.yaml', '.yml',
                       '.png', '.jpg', '.csv', '.db', '.sqlite', '.pth', '.bin', '.model'}

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(value, str) and any(value.endswith(ext) for ext in file_extensions):
                if not os.path.exists(value):
                    found.append(f"{current_path} = '{value}' (FILE NOT FOUND)")
            elif isinstance(value, (dict, list)):
                found.extend(find_missing_files_recursive(value, current_path))

    return found
```

### Step 4.3: Compare configs for inconsistencies

```python
def find_config_inconsistencies(config_analyses):
    """
    Compare multiple config files to find values that should match but don't.
    This catches the bug where the UI updates config A but the server reads config B.
    """

    inconsistencies = []

    # Collect all key-value pairs across all configs
    all_keys = {}  # key -> {config_file: value, config_file: value}

    for analysis in config_analyses:
        if not analysis["valid_format"]:
            continue

        config_file = analysis["path"]
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())

            if isinstance(data, dict):
                for key, value in data.items():
                    if key not in all_keys:
                        all_keys[key] = {}
                    all_keys[key][config_file] = value
        except Exception:
            continue

    # Find keys that appear in multiple configs with different values
    for key, sources in all_keys.items():
        if len(sources) > 1:
            values = list(sources.values())
            if not all(v == values[0] for v in values):
                inconsistency = f"Key '{key}' has different values across configs:"
                for config_file, value in sources.items():
                    inconsistency += f"\n    {config_file}: {value}"
                inconsistencies.append(inconsistency)

    if inconsistencies:
        print(f"[CONFIG] INCONSISTENCIES FOUND:")
        for inc in inconsistencies:
            print(f"[CONFIG]   {inc}")
    else:
        print(f"[CONFIG] All configs are consistent")

    return inconsistencies
```

### Step 4.4: Sync configs

```python
def sync_configs(config_files, master_config_path):
    """
    Synchronize all config files using one as the master/source of truth.

    IMPORTANT: Identify which config the SERVER actually reads.
    That should be the master. All others should match it.
    """

    print(f"[CONFIG] Master config: {master_config_path}")

    try:
        with open(master_config_path, 'r', encoding='utf-8') as f:
            master_data = json.loads(f.read())
    except Exception as e:
        print(f"[CONFIG] ERROR: Cannot read master config: {e}")
        return

    for config_file in config_files:
        if config_file == master_config_path:
            continue

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                other_data = json.loads(f.read())

            # Update shared keys to match master
            updated = False
            for key in master_data:
                if key in other_data and other_data[key] != master_data[key]:
                    print(f"[CONFIG] Syncing {config_file}: '{key}' = '{master_data[key]}' (was '{other_data[key]}')")
                    other_data[key] = master_data[key]
                    updated = True

            if updated:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(other_data, f, indent=4)
                print(f"[CONFIG] Updated: {config_file}")
            else:
                print(f"[CONFIG] Already in sync: {config_file}")

        except Exception as e:
            print(f"[CONFIG] ERROR syncing {config_file}: {e}")
```

---

## PHASE 5: SERVER-SIDE ERROR INVESTIGATION

When the server returns a 500 error, the problem is inside the server, not in your request. But your request might have triggered it.

### Step 5.1: Read the server's logs

```python
def investigate_server_error(response, server_log_paths=None):
    """
    When you get a 500 error, investigate the server side.
    """

    print(f"\n[SERVER] === SERVER ERROR INVESTIGATION ===")
    print(f"[SERVER] Status: {response.status_code}")
    print(f"[SERVER] Response body:\n{response.text[:1000]}")

    # Check response body for clues
    body = response.text

    clues = []

    if "traceback" in body.lower() or "error" in body.lower():
        clues.append("Server returned an error traceback - read it bottom-up (same as Python stack traces)")

    if "file" in body.lower() and "not found" in body.lower():
        clues.append("A file the server tried to access doesn't exist - check file paths in configs and payload")

    if "permission" in body.lower() or "denied" in body.lower():
        clues.append("The server doesn't have permission to access something - check file/directory permissions")

    if "memory" in body.lower() or "oom" in body.lower():
        clues.append("Server ran out of memory - the operation may need more RAM than available")

    if "timeout" in body.lower():
        clues.append("An operation inside the server timed out - it may be waiting on another service")

    if "database" in body.lower() or "sql" in body.lower():
        clues.append("Database error - check if the database is running and accessible")

    if "import" in body.lower() and "error" in body.lower():
        clues.append("The server is missing a Python module - check its virtual environment")

    for clue in clues:
        print(f"[SERVER] CLUE: {clue}")

    # Check server logs if paths are provided
    if server_log_paths:
        print(f"\n[SERVER] Checking server logs...")
        for log_path in server_log_paths:
            check_server_log(log_path)

def check_server_log(log_path):
    """Read the last N lines of a server log looking for errors"""
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Get last 50 lines
        recent_lines = lines[-50:]

        error_lines = []
        for line in recent_lines:
            if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'fatal', 'critical']):
                error_lines.append(line.strip())

        if error_lines:
            print(f"[SERVER] Errors in {log_path}:")
            for line in error_lines:
                print(f"[SERVER]   {line}")
        else:
            print(f"[SERVER] No errors in last 50 lines of {log_path}")

    except FileNotFoundError:
        print(f"[SERVER] Log file not found: {log_path}")
    except Exception as e:
        print(f"[SERVER] Cannot read log: {e}")
```

### Step 5.2: Test with minimal payload

```python
def test_minimal_payload(endpoint_url, format_type='json', timeout=10):
    """
    When the server crashes on your request, strip it down to the minimum.
    Find the smallest request that still causes the error.
    """

    # Start with the absolute minimum - empty request
    payloads_to_test = [
        ("Empty", {}),
        ("One required field", None),  # Fill this in based on API docs
    ]

    print(f"\n[MINIMAL] Testing minimal payloads to isolate the problem...")

    for name, payload in payloads_to_test:
        if payload is None:
            continue

        try:
            if format_type == 'json':
                response = requests.post(endpoint_url, json=payload, timeout=timeout)
            else:
                response = requests.post(endpoint_url, data=payload, timeout=timeout)

            print(f"[MINIMAL] '{name}' -> {response.status_code}")
            if response.status_code >= 400:
                print(f"[MINIMAL]   Response: {response.text[:200]}")
        except Exception as e:
            print(f"[MINIMAL] '{name}' -> ERROR: {e}")

    print(f"\n[MINIMAL] Now add fields one at a time until the error appears.")
    print(f"[MINIMAL] The field that causes the error is where the bug is.")
```

---

## PHASE 6: AUTHENTICATION AND HEADERS

If the API requires authentication, this phase checks that everything is set up correctly.

### Step 6.1: Check authentication

```python
def check_authentication(endpoint_url, auth_config=None, timeout=10):
    """
    Test different authentication methods.
    """

    print(f"\n[AUTH] === AUTHENTICATION CHECK ===")

    # Test 1: No auth at all
    try:
        response = requests.get(endpoint_url, timeout=timeout)
        print(f"[AUTH] No auth: {response.status_code}")
        if response.status_code == 200:
            print(f"[AUTH] Endpoint does NOT require authentication")
            return
        elif response.status_code == 401:
            print(f"[AUTH] Endpoint REQUIRES authentication (401 without credentials)")
        elif response.status_code == 403:
            print(f"[AUTH] Endpoint REQUIRES authentication (403 without credentials)")
    except Exception as e:
        print(f"[AUTH] No auth test failed: {e}")

    if not auth_config:
        print(f"[AUTH] No auth config provided. Check for:")
        print(f"[AUTH]   - API key in environment variable")
        print(f"[AUTH]   - Token in a config file")
        print(f"[AUTH]   - Username/password in .env file")
        return

    # Test 2: API key in header
    if 'api_key' in auth_config:
        headers_to_try = [
            ("Authorization: Bearer", {"Authorization": f"Bearer {auth_config['api_key']}"}),
            ("X-API-Key", {"X-API-Key": auth_config['api_key']}),
            ("Authorization: ApiKey", {"Authorization": f"ApiKey {auth_config['api_key']}"}),
        ]

        for header_name, headers in headers_to_try:
            try:
                response = requests.get(endpoint_url, headers=headers, timeout=timeout)
                print(f"[AUTH] {header_name}: {response.status_code}")
                if response.status_code == 200:
                    print(f"[AUTH] SUCCESS: Use header format '{header_name}'")
                    return
            except Exception as e:
                print(f"[AUTH] {header_name}: ERROR - {e}")

    print(f"[AUTH] No authentication method worked. Check API documentation for correct auth format.")
```

### Step 6.2: Check required headers

```python
def check_required_headers(endpoint_url, payload, timeout=10):
    """
    Some APIs require specific headers beyond authentication.
    """

    common_headers = [
        {"Content-Type": "application/json"},
        {"Content-Type": "application/x-www-form-urlencoded"},
        {"Accept": "application/json"},
        {"Content-Type": "multipart/form-data"},
    ]

    print(f"\n[HEADERS] Testing common headers...")

    # Baseline without extra headers
    try:
        response = requests.post(endpoint_url, json=payload, timeout=timeout)
        print(f"[HEADERS] No extra headers: {response.status_code}")
    except Exception as e:
        print(f"[HEADERS] Baseline failed: {e}")

    # Test each header
    for headers in common_headers:
        try:
            response = requests.post(endpoint_url, json=payload, headers=headers, timeout=timeout)
            header_name = list(headers.keys())[0]
            header_value = list(headers.values())[0]
            print(f"[HEADERS] {header_name}: {header_value} -> {response.status_code}")
        except Exception as e:
            print(f"[HEADERS] {headers}: ERROR - {e}")
```

---

## SUMMARY: THE API TROUBLESHOOTING ORDER

Run these phases in order. Stop as soon as you find the problem.

| Phase | What you're checking | If it fails |
|-------|---------------------|-------------|
| **1. Is it alive?** | Process running, port open, HTTP responds, endpoint exists | Start the server, fix the port, fix the URL |
| **2. Right format?** | JSON vs Form Data vs URL Encoded | Switch to the format that gets 200 |
| **3. Right data?** | Payload values, required fields, data types, file paths | Fix the payload values |
| **4. Configs in sync?** | All config files have consistent, non-placeholder values | Sync configs to match the master |
| **5. Server error?** | Read server logs, test minimal payload, isolate the crashing field | Fix server-side issue or the field causing the crash |
| **6. Auth and headers?** | API key, token, required headers | Fix authentication setup |

NO SHORTCUTS. NO WORKAROUNDS. NO DUMMIES. NO PLACEHOLDERS. NO STUBS. NO NUBS.
