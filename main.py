"""
Script Scheduler — Main Window
Orchestrator GUI for scheduling and running Python scripts on a weekly calendar.
"""

import sys
import datetime
import threading

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QPushButton, QLabel, QCheckBox, QTimeEdit,
    QSystemTrayIcon, QMenu, QMessageBox,
)
from PySide6.QtCore import Qt, QTime, QTimer, Slot, Signal, QObject
from PySide6.QtGui import QIcon, QAction

from config import (
    load_config, save_config, add_script_to_day, remove_script_from_day,
    toggle_script, get_today_scripts, WEEKDAYS, LOG_DIR,
)
from scheduler import ScriptRunner, EXECUTION_LOG_CSV
from theme import DARK_STYLESHEET
from widgets.file_explorer import FileExplorer
from widgets.week_calendar import WeekCalendar
from widgets.log_feed import LogFeed
from widgets.add_dialog import AddScriptDialog


class _RunnerSignals(QObject):
    """Qt signals to safely bridge background thread callbacks to the GUI thread."""
    log = Signal(str, str)
    script_complete = Signal(object)
    all_done = Signal(object)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Script Scheduler")
        self.setMinimumSize(1100, 700)
        self.resize(1300, 800)

        self._config = load_config()

        # Create signal bridge for thread-safe GUI updates
        self._signals = _RunnerSignals(self)
        self._signals.log.connect(self._on_log)
        self._signals.script_complete.connect(self._on_script_complete)
        self._signals.all_done.connect(self._on_all_done)

        self._runner = ScriptRunner(
            on_log=self._signals.log.emit,
            on_complete=self._signals.script_complete.emit,
            on_all_done=self._signals.all_done.emit,
        )

        self._build_ui()
        self._load_config_into_ui()
        self._setup_auto_run_timer()
        self._setup_tray_icon()

    # ──────────────────────────────────────────────
    # UI Construction
    # ──────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 8, 12, 0)
        root_layout.setSpacing(8)

        # ── Toolbar ──
        toolbar = self._build_toolbar()
        root_layout.addLayout(toolbar)

        # ── Main content: splitters ──
        # Horizontal split: file explorer | (calendar + log)
        h_splitter = QSplitter(Qt.Horizontal)

        # Left panel: file explorer
        self._file_explorer = FileExplorer(
            initial_dir=self._config.get("last_browse_dir", "")
        )
        self._file_explorer.script_selected.connect(self._on_script_selected)
        h_splitter.addWidget(self._file_explorer)

        # Right side: vertical split of calendar + log
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        v_splitter = QSplitter(Qt.Vertical)

        # Calendar
        self._calendar = WeekCalendar()
        self._calendar.config_changed.connect(self._on_config_changed)
        v_splitter.addWidget(self._calendar)

        # Log feed
        self._log_feed = LogFeed()
        v_splitter.addWidget(self._log_feed)

        v_splitter.setStretchFactor(0, 3)
        v_splitter.setStretchFactor(1, 2)

        right_layout.addWidget(v_splitter)
        h_splitter.addWidget(right_widget)

        h_splitter.setStretchFactor(0, 1)
        h_splitter.setStretchFactor(1, 3)

        root_layout.addWidget(h_splitter, 1)

        # ── Status bar ──
        self._status_label = QLabel()
        self._status_label.setObjectName("statusBar")
        self._update_status_bar()
        root_layout.addWidget(self._status_label)

    def _build_toolbar(self) -> QHBoxLayout:
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        # App title
        title = QLabel("⚙  SCRIPT SCHEDULER")
        title.setStyleSheet(
            "font-size: 15px; font-weight: 800; letter-spacing: 2px; color: #4a9eff;"
        )
        toolbar.addWidget(title)
        toolbar.addSpacing(20)

        # Run Today button
        self._run_btn = QPushButton("▶  Run Today")
        self._run_btn.setObjectName("runButton")
        self._run_btn.setToolTip("Execute all enabled scripts scheduled for today")
        self._run_btn.clicked.connect(self._run_today)
        toolbar.addWidget(self._run_btn)

        # Stop button
        self._stop_btn = QPushButton("■  Stop")
        self._stop_btn.setObjectName("stopButton")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_execution)
        toolbar.addWidget(self._stop_btn)

        toolbar.addSpacing(20)

        # Auto-run controls
        self._auto_run_check = QCheckBox("Auto-run at:")
        self._auto_run_check.setToolTip("Automatically execute today's scripts at the set time")
        self._auto_run_check.toggled.connect(self._on_auto_run_toggled)
        toolbar.addWidget(self._auto_run_check)

        self._auto_run_time = QTimeEdit()
        self._auto_run_time.setDisplayFormat("HH:mm")
        self._auto_run_time.setTime(QTime(6, 0))
        self._auto_run_time.setEnabled(False)
        self._auto_run_time.timeChanged.connect(self._on_auto_time_changed)
        toolbar.addWidget(self._auto_run_time)

        toolbar.addStretch()

        # Open logs folder
        logs_btn = QPushButton("Open Logs")
        logs_btn.setObjectName("smallButton")
        logs_btn.setToolTip(str(LOG_DIR))
        logs_btn.clicked.connect(self._open_logs_folder)
        toolbar.addWidget(logs_btn)

        # Open execution log CSV
        csv_btn = QPushButton("Execution Log")
        csv_btn.setObjectName("smallButton")
        csv_btn.setToolTip(f"Open {EXECUTION_LOG_CSV}")
        csv_btn.clicked.connect(self._open_execution_log)
        toolbar.addWidget(csv_btn)

        return toolbar

    # ──────────────────────────────────────────────
    # Config ↔ UI
    # ──────────────────────────────────────────────

    def _load_config_into_ui(self):
        self._calendar.load_from_config(self._config)

        auto = self._config.get("auto_run_enabled", False)
        self._auto_run_check.setChecked(auto)
        self._auto_run_time.setEnabled(auto)

        time_str = self._config.get("auto_run_time", "06:00")
        parts = time_str.split(":")
        if len(parts) == 2:
            self._auto_run_time.setTime(QTime(int(parts[0]), int(parts[1])))

    def _save_current_config(self):
        """Rebuild config from UI state and save."""
        for day in WEEKDAYS:
            col = self._calendar.get_column(day)
            if col:
                # Rebuild the schedule from the list widget
                scripts = []
                for i in range(col._list.count()):
                    item = col._list.item(i)
                    timeout = item.data(Qt.UserRole + 1)
                    if timeout is None:
                        timeout = self._config.get("default_timeout", 300)
                    scripts.append({
                        "path": item.data(Qt.UserRole),
                        "name": item.text(),
                        "enabled": item.checkState() == Qt.Checked,
                        "timeout": timeout,
                    })
                self._config["schedules"][day] = scripts

        self._config["auto_run_enabled"] = self._auto_run_check.isChecked()
        time = self._auto_run_time.time()
        self._config["auto_run_time"] = f"{time.hour():02d}:{time.minute():02d}"
        self._config["last_browse_dir"] = self._file_explorer.get_current_dir()

        save_config(self._config)

    def _on_config_changed(self):
        self._save_current_config()
        self._update_status_bar()

    # ──────────────────────────────────────────────
    # Script selection & scheduling
    # ──────────────────────────────────────────────

    def _on_script_selected(self, script_path: str):
        """File explorer selection → open add dialog."""
        dialog = AddScriptDialog(
            script_path,
            default_timeout=self._config.get("default_timeout", 300),
            parent=self,
        )
        if dialog.exec() == AddScriptDialog.Accepted:
            entry = {
                "path": script_path,
                "name": dialog.display_name,
                "enabled": True,
                "timeout": dialog.timeout,
            }
            for day in dialog.selected_days:
                self._calendar.add_script_to_day(day, entry)
                self._config = add_script_to_day(
                    self._config, day, script_path, dialog.display_name
                )
            self._save_current_config()
            self._update_status_bar()
            self._log_feed.log(
                f"Added '{dialog.display_name}' to {', '.join(d[:3] for d in dialog.selected_days)}",
                "info",
            )

    # ──────────────────────────────────────────────
    # Execution
    # ──────────────────────────────────────────────

    def _run_today(self):
        """Run all enabled scripts for today's day-of-week."""
        # Refresh config from UI before running
        self._save_current_config()
        scripts = get_today_scripts(self._config)

        if not scripts:
            today = datetime.datetime.now().strftime("%A")
            self._log_feed.log(f"No enabled scripts for {today}.", "warning")
            return

        self._run_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._runner.run_scripts(scripts)

    def _stop_execution(self):
        self._runner.stop()
        self._stop_btn.setEnabled(False)

    @Slot(str, str)
    def _on_log(self, message: str, level: str):
        """Thread-safe log callback — invoked from the runner thread."""
        # QTextEdit.append is thread-safe in PySide6
        self._log_feed.log(message, level)

    @Slot(object)
    def _on_script_complete(self, result):
        """Called per script completion — check for failures to notify."""
        if not result.success:
            self._send_notification(
                f"Script Failed: {result.name}",
                result.error_message[:200] if result.error_message else "Unknown error",
            )

    @Slot(list)
    def _on_all_done(self, results):
        """All scripts finished."""
        self._run_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._update_status_bar()

    # ──────────────────────────────────────────────
    # Auto-run timer
    # ──────────────────────────────────────────────

    def _setup_auto_run_timer(self):
        """Check every 30 seconds if it's time to auto-run."""
        self._auto_timer = QTimer(self)
        self._auto_timer.setInterval(30_000)  # 30 seconds
        self._auto_timer.timeout.connect(self._check_auto_run)
        self._auto_timer.start()
        self._last_auto_run_date: str = ""

    def _check_auto_run(self):
        if not self._auto_run_check.isChecked():
            return
        if self._runner.is_running:
            return

        now = datetime.datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        # Don't run on weekends
        if now.strftime("%A") not in WEEKDAYS:
            return

        # Only run once per day
        if self._last_auto_run_date == today_str:
            return

        target = self._auto_run_time.time()
        current_time = QTime(now.hour, now.minute)

        if current_time >= target:
            self._last_auto_run_date = today_str
            self._log_feed.log("Auto-run triggered!", "info")
            self._run_today()

    def _on_auto_run_toggled(self, checked: bool):
        self._auto_run_time.setEnabled(checked)
        self._save_current_config()
        state = "enabled" if checked else "disabled"
        self._log_feed.log(f"Auto-run {state}", "info")

    def _on_auto_time_changed(self):
        self._save_current_config()

    # ──────────────────────────────────────────────
    # Notifications
    # ──────────────────────────────────────────────

    def _setup_tray_icon(self):
        """Set up system tray icon for notifications."""
        self._tray = QSystemTrayIcon(self)
        # Use a default icon — won't crash if unavailable
        self._tray.setToolTip("Script Scheduler")
        self._tray.show()

    def _send_notification(self, title: str, message: str):
        """Desktop notification on script failure."""
        if self._tray and self._tray.supportsMessages():
            self._tray.showMessage(
                title, message, QSystemTrayIcon.Warning, 5000
            )

    # ──────────────────────────────────────────────
    # Status bar
    # ──────────────────────────────────────────────

    def _update_status_bar(self):
        now = datetime.datetime.now()
        today = now.strftime("%A")
        scripts = get_today_scripts(self._config)
        total_all = sum(
            len(self._config["schedules"].get(d, []))
            for d in WEEKDAYS
        )
        auto = "ON" if self._auto_run_check.isChecked() else "OFF"
        auto_time = self._auto_run_time.time().toString("HH:mm")

        self._status_label.setText(
            f"  Today: {today}  ·  {len(scripts)} scripts queued today  "
            f"·  {total_all} total across week  ·  Auto-run: {auto} ({auto_time})  "
            f"·  {now.strftime('%H:%M')}"
        )

    # ──────────────────────────────────────────────
    # Utility
    # ──────────────────────────────────────────────

    def _open_logs_folder(self):
        """Open the logs directory in the system file manager."""
        import subprocess, sys, os
        path = str(LOG_DIR)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _open_execution_log(self):
        """Open the CSV execution log file."""
        import os
        path = str(EXECUTION_LOG_CSV)
        if os.path.isfile(path):
            os.startfile(path)
        else:
            self._log_feed.log("No execution log yet — run scripts first.", "warning")

    def closeEvent(self, event):
        """Save config on close."""
        self._save_current_config()
        if self._tray:
            self._tray.hide()
        event.accept()


def main():
    import traceback, logging

    # Global exception handler — prevents silent crashes
    log_path = LOG_DIR / "crash.log"
    def _exception_hook(exc_type, exc_value, exc_tb):
        msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        try:
            from config import ensure_dirs
            ensure_dirs()
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n{'=' * 60}\n")
                f.write(f"Crash at {datetime.datetime.now()}\n")
                f.write(msg)
        except Exception:
            pass
        logging.critical("Unhandled exception:\n%s", msg)
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = _exception_hook
    threading.excepthook = lambda args: _exception_hook(args.exc_type, args.exc_value, args.exc_traceback)

    app = QApplication(sys.argv)
    app.setApplicationName("Script Scheduler")
    app.setStyle("Fusion")  # Consistent cross-platform base
    app.setStyleSheet(DARK_STYLESHEET)

    window = MainWindow()
    window.show()

    # Update status bar every minute
    status_timer = QTimer()
    status_timer.timeout.connect(window._update_status_bar)
    status_timer.start(60_000)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
