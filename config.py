"""
Configuration manager for Script Scheduler.
Handles loading, saving, and validating the JSON config file.
"""

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = {
    "auto_run_enabled": False,
    "auto_run_time": "06:00",
    "default_timeout": 300,
    "last_browse_dir": "",
    "schedules": {
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
    },
}

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

CONFIG_DIR = Path.home() / ".script_scheduler"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_DIR = CONFIG_DIR / "logs"


def ensure_dirs():
    """Create config and log directories if they don't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load config from JSON file, returning defaults if not found."""
    ensure_dirs()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return _merge_defaults(data)
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Save config to JSON file."""
    ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def _merge_defaults(data: dict) -> dict:
    """Ensure all default keys exist in loaded config."""
    merged = DEFAULT_CONFIG.copy()
    merged.update(data)
    # Ensure all weekdays exist in schedules
    if "schedules" not in merged:
        merged["schedules"] = DEFAULT_CONFIG["schedules"].copy()
    for day in WEEKDAYS:
        if day not in merged["schedules"]:
            merged["schedules"][day] = []
    return merged


def add_script_to_day(config: dict, day: str, script_path: str, name: str = "") -> dict:
    """Add a script entry to a specific day."""
    if day not in WEEKDAYS:
        raise ValueError(f"Invalid day: {day}")
    entry = {
        "path": str(script_path),
        "name": name or Path(script_path).stem,
        "enabled": True,
        "timeout": config.get("default_timeout", 300),
    }
    # Avoid duplicates
    existing_paths = [s["path"] for s in config["schedules"][day]]
    if str(script_path) not in existing_paths:
        config["schedules"][day].append(entry)
    return config


def remove_script_from_day(config: dict, day: str, script_path: str) -> dict:
    """Remove a script entry from a specific day."""
    if day not in WEEKDAYS:
        raise ValueError(f"Invalid day: {day}")
    config["schedules"][day] = [
        s for s in config["schedules"][day] if s["path"] != str(script_path)
    ]
    return config


def toggle_script(config: dict, day: str, script_path: str) -> dict:
    """Toggle enabled/disabled state of a script."""
    for entry in config["schedules"].get(day, []):
        if entry["path"] == str(script_path):
            entry["enabled"] = not entry["enabled"]
            break
    return config


def get_today_scripts(config: dict) -> list[dict]:
    """Get all enabled scripts scheduled for today."""
    import datetime
    today = datetime.datetime.now().strftime("%A")
    if today not in WEEKDAYS:
        return []
    return [s for s in config["schedules"].get(today, []) if s.get("enabled", True)]


def get_scripts_for_day(config: dict, day: str) -> list[dict]:
    """Get all scripts scheduled for a specific day."""
    return config["schedules"].get(day, [])
