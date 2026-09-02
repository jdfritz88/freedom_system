# Coding Process Step 03: Bug Fix Simulation (CP4SIM)

This document is the reference wiki for the CP4SIM subagent. CP4 receives a fix from CP3BUGFIX and simulates the app to verify the fix works.

NEVER ASSUME. NEVER GUESS. NO SHORTCUTS. NO WORKAROUNDS. NO DUMMIES. NO PLACEHOLDERS. NO STUBS. NO NUBS. A log with no error in it is not proof the fix worked - go look at the actual result.

---

## STEP 0: LOAD AND VERIFY YOUR MONITORING TOOLS

CP4 is a fresh agent - CP1 already loaded and verified these tools earlier in the pipeline, but CP4 does not inherit that. Do it again now:

```
ToolSearch({query: "select:mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__read_console_messages,mcp__claude-in-chrome__read_network_requests,mcp__windows-mcp__Screenshot,mcp__windows-mcp__Snapshot,mcp__windows-mcp__Process", max_results: 10})
```

Test whichever ones you'll actually use with one real call. If a tool fails after 3 attempts, stop and ask the user the same four options CP1 uses: Skip it / Keep retrying / Force it (best-effort process recovery, honest about needing a session restart if it doesn't work) / Stop here. Log every check to `[root folder]_Monitor_LOG.md`.

---

## STEP 1: READ THE LOGGING CONSOLE

CP3BUGFIX set up a logging console in the app's launch file. CP4SIM must watch and read this console for ERRORS.

### What to look for:
- The log file path (created by the logging console CP3 added)
- Console output (stdout/stderr)
- Any ERROR or FATAL lines
- Stack traces
- The specific error that CP1 originally found

### How to watch:
1. Identify the log file location from the launch file
2. Launch the app
3. Read the log file output in real time using `tail` or by reading the file repeatedly
4. Capture ALL output - don't skip anything

---

## STEP 1B: RE-CHECK THE PASSIVE LOGS CP1 CHECKED

Read the same passive log files CP1 read at the start (voice mode logs, `whisper_stt.log`, `boredom_monitor.log`, project-specific watchdog logs - whichever applied). Confirm the bug's specific error signature is actually gone from them, not just absent from the fresh console output in Step 1. Log this check to `[root folder]_Monitor_LOG.md`.

## STEP 1C: ACTUALLY LOOK AT THE RESULT

A clean log is not proof - go see the real thing, the same way CP1 did in Monitoring Check B:
- **Web app:** `mcp__claude-in-chrome__get_page_text` + `read_console_messages` + `read_network_requests` - see the real rendered page and real browser errors, not just what the server-side log claims happened
- **Windows desktop app:** `mcp__windows-mcp__Screenshot` or `Snapshot`

This is the actual evidence that goes into the final report, not just "no error appeared." Log it to `[root folder]_Monitor_LOG.md`.

## STEP 1D: CROSS-CHECK AGAIN

Look over `[root folder]_Monitor_LOG.md` for the whole pipeline run, CP1 through now. Did the fix introduce a NEW correlated anomaly across two or more monitors that wasn't there before (e.g. the original error is gone, but a browser console error now appears at the same moment a different watchdog fires)? If so, that's a Result B (different error) even if the original console log looks clean.

---

## STEP 2: LAUNCH THE APP WITH THE FIX APPLIED

Run the app using its launch file (the same `.bat` or `.py` that CP3 verified has logging).

### Launch rules:
- Use the exact same launch command the user would use
- Do not modify any launch parameters
- Do not suppress any output
- Let the app start fully before testing

---

## STEP 3: SIMULATE THE ORIGINAL ERROR

Run a simulation that tries to recreate the original error that CP1 found.

### Simulation requirements:
- Reproduce the exact conditions that caused the original bug
- Use the same inputs, same sequence of operations
- Watch the logging console for the original error
- Wait long enough for the error to appear (some bugs are timing-dependent)

