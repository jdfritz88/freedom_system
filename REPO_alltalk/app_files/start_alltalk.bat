@echo off
rem Placed here by REPO_alltalk (user decision 2026-09-29). AllTalk's setup program
rem (atsetup.bat) writes its own start_alltalk.bat; this one hands off to the REPO_alltalk
rem launcher instead, so starting AllTalk from here also gets the repo settings, the user
rem voices, the eSpeak NG phonemes tool and the weekly update check.
rem Source of truth: F:\Apps\freedom_system\REPO_alltalk\app_files\start_alltalk.bat
rem The setup program's original is kept in REPO_alltalk\archive.
call "F:\Apps\freedom_system\REPO_alltalk\launch_alltalk.bat" %*
