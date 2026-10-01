# Conversation log: AllTalk on the main processor - engine switching, three modes, streaming

**Date:** 2026-09-30, about 19:15 to 21:25 (PC clock)
**Started from:** `REPO_koboldccp_sst_tts_media` (Claude Code session)
**Follows:** `conversation_2026-09-30_alltalk_cpu_cuda_mode.md` (morning: CUDA/CPU switch; afternoon:
F5-TTS research, environment break and repair, XTTS vs F5-TTS measurements, sections 6-7)
**Code changed in:** `REPO_alltalk` (main `freedom_system` repo), `REPO_koboldccp_sst_tts_media`
(`launcher.py`), `REPO_claude_code_voice_mode` (`mic_panel.py`, `claude_code_voice_mode_mcp_server.py`)

**Commits (in order)**

| Time | Repo | Commit | What |
|---|---|---|---|
| 19:12 | freedom_system | `62731a25` | F5-TTS models in repo, no auto pip install, environment repaired (afternoon work) |
| 19:37 | freedom_system | `71d5b699` | `/api/enginereload` patch + launcher stops a server restarted by an engine switch |
| 19:55 | freedom_system | `d1bebda6` | `/api/enginereload` patch removed (user decision) |
| 20:01 | freedom_system | `da264d84` | mode countdown 5 s -> 10 s |
| 20:01 | koboldccp | `2d621b7` | launcher comment: 10-second countdown |
| 21:21 | freedom_system | `cc6b1d9f` | third mode: main processor with / without streaming |
| 21:21 | koboldccp | `452fab8` | launcher AllTalk menu: c / p / r |
| 21:21 | voice mode | `65871a2` | mic panel: three mode buttons, wrapping mode line |

**Not committed:** `REPO_claude_code_voice_mode/claude_code_voice_mode_mcp_server.py` - it holds this
session's changes (section 9) AND earlier uncommitted work that is not from this session (a
"voice missing from AllTalk" message-box check, 48 lines). The user has not decided how to commit it.

---

## 1. "Set XTTS as default, stop AllTalk so I can restart via the bat"

