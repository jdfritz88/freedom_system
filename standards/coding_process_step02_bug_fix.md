# Coding Process Step 02: Bug Fix (CP3BUGFIX)

This document is the reference wiki for the CP3BUGFIX subagent. CP3 receives a bug found by CP1BUGSEARCH and fixes it systematically.

NEVER ASSUME. NEVER GUESS. NO SHORTCUTS. NO WORKAROUNDS. NO DUMMIES. NO PLACEHOLDERS. NO STUBS. NO NUBS.

Do not disable, remove, or break anything CP1 set up while investigating - the logging console (Step 1 below), the passive logs CP1 read, or `[root folder]_Monitor_LOG.md`. CP4 needs all of it intact to verify your fix.

---

## STEP 1: CHECK FOR LOGGING CONSOLE IN LAUNCH FILE

**This is the first thing CP3 does. Every time. No exceptions.**

Before any fix is attempted, check if the app's launch file (`.bat` or `.py`) has a detailed logging console that logs every single app activity as the app tries to run.

CP4SIM/Claude Code needs to watch and read this logging console for ERRORS. If the logging console code doesn't exist, CREATE IT in the launch file.

### What the logging console must do:
- Log every single app activity as it happens
- Show timestamps for each activity
- Show errors with full stack traces
- Write output to both console AND a log file
- Be readable by CP4SIM in real time

### Python launch file example:

```python
import logging
import sys
import os
import traceback
from datetime import datetime

# === LOGGING CONSOLE - REQUIRED BY CP3BUGFIX ===
log_file = f"{__file__}_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding='utf-8')
    ]
)

logger = logging.getLogger("APP")
logger.info(f"=== APP LAUNCH START ===")
logger.info(f"Log file: {log_file}")
logger.info(f"Python: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")

# Wrap the entire app in a try/except to catch ALL errors
try:
    # ... original app code here ...
    pass
except Exception as e:
    logger.error(f"FATAL ERROR: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)
# === END LOGGING CONSOLE ===
```

### Batch file example:

```batch
@echo off
REM === LOGGING CONSOLE - REQUIRED BY CP3BUGFIX ===
set LOGFILE=%~dp0app_run_%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
echo === APP LAUNCH START === >> "%LOGFILE%" 2>&1
echo Timestamp: %date% %time% >> "%LOGFILE%" 2>&1
echo Working directory: %cd% >> "%LOGFILE%" 2>&1

REM Run the app with all output captured
python your_app.py 2>&1 | tee "%LOGFILE%"
REM === END LOGGING CONSOLE ===
```

### How to check if it already exists:
1. Read the launch file
2. Search for logging setup (logging.basicConfig, StreamHandler, FileHandler, or equivalent)
3. If found: verify it logs to both console AND file, verify it captures errors with stack traces
4. If not found or incomplete: ADD IT

---

## STEP 2: DETERMINE BUG SOURCE

CP1BUGSEARCH passes along which technique found the bug. This determines the fix path.

### Path A: Simple Fix (Technique 2 or 3)

If the bug came from:
- **Technique 2 (Environment Differences)**: Wrong Python version, missing package, wrong path, missing .env, etc.
- **Technique 3 (30-Second Obvious Checklist)**: Unsaved file, server not restarted, typo, wrong branch, missing import, etc.

**Action**: Just fix it directly. These are straightforward problems with obvious fixes.

Then launch subagent CP4SIM to simulate the app and verify the fix.

### Path B: Full Fix Process (Techniques 4, 5, 6, 7, 8, 9)

If the bug came from:
- **Technique 4 (Stack Trace Reading)**
- **Technique 5 (Binary Search Debugging)**
- **Technique 6 (Debugger Commands)**
- **Technique 7 (Rubber Duck Debugging)**
- **Technique 8 (Git Troubleshooting)**
- **Technique 9 (Minimal Reproducible Example)**

**Action**: Follow Steps 3 through 7 below.

---

## STEP 3: CHECK FOR FIX LOG

Check for `[root folder]_Fix_LOG.md`. If it doesn't exist, create it.

The fix log tracks every solution attempted so that:
- CP3 never tries the same solution twice
- CP4 can record which solutions failed and why
- There is a complete history of what was tried

### Fix log format:

