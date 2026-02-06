# Systematic Troubleshooting Process for Freedom System

This document establishes a systematic troubleshooting methodology based on systematic principles and successful resolution patterns from the Freedom System project.

---

## 🛡️ DISCIPLINE ENFORCEMENT STANDARDS

**CRITICAL**: These standards prevent quick-fix behaviors and ensure systematic troubleshooting:

### Anti-Pattern Prevention
You MUST NOT exhibit these behaviors:
- **Assumption-Based Solutions**: NEVER propose fixes based on assumptions without verification
- **Architecture Abandonment**: NEVER suggest switching architectures as a first solution
- **Design Disrespect**: NEVER ignore documented design decisions without understanding why they exist
- **Quick Fixes**: NEVER implement workarounds that bypass the actual problem
- **Placeholder Values**: NEVER use temporary or placeholder values as solutions

### Required Discipline
Before proposing ANY solution:
- Verify the problem with actual tests, not assumptions
- Respect existing architecture - understand before changing
- Address root causes, not symptoms

---

## 🔍 CORE TROUBLESHOOTING METHODOLOGY

The systematic approach follows five essential phases:

### Phase 1: Problem Definition
**Ask yourself:** "What exactly is failing and how do I know it's failing?"

```python
def define_problem():
    """Systematic problem definition questions"""
    questions = [
        "What are the specific symptoms?",
        "What was the expected behavior?",
        "When did this start happening?",
        "What changed recently?",
        "Can I reproduce this reliably?",
        "What error messages are shown?",
        "What do the logs actually say?"
    ]

    for question in questions:
        print(f"[ANALYSIS] {question}")
        # Document each answer before proceeding
```

⚠️ **MANDATORY VERIFICATION**:
- You MUST run actual commands to reproduce the issue before proceeding
- You MUST NOT proceed to Phase 2 until you have actual error output
- You MUST NOT say "probably" or "likely" - verify or say "unknown"

### Creating a Minimal Reproducible Example
**After reproducing the bug, SHRINK it:**

```python
def create_minimal_example():
    """Reduce the problem to its smallest form"""

    # Step 1: Start with the full failing code
    # Step 2: Remove half the code - does bug remain?
    # Step 3: If yes, remove another half. If no, add back last removed piece.
    # Step 4: Repeat until you have the SMALLEST code that still fails

    # Example process:
    original_code_lines = 500  # Full file
    after_removal_1 = 250      # Removed imports, unrelated functions
    after_removal_2 = 125      # Removed error handling, logging
    after_removal_3 = 60       # Removed configuration loading
    minimal_example = 15       # Just the core bug - NOW you can see it clearly
```

⚠️ **MINIMAL EXAMPLE RULES**:
- Remove everything that doesn't affect whether the bug appears
- If removing something makes the bug disappear, that code is involved
- A 15-line example is easier to debug than a 500-line file
- Share minimal examples when asking for help - others can actually read them

### Phase 2: Analysis and Investigation
**Ask yourself:** "What are all the possible causes and how can I test them?"

**30-Second Obvious Issues Checklist** (check these FIRST):
- [ ] Typo in variable or function name?
- [ ] Editing the correct file? (check file path)
- [ ] File saved after changes?
- [ ] Server/process restarted after code changes?
- [ ] Cache cleared? (browser, Python `__pycache__`, etc.)
- [ ] Correct git branch checked out?
- [ ] Import statement present for the module you're using?
- [ ] Syntax error earlier in the file breaking later code?

```python
def systematic_investigation():
    """Multi-layer analysis approach"""

    # Layer 1: Surface level analysis - USE THE CHECKLIST ABOVE FIRST
    print("[ANALYSIS] Checking obvious issues...")
    check_obvious_failures()

    # Layer 2: System level analysis
    print("[ANALYSIS] Examining system interactions...")
    analyze_component_interactions()

    # Layer 3: Deep architecture analysis
    print("[ANALYSIS] Investigating architectural patterns...")
    examine_underlying_architecture()

    # Layer 4: Root cause analysis
    print("[ANALYSIS] Finding fundamental cause...")
    trace_to_root_cause()
```

⚠️ **INVESTIGATION REQUIREMENTS**:
- You MUST test each possible cause with real commands
- You MUST NOT skip investigation layers even if you think you know the answer
- You MUST show command output that proves/disproves each hypothesis

### Binary Search Debugging
**When you can't find where the bug is, use divide-and-conquer:**

```python
def binary_search_debugging():
    """Find the bug location by eliminating half the code at a time"""

    # Method 1: Comment out half the code
    # - Comment out the bottom half of your function
    # - Does the bug still happen?
    #   - YES: Bug is in the top half. Comment out half of THAT.
    #   - NO: Bug is in the bottom half. Uncomment and comment out top half.
    # - Repeat until you find the exact line

    # Method 2: Add a return/exit midway
    def buggy_function():
        step_1()
        step_2()
        return  # <-- Add this temporarily. Bug still happens?
        step_3()  # If no bug, problem is below the return
        step_4()

    # Method 3: Print checkpoints
    def find_where_it_breaks():
        print("Checkpoint 1")  # See this?
        some_operation()
        print("Checkpoint 2")  # See this?
        another_operation()
        print("Checkpoint 3")  # If you see 2 but not 3, bug is in another_operation()
```

⚠️ **BINARY SEARCH TIPS**:
- This finds bugs in minutes, not hours
- Works for "it just stopped working" problems
- Works for "it works sometimes" problems (narrow down the conditions)
- Remove your debug code after finding the bug

### Phase 3: Solution Generation
**Ask yourself:** "What are multiple ways to solve this and which is most robust?"

⚠️ **SOLUTION DISCIPLINE**:
- You MUST NOT implement quick fixes that bypass the problem
- You MUST NOT use placeholder values or workarounds or dummy code or shortcuts or stubs or nubs
- You MUST first understand WHY the current architecture was chosen
- The proper_fix MUST address the root cause, not symptoms