User asked: stop AllTalk so they can restart it through the bat; make sure they get the option to
switch to non-CUDA and that the choice is saved; XTTS stays the default engine ("lets see how it
does at non-CUDA"). Taken as the answer to the open question "which engine for voice mode": keep XTTS.

State checked (not assumed): no AllTalk processes, port 7851 free, saved mode `cuda`,
`tts_engines.json` `"engine_loaded": "xtts"`. The bat already had the 5-second countdown (C/P/S) and
saved the pick.

## 2. AllTalk's engine-switch API - and a shortcut that was called out

### 2.1 What happened
- Earlier in the afternoon, switching engines for the XTTS-vs-F5 test was done two ways that are
  **not the documented way**: (a) calling `POST /api/enginereload?engine=...` from a script, and
  (b) editing `REPO_alltalk/settings/system/tts_engines/tts_engines.json` while AllTalk was stopped.
- `/api/enginereload` crashed: `AttributeError: 'AlltalkTTSEnginesConfigModel' object has no
  attribute 'save'` (`tts_server.py:306`, `tts_engines_config.change_engine(requested_engine).save()`
  - `change_engine()` is delegated to the inner pydantic model, returns the model, which has no
  `save()`). The user pasted this traceback.
- Claude offered "fix it with a patch" and described it as making "AllTalk's engine-switch button
  and voice mode's engine switching work again". **That description was wrong** (see 2.3). The user
  chose "fix it" based on it.
- Patch added (`alltalk_patches.py`, tts_server.py): `change_engine(...)` then
  `tts_engines_config.save()`. Tested by calling the API: xtts -> f5tts -> xtts, settings file saved
  each time. The HTTP caller gets "connection forcibly closed" instead of the success reply, because
  AllTalk restarts its server (`os.execv`) right after; that is stock behaviour after the save works.

### 2.2 A real launcher flaw found by that test (fixed, kept)
- An engine switch restarts AllTalk's server with `os.execv`, which on Windows creates a NEW
  process outside the process tree the launcher started. `launch_alltalk.bat`'s stop
  (`taskkill /T` on script.py) missed it: a server (pid 33336, `tts_server.py`, parent gone) kept
  port 7851, and the bat still printed "AllTalk stopped." after 64 s.
- Fix in `launch_alltalk.bat`: `:kill_port_owner` - after the tree kill, if the port is still held,
  stop whichever process holds it **only if its program path is inside `\alltalk_environment\`**;
  `:stop` now says "Port 7851 is STILL held - AllTalk did not fully stop" instead of "stopped" when
  that is the case. Retested: engine switches both ways, then stop: 5 s, nothing left, port free.
- Later correction (said to the user): Claude had claimed this fix "also covers your web-page
  button". Not known - the web-page switch stopped cleanly in testing and probably would have
  without the fix (AllTalk's web page restarts the server as a child of script.py). The fix is kept
  as a safety net for the API route.

### 2.3 User: "Via API? is that standard? are you shortcutting? ... check developer documentation"
Developer documentation checked:
- AllTalk QuickStart Guide: the standard way is the **"Swap TTS Engine" button on the
  "Generate TTS" tab** of the web page (port 7852); "Load Different Model" changes the model;
  "Refresh Server Settings" afterwards.
  https://github.com/erew123/alltalk_tts/wiki/AllTalk-V2-QuickStart-Guide
- AllTalk "Control and Configuration API" wiki page documents only: `PUT /api/stop-generation`,
  `GET /api/reload_config`, `POST /api/reload` (models within the current engine),
  `POST /api/deepspeed`, `POST /api/lowvramsetting`. **`/api/enginereload` is not documented; there is
  no documented API for switching engines.**
  https://github.com/erew123/alltalk_tts/wiki/API-%E2%80%90-Control-and-Configuration-API
- `tts_engines.json` wiki page describes the file's fields but not how to switch, and neither
  advises nor forbids hand edits.
  https://github.com/erew123/alltalk_tts/wiki/Configuration-File:-tts_engines.json
- In the code, the web page's engine switch (`script.py` ~2750-2770) calls `change_engine()` and then
  `tts_engines_config_loaded.save()` separately, so it never hit the bug. Searched the whole
  freedom_system for callers of `enginereload`: only AllTalk's own `system/admin.html` and the
  `_import/oobabooga_side_copy` copy. Nothing the user runs calls it.

Corrections given to the user: the error they pasted came from Claude's own test call to the
undocumented endpoint; the "fix" had been mis-described; the file-edit switching was also
undocumented.

### 2.4 The documented button, tested in Chrome
- AllTalk started headless; web page `http://127.0.0.1:7852` (takes ~20-30 s past "Loading...";
  console shows only "Error accessing the microphone: Permission denied", Gradio's mic widget).
- Generate TTS tab -> "TTS Engine" dropdown -> f5tts -> "Swap TTS Engine": AllTalk came back on
  `f5tts - f5tts_v1a` in 5 s; `tts_engines.json` saved `"engine_loaded": "f5tts"`.
- Switch back: the first click on "xtts" in the dropdown missed (dropdown still f5tts); AllTalk was
  stopped with f5tts saved. Restarted, reloaded the page, confirmed the dropdown value by reading
  the page (`input` value = "xtts") before pressing "Swap TTS Engine": back on `xtts - xttsv2_2.0.3`
  in 84 s, saved. Stopped: 3 s, nothing left.

### 2.5 User decision: remove the `/api/enginereload` patch
Removed from `alltalk_patches.py` (commit `d1bebda6`). AllTalk started afterwards with
"applied 3 patches to tts_server.py" (was 4), ready in 28 s, stopped in 2 s.

### 2.6 How to shut AllTalk down cleanly (user asked)
Answered without code changes: in the AllTalk console window press **Q** (stops server + web page,
frees ports, closes window; only prints "stopped" if the port is free). Closing the browser tab
does not stop AllTalk. From the mic panel: Shutdown Services -> Close AllTalk Only. From the KoboldCpp
launcher: stopping the stack. Closing the console with its X button: not tested, no promise made.
AllTalk's web page has no shut-down button (searched `script.py` for Button labels with
shut/exit/stop/quit/close: none).

## 3. User's own CPU test, and the countdown

- 19:58:36 user started the shortcut; countdown passed without a registered key; AllTalk came up
  on CUDA (ready 31 s, XTTS, DeepSpeed on, ~2,770 MiB used on the card in total).
