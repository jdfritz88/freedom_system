# Conversation log: AllTalk model, memory use, and the XTTS settings sync

**Dates:** 2026-09-29 evening to 2026-09-30 early morning
**Started from:** `REPO_koboldccp_sst_tts_media` (Claude Code session)
**Code changed in:** `REPO_alltalk` (part of the main `freedom_system` repo)
**Commits:** `b355d31a`, `788db862` (main `freedom_system` repo)

---

## 1. Which model AllTalk uses

**User asked:** which LLM AllTalk uses.

**Answer:** AllTalk is text-to-speech, not a chat model, so it has no LLM. It uses a voice
model: **XTTS v2, version 2.0.3**, with DeepSpeed on. The chat model in this repo's launcher
(KoboldCpp) is Rocinante-X-12B-v1b Q4_K_M (`REPO_koboldccp_sst_tts_media/launcher.py:104`).

**How it was found:**
- `REPO_alltalk/settings/system/tts_engines/tts_engines.json` (the copy `launch_alltalk.bat`
  gives AllTalk) says `"engine_loaded": "xtts"`, `"selected_model": "xtts - xttsv2_2.0.3"`.
- AllTalk's startup output from 2026-09-25, saved in an earlier Claude session transcript,
  shows `[REPO_alltalk] applied 2 patches to system/tts_engines/xtts/model_engine.py`.
  AllTalk only loads the code for the engine it is using.
- Claude's voice mode (`REPO_claude_code_voice_mode`) does not choose a model. It sends text
  and a voice name (`Freya.wav`) to AllTalk on port 7851; AllTalk speaks with whatever engine
  it has loaded.

## 2. File sizes and memory use

**File sizes (measured on disk):**

| Model | Size |
|---|---|
| XTTS v2 2.0.3 (`app_cabinet/alltalk_tts/models/xtts/xttsv2_2.0.3`) | 2.0 GB (`model.pth` 1.87 GB, `dvae.pth` 210 MB) |
| Rocinante-X-12B Q4_K_M (`app_cabinet/koboldcpp/models/`) | 7.5 GB (7,477,207,328 bytes) |

**Memory records found in the repo logs** (`REPO_koboldccp_sst_tts_media/logs/work_log_2026-09-02.md:20`,
measured 2026-09-02): AllTalk ~2.5 GB, Whisper ~1 GB, Rocinante all 41 layers on the graphics
card ~6.8 GB, 16K chat memory ~1.3 GB. `work_log_2026-09-02_continued.md:329` gives AllTalk +
Whisper together as ~5.5 GB. The logs do not say whether AllTalk was speaking or idle when
the ~2.5 GB was measured, or how it was measured.

**Measured in this conversation** (RTX 4080 Laptop, 12 GB; AllTalk started clean; other
programs using 777 MiB):

| AllTalk state | Graphics card memory AllTalk adds |
|---|---|
| Loaded, idle | 1,987 MiB (~2 GB) |
| Speaking a long passage in Freya (peak of 60 samples) | 2,853 MiB (~2.8 GB) |

The first measurement attempt was taken while a leftover AllTalk process from an earlier test
run was still running (see section 6). The table above is from the clean re-run.

## 3. The Piper finding

AllTalk's own settings file, `app_cabinet/alltalk_tts/system/tts_engines/tts_engines.json`,
said **Piper**. Its file date was 2026-09-27 22:39. The repo copy (XTTS) was unchanged since
2026-09-25.

- The layer (`REPO_alltalk/_boot/freedom_alltalk.py`) sends every read and write of that file
  to the repo copy, so AllTalk started through `launch_alltalk.bat` never saw the Piper copy.
- Later check: AllTalk's own copy **exactly matched the developer's committed version**, and
  Piper is the developer's default. It was factory state, not a random corruption. AllTalk's
  git tracks the file (`git ls-files`), and `git diff` was empty.
- What wrote it on 2026-09-27 22:39 was not determined.

## 4. Decisions made by the user