```python
def generate_solutions():
    """Create solution approaches - NO quick fixes or workarounds or dummy code or shortcuts or stubs or nubs"""

    # First, understand the current architecture
    print("[ANALYSIS] Understanding why current architecture was chosen...")
    print("[ANALYSIS] Ask user: Where should I look for design decisions? (analysis.md, README, commit history?)")
    research_current_design_rationale()

    solutions = {
        # "immediate_fix" - REMOVED: No quick patches allowed
        "proper_fix": "Address root cause systematically",
        "architecture_correction": "If proven wrong, implement correct architecture",
        "preventive_measures": "Prevent recurrence",
        "monitoring_improvements": "Detect similar issues faster"
    }

    for solution_type, description in solutions.items():
        print(f"[SOLUTION] {solution_type}: {description}")
```

### Phase 4: User Approval
**Ask yourself:** "Have I clearly explained my proposed solution and received user approval?"

⚠️ **MANDATORY USER APPROVAL**:
- You MUST NOT implement any solution without explicit user approval
- You MUST present solutions in plain language (no jargon without explanation)
- You MUST wait for user response before proceeding

**Requirements:**
1. Present the solution(s) you have identified in clear, accessible language - the user is an adult, not a student, so be direct and concise without being condescending
2. Be prepared to answer questions from the user about the proposed solution
3. Wait for the user to explicitly approve a solution before moving to implementation

```python
def get_user_approval():
    """Present solution and wait for user approval"""

    # Present solution clearly
    print("[SOLUTION] Here is what I found and propose to fix:")
    print("[SOLUTION] Problem: <clear description>")
    print("[SOLUTION] Root cause: <clear explanation>")
    print("[SOLUTION] Proposed fix: <what will be changed>")
    print("[SOLUTION] Files affected: <list of files>")

    # Wait for approval
    print("[WAITING] Do you approve this solution? (yes/no/questions)")
    # DO NOT PROCEED until user responds
```

### Phase 5: Implementation with Validation
**Ask yourself:** "How do I implement this safely and verify it works?"

```python
def implement_with_validation():
    """Safe implementation with validation"""

    # Pre-implementation validation
    backup_current_state()
    document_changes()
    prepare_rollback_plan()

    # Implementation
    apply_fix()

    # Post-implementation validation
    test_fix_effectiveness()
    verify_no_regressions()
    update_monitoring()
```

⚠️ **IMPLEMENTATION SAFEGUARDS**:
- You MUST test the fix in isolation first
- You MUST NOT implement without preparing rollback plan
- You MUST verify the fix addresses root cause, not just symptoms

### Phase 6: Evaluation and Prevention
**Ask yourself:** "Did this fully solve the problem and how do I prevent it happening again?"

```python
def evaluate_and_prevent():
    """Evaluation and prevention analysis"""

    # Effectiveness evaluation
    measure_problem_resolution()
    identify_remaining_risks()

    # Prevention measures
    update_standards()
    improve_monitoring()
    document_lessons_learned()
    enhance_testing_coverage()
```

⚠️ **EVALUATION REQUIREMENTS**:
- You MUST document what was actually wrong vs your initial assumptions
- You MUST identify if you made any incorrect assumptions during troubleshooting
- You MUST update docs if your understanding of the design was wrong

---

## 🛠️ ENHANCED LOGGING SYSTEM

### Universal Logging Function
**Always implement enhanced logging early in troubleshooting:**

```python
def log_enhanced(message, level="INFO", function_name="", component="SYSTEM"):
    """Enhanced logging with timestamp and function tracking"""
    import datetime

    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    prefix = f"[{component}]"

    if function_name:
        prefix = f"{prefix} [{function_name}]"

    full_message = f"{prefix} [{level}] {message}"
    print(full_message)

    # Also write to log file
    log_file = "F:/Apps/freedom_system/log/troubleshooting.log"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} {full_message}\n")
    except Exception as e:
        print(f"[LOGGING] Failed to write to log file: {e}")

# Example usage throughout troubleshooting
def troubleshoot_function():
    log_enhanced("Starting troubleshooting process", "INFO", "troubleshoot_function")

    try:
        # Investigation code here
        log_enhanced("Investigation step completed", "SUCCESS", "troubleshoot_function")
    except Exception as e:
        log_enhanced(f"Investigation failed: {str(e)}", "ERROR", "troubleshoot_function")
```

### API-Specific Enhanced Logging

```python
def log_api_request(endpoint, payload, response=None, error=None):
    """Enhanced logging for API troubleshooting"""
    import json

    log_enhanced(f"API Request to {endpoint}", "INFO", "log_api_request", "API")
    log_enhanced(f"Payload: {json.dumps(payload, indent=2)}", "DEBUG", "log_api_request", "API")

    if response:
        log_enhanced(f"Response Status: {response.status_code}", "INFO", "log_api_request", "API")
        log_enhanced(f"Response Headers: {dict(response.headers)}", "DEBUG", "log_api_request", "API")
        log_enhanced(f"Response Body: {response.text[:500]}", "DEBUG", "log_api_request", "API")

    if error:
        log_enhanced(f"API Error: {str(error)}", "ERROR", "log_api_request", "API")
        log_enhanced(f"Error Type: {type(error).__name__}", "ERROR", "log_api_request", "API")

# Example API troubleshooting with enhanced logging
def test_api_endpoint(endpoint, payload):
    log_enhanced("Starting API endpoint test", "INFO", "test_api_endpoint", "API")

    try:
        import requests
        response = requests.post(endpoint, data=payload, timeout=10)
        log_api_request(endpoint, payload, response=response)

        if response.status_code == 500:
            log_enhanced("Server Error 500 detected - investigating server logs", "WARNING", "test_api_endpoint", "API")
            investigate_server_error(response)

        return response

    except Exception as e:
        log_api_request(endpoint, payload, error=e)
        return None

def investigate_server_error(response):
    """Investigate server-side errors systematically"""
    log_enhanced("Analyzing server error response", "INFO", "investigate_server_error", "API")

    # Check for common patterns
    if "file" in response.text.lower() and "not found" in response.text.lower():
        log_enhanced("Likely file path issue detected", "WARNING", "investigate_server_error", "API")

    if "Please Refresh Settings" in response.text:
        log_enhanced("Placeholder value being used as actual parameter", "ERROR", "investigate_server_error", "API")
```

