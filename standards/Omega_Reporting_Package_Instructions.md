OMEGA PACKAGE REPORT PARAMETERS

Report Scope:
- Root Directory: F:\Apps\freedom_system
- Mode: Full recursive scan
- No partial updates

Required Script:
- freedom_system_scan.py (must be run first)
- freedom_system_scan log, with today's date in in the file name, must be present before report generation
- Located in F:\Apps\freedom_system\log\

File Types & Exclusions:
- Included: All .py, .bat, .txt, .md, .log, .safetensors
- Excluded: .git, __pycache__, all .pyc, and __init__.py

Key Report Sections:
1. STRUCTURE OVERVIEW
   - Scan target path
   - Exclusion rules listed
   - Total files and directories scanned


2. COMPLETION STATUS OF COMPONENTS 
- Include final percent estimate of total system readiness for each component
   - Emotion Core
   - Image System
   - Voice Input System
   - Voice Ouput System
   - Music Input Logic
   - UI Panels
   - Animation Modules
   - Face Trainer
   - FULL SYSTEM


3. RECENT ACCOMPLISHMENTS  
- Provide a description of what was accomplished over the last 72 hours as if speaking to a high schooler
- Break up each component by paragraph


4. MAPPING
- Must generate a full recursive folder and file listing, not just folder names.
- Every subfolder and file in F:\Apps\freedom_system must be shown, respecting the same exclusions (.git, __pycache__, *.pyc, __init__.py).
- Use an indented tree format like this:
  F:\Apps\freedom_system
  ├── su
  │   ├── text-generation-webui
  │   │   ├── text-generation-webui_env
  │   │   │   ├── bin
  │   │   │   └── lib
  │   ├── installation
  │   │   ├── text-generation-webui_installation
  │   │   │   ├── text-generation-webui_final_validation.py
  │   │   │   └── other files...
  └── log
      ├── freedom_system_scan_2025-07-05_[time].txt

- If the scan log contains the folder structure, parse and reuse it.
- If the scan log is incomplete, run a fresh recursive folder scan from F:\Apps\freedom_system before building the report.


5. REPORT OUTPUT 
-Report Name:
-Freedom-System-Omega-Package-FULL-[YYYY-MM-DD]-[PST-TIME].[ext]
-Always generate a report in the following output formats that the user will save to the hard drive:
 - Markdown (.md)
 - Plaintext (.txt)
 - All versions regenerated fresh from scratch each time—no reuse or overwrite of prior snapshots
