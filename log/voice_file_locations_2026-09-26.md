# Voice file locations — 2026-09-26 (updated 2026-09-27)

> **Update 2026-09-27:** backups #6 and #7 — and then the whole backup folder
> `F:\Apps\freedom_system_BACKUP_ooba_v3.12\` — were **deleted** on the user's instruction.
> Six folders with voice files remain. See "2026-09-27: backups deleted" below.

Where every voice `.wav` file lives after the oobabooga + AllTalk update of 2026-09-24/25
(see `conversation_2026-09-24_ooba_alltalk_update.md`), and why there are extra copies.

## How this was searched

- Scope: all of `F:\Apps`, skipping `.git`, `node_modules`, `site-packages`, `venv`, `env`,
  `installer_files`, `alltalk_environment`.
- Rule 1: every folder holding `.wav` files whose path mentions "voice" or "speaker".
- Rule 2: every folder holding the user's own voices by file name
  (Freya, Peach, Succubus, yandere, Dinner, Doggy, Game, Massage).
- Limit: a voice `.wav` in a folder whose name doesn't mention "voice"/"speaker" and isn't one of
  the named voices would not be found.
- An earlier search that only matched folders literally named `voices` missed #2
  (`voice_profiles`).

## The 8 folders (as found on 2026-09-26)

| # | Folder | .wav | Size | Whose | Notes |
|---|---|---|---|---|---|
| 1 | `F:\Apps\freedom_system\REPO_alltalk\voices` | 8 | 1.1 GB | **User** | **The working copy AllTalk uses.** Dinner, Doggy, Freya, Game, Massage, Peach, Succubus, yandere (+ 11 `.mp4` source videos). **Not in git** (user decision 2026-09-25, `REPO_alltalk\.gitignore`). The only copy of Dinner, Doggy, Game, Massage, Peach, Virgin, Workout and the two Xvideos `.mp4`. |
| 2 | `F:\Apps\freedom_system\REPO_avatarAI\backend\voice_profiles` | 4 | 18 MB | avatarAI project | Four `.wav` named by ID (e.g. `74596d4a-....wav`). Not tracked by that repo's git. Not part of this update. |
| 3 | `F:\Apps\freedom_system\REPO_oobabooga\user_data\extensions\coqui_tts_api\voices` | 5 | 1.8 MB | User's add-on | The old `coqui_tts_api` oobabooga add-on: arnold, cn-taco-ddc-gpu, female_01, female_02, sample_1. |
| 4 | `F:\Apps\freedom_system\app_cabinet\alltalk_tts\voices` | 19 | 8.9 MB | AllTalk (stock) | The developer's voices: Arnold, Clint Eastwood (2), David Attenborough, James Earl Jones, Morgan Freeman, Sophie Anderson, female_01–07, male_01–05. AllTalk lists these together with #1. |
| 5 | `F:\Apps\freedom_system\app_cabinet\text-generation-webui\extensions\coqui_tts\voices` | 3 | 1.7 MB | oobabooga (stock) | arnold, female_01, female_02 — ships with oobabooga's own coqui_tts extension. |
| 6 | ~~`F:\Apps\freedom_system_BACKUP_ooba_v3.12\extensions_moved_out_2026-09-25\alltalk_tts\voices`~~ | 21 | 460 MB | Backup | **DELETED 2026-09-27.** Old stock AllTalk voices + **identical copies** of Freya.wav, Succubus.wav/.mp4, yandere.wav/.mp4. |
| 7 | ~~`F:\Apps\freedom_system_BACKUP_ooba_v3.12\extensions_moved_out_2026-09-25\coqui_tts_api\voices`~~ | 5 | 1.8 MB | Backup | **DELETED 2026-09-27.** Identical copy of #3. |
| 8 | `F:\Apps\YuE\jacob-YuE-UI\tmp\8cbf1878f05e2e8f608fb814cf6c34f54d450c94c00485ff1d410b3a34d274ef` | 1 | 18 MB | YuE app | YuE's own temp copy of Freya.wav — **identical** to #1. |

## Why #6 and #7 existed

No program copies voice files — not the launchers, update checks, watcher or REPO_alltalk layer.
The backup folders exist because of one manual move during the update (plan step 7), which moved
the old second AllTalk copy and the old add-ons out of oobabooga's folder instead of deleting them:

```powershell
Move-Item -LiteralPath "$X\alltalk_tts" -Destination "$B\alltalk_tts"      # also boredom_monitor, coqui_tts_api
# X = F:\Apps\freedom_system\app_cabinet\text-generation-webui\extensions
# B = F:\Apps\freedom_system_BACKUP_ooba_v3.12\extensions_moved_out_2026-09-25
```

That old AllTalk copy carried its own `voices\` folder, so its Freya, Succubus and yandere are now
duplicates of the ones in #1.

## Copies of the user's own voices (after the 2026-09-27 deletion)

| Voice | Copies on disk | Where |
|---|---|---|
| Freya.wav | 2 | #1, #8 (identical) |
| Succubus.wav / .mp4 | 1 | #1 only |
| yandere.wav / .mp4 | 1 | #1 only |
| Dinner, Doggy, Game, Massage, Peach (.wav + .mp4), Virgin.mp4, Workout.mp4, 2 Xvideos .mp4 | 1 | #1 only |

## In git

- Voice files are kept out of git (user decision, question 31). They were in the first backup
  commit of branch `ooba-alltalk-update`; that branch was rewritten on 2026-09-26 to remove them
  (two were over GitHub's 100 MB limit: yandere.wav 202.6 MB, Succubus.wav 128.3 MB) and pushed.
- The local-only branch `backup/ooba-alltalk-update-before-voice-removal` (not pushed) still
  holds 45 voice files from the old copy, including Freya, Succubus and yandere `.wav`.

## 2026-09-27: backups deleted

User instruction: move every audio file from backups #6 and #7 into `REPO_alltalk\voices`, except
duplicates (unless the files differ), then delete the backups.

- **Nothing was moved** — every audio file in #6 and #7 had an identical copy elsewhere:
  - #6: Freya, Succubus, yandere (`.wav` + `.mp4`) identical to #1; the 19 stock voices identical to #4.
  - #7: all 5 identical to #3 (`arnold`, `female_01`, `female_02` are also identical to #4's stock voices).
- **Deleted:** folder #6 (47 files: 23 audio + 24 stock `.reference.txt` / xtts placeholder files)
  and folder #7 (5 audio files).
- **Then deleted, on a further instruction:** the whole `F:\Apps\freedom_system_BACKUP_ooba_v3.12\`
  (about 24.9 GB): oobabooga's old v3.12 environment (11.2 GB; rolling back to it is no longer
  possible) and the old AllTalk copy (incl. its 9.9 GB environment), boredom_monitor and
  coqui_tts_api (13.7 GB). Current copies of boredom_monitor and coqui_tts_api remain in
  `REPO_oobabooga\user_data\extensions`; the old AllTalk copy's code remains in git under
  `REPO_alltalk\_import\` (without voices).

**Folders with voice files now: 6** — #1, #2, #3, #4, #5, #8.

## 2026-09-27: all user voice files moved to one folder

User decision: every user voice file for every repo/app goes in one flat folder,
**`F:\Apps\freedom_system\user_voice_files`** (REPO_waiver always excluded), kept out of git.

- **Moved (23 files, 1.02 GB, no name clashes):** the 19 files from `REPO_alltalk\voices`
  (8 `.wav` voices + 11 `.mp4` source videos) and avatarAI's 4 cloned voices from
  `REPO_avatarAI\backend\voice_profiles`. `REPO_alltalk\voices` removed (empty).
- **avatarAI's `index.json` stays** in `backend\voice_profiles` (user's choice; git ignores that
  folder, so updates don't erase it). Its 4 paths now point to `user_voice_files`; the old version
  is kept as `index.json.backup_2026-09-27`.
- **Deleted (user's choice):** the whole old `coqui_tts_api` add-on (`REPO_oobabooga\user_data\
  extensions\coqui_tts_api`, 18 files incl. its 5 voices; recoverable from git history).
- **AllTalk:** `REPO_alltalk\_boot\freedom_alltalk.py` `REPO_VOICES` now = `user_voice_files`;
  voice-list merging now ignores upper/lower case.
- **avatarAI:** `REPO_avatarAI\freedom_boot\sitecustomize.py` (loaded by `start_avatarAI.bat`)
  saves new recordings in `user_voice_files`, in memory only.
- **Side effect of one flat folder:** AllTalk now also lists avatarAI's 4 cloned voices (31 voices).

**Verified 2026-09-27:** AllTalk lists 31 voices, no duplicates; Freya via voice mode's route
(HTTP 200, 202 Hz); Claude's voice hook spoke from the new folder; oobabooga chat reply spoken in
Freya (204 Hz, add-on log "Actual character_voice used: Freya.wav"); avatarAI lists all 4 voices
and each preview returns the exact file from `user_voice_files`; avatarAI's safety stop works;
AllTalk's folder unchanged.

**Folders with voice files now:** `user_voice_files` (all user voices), `app_cabinet\alltalk_tts\
voices` and `app_cabinet\text-generation-webui\extensions\coqui_tts\voices` (stock), and the YuE
temp copy of Freya (outside freedom_system).

## Corrections made in the conversation

- `REPO_alltalk\voices` is 1.1 GB, not "about 0.5 GB" as first stated.