### Reading Stack Traces
**Stack traces tell you exactly where the problem is - if you know how to read them:**

```python
# Example stack trace:
"""
Traceback (most recent call last):
  File "main.py", line 45, in start_server        <-- (3) Origin: where it started
    initialize_components()
  File "components.py", line 123, in initialize   <-- (2) Middle: the path it took
    load_config()
  File "config.py", line 67, in load_config       <-- (1) LOOK HERE FIRST
    data = json.loads(content)
ValueError: Expecting property name: line 5       <-- The actual error
"""

# How to read it:
# 1. Start at the BOTTOM - that's the actual error message
# 2. Look at the line JUST ABOVE the error - that's where it crashed
# 3. The crash line often isn't the bug - look at what DATA went into it
# 4. YOUR code matters more than library code (json, requests, etc.)
```

⚠️ **STACK TRACE RULES**:
- The real bug is often 1-3 lines BEFORE the crash line
- If crash is in library code, your mistake is in how you called it
- "NoneType has no attribute X" = something returned None unexpectedly
- "KeyError" = dictionary doesn't have that key - print the dict to see what's there
- "IndexError" = list is shorter than you expected - print its length

---

## 🔬 DEBUGGER TECHNIQUES

### Using Python Debuggers
**Debuggers let you pause code mid-run and inspect everything:**

```python
def function_with_bug():
    data = fetch_some_data()

    breakpoint()  # <-- Code STOPS here. You can now inspect 'data'

    # In the debugger prompt:
    # (Pdb) print(data)        # See what data contains
    # (Pdb) print(type(data))  # See its type
    # (Pdb) n                  # Execute next line
    # (Pdb) c                  # Continue running
    # (Pdb) q                  # Quit debugger

    result = process(data)
    return result
```

**Common Debugger Commands (pdb):**
| Command | What it does |
|---------|--------------|
| `n` | Next line (step over) |
| `s` | Step into function |
| `c` | Continue until next breakpoint |
| `p variable` | Print variable value |
| `pp variable` | Pretty-print (for dicts/lists) |
| `l` | Show code around current line |
| `q` | Quit debugger |

⚠️ **DEBUGGER TIPS**:
- Better than print statements for complex bugs
- Can inspect ANY variable at the pause point
- Remove `breakpoint()` before committing code
- VS Code has visual debugging - even easier

---

## 📂 GIT TROUBLESHOOTING

### Using Git to Find Bugs
**Git history often reveals when and why things broke:**

```bash
# What changed recently?
git diff                     # Uncommitted changes
git diff HEAD~3              # Changes in last 3 commits
git log --oneline -10        # Last 10 commit messages

# When did this file change?
git log --oneline -5 -- path/to/file.py

# What did a specific commit change?
git show abc1234

# Test if bug exists in older version
git stash                    # Save current work
git checkout HEAD~5          # Go back 5 commits
# Test here - does bug exist?
git checkout -               # Go back to where you were
git stash pop                # Restore your work

# Find exactly which commit introduced the bug
git bisect start
git bisect bad               # Current version has bug
git bisect good abc1234      # This old commit was good
# Git will checkout middle commits for you to test
# After each test, run: git bisect good OR git bisect bad
# Git finds the breaking commit automatically
```

⚠️ **GIT SAFETY**:
- Never run `git reset --hard` or `git clean -f` without understanding what you'll lose
- Use `git stash` to save work before experimenting
- `git reflog` can recover "lost" commits for 30 days

---

## 🎯 SYSTEMATIC QUESTIONING FRAMEWORK

### Self-Questioning Process
**Always ask these questions in sequence:**

```python
def systematic_self_questions():
    """Framework for systematic self-questioning during troubleshooting"""

    problem_definition_questions = [
        "What exactly is the error message?",
        "What was I trying to accomplish?",
        "What should have happened instead?",
        "Can I reproduce this error consistently?",
        "What were the exact steps that led to this error?"
    ]

    analysis_questions = [
        "What components are involved in this operation?",
        "Which component is actually failing?",
        "Are there multiple systems that need to communicate?",
        "What assumptions am I making that might be wrong?",
        "Am I looking at the right logs/files?",
        "Are there other similar systems I can compare against?"
    ]

    solution_questions = [
        "What are 3 different ways I could solve this?",
        "Which solution addresses the root cause vs. just symptoms?",
        "What could go wrong with each solution approach?",
        "How will I know if the solution actually worked?",
        "What would prevent this problem from happening again?"
    ]

    validation_questions = [
        "Did the fix actually solve the original problem?",
        "Did I break anything else in the process?",
        "Can I reproduce the success consistently?",
        "What would I do differently if this happens again?",
        "How can I improve monitoring to catch this sooner?"
    ]

# Use this framework during troubleshooting
def apply_questioning_framework():
    log_enhanced("Starting systematic questioning process", "INFO", "apply_questioning_framework")

    for phase, questions in [
        ("Problem Definition", problem_definition_questions),
        ("Analysis", analysis_questions),
        ("Solution Generation", solution_questions),
        ("Validation", validation_questions)
    ]:
        log_enhanced(f"Phase: {phase}", "INFO", "apply_questioning_framework")
        for i, question in enumerate(questions, 1):
            log_enhanced(f"Question {i}: {question}", "INFO", "apply_questioning_framework")
            # Pause here to actually answer each question before proceeding
```