```markdown
# [Root Folder Name] Fix Log

## Bug 1: [description of bug from CP1]
### Attempt 1
- **Solution**: [description of solution]
- **Technique that found bug**: [technique number and name]
- **Result**: [PASS / FAIL - same error / FAIL - different error]
- **Date**: [timestamp]

### Attempt 2
- **Solution**: [description of NEW solution]
- **Technique that found bug**: [technique number and name]
- **Result**: [PASS / FAIL - same error / FAIL - different error]
- **Date**: [timestamp]
```

---

## STEP 4: CREATE A SOLUTION

### First: Answer These (Questioning Framework - Group 3)
- What are 3 different ways to fix this? Which fix hits the root cause vs just the symptom? What could go wrong with each fix?

See `standards/questioning_framework.md` for the full framework.

Read the `[root folder]_Fix_LOG.md`. Create a solution that is NOT IN THE LOG.

NO SHORTCUTS. NO WORKAROUNDS. NO DUMMIES. NO PLACEHOLDERS. NO STUBS. NO NUBS.

### Solution requirements:
- Must address the ROOT CAUSE of the bug, not symptoms
- Must NOT be a solution already tried (check the log)
- Must NOT use shortcuts, workarounds, dummies, placeholders, stubs, or nubs
- Must NOT bypass the problem - must solve it
- Must be a real, permanent fix

### Before creating a solution:
1. Understand WHY the current code/architecture was built this way
2. Check commit history, README, comments for design decisions
3. Ask the user if unclear about design intent

### Solution types (acceptable):
| Type | When to use |
|------|-------------|
| **Root cause fix** | You know exactly what's wrong and fix it directly |
| **Architecture correction** | The design itself is flawed and needs restructuring |
| **Prevention fix** | Fix the bug AND add guards to prevent it recurring |

### Solution types (NOT acceptable):
| Type | Why it's banned |
|------|-----------------|
| Shortcut | Bypasses the problem instead of solving it |
| Workaround | Goes around the issue instead of through it |
| Dummy value | Fake data masking the real problem |
| Placeholder | Temporary value pretending to be real |
| Stub | Empty function pretending to work |
| Nub | Partial implementation pretending to be complete |

NO SHORTCUTS. NO WORKAROUNDS. NO DUMMIES. NO PLACEHOLDERS. NO STUBS. NO NUBS.

---

## STEP 5: ADD SOLUTION TO LOG

Before implementing, add the solution to `[root folder]_Fix_LOG.md`:
- Description of the solution
- Which technique found the bug
- What files will be changed
- Result field left as "PENDING" until CP4SIM verifies

---

## STEP 6: IMPLEMENT THE SOLUTION

Apply the fix to the codebase.

### Implementation rules:
- Work in the folder WITHOUT the ORIGINAL tag (backup was made by CP1)
- Make the minimum changes needed to fix the bug
- Do not refactor surrounding code unless it's part of the fix
- Do not add features beyond the fix
- Ensure the logging console from Step 1 is still intact

NO SHORTCUTS. NO WORKAROUNDS. NO DUMMIES. NO PLACEHOLDERS. NO STUBS. NO NUBS.

---

## STEP 7: LAUNCH CP4SIM

After implementing the solution, launch subagent CP4SIM to:
1. Watch the logging console
2. Launch the app
3. Simulate the original error
4. Report back whether the fix worked

Pass to CP4SIM:
- The original bug description from CP1
- Which technique found it
- What solution was applied
- Where the logging console output goes

---

## LOOP BACK RULES

### CP4SIM says: SAME ERROR
- The fix didn't work
- CP4SIM will undo the fix
- CP4SIM updates the fix log with FAIL - same error
- Control returns to CP3 Step 4: Create a NEW solution (not in the log)
- NO SHORTCUTS. NO WORKAROUNDS. NO DUMMIES. NO PLACEHOLDERS. NO STUBS. NO NUBS.

### CP4SIM says: DIFFERENT ERROR
- The fix changed something but introduced a new bug
- Control returns to CP1 to search for the new bug
- The original fix stays (it solved the original problem)
- CP1 starts the search process over for the new error

### CP4SIM says: NO ERROR
- The fix worked
- Update the fix log with PASS
- Done