- User: "I pressed p but was too late. change the wait time to ten seconds."
- The bat could not be edited while its window was running (cmd reads a .bat line by line from
  disk). User closed AllTalk (window gone at 19:59:31); then: `set /a LEFT=10`, texts "10-second" /
  "No key within 10 seconds", KoboldCpp launcher comment. Note: Git-Bash `sed -i` stripped the CRLF
  line endings once during this edit; they were restored and checked with `file`.
- Timed with no key pressed: countdown window closed after 10.4 s, saved mode kept.
- 20:05:00 user started again and pressed P at 20:05:06: saved `cuda -> cpu`; ready 35 s; XTTS,
  DeepSpeed off; neither AllTalk process on the graphics card; total graphics card use 803 MiB
  (same as with AllTalk off).

## 4. "The voice is cutting out" - evidence

Voice mode log (`REPO_claude_code_voice_mode/logs/claude_code_voice_mode.log`):
- 20:05:45-20:06:34, reply "Yes, I can see it...": streamed 132 chunks = 11.1 s of audio over
  48.4 s, then `[STREAM-STALL] No chunk for 17.8s`, streaming disabled, recovery -> Method 2 (OpenAI
  endpoint) `Read timed out (read timeout=30)` -> Method 3.
- 20:08:12, reply "AllTalk is up in main processor mode, exac..." (exactly where the user said it
  cut off): 33 chunks = 2.7 s of audio, then `No chunk for 13.4s`, stall.
- 20:08:00 another Claude session's reply ("Today's full record is logged...") reached AllTalk at
  the same time - sessions compete for the same CPU AllTalk.
- Voice mode's stall rule (`claude_code_voice_mode_mcp_server.py:384`): a gap of more than 10 s
  between chunks = stall. Its comment says it was set for "1-5s total generation" (graphics card).
  Whole-clip fallback timeouts: 30 s (lines ~506, ~535).

## 5. Research: streaming on CPU - developer, docs, community, code

User asked what the developer and community experts say, and which settings exist; no guessing.
- AllTalk README, GPU Support: "Most of the engines will run on CPU, but some may be very slow on
  CPU." https://github.com/erew123/alltalk_tts/tree/alltalkbeta
- AllTalk FAQ: no CPU/streaming guidance beyond a table of which engines stream.
  https://github.com/erew123/alltalk_tts/wiki/FAQ,-Quirks-&-General-Questions
- Coqui XTTS docs: "Streaming inference is typically slower than regular inference, but it allows
  to get a first chunk of audio faster." No CPU guidance, no parameter recommendations.
  https://coqui-tts.readthedocs.io/en/latest/models/xtts.html
- Community: one CPU measurement, unanswered (RTF 2.05 CPU vs 0.67 GPU)
  https://github.com/coqui-ai/TTS/discussions/3695 ; AllTalk streaming discussion - speed praise is
  about DeepSpeed (GPU only) https://github.com/erew123/alltalk_tts/discussions/10 ; PR to improve
  AllTalk's XTTS streaming closed unmerged https://github.com/erew123/alltalk_tts/pull/478 ; the
  Baseten article runs on a T4 GPU and does not document chunk-size effects. Search-engine summaries
  that mixed in an IndexTTS paper's chunk-size claims were NOT used.
- Installed code (`TTS/tts/models/xtts.py`, `inference_stream`, lines 618-697): every
  `stream_chunk_size` sound tokens (AllTalk passes 20, `system/tts_engines/xtts/model_engine.py:1085`,
  hard-coded) it concatenates **all latents of the sentence so far** and runs the HiFi-GAN decoder
  on them again - work per sentence grows with every chunk. `enable_text_splitting=True` (AllTalk)
  resets it per sentence.
- Settings found (none on a settings page): chunk size (AllTalk code, 20); voice mode stall limit
  (10 s) and whole-clip timeout (30 s); PyTorch threads in AllTalk's env: 14 of 20 logical CPUs
  (default; PyTorch docs warn about oversubscription; untested); DeepSpeed (GPU only).

## 6. User's design: three modes

User: P = CPU "without streaming (current default)", R = CPU "with streaming"; "add these and create
the patches, then test". R was already "restart" in the running menu - asked; user chose: R =
CPU with streaming everywhere, restart moves to T. (User first typed "1" for a lettered question;
re-asked; answer "a".)