### Rubber Duck Debugging
**When stuck, explain the problem out loud:**

The act of explaining forces you to slow down and often reveals the answer.

**How to do it:**
1. Get a rubber duck (or any object, or a coworker, or a text file)
2. Explain what your code is SUPPOSED to do, line by line
3. Explain what it's ACTUALLY doing
4. The mismatch often becomes obvious while explaining

```python
# Example rubber duck session (talking out loud or typing):
"""
OK duck, this function should:
1. Read the config file... wait, does the file exist? Let me check...
2. Parse the JSON... hmm, what if the JSON is malformed?
3. Return the 'api_key' field... oh. I'm looking for 'api_key' but
   I named it 'apiKey' in the config file. THAT'S the bug.
"""
```

⚠️ **WHEN TO USE RUBBER DUCK**:
- You've been stuck for 15+ minutes
- You're going in circles trying the same things
- The bug "makes no sense"
- Before asking a coworker (often solves it without bothering them)

---

## 🌐 API-SPECIFIC TROUBLESHOOTING PROCESS

### API Connection and Communication Issues

```python
def troubleshoot_api_connectivity():
    """Systematic API connectivity troubleshooting"""

    log_enhanced("Starting API connectivity troubleshooting", "INFO", "troubleshoot_api_connectivity", "API")

    # Phase 1: Basic connectivity
    connectivity_checks = [
        ("Server Process Check", check_server_process_running),
        ("Port Availability", check_port_availability),
        ("Basic HTTP Response", check_basic_http_response),
        ("API Endpoint Availability", check_api_endpoints)
    ]

    for check_name, check_function in connectivity_checks:
        log_enhanced(f"Running check: {check_name}", "INFO", "troubleshoot_api_connectivity", "API")
        try:
            result = check_function()
            log_enhanced(f"Check result: {result}", "INFO" if result else "WARNING", "troubleshoot_api_connectivity", "API")
        except Exception as e:
            log_enhanced(f"Check failed: {str(e)}", "ERROR", "troubleshoot_api_connectivity", "API")

    # Phase 2: API request format validation
    log_enhanced("Validating API request formats", "INFO", "troubleshoot_api_connectivity", "API")
    test_api_formats()

    # Phase 3: Response analysis
    log_enhanced("Analyzing API responses", "INFO", "troubleshoot_api_connectivity", "API")
    analyze_api_responses()

def check_server_process_running():
    """Check if server process is actually running"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:7851/api/ready", timeout=3)
        return response.status_code == 200
    except Exception as e:
        log_enhanced(f"Server process check failed: {e}", "ERROR", "check_server_process_running", "API")
        return False

def test_api_formats():
    """Test different API request formats to identify correct one"""
    test_payload = {"text_input": "Test message", "voice": "female_01.wav"}

    formats_to_test = [
        ("JSON", lambda: requests.post("http://127.0.0.1:7851/api/tts-generate", json=test_payload)),
        ("Form Data", lambda: requests.post("http://127.0.0.1:7851/api/tts-generate", data=test_payload)),
        ("URL Encoded", lambda: requests.post("http://127.0.0.1:7851/api/tts-generate", data=test_payload, headers={"Content-Type": "application/x-www-form-urlencoded"}))
    ]

    for format_name, request_func in formats_to_test:
        try:
            log_enhanced(f"Testing {format_name} format", "INFO", "test_api_formats", "API")
            response = request_func()
            log_enhanced(f"{format_name} result: {response.status_code}", "INFO", "test_api_formats", "API")

            if response.status_code != 200:
                log_enhanced(f"{format_name} error response: {response.text[:200]}", "WARNING", "test_api_formats", "API")
        except Exception as e:
            log_enhanced(f"{format_name} format failed: {str(e)}", "ERROR", "test_api_formats", "API")
```

### Configuration Troubleshooting for APIs