| # | Question | User's answer |
|---|---|---|
| Q1 | May I start the first plan (hand-edit AllTalk's copy to XTTS)? | Replaced by new instructions (below) |
| - | New instruction | `start_alltalk.bat` must use the repo settings; AllTalk's own copy must be updated (even after an update overwrites it) without triggering the watcher |
| Q2 | How should `start_alltalk.bat` pick up the repo settings? | **1: edit it to hand off to `launch_alltalk.bat`** |
| Q3 | Which settings files does the sync copy? | **3: every repo settings file**, with the rule: Freya must not be permanent; the voice must be changeable in AllTalk as often as wanted and save to the repo; apps must be able to change voices without restarting and still keep the settings |
| Q4 | How to test the in-page voice save? | **1: call the page's own save function directly** |
| Q5 | How should Claude's voice mode choose and keep its voice? | **4: a shared file in the main repo**, readable by every other repo |
| Q6 | May I start the plan for option 4? | Not answered; **the user dropped the voice-mode topic** ("lets drop for now") |
| Q7 | Where does this log go? | **1: `REPO_alltalk/logs/`** |

## 5. What was built

### 5.1 `start_alltalk.bat` hands off to the launcher (commit `b355d31a`)
- `start_alltalk.bat` is **not** the developer's file. AllTalk's setup program (`atsetup.bat`,
  line ~603) writes it, and AllTalk's git lists it as untracked.
- New master copy: `REPO_alltalk/app_files/start_alltalk.bat`. It calls
  `F:\Apps\freedom_system\REPO_alltalk\launch_alltalk.bat %*`, so starting AllTalk from it
  gets the repo settings, the user voices, eSpeak NG and the weekly update check.
- The master copy was copied over `app_cabinet/alltalk_tts/start_alltalk.bat`.
- The setup program's original is kept at
  `REPO_alltalk/archive/start_alltalk_stock_2026-09-29.bat`.
- **Known limit (accepted with option 1):** running AllTalk's setup program again rewrites
  `start_alltalk.bat` and undoes the hand-off.

### 5.2 Watcher recognizes files the repo places (commits `b355d31a`, `788db862`)
File: `REPO_alltalk/watcher/alltalk_folder_watcher.py`
- New `PLACED_FILES` map (`start_alltalk.bat` → `app_files/start_alltalk.bat`) and
  `is_placed_by_repo()`.
- A new or changed file in AllTalk's folder that **exactly matches** its source (a
  `PLACED_FILES` entry, or its twin under `REPO_alltalk/settings/`) is logged as
  `placed by REPO_alltalk, matches its source - not alerted`. Anything else still alerts.
- It does not fake file dates and does not edit the known-files list to hide a change.

### 5.3 Settings sync (commit `788db862`)
File: `REPO_alltalk/_boot/freedom_alltalk.py`
- `mirror_all_settings()` runs in `boot()` and `boot_host()`. It copies every `*.json` under
  `REPO_alltalk/settings/` onto AllTalk's own copy **if they differ**. An update that
  overwrote them is put back on the next start.
- `_MirrorOnClose`: when AllTalk opens a settings file for writing, the layer already sends
  the write to the repo copy. The file object is now wrapped, and on close the repo copy is
  copied onto AllTalk's own copy. **A voice or engine picked in AllTalk's page, or by any app
  that saves through AllTalk, shows in both places at once with no restart.**
- Nothing is hard-coded. Whatever the repo settings say is what gets copied, so Freya is not
  made permanent.
- Messages go to **stderr** and to `REPO_alltalk/logs/settings_mirror.log`.
- Module docstring updated: AllTalk's folder is never written to, except by this sync
  (user decision 2026-09-29).

### 5.4 Update check puts the developer's versions back first (commit `788db862`)
File: `REPO_alltalk/update_check.ps1`
- After the user says Yes to an update, and before `git pull --ff-only`, every repo settings
  file that is a tracked developer file and differs locally gets `git checkout -- <file>`.
  The pull then can't fail on local changes to those files. The next start copies the repo
  settings over them again. The files put back are listed in `logs/update_checks.log`.
- This happens inside the existing watcher update window, so the watcher does not alert.

## 6. Tests and results

| Test | Result |
|---|---|
| Watcher, `start_alltalk.bat` matching its source | Logged, **no alert** |
| Watcher, `start_alltalk.bat` with one extra line | **Alerted** as MODIFIED (file restored afterwards) |
| Start AllTalk from `start_alltalk.bat` | Repo layer loaded, patches applied, **XTTS loaded** (`/api/currentsettings`: `current_engine_loaded: xtts`, `current_model_loaded: xtts - xttsv2_2.0.3`, `deepspeed_enabled: true`) |
| Overwrite repair: AllTalk's own `tts_engines.json` set back to the developer's Piper version with `git checkout`, then start | Log: `settings copied to AllTalk's own copy: system\tts_engines\tts_engines.json`; file back to XTTS; XTTS loaded |
| All 10 repo settings files vs AllTalk's own copies after start | All identical |
| Save a voice through AllTalk's page save function (`/xtts_model_update_settings`, called with `gradio_client` on the running AllTalk) | Setting `female_01.wav`: repo **and** AllTalk's copy both changed instantly, files identical. Setting Freya back: both changed back. Repo file byte-identical to before the test. |
| Watcher during the runs | `placed by REPO_alltalk, matches its source - not alerted: mem_config.json, system\tts_engines\tts_engines.json`; no alerts |
| Update-check file selection (dry run, nothing changed) | Picked exactly the 4 files that differ from the developer's (`confignew.json`, `tgwui_remote_config.json`, `tts_engines.json`, `xtts/model_settings.json`); skipped the 6 identical ones |
| Memory idle / speaking | See section 2 |

