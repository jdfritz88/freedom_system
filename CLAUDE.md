1) No guessing or assuming on errors or bugs.
2) Never assume my what I want. If my instructions are vague and allow for multiple interpretations, then ask for more clarity.
3) ALWAYS ask my permission to START a task when it immediately follows a discussion — even under bypass-permissions / auto-accept / plan-approved modes or any mode where you would otherwise act on your own. Present the plan, then wait for an explicit go-ahead before doing the work.
# Voice Mode

Voice output is automatic and does NOT depend on you remembering to call anything: a user-level `Stop` hook (`~/.claude/settings.json`, script at `F:/Apps/freedom_system/REPO_claude_code_voice_mode/.claude/hooks/speak_on_stop.py`) fires after every response you give, strips code blocks and markdown formatting out of it, and speaks whatever prose remains via the `claude_code_voice_mode_mcp_server` TTS pipeline.

Do NOT call the `speak` tool yourself for normal responses — the hook already handles it, and calling it manually will make the response play twice. This applies in every project under `freedom_system`, not just the voice-mode repo itself.

Start a new conversation with a short, natural greeting confirming voice mode is active (e.g. "Voice mode is on. I can hear and speak.") under 15 words — just write it normally, the hook will speak it. The mic starts muted - the user will unmute when ready to talk.

Write responses in concise, natural prose since anything outside code blocks/structured data gets read aloud verbatim. Code blocks, file paths, and structured data are stripped before speaking, so it's fine to include them for the written record.

If you need to say something that should be spoken but NOT written to the transcript (e.g. the DMAIC audio-failure recovery flow), call the `speak` tool directly for that one case — the hook still fires afterward on your final message, so keep the written response for that turn free of duplicate prose.

# Browser

Google Chrome has multiple profiles. Always use the **"John Doe"** profile — never the "Jacob" profile — whenever opening Chrome or a profile picker appears (e.g. launch with `--profile-directory` for the John Doe profile, or select it in the picker).

# Debugging Pipeline: CP1 → CP2 → CP3 → CP4

When debugging, use the 4-subagent pipeline. Each subagent enforces every step automatically.

**CP1BUGSEARCH** → Finds the bug using 9 ordered techniques
**CP2API** → (only if the bug involves an API) diagnoses the API failure using 6 ordered phases
**CP3BUGFIX** → Fixes the bug (with logging console + fix log to prevent repeats)
**CP4SIM** → Simulates the app to verify the fix worked

### The Loop
- Same error after fix? → Back to CP3 (new solution, not in the log)
- Different error? → Back to CP1 (new bug search)
- No error? → Done

### Rules
- NEVER ASSUME. NEVER GUESS. NO SHORTCUTS. NO WORKAROUNDS. NO DUMMIES. NO PLACEHOLDERS. NO STUBS. NO NUBS.
- CP3 must check for a logging console in the launch file before fixing anything
- CP3 must check `[root folder]_Fix_LOG.md` and create solutions NOT already in the log
- If the bug involves an API, CP1 launches CP2 first (6-phase API troubleshooting)
- CP1 loads every monitoring tool (Windows-MCP, Chrome browser tools) up front and verifies each one actually works before relying on it - never assume a tool is available just because it's listed
- CP1, CP2, and CP4 all log every monitoring check to `[root folder]_Monitor_LOG.md` - passive log files, screenshots, browser reads, interference checks. Nothing gets checked silently
- CP4 cannot declare a fix verified from a clean console log alone - it must also re-check passive logs and actually look at the running result (screenshot or browser read)

### Reference Files
- `standards/coding_process_step01_bug_search.md` - 9 debugging techniques
- `standards/coding_process_step01_API.md` - API troubleshooting (6 phases)
- `standards/coding_process_step02_bug_fix.md` - bug fix process
- `standards/coding_process_step03_bug_fix_simulation.md` - simulation/verification
- `standards/questioning_framework.md` - 4 groups of self-check questions