```python
def troubleshoot_configuration_sync():
    """Systematic configuration troubleshooting for API systems"""

    log_enhanced("Starting configuration sync troubleshooting", "INFO", "troubleshoot_configuration_sync", "CONFIG")

    # Phase 1: Discovery - find all configuration files
    log_enhanced("Phase 1: Discovering configuration files", "INFO", "troubleshoot_configuration_sync", "CONFIG")
    config_files = discover_all_config_files()

    for config_file in config_files:
        log_enhanced(f"Found config file: {config_file}", "INFO", "troubleshoot_configuration_sync", "CONFIG")

    # Phase 2: Analysis - examine each configuration
    log_enhanced("Phase 2: Analyzing configuration contents", "INFO", "troubleshoot_configuration_sync", "CONFIG")
    config_analysis = {}

    for config_file in config_files:
        analysis = analyze_config_file(config_file)
        config_analysis[config_file] = analysis

        log_enhanced(f"Config analysis for {config_file}:", "INFO", "troubleshoot_configuration_sync", "CONFIG")
        for key, value in analysis.items():
            log_enhanced(f"  {key}: {value}", "INFO", "troubleshoot_configuration_sync", "CONFIG")

    # Phase 3: Validation - check for inconsistencies
    log_enhanced("Phase 3: Validating configuration consistency", "INFO", "troubleshoot_configuration_sync", "CONFIG")
    inconsistencies = find_config_inconsistencies(config_analysis)

    if inconsistencies:
        log_enhanced("Configuration inconsistencies found:", "WARNING", "troubleshoot_configuration_sync", "CONFIG")
        for inconsistency in inconsistencies:
            log_enhanced(f"  {inconsistency}", "WARNING", "troubleshoot_configuration_sync", "CONFIG")
    else:
        log_enhanced("No configuration inconsistencies found", "INFO", "troubleshoot_configuration_sync", "CONFIG")

    # Phase 4: Solution - synchronize configurations
    if inconsistencies:
        log_enhanced("Phase 4: Synchronizing configurations", "INFO", "troubleshoot_configuration_sync", "CONFIG")
        synchronize_all_configs(config_files)

def discover_all_config_files():
    """Discover all configuration files in the system"""
    import os
    from pathlib import Path

    search_patterns = [
        "**/*config*.json",
        "**/*settings*.json",
        "**/*.conf",
        "**/config.yaml",
        "**/settings.yaml"
    ]

    config_files = []
    base_path = Path(".")

    for pattern in search_patterns:
        for file_path in base_path.glob(pattern):
            if file_path.is_file():
                config_files.append(str(file_path))

    return config_files

def analyze_config_file(config_file):
    """Analyze a configuration file for common issues"""
    import json

    analysis = {
        "exists": os.path.exists(config_file),
        "readable": False,
        "valid_json": False,
        "placeholder_values": [],
        "missing_files": [],
        "key_count": 0
    }

    if not analysis["exists"]:
        return analysis

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            analysis["readable"] = True

        config_data = json.loads(content)
        analysis["valid_json"] = True
        analysis["key_count"] = len(config_data) if isinstance(config_data, dict) else 0

        # Check for placeholder values
        placeholder_values = ["Please Refresh Settings", "Select...", "Choose...", ""]
        analysis["placeholder_values"] = find_placeholder_values(config_data, placeholder_values)

        # Check for file references
        analysis["missing_files"] = find_missing_file_references(config_data)

    except Exception as e:
        log_enhanced(f"Error analyzing config file {config_file}: {str(e)}", "ERROR", "analyze_config_file", "CONFIG")

    return analysis

def find_placeholder_values(data, placeholders, path=""):
    """Recursively find placeholder values in configuration"""
    found_placeholders = []

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if value in placeholders:
                found_placeholders.append(f"{current_path} = '{value}'")
            elif isinstance(value, (dict, list)):
                found_placeholders.extend(find_placeholder_values(value, placeholders, current_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]"
            if item in placeholders:
                found_placeholders.append(f"{current_path} = '{item}'")
            elif isinstance(item, (dict, list)):
                found_placeholders.extend(find_placeholder_values(item, placeholders, current_path))

    return found_placeholders
```

---

## 🔧 NON-API SPECIFIC TROUBLESHOOTING PROCESS

### File System and Path Issues

```python
def troubleshoot_file_system_issues():
    """Systematic file system troubleshooting"""

    log_enhanced("Starting file system troubleshooting", "INFO", "troubleshoot_file_system_issues", "FILESYSTEM")

    # Phase 1: Path validation
    log_enhanced("Phase 1: Validating file paths", "INFO", "troubleshoot_file_system_issues", "FILESYSTEM")
    validate_all_file_paths()

    # Phase 2: Permission checks
    log_enhanced("Phase 2: Checking file permissions", "INFO", "troubleshoot_file_system_issues", "FILESYSTEM")
    check_file_permissions()

    # Phase 3: Disk space and accessibility
    log_enhanced("Phase 3: Checking disk space and accessibility", "INFO", "troubleshoot_file_system_issues", "FILESYSTEM")
    check_disk_accessibility()

    # Phase 4: File locking issues
    log_enhanced("Phase 4: Checking for file locking issues", "INFO", "troubleshoot_file_system_issues", "FILESYSTEM")
    check_file_locks()

def validate_all_file_paths():
    """Validate all file paths referenced in the system"""
    import os
    from pathlib import Path

    # Common file paths to check
    critical_paths = [
        "F:/Apps/freedom_system/log/",
        "voices/",
        "models/",
        "configs/",
        "temp/"
    ]

    for path in critical_paths:
        path_obj = Path(path)
        log_enhanced(f"Checking path: {path}", "INFO", "validate_all_file_paths", "FILESYSTEM")

        if path_obj.exists():
            if path_obj.is_dir():
                file_count = len(list(path_obj.iterdir()))
                log_enhanced(f"Directory exists with {file_count} items", "INFO", "validate_all_file_paths", "FILESYSTEM")
            else:
                file_size = path_obj.stat().st_size
                log_enhanced(f"File exists, size: {file_size} bytes", "INFO", "validate_all_file_paths", "FILESYSTEM")
        else:
            log_enhanced(f"Path does not exist: {path}", "WARNING", "validate_all_file_paths", "FILESYSTEM")

            # Ask: Should this path be created?
            if path.endswith("/"):  # Directory
                log_enhanced(f"Should directory be created? {path}", "QUESTION", "validate_all_file_paths", "FILESYSTEM")
```

### Import and Dependency Issues

```python
def troubleshoot_import_issues():
    """Systematic import and dependency troubleshooting"""

    log_enhanced("Starting import troubleshooting", "INFO", "troubleshoot_import_issues", "IMPORTS")

    # Phase 1: Python path investigation
    log_enhanced("Phase 1: Investigating Python paths", "INFO", "troubleshoot_import_issues", "IMPORTS")
    investigate_python_paths()

    # Phase 2: Module availability check
    log_enhanced("Phase 2: Checking module availability", "INFO", "troubleshoot_import_issues", "IMPORTS")
    check_module_availability()

    # Phase 3: Circular import detection
    log_enhanced("Phase 3: Detecting circular imports", "INFO", "troubleshoot_import_issues", "IMPORTS")
    detect_circular_imports()

    # Phase 4: Version compatibility
    log_enhanced("Phase 4: Checking version compatibility", "INFO", "troubleshoot_import_issues", "IMPORTS")
    check_version_compatibility()

def investigate_python_paths():
    """Investigate Python path configuration"""
    import sys

    log_enhanced(f"Python executable: {sys.executable}", "INFO", "investigate_python_paths", "IMPORTS")
    log_enhanced(f"Python version: {sys.version}", "INFO", "investigate_python_paths", "IMPORTS")

    log_enhanced("Python path entries:", "INFO", "investigate_python_paths", "IMPORTS")
    for i, path in enumerate(sys.path):
        log_enhanced(f"  {i}: {path}", "INFO", "investigate_python_paths", "IMPORTS")

    # Check current working directory
    import os
    log_enhanced(f"Current working directory: {os.getcwd()}", "INFO", "investigate_python_paths", "IMPORTS")

def check_module_availability():
    """Check availability of critical modules"""
    critical_modules = [
        "requests", "json", "os", "sys", "pathlib", "datetime",
        "subprocess", "signal", "atexit", "threading", "time"
    ]

    for module_name in critical_modules:
        try:
            __import__(module_name)
            log_enhanced(f"Module available: {module_name}", "INFO", "check_module_availability", "IMPORTS")
        except ImportError as e:
            log_enhanced(f"Module missing: {module_name} - {str(e)}", "ERROR", "check_module_availability", "IMPORTS")
        except Exception as e:
            log_enhanced(f"Module import error: {module_name} - {str(e)}", "WARNING", "check_module_availability", "IMPORTS")
```

