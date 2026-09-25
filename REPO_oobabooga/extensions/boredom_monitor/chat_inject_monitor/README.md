# Chat Inject Monitor

A standalone GUI application with 16 verification methods to test if messages were successfully injected into the text-generation-webui chat.

## What This Does (Simple Explanation)

When the Boredom Monitor (or any extension) injects a message into the chat, we need to verify it actually worked. This app has 16 different ways to check if a message appeared in the chat.

**No command line knowledge needed!** Everything is done with buttons.

## How to Start

**Double-click** `start_chat_inject_monitor.bat`

The GUI window will open with:
- Configuration section (WebUI URL, test message)
- Quick action buttons
- 16 individual method buttons
- Status console showing all activity

## Features

### Buttons Available

**Configuration Area:**
- **Save URL** - Save the WebUI URL to config
- **Check Connection** - Test if WebUI is accessible

**Quick Actions:**
- **Quick Verify** - Run fast API-based verification
- **Run ALL 16 Methods** - Run every verification method
- **Clear Status** - Clear the status console

**16 Individual Method Buttons:**
Each button runs one verification method. Click any button to run that specific check.

### Status Console

The large text area at the bottom shows:
- Every action you take
- HTTP requests being made
- Results from each verification method
- Timestamps for all activity
- Color-coded messages (green=success, red=error, orange=warning)

## The 16 Verification Methods

| # | Name | Description |
|---|------|-------------|
| 1 | HISTORY_STATE | Check history via API |
| 2 | MESSAGE_COUNT | Count messages via API |
| 3 | DISPLAY_HTML | Check display HTML |
| 4 | METADATA_TIMESTAMP | Check for recent timestamps |
| 5 | API_STATE | Query internal API state |
| 6 | VERIFICATION_ENDPOINT | Custom verification endpoint |
| 7 | DOM_CONTENT | Check browser DOM (requires browser) |
| 8 | MUTATION_OBSERVER | Check DOM mutations (requires browser) |
| 9 | DATA_RAW | Check data-raw attributes |
| 10 | DOM_MESSAGE_COUNT | Count DOM elements (requires browser) |
| 11 | SSE_EVENTS | Monitor server events |
| 12 | REQUEST_MONITOR | Monitor HTTP requests |
| 13 | SELENIUM | Browser automation |
| 14 | COMPREHENSIVE | Run multiple methods combined |
| 15 | BROWSER_CALLBACK | Check browser JS callback |
| 16 | BROWSER_API_QUERY | Query browser verification API |

## Configuration

Edit `config.json` to change default settings:

```json
{
  "webui_base": "http://127.0.0.1:7860",
  "timeout_seconds": 5,
  "log_to_file": true,
  "log_file": "chat_inject_monitor.log",
  "default_test_message": "[INJECTION-TEST] Hello World"
}
```

Or change them in the GUI and click "Save URL".

## Log Files

Logs are saved to: `F:\Apps\freedom_system\log\chat_inject_monitor.log`

## Requirements

- Python 3.8+ (included with text-generation-webui)
- requests library (included with text-generation-webui)
- tkinter (included with Python)

## Troubleshooting

**"Connection refused" error:**
- Make sure text-generation-webui is running
- Check the WebUI URL is correct (default: http://127.0.0.1:7860)

**GUI doesn't open:**
- Make sure you're running the .bat file, not the .py file directly
- Check that Python path in the .bat file is correct

**Methods show "REQUIRES_BROWSER":**
- Some methods need a web browser to work
- Use methods 1, 2, 5, 6, 14, 15, 16 for standalone verification
