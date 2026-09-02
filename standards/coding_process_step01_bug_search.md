# Coding Process Step 01: Bug Search (CP1BUGSEARCH)

This document is the reference wiki for the CP1BUGSEARCH subagent. CP1 finds bugs using 9 ordered techniques, plus a monitoring layer that watches the actual running app instead of just its code and logs.

NEVER ASSUME. NEVER GUESS. NO SHORTCUTS. NO WORKAROUNDS. NO DUMMIES. NO PLACEHOLDERS. NO STUBS. NO NUBS.

---

## 🔭 STEP 0: Load Every Monitoring Tool

**Before touching any of the 9 techniques below, load everything you might need in one call - don't guess ahead of time which ones "seem relevant." That guessing is exactly how a browser or desktop monitoring tool ends up silently unused when it turns out to matter.**

```
ToolSearch({query: "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__read_console_messages,mcp__claude-in-chrome__read_network_requests,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__tabs_close_mcp,mcp__windows-mcp__Screenshot,mcp__windows-mcp__Snapshot,mcp__windows-mcp__App,mcp__windows-mcp__Process,mcp__windows-mcp__PowerShell,WebFetch,WebSearch", max_results: 20})
```

This is unconditional - run it every single time, on every bug, regardless of what kind of app it looks like at first glance.

## 🩺 STEP 0B: Verify Every Tool Actually Works

**A tool showing up after ToolSearch only proves its description loaded - it does not prove the tool works. Test it with one real, cheap call before trusting it.**

- `mcp__claude-in-chrome__tabs_context_mcp` if a browser is involved
- `mcp__windows-mcp__Screenshot` if a Windows desktop app is involved

If a test call fails, retry up to 3 attempts total. If it's still failing after 3 attempts, do not silently skip it and do not just write it to a log where it could go unnoticed - stop and ask the user directly:

> "Tool [name] hasn't responded after 3 attempts. What do you want me to do?"
> 1. **Skip it** - continue without this tool for this run
> 2. **Keep retrying** - same approach, try again
> 3. **Force it** - check whether the underlying process is hung or dead (`mcp__windows-mcp__Process` mode="list", or `tasklist`/`Get-Process`) and try to recover it; if it's still dead after that, say so plainly - a fully broken MCP connection usually needs a new Claude Code session, and claiming it's fixed when it isn't is worse than admitting it needs a restart
> 4. **Stop here** - halt until it's fixed

## 📋 STEP 0C: Scope Check and the Monitor Log

**Figure out what actually applies to this app before digging in - not to decide which tools to load (you loaded everything in STEP 0 regardless), but to decide which passive log files are worth checking.**