Before editing, the user's AllTalk window was found broken: processes alive but port 7851 not
listening since 20:09:12 (`OSError: [WinError 64] The specified network name is no longer available`,
"Accept failed on a socket"), with two generations of 597.47 s and 1394.38 s (another session's long
reply among them). Cause of the socket error not established. The window had closed by the time a
stop was requested.

## 7. What was built

### 7.1 `launch_alltalk.bat`
- Saved modes: `cuda`, `cpu` (main processor WITHOUT streaming), `cpu_stream` (WITH streaming).
- Countdown (10 s): `C` graphics card, `P` main processor (CPU) without streaming (current
  default), `R` main processor (CPU) with streaming, `S` start now. `choice /c CPRSX`.
- Running menu: `C`, `P`, `R` switch; `T` restart; `Q` stop; `M` menu. `choice /c CPRTQMX`.
- Labels: "graphics card (CUDA)", "main processor (CPU) without streaming", "main processor (CPU)
  with streaming".
- Sets for AllTalk: `FREEDOM_ALLTALK_DEVICE=<mode>`; `CUDA_VISIBLE_DEVICES=-1` in both CPU modes;
  `FREEDOM_ALLTALK_STREAM_CHUNK=%FREEDOM_ALLTALK_CPU_STREAM_CHUNK%` only in `cpu_stream` (default 20,
  overridable from outside for measuring).

### 7.2 `patches/alltalk_patches.py` (XTTS `model_engine.py`)
- Mode `cpu`: `self.streaming_capable = False` -> AllTalk's `generate_audio` raises
  "Streaming not supported by current TTS engine" (HTTP 400 on `/api/tts-generate-streaming`), so
  every client gets whole clips.
- `stream_chunk_size=int(os.environ.get("FREEDOM_ALLTALK_STREAM_CHUNK") or 20)`.

### 7.3 KoboldCpp launcher (`launcher.py`)
`ALLTALK_MODES`, `_alltalk_mode()`, three labels; option "a": `c` / `p` / `r`.

### 7.4 Mic panel (`mic_panel.py`)
Single toggle replaced by three buttons "Graphics card", "CPU, no stream", "CPU + stream"; the
current mode's button shows pressed (dark blue, disabled); the mode line wraps (`wraplength=250`) -
it was cut off at "...without strea".

### 7.5 Voice mode speech code (`claude_code_voice_mode_mcp_server.py`, uncommitted)
- Reads `REPO_alltalk/runtime/running_mode.txt`. Mode `cpu`: skips streaming, asks for the whole clip.
- Whole-clip wait: 30 s on CUDA; on CPU `60 + 0.25 s x characters` (measured 0.11 s/char, x~2.3 for
  other sessions sharing AllTalk).
- After the wait runs out it does **not** ask again via Method 3 (that queued the same text a second
  time behind the first - consistent with the 597 s / 1394 s generations).
- Bug found in this change and fixed: a timeout while the clip is downloading arrives as
  `requests.exceptions.ConnectionError`, not `ReadTimeout` (`requests/models.py:825-826`), so the first
  version still asked again (seen at 20:57:16). Now judged by elapsed time (>= 90% of the wait).