### Environment Differences ("Works on My Machine")
**When code works in one place but not another, check these:**

**Quick Environment Checklist:**
- [ ] Python version match? (`python --version`)
- [ ] Virtual environment activated? (check prompt prefix)
- [ ] Same packages installed? (`pip freeze` vs requirements.txt)
- [ ] Environment variables set? (`echo %VAR_NAME%` on Windows, `echo $VAR_NAME` on Linux)
- [ ] Database/service running and accessible?
- [ ] File paths correct? (Windows `\` vs Linux `/`)
- [ ] Permissions correct? (especially on Linux)
- [ ] Same working directory when running?

```python
def diagnose_environment_differences():
    """Print environment info for comparison between machines"""
    import sys
    import os

    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"CWD: {os.getcwd()}")
    print(f"PATH entries: {len(os.environ.get('PATH', '').split(os.pathsep))}")

    # Check critical environment variables
    critical_vars = ['HOME', 'USER', 'VIRTUAL_ENV', 'PYTHONPATH']
    for var in critical_vars:
        print(f"{var}: {os.environ.get(var, 'NOT SET')}")

    # Check if key files exist
    key_files = ['config.json', '.env', 'requirements.txt']
    for f in key_files:
        print(f"{f}: {'EXISTS' if os.path.exists(f) else 'MISSING'}")
```

⚠️ **COMMON ENVIRONMENT TRAPS**:
- Hardcoded absolute paths that only exist on one machine
- Missing `.env` file (often not committed to git)
- Different line endings (Windows CRLF vs Linux LF)
- Case sensitivity (Windows ignores case, Linux doesn't)

---

## 🎯 SUCCESSFUL RESOLUTION PATTERNS

### Pattern 1: The "Please Refresh Settings" Issue Resolution

```python
def pattern_placeholder_value_resolution():
    """
    Pattern: Placeholder values being used as actual parameters

    Problem Signs:
    - Error logs showing "Please Refresh Settings" in file paths
    - UI showing placeholder text instead of actual values
    - 500 errors from API calls with invalid parameters

    Investigation Process:
    1. Search for all occurrences of placeholder text in codebase
    2. Identify where placeholder values are initialized
    3. Trace the flow from initialization to actual usage
    4. Find the gap between UI updates and actual parameter usage

    Root Cause Discovery:
    - Default/fallback values set to placeholder text
    - Configuration not synchronized between UI and backend
    - Resource discovery not running properly on startup

    Solution Pattern:
    1. Replace placeholder defaults with actual valid defaults
    2. Implement resource discovery and synchronization
    3. Add validation to prevent placeholder usage
    4. Implement proper error handling when resources unavailable
    """

    log_enhanced("Applying placeholder value resolution pattern", "INFO", "pattern_placeholder_value_resolution", "PATTERN")

    # Step 1: Find all placeholder values
    placeholder_locations = find_all_placeholder_occurrences()

    # Step 2: Replace with valid defaults
    for location in placeholder_locations:
        replace_placeholder_with_valid_default(location)

    # Step 3: Add validation
    add_placeholder_validation()

    # Step 4: Implement resource sync
    implement_resource_synchronization()

