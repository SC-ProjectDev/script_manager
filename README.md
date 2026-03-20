# Script Scheduler

A desktop GUI orchestrator for scheduling and executing Python scripts on a weekly Mon–Fri calendar.
Built with PySide6 — dark theme, parallel execution, live telemetry feed.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)
![PySide6](https://img.shields.io/badge/GUI-PySide6-green)

---

## Features

- **Weekly calendar view** — Mon–Fri columns; assign scripts to any day(s)
- **File explorer** — browse your filesystem and select `.py` scripts
- **Add dialog** — pick days, set display name, configure timeout per script
- **Quick-schedule presets** — "All days", "Mon/Wed/Fri", "Tue/Thu" buttons
- **Parallel execution** — all scripts for today run simultaneously via `subprocess`
- **Enable/disable toggle** — per-script checkbox; disabled scripts stay visible but are skipped
- **Auto-run** — optional timer: runs today's scripts automatically at a set time (Mon–Fri only)
- **Live log feed** — color-coded telemetry (green=success, red=fail, purple=running, amber=warning)
- **Log to file** — every run writes a timestamped log to `~/.script_scheduler/logs/`
- **Desktop notifications** — system tray notification on script failure
- **Persistent config** — JSON config saved at `~/.script_scheduler/config.json`
- **Dark theme** — ops-console aesthetic, easy on the eyes

---

## Installation

```bash
# 1. Ensure Python 3.10+
python --version

# 2. Install PySide6
pip install PySide6

# 3. Run the app
cd script_scheduler
python main.py
```

---

## Project Structure

```
script_scheduler/
├── main.py                  # App entry point + main window
├── config.py                # JSON config load/save/validation
├── scheduler.py             # Parallel script execution engine
├── theme.py                 # Dark theme stylesheet + color palette
├── widgets/
│   ├── __init__.py
│   ├── file_explorer.py     # Left panel file browser
│   ├── week_calendar.py     # Mon–Fri calendar grid
│   ├── log_feed.py          # Scrolling telemetry panel
│   └── add_dialog.py        # "Add to schedule" dialog
└── README.md
```

---

## Usage

### Adding Scripts
1. Use the **File Explorer** (left panel) to browse to your scripts directory
2. Double-click a `.py` file or select it and click **"Select Script"**
3. In the dialog, pick which day(s), set a display name, and configure timeout
4. The script appears in the calendar under the selected days

### Running Scripts
- Click **"▶ Run Today"** to execute all enabled scripts for today's day-of-week
- Watch the **Execution Log** for real-time status
- Click **"■ Stop"** to cancel (running scripts will finish their current operation)

### Auto-Run
- Check **"Auto-run at:"** and set a time (e.g., 06:00)
- The app checks every 30 seconds; when the time is reached, it auto-executes
- Only triggers once per day, only on weekdays (Mon–Fri)
- Uncheck to disable — you can still run manually with the Run button

### Managing Scripts
- **Right-click** a script in any day column → "Remove"
- **Uncheck** the checkbox next to a script to disable it (greyed out, skipped on execution)
- All changes auto-save to the JSON config

---

## Config File

Located at `~/.script_scheduler/config.json`:

```json
{
  "auto_run_enabled": false,
  "auto_run_time": "06:00",
  "default_timeout": 300,
  "last_browse_dir": "/path/to/scripts",
  "schedules": {
    "Monday": [
      {
        "path": "/path/to/daily_report.py",
        "name": "Daily Sales Report",
        "enabled": true,
        "timeout": 300
      }
    ],
    "Tuesday": [],
    "Wednesday": [],
    "Thursday": [],
    "Friday": []
  }
}
```

---

## Logs

Execution logs are saved to `~/.script_scheduler/logs/` with filenames like
`run_20260320_143201.log`. Click **"Open Logs"** in the toolbar to open the folder.

---

## Tips

- Scripts run from their own directory (`cwd` = script's parent folder), so relative
  paths inside your scripts will work as expected.
- Each script runs in a fresh Python subprocess — no shared state between scripts.
- If a script fails, other scripts continue running (parallel, independent).
- The timeout is per-script. Default is 300 seconds (5 minutes). Adjust in the Add dialog
  or edit the JSON config directly.