Ask: Does it have a browser/web component? Does it have a Windows desktop window? Which project is this (so you know which project-specific logs exist, e.g. AvatarAI's watchdog logs only exist in that project)?

Create (or open) `[root folder]_Monitor_LOG.md` in the project root. Every monitoring check anywhere in the pipeline - CP1, CP2, or CP4 - gets one line here, whether it found something or not:

```markdown
## [timestamp] - [CP stage] - [tool/monitor name]
- **Checked:** [what was checked]
- **Result:** [what was found - "nothing unusual" counts as a result, not silence]
```

A monitor that was never checked and a monitor that was checked and found nothing look identical unless both get written down. Write both down.

---

## 🧰 DEBUGGING TOOLKIT

The following 9 techniques are ordered from first-to-try to last-resort. Follow this order.

### Before Starting: Define the Problem (Questioning Framework - Group 1)
Answer these before running any technique:
- What is the exact error message? What was I trying to do? What should have happened instead? Can I make it break again on purpose? What exact steps caused the error?

See `standards/questioning_framework.md` for the full framework.

---

### Technique 1: Backup Everything

**Make a complete copy of the entire root folder - every subfolder, every file, EVERYTHING. Name the copy with " ORIGINAL" at the end of the folder name. Now continue all work in the folder WITHOUT the ORIGINAL tag. If anything goes wrong, you always have the untouched copy to go back to.**

```python
import shutil
from pathlib import Path

def backup_everything(project_root):
    """Copy the entire project before touching anything"""
    source = Path(project_root)
    backup = Path(f"{project_root} ORIGINAL")

    if backup.exists():
        print(f"[BACKUP] Backup already exists: {backup}")
        return

    print(f"[BACKUP] Copying {source} -> {backup}")
    shutil.copytree(source, backup)
    print(f"[BACKUP] Complete. Continue work in: {source}")
    print(f"[BACKUP] Untouched copy at: {backup}")
```

⚠️ **BACKUP RULES**:
- Do this BEFORE you change anything
- Copy EVERYTHING - don't pick and choose
- Work in the original folder, leave the ORIGINAL copy alone
- If everything goes sideways, you can always start over from the ORIGINAL

---

### Monitoring Check A: Read the Logs That Already Exist

**Before digging into anything, read whatever passive log files apply per STEP 0C - these are free, they're already sitting on disk, no extra work required to produce them.**

- `log/claude_code_voice_mode.log`, `log/claude_code_voice_mode_mic_panel.log`, `log/whisper_stt.log` (if voice mode is involved)
- `log/boredom_monitor.log` and the `log/*_extension.log` files (if text-generation-webui is involved)
- Project-specific watchdog logs (e.g. AvatarAI's `Logs/cuda_graph_watchdog_incidents.log`, `worker_stderr_*.log` - only if this is that project)

Log every check to `[root folder]_Monitor_LOG.md`, including logs that showed nothing relevant.

### Technique 2: Environment Differences

**"Works on my machine!" The usual suspects: different Python version, missing packages, wrong file paths (Windows `\` vs Linux `/`), missing `.env` file, case sensitivity. A checklist for when code works in one place but not another.**

**Quick Environment Checklist:**
- [ ] Python version match? (`python --version`)
- [ ] Virtual environment activated? (check prompt prefix)
- [ ] Same packages installed? (`pip freeze` vs requirements.txt)
- [ ] Environment variables set? (`echo %VAR_NAME%` on Windows, `echo $VAR_NAME` on Linux)
- [ ] Database/service running and accessible?
- [ ] File paths correct? (Windows `\` vs Linux `/`)
- [ ] Permissions correct? (especially on Linux)
- [ ] Same working directory when running?

**Also check for background Windows software interfering** - only if the above doesn't explain the failure:
- [ ] Is antivirus (Windows Defender) scanning or blocking a file/port right now?
- [ ] Is the Killer networking software throttling a local connection?
- [ ] Is a scheduled update task (Adobe, NVIDIA, etc.) eating CPU at this exact moment?
- [ ] Is Citrix intercepting network, clipboard, or USB in a way that could explain this?

Check via `tasklist`/`Get-Process` and `schtasks /query`/`Get-ScheduledTask`. Log what you checked and found to `[root folder]_Monitor_LOG.md`, even if the answer is "nothing interfering."

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

### Technique 3: 30-Second Obvious Checklist

**Before spending an hour debugging, check the dumb stuff: Did you save the file? Restart the server? Typo? Editing the right file? Browser cache? Right git branch? Forgot an import? 90% of "impossible" bugs are one of these.**

- [ ] Typo in variable or function name?
- [ ] Editing the correct file? (check file path)
- [ ] File saved after changes?
- [ ] Server/process restarted after code changes?
- [ ] Cache cleared? (browser, Python `__pycache__`, etc.)
- [ ] Correct git branch checked out?
- [ ] Import statement present for the module you're using?
- [ ] Syntax error earlier in the file breaking later code?

---

### Monitoring Check B: Actually Look At It

**Don't just infer what's happening from code and logs - look at the real thing.**

- **Web app / browser involved:** use `mcp__claude-in-chrome__get_page_text`, `read_console_messages`, and `read_network_requests` to see the actual rendered page, real browser errors, and real network traffic - not what the code says should happen
- **Windows desktop app involved:** use `mcp__windows-mcp__Screenshot` (fast) or `mcp__windows-mcp__Snapshot` (full UI element detail) to see the actual screen

Log what you looked at and what you saw to `[root folder]_Monitor_LOG.md`.

### Monitoring Check C: Cross-Check

**Look back over `[root folder]_Monitor_LOG.md` so far. Did two or more independent monitors show something unusual close together in time?** For example, a watchdog log entry and a browser console error within the same few seconds. That correlation is a stronger lead than either alone - call it out explicitly and investigate it first before moving into the deeper techniques below.

---

### Technique 4: Stack Trace Reading

**When Python crashes and throws a wall of text, start reading from the BOTTOM - that's the real error. One line above is where it crashed. The actual bug is usually a few lines before that, where bad data got fed in.**

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

### Technique 5: Binary Search Debugging

**Can't find the bug? Comment out half your code. Still broken? Bug's in the top half. Cut that in half. Repeat until you're staring at the exact line. Like a "higher or lower" guessing game for code.**

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

---

### Technique 6: Debugger Commands (pdb)

**Instead of spamming `print()` everywhere, drop in `breakpoint()` and your code freezes mid-run. You can inspect any variable, step through line by line. Like pausing a movie frame-by-frame instead of squinting at full speed.**

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

### Technique 7: Rubber Duck Debugging

**Claude Code reads every file in the root folder, then every file in every subfolder, systematically looking for the cause. Instead of guessing, it walks through the entire codebase file by file until it finds what's wrong.**

```python
def rubber_duck_debugging(project_root):
    """Systematically read every file in the project looking for the cause"""
    from pathlib import Path

    root = Path(project_root)
    code_extensions = {'.py', '.js', '.json', '.yaml', '.yml', '.conf', '.bat', '.sh'}

    # Phase 1: Read every file in the root folder
    print("[RUBBER DUCK] Phase 1: Reading root folder files...")
    for file_path in sorted(root.iterdir()):
        if file_path.is_file() and file_path.suffix in code_extensions:
            print(f"[RUBBER DUCK] Reading: {file_path.name}")
            analyze_file_for_issues(file_path)

    # Phase 2: Read every file in every subfolder
    print("[RUBBER DUCK] Phase 2: Reading all subfolder files...")
    for file_path in sorted(root.rglob("*")):
        if file_path.is_file() and file_path.suffix in code_extensions:
            print(f"[RUBBER DUCK] Reading: {file_path.relative_to(root)}")
            analyze_file_for_issues(file_path)

def analyze_file_for_issues(file_path):
    """Read a file and look for common problems"""
    try:
        content = file_path.read_text(encoding='utf-8')
        # Look for: hardcoded paths, placeholder values, missing imports,
        # syntax issues, mismatched variable names, dead code, etc.
    except Exception as e:
        print(f"[RUBBER DUCK] Cannot read {file_path}: {e}")
```

⚠️ **RUBBER DUCK RULES**:
- Don't skip files - read EVERYTHING
- Start at the root, then go deeper
- Look for patterns across files, not just within one file
- The bug might be in a file you didn't expect

---

### Technique 8: Git Troubleshooting

**Code used to work, now it doesn't. Git remembers every save. `git diff` shows what changed, `git bisect` auto-finds which commit broke things, `git stash` lets you test old versions without losing your work. A time machine for code.**

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

### Technique 9: Minimal Reproducible Example

**Your bug is hiding in 500 lines. Start deleting everything that doesn't matter. If the bug survives, delete more. Get down to the smallest code that still breaks - maybe 15 lines. Now the bug has nowhere to hide and someone else can actually help you.**

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

---

### After Finding a Bug: Verify It (Questioning Framework - Group 2)
Before handing off to CP3BUGFIX, answer these:
- Which specific part is actually failing? What am I assuming that might be wrong? Am I looking at the right thing?

See `standards/questioning_framework.md` for the full framework.

### If the Bug Involves an API: Use CP2API
If the bug is about one program talking to another over HTTP, see `standards/coding_process_step01_API.md` for the full 6-phase API troubleshooting process. Launch the CP2API subagent to run this process before handing off to CP3BUGFIX.

---
