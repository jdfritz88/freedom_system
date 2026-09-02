# Everything On This Computer That Can Watch Something

This is a plain-language list of every program, script, or add-on we could find that can watch, record, or report on things happening on this Windows computer — your apps, your code projects, your browser, or your desktop in general. It covers the whole `freedom_system` folder (all its projects) plus a look at the live computer itself (running programs, scheduled tasks, installed software, and browser add-ons).

A short note on words we'll use a lot:
- **Local-only** means the data never leaves this computer — it's just written to a file here.
- **Reports to** means the data gets sent somewhere else over the internet (a company's server, for example).
- **Telemetry** is a fancy word for "usage data a program quietly sends back to whoever made it," usually to help them fix bugs or see how their product is used.

There's an earlier, narrower report that covers one project (AvatarAI) in a lot of detail: `standards/claude-monitor-tools-2026-08-24_0822.md`. This report includes short summaries of everything in that one so you don't have to read both, plus a lot of new stuff that report didn't cover — the voice system, the browser, and the computer itself.

---

## The single most important thing we found

There's a program installed on this computer called **Windows-MCP** that gives an AI assistant (Claude Desktop) the ability to see and control your entire desktop — not just one app, the whole screen. It can take screenshots of your monitors, read the text and buttons on any window that's open, move your mouse, click things, type text, read and write your clipboard, read/write/delete files, read and change the Windows Registry, run any PowerShell command, and list or kill running programs.

It only does any of this when Claude Desktop actually asks it to (it's not secretly watching you all the time in the background) — but it is currently running on this computer right now, waiting for those requests. And separately from that, it automatically sends small "usage reports" about itself to a company called PostHog every time one of its tools is used — see section 3 below for exactly what that includes. This is worth knowing about even though it's an intentional AI tool you or someone using this computer installed on purpose.

---

## 1. Voice Mode system (Claude Code talking and listening)

This is the setup that lets Claude Code speak its replies out loud and listen to you talk back, using two local programs: **AllTalk** (text-to-speech) and **Whisper** (speech-to-text, converts your voice into text).

### 1.1 The "read replies out loud" hook
- **What it monitors:** Every single response Claude Code gives you, automatically, the moment it finishes typing.
- **How deep:** It reads Claude's *own* saved conversation transcript file (a file Claude Code already writes to your hard drive for every chat), strips out code blocks and formatting, and speaks whatever plain text is left.
- **Where it's located:** `REPO_claude_code_voice_mode/.claude/hooks/speak_on_stop.py` (this is the one actually turned on right now — set up in your Windows-wide Claude settings) and a very similar older copy at `REPO_claude_code_voice_mode/tts_hook.py`.
- **Who it reports to:** Nobody outside this computer. It sends the text to AllTalk running at `http://127.0.0.1:7851` — `127.0.0.1` always means "this same computer," so this never leaves your machine.
- **Where it saves logs:** `log/claude_code_voice_mode.log`.

### 1.2 The "listen to your voice" tool
- **What it monitors:** Your microphone — but *only* when Claude Code specifically calls its "listen" tool (for example, because you asked it to, or because it's mid-conversation and waiting for your spoken reply). It is not a background always-on wiretap; nothing is recorded unless that specific tool is triggered.
- **How deep:** While listening, it constantly checks your audio for "is this speech or silence" (called Voice Activity Detection, or VAD) so it knows when you've stopped talking.
- **Where it's located:** `REPO_claude_code_voice_mode/claude_code_voice_mode_mcp_server.py`.
- **Who it reports to:** Nobody outside this computer. Your recorded voice is sent to the local Whisper program at `http://127.0.0.1:8787` to be turned into text, and that's it.
- **Where it saves logs:** `log/claude_code_voice_mode.log` (event log, like "recording started/stopped") and `log/whisper_stt.log` (the actual text of what was transcribed, plus any errors — this file does contain the words you've spoken to it in past sessions).

### 1.3 The floating Mic Control Panel window
This is the little always-on-top window with the microphone button, volume slider, and mode switches.
- **What it monitors, beyond audio:** To let you pick which open terminal window Claude Code should type into, this panel asks Windows for a list of **every single `cmd.exe` window currently open on the whole computer**, along with each one's exact title/command line text — not just windows belonging to this project. It only reads window titles, not their contents, and only does this when you click the refresh button or the panel starts up.
- **Where it's located:** `REPO_claude_code_voice_mode/mic_panel.py`.
- **Who it reports to:** Nobody. All local.
- **Where it saves logs:** `log/claude_code_voice_mode_mic_panel.log`.

### 1.4 Voice-related Claude Code plug-ins (MCP servers)
Two small helper programs are registered so Claude Code can use voice tools at all:
- **`claude_code_voice_mode_mcp_server`** — the same local program described in 1.2 above, just the plug-in registration for it.
- **`voicemode`** (an open-source tool called "voice-mode," installed via a tool called `uvx`) — also just talks to the same local AllTalk (port 7851) and Whisper (port 5001/8787) addresses on this computer.
- **Where they're configured:** `C:\Users\jespe\.claude.json` (this is Claude Code's own settings file, not part of any project folder).
- **Who they report to:** Nobody outside this computer, based on their configuration.

---

## 2. Custom monitoring code already in this project (from the AvatarAI report)

The earlier report (`standards/claude-monitor-tools-2026-08-24_0822.md`) already covered these in full detail — here's the short version so you have the full picture in one place. All four of these are **local-only**: they write to log files on this computer and none of them send anything over the internet.

- **CUDA-graph watchdog** — watches whether the AvatarAI lip-sync animation is running correctly and fast enough on the graphics card; if it breaks 3 times in a short window, it turns off the speed-up shortcut for the rest of that run. Logs to `Logs/cuda_graph_watchdog_incidents.log` inside that project. Only exists in one of two copies of the same file.
- **Inference timeout-and-fallback** — makes sure AvatarAI never just hangs forever; if an animation takes too long, it kills that process and shows a plain picture instead. Also the thing that actually tells *you* when the watchdog above catches a problem.
- **Worker console-output capture** — every time a background animation worker starts, its error output gets saved to a brand-new timestamped log file (`worker_stderr_*.log`), so nothing is overwritten between runs.
- **Hallo2 worker self-healing** — before each request, checks if a specific background worker died, and restarts it automatically if so.

The same report also found 3 log-file types that *looked* like project monitoring tools (a full system-wide process/GPU watcher, and two console-output capture files) that turned out **not to exist anywhere in the project's actual code, past or present** — meaning someone ran those by hand, separately from the app itself, and whatever script did that isn't saved anywhere. See that report for full detail if you want to try to recreate it.

---

## 3. The Windows-MCP Claude Desktop extension (the big one)

Covered at the top of this report — repeating the specifics here.

- **What it monitors:** Everything on your desktop, when asked: full-screen screenshots (any monitor), a list of every open window and its clickable buttons/text fields/links, your clipboard contents, your file system, the Windows Registry, and your list of running programs. It can also click, type, scroll, and drag your mouse, run PowerShell commands, and send Windows notification pop-ups.
- **How deep:** As deep as a human sitting at the keyboard — it isn't limited to one app or one project folder. `FileSystem` operations default to your Desktop folder but can reach anywhere you give it a full path to.
- **Where it's located:** `C:\Users\jespe\AppData\Roaming\Claude\Claude Extensions\ant.dir.cursortouch.windows-mcp\` — made by a company called CursorTouch, not by Anthropic (the maker of Claude) and not part of this `freedom_system` project.
- **Is it running right now:** Yes — we found two copies of its process (`windows-mcp.exe`) actively running while writing this report.
- **Who it reports to:** It automatically sends small "usage report" messages to a company called **PostHog** (`us.i.posthog.com`) every single time one of its tools runs. Each message includes: which tool was used, whether it succeeded or failed, how long it took, and a made-up random ID number that stays the same across sessions (saved in a temp file) so PostHog can tell "this is the same computer as last time" without knowing your name. If a tool errors out, the error message text gets sent too. It does **not** send your actual screenshots, file contents, or typed text — just *that* an action happened and whether it worked. One extra detail: PostHog is allowed to guess your rough location from your internet connection unless that's turned off, and by default here it isn't.
- **Extra option that exists but we could not confirm is turned on:** The extension has a "remote mode" where, instead of running on this computer, it can hand full control to a cloud service at `windowsmcp.io` using an ID/API key. We could not find where this computer's actual chosen setting (on/off, local/remote) is saved, so we can't tell you which one is active — just that "local" is the default if nobody changed it.
- **Where it saves logs:** Prints to its own console window; a "Debug Mode" option (off by default) turns on more detailed logging for troubleshooting, also just to the console — nothing saved to a permanent file by default.

---

## 4. Other custom monitoring code in this project's other tools

- **Boredom Monitor** (`app_cabinet/text-generation-webui/extensions/boredom_monitor/`) — for a *different* local chatbot project (text-generation-webui, not AvatarAI). Watches how long it's been since the last chat message in that specific chat window, and after 7 minutes of silence, has the AI send itself a new message to keep the conversation going. It only tracks time-since-last-message inside that one chat — it does **not** watch your mouse, keyboard, or anything outside that chat window.
  - **Reports to:** Nobody outside this computer — everything it talks to (`127.0.0.1:5000` and `127.0.0.1:7851`) is local.
  - **Logs:** `log/boredom_monitor.log` and several `log/*_extension.log` files, one per piece of the system.

- **Whisper STT server** (`app_cabinet/whisper_stt/server.py`) — the same local speech-to-text server used by Voice Mode above (section 1.2). Every time it transcribes audio, it writes down the *actual words it heard* to its log file.
  - **Logs:** `log/whisper_stt.log` — worth knowing this file contains a plain-text history of things spoken to it.

---

## 5. Windows-level security and remote-access software

This section is about programs already installed on this computer, separate from anything in the freedom_system project.

- **Windows Defender / Microsoft Defender Antivirus** — the built-in Windows security software (we saw its processes running: `MsMpEng`, `NisSrv`, `MpDefenderCoreService`, `SecurityHealthService`). This is normal, expected antivirus behavior for any Windows computer — it watches files and programs for malware. No sign of any other, third-party antivirus installed.

- **Citrix Workspace (full suite)** — a set of programs (`Citrix Workspace`, `Citrix Desktop Lock`, `Citrix Secure Access Endpoint Analysis`, `Citrix Authentication Manager`, and others) that let this computer connect into a remote/virtual desktop, usually run by an employer or organization. Worth calling out specifically:
  - **Citrix Desktop Lock** is typically used to turn a computer into a locked-down "kiosk" that can only be used to access that remote desktop.
  - **Citrix Secure Access Endpoint Analysis** actively scans *this* computer's security status (like whether antivirus is on) before letting it connect, as a condition of access.
  - These were found installed and several of their processes (`concentr.exe`, `Receiver.exe`, `redirector.exe`, `SelfServicePlugin.exe`) were actively running at the time of this report. If this machine connects to a work or school Citrix environment, it's worth knowing that environment's IT administrators can typically see and manage activity inside that remote session — this is standard for Citrix, not a hidden or unusual behavior, but distinct from everything else in this report since it's about a remote session rather than this computer's own files.

- **Dell/Alienware support software** (`SupportAssistAgent`, `Dell.TechHub` and its several sub-agents, `Dell.Remediation.Agent`) — Dell's built-in hardware diagnostics and remote-support tools that came with this computer. These can report hardware health information back to Dell and, in some configurations, allow Dell support staff to run diagnostics remotely with your permission. Normal for a Dell/Alienware PC, but genuinely capable of monitoring hardware state and, with remote support enabled, more than that.

- **Killer Networking software** (`KillerNetworkService`, `KillerAnalyticsService`, `KillerProviderDataHelperService`) — network-prioritization software for this computer's network card. The "Analytics" service name suggests it collects network usage data, likely sent back to the manufacturer (Rivet/Killer) to improve the product.

- **Scheduled background update tasks** — checked Windows Task Scheduler for anything monitoring-flavored. Found only routine auto-update tasks for Adobe, NVIDIA, Zoom, and a couple of Google-related "PlatformExperienceHelper" tasks (one specifically named "Metrics," suggesting it reports basic usage stats to Google). Nothing that looked like a hidden or unusual monitoring tool.

---

## 6. Browser add-ons that can see what you do online

We checked every extension installed in both Chrome and Edge and read what each one is allowed to see, based on its own permissions list.

**Chrome:**
- **Claude (official browser extension)** — can see and interact with **any web page you visit** (all URLs), including reading page content and attaching a debugging connection to it. This is the extension that lets Claude Code's browser-automation tools work when you ask it to click things or read a page for you — it only acts when Claude is actually told to do something in the browser, it isn't watching passively.
- **Acrobat PDF Viewer (Adobe)** — also allowed to see **any web page**, plus can inject its own code specifically into Gmail and Google Drive pages (for things like "convert this attachment to PDF" buttons). Reports back to Adobe as part of normal use (sign-in, cloud features).
- **An unnamed Google extension (ID `ghbmnnjooekpmoecnnnilnnbdlolhkhi`)** — can read and write your clipboard, and only works on `docs.google.com`/`drive.google.com`. Its settings file is named in a way ("dasherSettingSchema") that strongly suggests it was installed automatically by a Google Workspace organization admin, not by you personally — worth checking if this computer is enrolled in a managed Google Workspace account.
- **Zoom Chrome Extension** — limited to zoom.us and Google Calendar pages, for scheduling meetings. Normal.
- **Google Drive sync helper** — limited to docs.google.com/drive.google.com, connects to the Google Drive desktop app. Normal.
- One more built-in Google Pay component that ships as part of Chrome itself, not something separately installed.

**Edge:** the same unnamed Google extension as above, plus **BrainBox** (a clipper for a note-taking tool called TheBrain, limited to thebrain.com), plus a built-in Microsoft Edge accessibility component. Nothing unusual.

---

## 7. Claude Code's own built-in tools (recap)

Section 1 of the earlier AvatarAI report already lists these in detail (Bash, Read, Write, Edit, Glob, Grep, Agent, AskUserQuestion, ScheduleWakeup) — those are general-purpose and not specific to any one project, so we won't repeat them here. New to this report: the **claude-in-chrome tools** (used to automate the actual Chrome browser via the extension in section 6) can, when Claude is told to use them, read a page's full text, click things, type into forms, and read a browser tab's console/network logs — but again, only when specifically invoked, not continuously.

---

## 8. Custom Claude Code agents you wrote (recap)

Also already fully covered in the earlier report's Section 4 — the CP1/CP2/CP3 debugging pipeline (`cp1-bug-search`, `cp1-api`, `cp2-bug-fix`, `cp3-simulation`) and `boredom-monitor-builder`, all stored in `.claude/agents/`. These are tools *you* asked Claude Code to use, on your instruction each time — not background monitors.

---

## How this report was put together
- Section 1 came from reading the actual source code of every file in `REPO_claude_code_voice_mode` and the Claude Code settings files that turn its hooks on.
- Section 2 is a condensed summary of the earlier, more detailed AvatarAI-specific report.
- Section 3 came from finding the Windows-MCP extension's live running processes, reading its manifest and source code (including its `analytics.py` file, which shows exactly what it sends to PostHog and how).
- Section 4 came from reading the boredom_monitor extension's actual detector/logging code and the whisper server's logging setup.
- Section 5 came from live commands run against this computer: a full list of running programs, Windows Task Scheduler, and the list of installed software from the Windows registry.
- Section 6 came from reading the actual `manifest.json` permission list inside every installed Chrome and Edge extension folder on this computer.
- Everything reporting "local-only" was confirmed by reading the actual code for what web addresses it contacts, not assumed from the program's name or purpose.