## 7. Problems hit and how they were handled

1. **Wrong launch command.** `cmd //c "start_alltalk.bat"` from Git Bash did not pick up the
   folder ("not recognized"). Fixed by using the full path.
2. **The layer also loads inside `conda.exe`.** `launch_alltalk.bat` runs
   `conda.bat activate`, which runs `conda.exe` (a Python program). `conda.exe` inherits
   `PYTHONPATH` and the `FREEDOM_ALLTALK_*` variables, so `sitecustomize.py` boots the layer
   there too (proven with `conda.exe --version`). `conda.bat` captures conda's stdout into a
   temp file and reads the activation script path back from it. The sync's first messages
   went into that captured output, so they never reached the screen. Activation still worked,
   because conda uses the last line. **Fix:** sync messages go to stderr (which conda leaves
   on screen) and to `logs/settings_mirror.log`.
3. **Typo in my edit.** A line break landed inside an f-string, and the layer failed with
   `SyntaxError` (AllTalk would have refused to start). It was caught by the `conda.exe` test
   before any real start, fixed, and compile-checked.
4. **A leftover process from the first test run.** When stopping the first run, AllTalk's main
   process (PID 32028, command line just `python  script.py`) was missed, because the stop
   filter looked for `alltalk_tts` in the command line. It kept port 7852. The second run's
   page then failed (`Cannot find empty port in range: 7852-7852`), and the page Chrome showed
   belonged to the leftover process. **Fix:** all test processes were stopped by the ports they
   own and their parent/child processes, then AllTalk was started clean and memory was
   re-measured.
5. **Chrome froze on AllTalk's settings page** (screenshots and scripts timing out; the page
   takes close to a minute to load). After several failed attempts, the user chose to test the
   save by calling the page's own save function directly (Q4 option 1). **Not tested:** the
   physical click on the Update Settings button.

## 8. Not done / not tested

- A **real** AllTalk update through `update_check.ps1`. Only the file selection was dry-run.
- Whether each app (oobabooga add-on, KoboldCpp chat, voice mode) picks up a changed
  **default** voice without a restart. The saved change reaches both files at once (tested).
  AllTalk's voice server reads the XTTS default only when XTTS loads
  (`system/tts_engines/xtts/model_engine.py:350`), so the running server keeps the old default
  until XTTS reloads or AllTalk restarts.
- Running AllTalk's setup program again rewrites `start_alltalk.bat` (known and accepted).
- What wrote Piper into AllTalk's own `tts_engines.json` on 2026-09-27 22:39 is unknown.

## 9. Voice-mode topic (dropped by the user)

This topic was raised by Claude, not the user, while checking the user's rule about changing
voices without restarting. Findings, for the record:

- Voice mode has `Freya.wav` written into its code (`DEFAULT_VOICE` in
  `claude_code_voice_mode_mcp_server.py` and in the older, unused `tts_hook.py`).
- The spoken replies come from the Stop hook (`.claude/hooks/speak_on_stop.py`). It starts a
  new process after every reply and calls `speak_text()` with no voice, so it always uses the
  default, Freya. The `set_voice` tool only changes the background server's in-memory voice,
  so **a voice switch never reaches the spoken replies**, and nothing is saved across restarts.
- Other apps' voice settings, for context:
  - **KoboldCpp launcher:** `REPO_koboldccp_sst_tts_media/alltalk_profile.json` has
    `"voice": "Freya.wav"`, but `configure_alltalk()` only uses the DeepSpeed setting. **The
    voice line is unused.** Where KoboldCpp's chat page chooses its voice was not checked.
  - **oobabooga's AllTalk add-on:** reads the voice from `REPO_alltalk/settings/confignew.json`
    fresh before every message ("Forcing config refresh before reading voice settings"), so
    changes there apply without a restart. That file moved into the repo on 2026-09-25
    (commit `6f549f16`).
  - **SillyTavern:** text-to-speech is off, and the provider is "System" (the Windows/browser
    voice, not AllTalk), with no voices mapped (`app_cabinet/sillytavern/data/default-user/settings.json`,
    last saved 2026-09-01).
- The user picked option 4 (a shared voice file in the main repo, readable by every repo).
  The plan was presented, then **the user dropped the topic**. Nothing in voice mode was
  changed. Freya is still its voice exactly as before.

## 10. State at the end

- AllTalk is **not running**. All test processes were stopped, ports 7851/7852 are free, and
  graphics card memory was back to 647 MiB.
- The Chrome test tab is closed. The two test audio files (`outputs/vram_test_*.wav`,
  `outputs/vram_test2_*.wav`) were deleted.
- AllTalk's own settings copies all match `REPO_alltalk/settings/` (XTTS, Freya).
- There are no open questions.
