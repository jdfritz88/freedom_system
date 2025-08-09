# FREEDOM SYSTEM INSTALLER CODING STANDARDS – ENFORCED MODE

## Mandatory Script Header
Every script must include this simplified header unless already present:
```python
# ==========================================
# FREEDOM SYSTEM INSTALLER - ENFORCED MODE
# Follows Freedom_Installer_Coding_Standards.txt
# ==========================================
```

## 🖥️ SYSTEM COMPATIBILITY REQUIREMENTS (CRITICAL)

### ❌ FORBIDDEN - DO NOT USE:

**Unicode Characters:**
- NO emoji symbols: ✅ ❌ ⚠️ 🎯 🔍 📤 📋 🏆 etc.
- NO special Unicode symbols or decorative characters
- NO non-ASCII characters in print statements or comments

**Advanced String Formatting:**
- NO f-string formatting: `f"text {variable}"` 
- NO .format() method: `"text {}".format(variable)`
- These can cause compatibility issues on some systems

### ✅ REQUIRED - ALWAYS USE:

**Plain ASCII Text Only:**
- Use simple words: SUCCESS, ERROR, WARNING, INFO
- Use basic symbols: -, +, *, =, |, [, ], (, )
- All text must be readable in basic terminal/console

**Simple String Concatenation:**
- Use + operator: `"text " + str(variable)`
- Use % formatting if needed: `"text %s" % variable` 
- Keep string operations simple and compatible

### EXAMPLES:

**❌ WRONG:**
```python
print(f"✅ API is working at {url}")
print("🔍 Scanning endpoints...")
print(f"⚠️ Warning: {error_message}")
```

**✅ CORRECT:**
```python
print("SUCCESS: API is working at " + url)
print("SCANNING: Checking endpoints...")
print("WARNING: " + str(error_message))
```

### CONSOLE OUTPUT STANDARDS:

Use these prefixes for consistent, compatible logging:
- `SUCCESS:` instead of ✅
- `ERROR:` instead of ❌  
- `WARNING:` instead of ⚠️
- `INFO:` instead of 🔍
- `SCANNING:` instead of 🎯
- `TESTING:` instead of 📤
- `FOUND:` instead of 📋
- `[OK]` and `[FAIL]` for installer status
- `[DONE]` only when all validation passes

### WHY THESE RULES:

1. **System Compatibility:** Unicode can cause crashes on older systems
2. **Console Compatibility:** Not all terminals support Unicode properly
3. **Encoding Issues:** Unicode can break file operations and logging
4. **Cross-Platform:** ASCII works everywhere, Unicode doesn't
5. **Debugging:** ASCII is easier to read in logs and error messages

### COMPLIANCE CHECK:

Before submitting any code, verify:
- [ ] No emoji or Unicode symbols anywhere
- [ ] No f-string formatting used
- [ ] All print statements use simple string concatenation
- [ ] All console output is plain ASCII text
- [ ] Error messages are readable without special characters

---

## 📊 LOGGING RULES (ALL TYPES)

### Global Launcher Logging
- Every `.bat` launcher must log to: `F:\Apps\freedom_system\log\launcher_log.txt`
- Log must include:
  - Component name
  - Date and time
  - Success/fail result

### Installer Logging
- Log to: `log/installer_log.txt` or module-specific log
- Each major step: `[OK]` or `[FAIL]`
- Timestamps optional

### Failure Logging
- Never suppress or ignore errors
- If any subtask fails → exit with `[FAIL]`
- Never print `[DONE]` unless ALL validation checks pass

---

## 🔐 GIT IDENTITY & CREDENTIAL VERIFICATION

- Run `set_git_identity.py` to configure Git (username, email, token)
- Exit immediately if identity not cached
- Never use `git clone` via HTTPS without identity verification
- Detect and halt on: `fatal: could not read Username`

---

## 📦 DEPENDENCY MANAGEMENT & PIP RULES

### Installation Verification
- After any `pip install`, check `.returncode`
- If not 0 → exit with `[FAIL]`
- Never assume install success

### Pip Upgrade Policy
- After creating environment, run: `<env_path>\Scripts\python.exe -m pip install --upgrade pip`
- **Only upgrade if pip reports a newer version is available**
- If pip reports newer version available AND upgrade fails → `[FAIL]`
- Never allow `[DONE]` if pip is outdated

### Universal Module Import Validation
- Do **not** trust pip output alone
- Validate with: `verify_module_import.py <modulename>`
- Script behavior:
  - Takes module name, attempts import
  - Returns `[OK]` or `[FAIL]` with exit code
- Required in **all future installers**
- Script location: `F:\Apps\freedom_system\componentsave\installation\verify_module_import.py`

---

## 📁 CLONING SANITY CHECKS

- After cloning, each installer decides what critical files to validate based on component needs
- Common examples: `start_windows.bat`, `webui-user.bat`, `driver.py`, or module-specific launchers
- If missing required files → log and exit `[FAIL]`

---

## ✅ FILE & ENVIRONMENT VALIDATION

### Launcher Validation
- Confirm launchers:
  - Created successfully
  - Point to real targets
  - Logged as confirmed

### Environment Validation
- Validate environment:
  - Python present in venv
  - `pip` works and callable
  - `Scripts/python.exe -m pip --version` passes
  - Validate all imports via `verify_module_import.py`

---

## ❌ [DONE] VALIDATION REQUIREMENTS

The `[DONE]` message must **only** appear if ALL conditions below are true:
- Git identity valid
- All pip installs succeeded (returncode = 0)
- All required files exist
- Import checks passed via `verify_module_import.py`
- Launchers verified and run once successfully
- Pip upgraded if newer version was available

---

## 🧠 INSTALLATION SEQUENCE GUIDELINE (GENERIC)

1. **Environment Setup**
   - Create venv, upgrade pip if newer version available, confirm pip works

2. **Primary Package Installation**
   - Install key module(s) for the component
   - Validate each with `verify_module_import.py`

3. **Secondary Package Installation**
   - Install supporting modules (e.g., numpy, sounddevice, etc.)
   - Validate imports post-install

4. **Final Validation Phase**
   - Confirm launchers exist and are valid
   - Run launcher once for confirmation
   - Log all outcomes

---

## 🧠 ENFORCEMENT HISTORY & BUG NOTE

- Historical issue: pip falsely claimed success while import failed
- Future installs must **never** rely on pip alone
- All installers must enforce direct import testing
- Unicode compatibility issues have caused system crashes
- F-string formatting has caused failures on some Python installations

---

## 🚨 INSTALLER EXECUTION AUTHORIZATION

You are authorized to begin installer prep only after the Freedom System is launched.
Until then, you may stage necessary code but do not finalize or execute it unless instructed.

---

## 🔧 COMPATIBILITY ENFORCEMENT

**REMEMBER:** This system must work reliably across different environments. Following these standards ensures maximum compatibility and prevents runtime errors caused by Unicode characters, advanced formatting, or encoding issues.