def find_all_placeholder_occurrences():
    """Find all occurrences of placeholder values in code and configs"""
    import os
    import re

    placeholder_patterns = [
        "Please Refresh Settings",
        "Select...",
        "Choose...",
        "Loading..."
    ]

    occurrences = []

    # Search in Python files
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(('.py', '.json')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    for pattern in placeholder_patterns:
                        if pattern in content:
                            occurrences.append({
                                "file": file_path,
                                "placeholder": pattern,
                                "context": extract_context_around_match(content, pattern)
                            })

                except Exception as e:
                    log_enhanced(f"Error searching file {file_path}: {e}", "WARNING", "find_all_placeholder_occurrences", "PATTERN")

    return occurrences

def replace_placeholder_with_valid_default(location):
    """Replace placeholder with valid default value"""
    log_enhanced(f"Replacing placeholder in {location['file']}: {location['placeholder']}", "INFO", "replace_placeholder_with_valid_default", "PATTERN")

    # Determine appropriate default based on context
    if "voice" in location['context'].lower():
        default_value = "female_01.wav"  # Valid voice file
    elif "model" in location['context'].lower():
        default_value = "xtts"  # Valid model name
    elif "engine" in location['context'].lower():
        default_value = "xtts"  # Valid engine
    else:
        default_value = "default"  # Generic safe default

    log_enhanced(f"Using default value: {default_value}", "INFO", "replace_placeholder_with_valid_default", "PATTERN")
```

### Pattern 2: Configuration Synchronization Resolution

```python
def pattern_config_sync_resolution():
    """
    Pattern: Multiple configuration files out of sync

    Problem Signs:
    - UI changes don't persist
    - Server uses different settings than UI shows
    - Refresh buttons don't work
    - Settings revert after restart

    Investigation Process:
    1. Find all configuration files in the system
    2. Determine which config the server actually reads
    3. Determine which config the UI updates
    4. Trace the synchronization (or lack thereof) between them

    Root Cause Discovery:
    - Multiple configuration files serving different components
    - UI updating one config, server reading another
    - No synchronization mechanism between configs
    - Initialization not updating all configs

    Solution Pattern:
    1. Implement configuration discovery on startup
    2. Create synchronization function for all configs
    3. Update UI handlers to sync all relevant configs
    4. Add validation to ensure configs stay synchronized
    """

    log_enhanced("Applying configuration synchronization pattern", "INFO", "pattern_config_sync_resolution", "PATTERN")

    # Step 1: Discover all configurations
    all_configs = discover_all_configuration_files()

    # Step 2: Analyze configuration relationships
    config_relationships = analyze_config_relationships(all_configs)

    # Step 3: Implement synchronization
    implement_config_synchronization(config_relationships)

    # Step 4: Update UI handlers
    update_ui_handlers_for_sync(all_configs)

def implement_config_synchronization(config_relationships):
    """Implement synchronization between related configurations"""

    def sync_all_configs():
        """Main synchronization function"""
        log_enhanced("Starting configuration synchronization", "INFO", "sync_all_configs", "CONFIG")

        # Get current resources
        resources = scan_available_resources()

        # Update each configuration file
        for config_file, update_function in config_relationships.items():
            try:
                log_enhanced(f"Updating config: {config_file}", "INFO", "sync_all_configs", "CONFIG")
                update_function(config_file, resources)
            except Exception as e:
                log_enhanced(f"Failed to update {config_file}: {str(e)}", "ERROR", "sync_all_configs", "CONFIG")

        log_enhanced("Configuration synchronization complete", "INFO", "sync_all_configs", "CONFIG")

    return sync_all_configs

def scan_available_resources():
    """Scan for available resources (voices, models, etc.)"""
    from pathlib import Path

    resources = {
        "voices": [],
        "models": [],
        "engines": []
    }

    # Scan voices directory
    voices_dir = Path("voices")
    if voices_dir.exists():
        resources["voices"] = [f.name for f in voices_dir.glob("*.wav")]

    # Scan models directory
    models_dir = Path("models")
    if models_dir.exists():
        resources["models"] = [f.name for f in models_dir.glob("*")]

    # Default engines
    resources["engines"] = ["xtts", "silero", "coqui"]

    log_enhanced(f"Resources found: {resources}", "INFO", "scan_available_resources", "CONFIG")
    return resources
```

---

## 🧪 VALIDATION AND TESTING PATTERNS

### Test-Driven Troubleshooting

```python
def test_driven_troubleshooting():
    """
    Use testing to validate fixes and prevent regressions
    """

    log_enhanced("Starting test-driven troubleshooting", "INFO", "test_driven_troubleshooting", "TEST")

    # Phase 1: Reproduce the problem with a test
    log_enhanced("Phase 1: Creating test to reproduce problem", "INFO", "test_driven_troubleshooting", "TEST")
    problem_reproduction_test = create_problem_reproduction_test()

    # Verify the test fails (reproduces the problem)
    if not problem_reproduction_test():
        log_enhanced("Problem reproduction test passes - problem may be fixed or test is incorrect", "WARNING", "test_driven_troubleshooting", "TEST")
    else:
        log_enhanced("Problem successfully reproduced with test", "INFO", "test_driven_troubleshooting", "TEST")

    # Phase 2: Apply fix
    log_enhanced("Phase 2: Applying fix", "INFO", "test_driven_troubleshooting", "TEST")
    apply_fix()

    # Phase 3: Verify fix with test
    log_enhanced("Phase 3: Verifying fix", "INFO", "test_driven_troubleshooting", "TEST")
    if problem_reproduction_test():
        log_enhanced("Test still fails - fix was not effective", "ERROR", "test_driven_troubleshooting", "TEST")
    else:
        log_enhanced("Test now passes - fix appears effective", "SUCCESS", "test_driven_troubleshooting", "TEST")

    # Phase 4: Add regression tests
    log_enhanced("Phase 4: Adding regression tests", "INFO", "test_driven_troubleshooting", "TEST")
    create_regression_tests()

def create_problem_reproduction_test():
    """Create a test that reproduces the original problem"""

    def test_placeholder_value_usage():
        """Test that reproduces the placeholder value problem"""
        log_enhanced("Testing for placeholder value usage", "INFO", "test_placeholder_value_usage", "TEST")

        # Create test configuration with placeholder
        test_config = {
            "character_voice": "Please Refresh Settings",
            "narrator_voice": "Please Refresh Settings"
        }

        # Attempt to use configuration in API call
        try:
            result = make_api_call_with_config(test_config)

            # If this succeeds, the placeholder handling is working
            if result and result.status_code == 200:
                log_enhanced("Placeholder values handled correctly", "SUCCESS", "test_placeholder_value_usage", "TEST")
                return False  # Test passes (no problem)
            else:
                log_enhanced("Placeholder values caused API failure", "INFO", "test_placeholder_value_usage", "TEST")
                return True  # Test fails (problem reproduced)

        except Exception as e:
            log_enhanced(f"Placeholder usage caused exception: {str(e)}", "INFO", "test_placeholder_value_usage", "TEST")
            return True  # Test fails (problem reproduced)

    return test_placeholder_value_usage

def make_api_call_with_config(config):
    """Make API call using provided configuration"""
    import requests

    payload = {
        "text_input": "Test message",
        "character_voice_gen": config.get("character_voice", "female_01.wav"),
        "text_filtering": "standard"
    }

    try:
        response = requests.post("http://127.0.0.1:7851/api/tts-generate", data=payload, timeout=5)
        return response
    except Exception as e:
        log_enhanced(f"API call failed: {str(e)}", "ERROR", "make_api_call_with_config", "TEST")
        return None
```

---

## 📚 LESSON EXTRACTION AND DOCUMENTATION

### Post-Resolution Documentation

```python
def document_resolution_lessons():
    """Document lessons learned from successful resolutions"""

    resolution_template = {
        "problem_description": "",
        "symptoms_observed": [],
        "investigation_steps": [],
        "root_cause_discovered": "",
        "solution_implemented": "",
        "validation_performed": [],
        "prevention_measures": [],
        "patterns_identified": []
    }

    log_enhanced("Documenting resolution lessons", "INFO", "document_resolution_lessons", "DOCS")

    # Example documentation for AllTalk TTS issue
    alltalk_resolution = {
        "problem_description": "AllTalk TTS extension returning 500 errors and using placeholder values",
        "symptoms_observed": [
            "Server logs showing 'voices\\Please Refresh Settings' file path errors",
            "UI refresh button not working",
            "API calls returning HTTP 500",
            "TTS generation failing"
        ],
        "investigation_steps": [
            "Analyzed server error logs for file path issues",
            "Traced placeholder value from UI to server configuration",
            "Discovered multiple configuration files (confignew.json, tgwui_remote_config.json)",
            "Identified configuration synchronization gap",
            "Tested API with corrected parameters"
        ],
        "root_cause_discovered": "Multiple configuration files not synchronized - UI updating one config, server reading another, with placeholder defaults in fallback values",
        "solution_implemented": [
            "Created voice synchronization system",
            "Replaced placeholder defaults with valid defaults",
            "Added configuration file discovery and sync on startup",
            "Updated UI handlers to persist changes to all relevant configs"
        ],
        "validation_performed": [
            "Verified API calls succeed with valid voice files",
            "Confirmed UI changes persist after restart",
            "Tested refresh button functionality",
            "Validated no more placeholder values in actual usage"
        ],
        "prevention_measures": [
            "Added startup configuration synchronization",
            "Implemented placeholder value validation",
            "Added comprehensive logging for config operations",
            "Created resource discovery and validation system"
        ],
        "patterns_identified": [
            "Multiple config files need synchronization mechanisms",
            "Placeholder defaults should never be used in production",
            "UI changes must persist to all relevant configurations",
            "Resource discovery should run on every startup"
        ]
    }

    # Save documentation
    save_resolution_documentation("alltalk_tts_resolution", alltalk_resolution)

def save_resolution_documentation(issue_name, documentation):
    """Save resolution documentation for future reference"""
    import json
    from pathlib import Path

    docs_dir = Path("F:/Apps/freedom_system/log/resolutions")
    docs_dir.mkdir(exist_ok=True)

    doc_file = docs_dir / f"{issue_name}_resolution.json"

    try:
        with open(doc_file, 'w', encoding='utf-8') as f:
            json.dump(documentation, f, indent=4)

        log_enhanced(f"Resolution documentation saved: {doc_file}", "INFO", "save_resolution_documentation", "DOCS")
    except Exception as e:
        log_enhanced(f"Failed to save documentation: {str(e)}", "ERROR", "save_resolution_documentation", "DOCS")
```

---

## 🎯 IMPLEMENTATION REQUIREMENTS

### Mandatory Enhanced Logging Integration

**REQUIREMENT**: All extensions must implement enhanced logging from the start:

```python
# Add this to extension standards
def setup_enhanced_logging(component_name):
    """Setup enhanced logging for any extension or system"""
    global log_enhanced

    def log_enhanced(message, level="INFO", function_name="", component=component_name):
        import datetime

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = f"[{component}]"

        if function_name:
            prefix = f"{prefix} [{function_name}]"

        full_message = f"{prefix} [{level}] {message}"
        print(full_message)

        # Write to component-specific log file
        log_file = f"F:/Apps/freedom_system/log/{component_name.lower()}_troubleshooting.log"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} {full_message}\n")
        except Exception:
            pass  # Don't fail on logging failures

    return log_enhanced

