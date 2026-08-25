# Tools Used to Watch and Debug the AvatarAI Project

This is a catalog of every tool involved in watching, logging, or debugging this project — split by where each one actually comes from. Some tools are things Claude Code used directly in this conversation. Some are monitoring code that's actually built into the avatarAI app itself (confirmed by reading the real source code, not guessed from log output). Some are things that LOOK like project monitoring tools because their output sits in the Logs folder, but turned out not to exist anywhere in the project's code at all — meaning they were almost certainly run by hand from outside the project. And some are custom Claude Code agents the user wrote.

---

## 1. Tools Claude Code used directly (source: Claude, this session)

These are the general-purpose tools Claude itself reached for while reading the 150 log files and building this catalog — not anything specific to avatarAI.

- **Bash** — runs real terminal commands (this machine uses Git Bash).
  - Strengths: great for quick counting, math, running small scripts, checking git history, cleaning up temp files.
  - Limitations: not sandboxed, so a careless command could do real damage; output can get huge and clog up the conversation if not careful.

- **Read** — opens a file and shows its exact contents, with line numbers.
  - Strengths: precise and required before editing anything; forces looking at the real code instead of assuming what it says.
  - Limitations: only shows a limited number of lines at a time by default, so a very large file (tens of megabytes) can't be read in one go — it has to be read in chunks.

- **Write** — creates a brand-new file, or completely replaces an existing one.
  - Strengths: simple way to produce a new report or log file from scratch.
  - Limitations: replaces the *whole* file rather than changing one small part, so it's the wrong tool for a minor tweak to something that already exists.

- **Edit** — makes one exact, targeted change inside an existing file (find this exact text, replace it with that).
  - Strengths: much safer and cheaper than rewriting an entire file just to fix one thing.
  - Limitations: the text it's looking for has to match exactly and be unique in the file, or it refuses to guess and just fails.

- **Glob** — finds files by name pattern (like "every file ending in .md").
  - Strengths: fast way to discover what files exist without opening folders one by one.
  - Limitations: only matches file names/paths — it has no idea what's actually written inside those files.

- **Grep** — searches inside files for specific words or text patterns.
  - Strengths: the main way to find "where in a huge codebase does this word or piece of code live" quickly.
  - Limitations: it only finds what you specifically search for — if the search term is wrong or too narrow, it can miss the real answer without saying so.

- **Agent (sub-agents)** — spins up a separate, independent copy of Claude to do a chunk of work on its own, often several at once, in the background.
  - Strengths: lets a huge job (like reading 150 files, or digging through source code) get split up and done in parallel instead of one thing at a time, and keeps the main conversation from getting clogged with every little detail each one reads.
  - Limitations: each one starts with a blank memory — it doesn't know anything about the conversation so far, so it needs very complete, self-contained instructions; there's also no way to check in on one partway through, only after it's completely finished.

- **AskUserQuestion** — pauses and asks the user to pick between a few real options.
  - Strengths: stops Claude from guessing on a genuine judgment call and keeps a human in charge of ambiguous decisions (this was used several times in this project specifically to avoid guessing on how to handle huge files, filename formats, and duplicate errors).
  - Limitations: only good for real either/or type decisions — it's not built for wide-open questions with no set list of answers.

- **ScheduleWakeup** — tells Claude to automatically check back in after a set amount of time.
  - Strengths: useful for a task that's meant to check on something repeatedly over time (like a recurring "keep checking every 10 minutes" job).
  - Limitations: it's built for that specific repeating-check use case — it is NOT the right tool just to "wait" for background agents to finish, since those already send an automatic notification the moment they're done. It was used once by mistake in this project and had to be cancelled right after.

---

## 2. Monitoring tools genuinely built into the avatarAI project's own code (source: Project)

These were confirmed by directly reading the actual Python source files — not guessed from what the log files looked like.