### What counts as "the same error":
- Same error message
- Same stack trace location
- Same type of failure (even if the exact message differs slightly)
- The same operation fails in the same way

### What counts as "a different error":
- Different error message about a different problem
- Different stack trace pointing to different code
- A new failure that didn't exist before the fix
- The original operation succeeds but something else breaks

---

## STEP 4: EVALUATE THE RESULT

### First: Answer These (Questioning Framework - Group 4)
- Did the fix solve the original problem? Did anything else break? Does it work every time, not just once?

See `standards/questioning_framework.md` for the full framework.

### Result A: SAME ERROR as CP1 found

The fix didn't work.

1. **Undo the fix** - revert all changes CP3 made
2. **Update the fix log** - mark the solution as `FAIL - same error` in `[root folder]_Fix_LOG.md`
3. **Add the failed solution to the log** so CP3 doesn't try it again
4. **Return to CP3** - CP3 will create a NEW solution that is NOT in the log
   - NO SHORTCUTS. NO WORKAROUNDS. NO DUMMIES. NO PLACEHOLDERS. NO STUBS. NO NUBS.

### Result B: DIFFERENT ERROR

The original bug is fixed but a new bug appeared.

1. **Keep the fix** - the original bug is solved
2. **Update the fix log** - mark the solution as `PASS (but introduced new error)`
3. **Return to CP1** - start the bug search over for the new error
4. CP1 will run its 9 techniques on the new error

### Result C: NO ERROR

The fix worked - but "no error in the console log" alone is NOT enough to declare this. Confirm STEP 1B (passive logs re-checked) and STEP 1C (actually looked at the result) both back this up before reporting success. A clean log with no visual/passive-log confirmation is not Result C - go get the missing evidence first.

1. **Update the fix log** - mark the solution as `PASS`
2. **Report success** - describe what was fixed and how, including what STEP 1C actually showed (screenshot description / page content / console state), not just "no error appeared"
3. **Done** - the pipeline is complete

---

## LOGGING CONSOLE READING GUIDE

### What to capture from the console:

```
=== APP LAUNCH START ===          <-- App started
[INFO] Loading configuration...    <-- Normal activity
[INFO] Connecting to database...   <-- Normal activity
[ERROR] Failed to connect: ...     <-- THIS IS WHAT YOU'RE LOOKING FOR
[ERROR] Traceback: ...             <-- Full error details
```

### Reading strategy:
1. Let the app run through its startup sequence
2. Watch for any ERROR or WARNING lines
3. If the app starts successfully, trigger the operation that caused the original bug
4. Watch for the error to appear (or not appear)
5. Compare what you see to what CP1 originally reported

### Timeout:
- If the app doesn't produce the original error within a reasonable time, and the operation that triggered it has been performed, count it as NO ERROR
- "Reasonable time" depends on the app - if it's a web server, a few seconds after the request. If it's a batch process, wait for it to complete.

---

## WHAT CP4SIM RECEIVES FROM CP3

CP3 passes the following information:
- **Original bug description**: What CP1 found
- **Technique number**: Which of the 9 techniques found it
- **Solution applied**: What CP3 changed
- **Log file location**: Where the logging console writes output
- **Launch command**: How to start the app

CP4SIM uses all of this to:
1. Know what error to look for
2. Know where to read the logs
3. Know how to start the app
4. Know what was changed (in case it needs to be undone)

---

## UNDO PROCEDURE (for SAME ERROR result)

When the fix didn't work and needs to be undone:

1. Identify all files CP3 changed
2. Revert each file to its state before CP3's changes
3. Verify the revert is complete (no partial changes left)
4. Do NOT undo the logging console - that stays regardless
5. Do NOT undo the fix log - that stays as a record

The ORIGINAL backup folder (created by CP1) is the ultimate safety net. If reverting individual files fails, the entire original codebase is still there.