# Usage in extensions
log_enhanced = setup_enhanced_logging("EXTENSION_NAME")
```

### Troubleshooting Integration Points

```python
def integrate_troubleshooting_into_extension():
    """Integration points for troubleshooting in extensions"""

    # 1. Startup troubleshooting
    def extension_startup():
        log_enhanced("Starting extension with troubleshooting integration", "INFO", "extension_startup")

        # Apply systematic startup checks
        startup_issues = run_startup_diagnostics()
        if startup_issues:
            log_enhanced(f"Startup issues detected: {startup_issues}", "WARNING", "extension_startup")
            attempt_automatic_resolution(startup_issues)

        # Continue with normal startup
        continue_normal_startup()

    # 2. Error handling with troubleshooting
    def handle_error_with_troubleshooting(error, context):
        log_enhanced(f"Error occurred: {str(error)}", "ERROR", "handle_error_with_troubleshooting")
        log_enhanced(f"Error context: {context}", "ERROR", "handle_error_with_troubleshooting")

        # Apply systematic error analysis
        error_analysis = analyze_error_systematically(error, context)

        # Attempt automatic resolution
        resolution_attempted = attempt_error_resolution(error_analysis)

        if not resolution_attempted:
            log_enhanced("Manual troubleshooting required", "WARNING", "handle_error_with_troubleshooting")
            generate_troubleshooting_report(error, context, error_analysis)

    # 3. Periodic health checks with troubleshooting
    def periodic_health_check():
        log_enhanced("Running periodic health check", "INFO", "periodic_health_check")

        health_issues = run_systematic_health_diagnostics()

        if health_issues:
            log_enhanced(f"Health issues detected: {health_issues}", "WARNING", "periodic_health_check")
            apply_health_issue_resolution(health_issues)
```

---

This troubleshooting process framework provides a systematic approach to identifying, analyzing, and resolving issues in the Freedom System using systematic principles combined with enhanced logging and validation techniques proven effective in real-world scenarios.