### 2.1 CUDA-graph watchdog / circuit breaker
**Where it lives:** `backend/models/MuseTalk/scripts/musetalk_worker.py` (the copy of the worker script that actually runs — there's a second, older copy at `backend/musetalk_worker.py` that does NOT have this feature at all).

- **What it does:** The lip-sync animation step uses a graphics-card shortcut ("CUDA graph") to run about twice as fast. This tool constantly checks two things about that shortcut: (1) is the output actually correct, comparing it against the slow-but-always-correct method every so often, and (2) is a single step taking way longer than normal (more than 6 times the recent average, or over 1 full second, whichever is bigger). A single one-off bad or slow step is quietly worked around and doesn't count against anything. But if 3 such problems happen within any 50-step window, the tool treats that as a real pattern — it throws away the shortcut and rebuilds it fresh, once. If that same pattern happens again after the rebuild, it permanently turns the shortcut off for the rest of that run and switches to the slower, always-reliable method instead. Every single flagged event, big or small, gets written to `Logs/cuda_graph_watchdog_incidents.log`.
- **Strengths:**
  - Checks for two totally different kinds of failure (wrong answer vs. just too slow) instead of assuming one always means the other.
  - Its "how sensitive should this be" numbers were set based on real, measured normal behavior, not just guessed, so it's less likely to cry wolf over harmless noise.
  - Gives the shortcut a genuine second chance (one rebuild) instead of instantly giving up on the first hiccup.
  - Writes down every single flagged event with rich detail, which is what let later investigations (like this project's own log summaries) piece together what was actually going wrong.
- **Limitations:**
  - Once it permanently disables the shortcut, there's no code found anywhere that automatically restarts that worker to give the shortcut another chance — it stays disabled until the worker process happens to restart for some unrelated reason.
  - Its "is the answer correct" check only runs occasionally (about every 100th step), not on every single step, so a rare bad result could theoretically slip through between checks.
  - It only gets exactly one "rebuild and try again" attempt — after that, any repeat is treated as permanent, with no in-between option.
  - This entire safety feature only exists in one specific copy of the worker file. If that particular file were ever missing (say, after a fresh reinstall), the app would silently fall back to the older worker file that has none of this protection, with nothing warning that the safety net is gone.

### 2.2 Inference timeout-and-fallback
**Where it lives:** `backend/app/services/animator.py` and `backend/app/websocket.py`.

- **What it does:** This is a separate, simpler safety net that makes sure the app never just hangs forever, no matter what's wrong. If the animation worker takes more than 30 seconds to even start up, or more than roughly 30 seconds (scaled up for longer audio clips) to finish one piece of animation, the app kills that stuck process completely (including a special Windows-specific fix to make sure a "hidden" leftover process doesn't keep running unnoticed) and instead shows a plain, non-moving picture with the voice audio so the reply still gets delivered. If the CUDA-graph watchdog above (2.1) ever flags something, this same system is what actually tells the person using the app about it, by sending a message to their screen — otherwise that event would only ever sit quietly in a log file nobody's watching.
- **Strengths:**
  - Built directly from a real incident this project hit before (a cancelled request whose background process kept running anyway for over 19 minutes) — the fix specifically covers that exact situation now.
  - Handles a tricky Windows-only quirk where simply "killing" a process could leave a hidden, still-running copy behind — this was tested and fixed.
  - However long a reply takes to hang or fail, the user still gets *something* back (a plain picture instead of the fancy lip-synced video) rather than the chat just freezing.
  - Passes the watchdog's internal alerts (2.1) through to the actual user, closing the gap between "the system silently worked around a GPU problem" and "the person actually finds out about it."
- **Limitations:**
  - The message that tells the user about a watchdog event is a single shared value that gets checked and cleared each time — if two conversations were hitting this at the exact same moment, one could clear it before the other gets to see it, silently dropping that one alert.
  - It treats every single type of animation failure the same way (fall back to a plain picture), so it can't tell "a one-time hiccup" apart from "this keeps happening over and over" — it just retries the same way every time.
  - The exact timing numbers (30 seconds, scaled for clip length) were tuned from specific real situations that happened before, not from a hard mathematical guarantee — an unusually slow but otherwise legitimate render could still get killed and downgraded if it runs long enough.

### 2.3 Worker console-output capture (`worker_stderr_*.log` files)
**Where it lives:** `backend/app/services/animator.py` (for the MuseTalk lip-sync worker) and `backend/app/services/hallo2_animator.py` (for the separate Hallo2 idle-video worker) — same design in both places.

- **What it does:** Every time one of these background worker programs is started, the app opens a brand-new, uniquely timestamped file and tells the worker to send all of its diagnostic/error output straight into that file, instead of through a live connection back to the main app.
- **Strengths:**
  - This design choice fixed a real bug: an earlier version tried to pipe that output live back to the app, but if nobody was actively reading it fast enough, that pipe would fill up and freeze the whole worker — writing straight to a file avoids that freeze entirely.
  - A brand-new file every time a worker starts means older evidence from a previous run is never accidentally overwritten or lost.
  - If a worker fails to start properly, the app automatically reads the end of this same file back in to include in its own error message — so it's actively used for troubleshooting, not just sitting there unused.
- **Limitations:**
  - Nothing in the code ever deletes or cleans up old copies of these files, so the Logs folder just keeps growing forever, one file per worker restart.
  - It only captures that one worker process's error output — not the main app's own console output.

### 2.4 Hallo2 worker self-healing (lazy restart)
**Where it lives:** `backend/app/services/hallo2_animator.py`.

- **What it does:** Before asking the Hallo2 idle-video worker to do anything, the app first checks if that worker process is still alive. If it died for any reason, the very next request automatically starts a brand-new one — there's no separate "watcher" constantly checking; it just checks right when it's actually needed.
- **Strengths:**
  - Simple and reliable — the app never gets stuck permanently just because one background worker happened to crash once.
  - Confirmed in the real logs: exactly this behavior recovered the app automatically, twice, after the Hallo2 worker unexpectedly died mid-job.
- **Limitations:**
  - It only checks and restarts right before a new request — there's a real gap between when the old worker actually died and when the next request happens to notice, during which an avatar's idle video playlist can be left temporarily stale or incomplete.
  - It doesn't investigate or record *why* the worker died — it just quietly moves on and starts a new one.

---

## 3. Log files that LOOK like project monitoring tools but were NOT found anywhere in the project's code (source: unknown / likely run by hand, outside the project)

Two agents searched the entire project folder, its full git history (including every file ever deleted), and the whole `freedom_system` folder tree for these. None of them turned up. This isn't a guess — it's a confirmed "this does not exist in the codebase as it stands today."

### 3.1 RENDER_MONITOR (the process + GPU watcher)
- **What it appears to do, based only on what's visible in the log text itself:** About every 3 seconds, it writes down the graphics card's usage percentage, memory use, and temperature, plus the main backend program's memory/CPU/thread usage, and it also watches for and logs any brand-new program starting up anywhere on the whole computer (not just this project).
- **Strengths (of the idea itself):** Checking every 3 seconds is fine-grained enough to catch a short crash or freeze that a slower check would completely miss; watching both the graphics card and the specific program's resource use at the same time is genuinely useful for figuring out if a slowdown is caused by resource starvation.
- **Limitations:**
  - It is not saved anywhere in this project — not in the current files, not in any deleted file in the project's entire history. If whoever ran it doesn't remember exactly how, it cannot currently be recreated.
  - Because it logs literally every program running on the whole computer, not just this project, the resulting files are enormous (14-20 megabytes) and mostly unrelated noise.
  - Because there's no code to check, nobody can verify how it behaves in edge cases (e.g., what it does if it briefly can't reach the graphics card).
  - Several of these log files have handwritten notes typed directly above the raw data, confirming a person was actively running this tool and watching it live during a specific debugging session — this was a manual, one-off debugging tool, not an automatic or permanent part of the app.