- The Stop hook (`.claude/hooks/speak_on_stop.py`, run by voice mode's venv python) imports
  `speak_text` fresh for every reply, so these changes apply on the next reply.

## 8. Measurements (same 329-character Freya paragraph; virtual playback, no sound)

Script: `stream_probe.py` - streams, records arrival times, replays them on a virtual player that
starts at the first piece and only pauses when empty. AllTalk started with the real launcher
(headless) for each row, one warm-up request first.

| Mode | Voice starts | Silent gaps while playing | Longest gap between pieces | Total time to make | Audio |
|---|---|---|---|---|---|
| Graphics card, streaming (chunk 20) | 1.3 s | none | 0.9 s | 5.7 s | 19.4 s |
| Main processor, **no streaming** (whole clip) | 36.7 s | none | - | 36.7 s | ~19 s |
| Main processor, streaming, chunk 20 | 7.6 s | 7, total 34.9 s, longest 8.7 s | **11.5 s** (> voice mode's 10 s) | 61.8 s | 19.8 s |
| Main processor, streaming, chunk 60 | 12.2 s | 3, total 39.1 s, longest 17.8 s | 23.4 s | 95.6 s | 19.4 s |
| Main processor, streaming, chunk 120 | 31.6 s | 1, 30.3 s | 41.4 s | 300.9 s | 20.9 s |
| Main processor, streaming, chunk 250 | 33.2 s | none - all audio arrived at once at 33.2 s | 0.0 s | 33.2 s | 17.3 s |

- Chunk 120 is **contaminated**: three replies from other Claude sessions reached AllTalk during it
  (voice log 20:40:19, 20:41:40, 20:43:28).
- In mode `cpu` the streaming request was refused: HTTP 400 `Streaming not supported by current TTS
  engine` (as designed).
- Conclusion: on this processor XTTS makes speech slower than it plays, so any early start runs dry;
  no chunk size tried gives early speech without gaps. To play without gaps from chunk 20 a player
  would have to wait ~42 s (61.8 s total - 19.8 s audio), later than the whole clip (36.7 s).
- A reply from another session ("You're right...", 20:38:17) got 0.6 s of audio before the test
  script stopped AllTalk - that is the "You were right and then nothing more" the user heard.

## 9. Tests of the built pieces

| Test | Result |
|---|---|
| Countdown, R pressed (sent by tool) | saved `cpu_stream`; menu shows C/P/R/S with the user's wording |
| Start via shortcut, S (saved cpu_stream) | up in cpu_stream, 28 s, streaming_capable True |
| Running menu T | restarted, new pid, same mode, 24 s |
| Running menu M | menu printed again |
| Running menu P (tool sent lowercase "p") | **no reaction**, twice |
| Same key test in a plain window (`choice /c CPRTQMX`) | p->2, m->6, p->2, t->4 (correct) |
| Running menu P (tool sent uppercase "P") | switched: saved `cpu`, running cpu in 8 s, streaming_capable False |
| Running menu R | saved `cpu_stream`, running in 24 s, streaming_capable True |
| Running menu Q | stopped in 2 s, nothing left, port free |
| KoboldCpp launcher option a: p / c / r (AllTalk stopped) | saved cpu / cuda / cpu_stream, right wording |
| Mic panel "CPU, no stream" (AllTalk on cpu_stream) | saved cpu; "AllTalk is back on the main processor (CPU) without streaming"; streaming_capable False |
| Mic panel label after fix | wraps: "AllTalk: not running (saved: main processor (CPU) without streaming)" |
| Voice mode speak_text, mode cpu, 280 chars | whole clip, Method 2 success in 56.9 s, played; **user heard the complete passage** |
| Voice mode speak_text, mode cpu, 840 chars | **failed** after 617.6 s: queued behind four other sessions' replies; the timeout-as-ConnectionError bug made it ask twice (fixed afterwards) |
| Forced 1 s wait (timeout fix) | "Method 2 timed out ... not asking again", no Method 3 (only the before-reply timeout case was produced; the mid-download case relies on the same elapsed check) |

Notes:
- Why the tool's lowercase "p" did not reach the Windows Terminal AllTalk window while lowercase
  "m" and "t" did is **not known**. The user's own physical P press in the countdown worked (20:05:06).
- The voice log stopped being written at 20:58:41 while the 840-character test ran until ~21:01:30;
  writing resumed at 21:02:47. Cause not established.
- "Restart Mic" (mic panel) restarts the panel and with it the AllTalk running inside the old
  panel's terminal; the new panel starts AllTalk again in the saved mode. Existing behaviour.

## 10. Found: AllTalk rewrites its own files when started without a graphics card

The AllTalk folder watcher showed a message box: files modified inside `app_cabinet/alltalk_tts`:
`system/tts_engines/rvc/configs/v1/32000.json, 40000.json, 48000.json`,
`.../configs/v2/32000.json, 48000.json`, `system/tts_engines/rvc/train/preprocess/preprocess.py`.
- All six have mtime 21:19:23 = the moment AllTalk restarted in main processor mode.
- `git diff` (AllTalk's repo): `"fp16_run": true` -> `false` in the five json files; `preprocess.py`
  rewritten with the same content.
- Cause, in AllTalk's code: `system/tts_engines/rvc/configs/config.py` `device_config()` - when no
  CUDA device is visible ("No supported Nvidia GPU found") it calls `use_fp32_config()` (lines 64-79),
  which rewrites every RVC config file replacing "true" with "false" and rewrites preprocess.py
  ("3.7" -> "3.0"). `Config()` is created when AllTalk imports its RVC inference code
  (`system/tts_engines/rvc/infer/infer.py:32`). The CUDA branch does not set them back (it only
  writes FP32 for older GPUs), so the change stays after switching back to the graphics card.
- These settings are used by RVC training (`train.py`: `fp16_run`). Not yet handled - parked question.

## 11. Open at the end of this log

- **Asking:** what R (main processor with streaming) should do, given it cannot stream without gaps
  on this processor: keep as is / hold playback until it can finish without gaps (~42 s start) /
  remove R / keep R but raise voice mode's stall limit so it rides out the gaps.
- **Parked:** how to handle AllTalk rewriting its RVC settings files on every start without a
  graphics card.
- Voice mode speech code changes not committed (mixed with earlier uncommitted work).
- State at the end: the mic panel had just restarted AllTalk in the saved mode `cpu` (main
  processor without streaming); engine XTTS.

## 12. Files used for measuring (scratchpad, not kept in any repo)

`stream_probe.py` (virtual-player stream measurement), `run_mode_bench.ps1` (series driver),
`mode_bench_results.txt`, `voice_mode_speak_test.py` / `run_p_test.ps1` (voice mode speak_text test),
`choice_test.bat` (key-code test), `sendkeys_safe.ps1` / `click_safe.ps1` (send keys / clicks only
to a named window), `conread.ps1` (read another console's screen, from
`REPO_koboldccp_sst_tts_media/docs/console_attach_and_read.md`).

## 13. Decision on R, and the processor warning (22:30)

- User asked where AllTalk's web page has settings for this. Checked in the page code: none.
  "Generation Mode" (Standard / Streaming) on the TTS Generator tab only affects that page's own
  generator; Xtts "Default Settings" are Low VRAM, DeepSpeed, Temperature, Repetition Penalty,
  Pitch, Speed and voices; "Engine Information" shows "Streaming Capable: Yes" (display only). The
  chunk size is fixed in AllTalk's XTTS code (now settable for mode R by the bat); voice mode's stall
  limit and whole-clip wait are in voice mode's code.
- **User decision: keep R as it is** (AllTalk's own chunk 20; voice mode's 10 s stall limit unchanged),
  **plus a warning in the menu** that both main processor options need a faster processor than this PC's.
- This PC's processor (Win32_Processor): 13th Gen Intel(R) Core(TM) i9-13900HK, 14 cores, 20 threads.
- Added to both `launch_alltalk.bat` menus (countdown and running menu):
  "WARNING: P and R need a faster processor than this PC's Intel Core i9-13900HK.
   Measured here 2026-09-30: P speaks after about 37 s for 20 s of speech;
   R starts after about 8 s but cuts in and out."
- Checked on screen: countdown (`--choose-mode`) and running menu (AllTalk started in a window, menu
  read from the console, then Q: stopped, nothing left).

## 14. RVC files: the watcher ignores them (22:45)

- The user did not know what RVC is. Checked and explained: AllTalk's own text calls it
  "Retrieval-based Voice Conversion" - an add-on that reshapes AllTalk's speech into another voice,
  after training a voice model for it ("RVC training"). On this PC it is not used: AllTalk's RVC
  character voice is "Disabled" (`REPO_alltalk/settings/confignew.json`), `models/rvc_voices` and
  `REPO_alltalk/rvc_training` are empty.
- Why it was raised: P and R make AllTalk start without a graphics card, and AllTalk's RVC code then
  edits files in AllTalk's own folder - against the "AllTalk's folder stays untouched" rule - and the
  folder watcher shows a warning box about it.
- Correction: the question first said "five files"; AllTalk rewrites **six** (five RVC configs +
  `preprocess.py`, same content but a new file date).
- **User decision: the watcher ignores all six.** `watcher/alltalk_folder_watcher.py`: added to
  `SKIP_FILES` with the reason; docstring updated. AllTalk is still allowed to edit them.
- Tested with the watcher's own `scan()` in AllTalk's Python: all six exist and are no longer
  watched; `rvc/configs/config.py` still watched; 641 files watched in total. No watcher process was
  running at the time, so the next one (started with AllTalk) uses the new list.