### 3.2 Raw backend and frontend console capture (`_raw_backend_stdout_*.log`, `_frontend_stdout_*.log`)
- **What it appears to do:** Saves a plain, unmodified copy of everything the main backend program and the website's frontend program print to their own console windows.
- **Strengths:** Having a saved copy of exactly what the program printed is genuinely useful for debugging after the fact.
- **Limitations:** The actual launch scripts for this project (both the current one and the one it replaced) open these programs in plain windows with no saving/redirecting turned on at all — so whatever captured this output isn't part of the project's own startup process. It's a separate, unaccounted-for step someone added by hand.

### 3.3 Redis console capture (`redis_*.log`)
- **What it appears to do:** Saves a copy of the database program's (Redis) own startup messages.
- **Limitations:** Redis's own settings file explicitly has file-logging turned OFF (it's set to print to the console only), and nothing in the launch scripts redirects that console output to a file either — so, just like 3.2, something outside the project's own code is capturing this by hand.

---

## 4. Custom Claude Code agents the user personally wrote (source: user)

These live in `F:\Apps\freedom_system\.claude\agents\` and are shared across all of the user's freedom_system projects, not stored inside avatarAI itself.

### 4.1 cp1-bug-search (CP1BUGSEARCH)
- **What it does:** The very first step in a 3-step debugging pipeline (CP1 → CP2 → CP3, referenced directly in this project's own instructions). Its only job is to FIND a bug — never fix it — by trying 9 specific techniques in a strict, fixed order (things like checking the environment, reading the crash message from the bottom up, cutting code in half to narrow down the problem, and checking recent git history), stopping the moment the first one actually finds something.
- **Strengths:** Going through the same 9 techniques in the same order every time means nothing obvious gets skipped just because it seemed unlikely; refusing to also fix things keeps it focused only on diagnosis, so it doesn't rush past understanding the real problem.
- **Limitations:** Because it always stops at the very first technique that finds *something*, it could settle on the first plausible explanation without confirming it's the actual root cause; going through all 9 steps in strict order can be slower than jumping straight to the one technique an experienced person would recognize as the obvious fit.

### 4.2 cp1-api (CP1API)
- **What it does:** A specialized helper that CP1 calls in specifically when a bug involves two programs talking to each other over the network (like a connection timeout or an error code). It checks, in order: is the other program even running, is it sending data in the right format, is the actual data correct, do the configuration files agree with each other, what does the server's own error say, and is a login/authentication problem involved.
- **Strengths:** Covers the most common ways two programs fail to talk to each other in a clear, repeatable checklist, which is especially useful for exactly the kind of routing/credential bugs found in this project's own logs (like the Silva avatar routing bug).
- **Limitations:** It's specifically built for HTTP/API-style problems — it won't help with a bug that has nothing to do with two programs communicating, like a purely visual glitch or a math mistake.

### 4.3 cp2-bug-fix (CP2BUGFIX)
- **What it does:** The second step in the pipeline — takes a bug that CP1 already found and actually fixes it. Before touching any code, it makes sure the app has a proper activity log set up (creating one if it's missing), checks a running "fix log" file so it never repeats a solution that already failed before, and insists on a real, permanent fix rather than a shortcut, a fake placeholder, or a partial patch.
- **Strengths:** Keeping a written fix log directly prevents wasting time trying the same failed solution twice; refusing shortcuts/placeholders pushes toward actually solving the real problem instead of just hiding the symptom.
- **Limitations:** It explicitly refuses to look for new bugs itself, so it's only as good as what CP1 handed it — a wrong or incomplete diagnosis from CP1 leads it to "fix" the wrong thing; its strict "no shortcuts ever" rule can make it slower in situations where a quick, honest workaround might genuinely be the right call for now.

### 4.4 cp3-simulation (CP3SIM)
- **What it does:** The third and final step — actually runs the app after CP2's fix and tries to make the original bug happen again, watching the activity log the whole time, to prove whether the fix really worked, whether it's still broken the same way, or whether it broke something new instead.
- **Strengths:** Actually testing the real running app is much stronger proof than just reading the code and assuming a fix will work; it has a clear, honest way to score the result (same error = fix failed, new error = partially fixed, no error = truly fixed) instead of just guessing.
- **Limitations:** It can only test for the *specific* original bug it was told to look for — it's not a general safety net that would notice some other, unrelated problem was introduced by accident, unless that problem happens to show up during the exact same test.

### 4.5 boredom-monitor-builder
- **Note:** This one is for a *different* project entirely — a chat inactivity feature for something called "text-generation-webui" — not avatarAI. It's included here because it's stored in the same shared agents folder and is genuinely a "monitoring" tool by name and purpose.
- **What it does:** Builds and debugs a feature that watches how long it's been since the last chat message, and automatically sends a new AI-generated message after 7 minutes of silence to keep the conversation going.
- **Strengths:** Requires a full backup before any change, insists on detailed logging at every step (timer starts, timer resets, message generation, sending the message), and refuses to consider the job done while any errors are still showing.
- **Limitations:** Deliberately narrow — it's told to work on this one feature and nothing else, so it can't be reused as-is for a different kind of monitoring problem; its process is quite heavy (one method at a time, wait for the user to test, document everything) which is thorough but slower than just making the change directly.

---

## Notes on how this was put together
- Section 1 was written directly from this session's own actions.
- Sections 2 and 3 came from two agents who read the actual project source code (not just the log files) specifically to verify what's real project code versus what's an untracked, hand-run tool — including one important correction they caught: the CUDA-graph watchdog only exists in one of two copies of the same worker script file, and the other copy has none of that protection.
- Section 4 came from directly reading the 5 custom agent definition files the user has saved for Claude Code to use.
