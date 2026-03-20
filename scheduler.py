"""
Script execution engine for Script Scheduler.
Runs scripts in parallel subprocesses with timeout, logging, and status reporting.
"""

import csv
import subprocess
import sys
import os
import datetime
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional

from config import LOG_DIR, ensure_dirs

EXECUTION_LOG_CSV = LOG_DIR / "execution_log.csv"
CSV_HEADERS = [
    "run_id", "script_name", "script_path", "scheduled_day",
    "start_time", "end_time", "duration_seconds", "status",
    "return_code", "error_message", "timed_out", "timeout_setting",
]


class ScriptResult:
    """Result of a single script execution."""

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.success: bool = False
        self.return_code: Optional[int] = None
        self.stdout: str = ""
        self.stderr: str = ""
        self.error_message: str = ""
        self.start_time: Optional[datetime.datetime] = None
        self.end_time: Optional[datetime.datetime] = None
        self.timed_out: bool = False
        self.timeout_setting: int = 0

    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def status_label(self) -> str:
        if self.timed_out:
            return "TIMEOUT"
        if self.success:
            return "OK"
        return "FAILED"


class ScriptRunner:
    """
    Executes multiple scripts in parallel with live status callbacks.
    """

    def __init__(
        self,
        on_log: Optional[Callable[[str, str], None]] = None,
        on_complete: Optional[Callable[[ScriptResult], None]] = None,
        on_all_done: Optional[Callable[[list[ScriptResult]], None]] = None,
    ):
        """
        Args:
            on_log: Callback(message, level). level = 'info'|'success'|'error'|'warning'|'running'
            on_complete: Callback(ScriptResult) fired when each script finishes.
            on_all_done: Callback(list[ScriptResult]) fired when all scripts are done.
        """
        self.on_log = on_log or (lambda msg, lvl: None)
        self.on_complete = on_complete or (lambda r: None)
        self.on_all_done = on_all_done or (lambda rs: None)
        self._stop_event = threading.Event()
        self._running = False
        self._executor: Optional[ThreadPoolExecutor] = None

    @property
    def is_running(self) -> bool:
        return self._running

    def stop(self):
        """Signal all running scripts to stop."""
        self._stop_event.set()
        self.on_log("Stop requested — waiting for running scripts to finish...", "warning")

    def run_scripts(self, scripts: list[dict]):
        """
        Run a list of script dicts in parallel (non-blocking — runs in a thread).
        Each dict: {"path": str, "name": str, "enabled": bool, "timeout": int}
        """
        if self._running:
            self.on_log("Already running — please wait.", "warning")
            return

        enabled = [s for s in scripts if s.get("enabled", True)]
        if not enabled:
            self.on_log("No enabled scripts to run today.", "info")
            return

        self._stop_event.clear()
        self._running = True

        thread = threading.Thread(target=self._run_all, args=(enabled,), daemon=True)
        thread.start()

    def _run_all(self, scripts: list[dict]):
        """Internal: execute all scripts in a thread pool."""
        now = datetime.datetime.now()
        self.on_log(
            f"{'═' * 50}", "info"
        )
        self.on_log(
            f"  Execution started — {now.strftime('%A %Y-%m-%d %H:%M:%S')}", "info"
        )
        self.on_log(
            f"  Scripts to run: {len(scripts)}", "info"
        )
        self.on_log(
            f"{'═' * 50}", "info"
        )

        results: list[ScriptResult] = []
        log_file = self._open_log_file(now)
        run_id = now.strftime("run_%Y%m%d_%H%M%S")

        try:
            with ThreadPoolExecutor(max_workers=min(len(scripts), 8)) as executor:
                self._executor = executor
                futures = {
                    executor.submit(self._run_single, s): s for s in scripts
                }
                for future in as_completed(futures):
                    if self._stop_event.is_set():
                        break
                    try:
                        result = future.result()
                    except Exception as exc:
                        script = futures[future]
                        result = ScriptResult(script["name"], script["path"])
                        result.start_time = datetime.datetime.now()
                        result.end_time = datetime.datetime.now()
                        result.error_message = f"Unexpected error: {exc}"
                    results.append(result)
                    self._report_result(result)
                    self._write_log(log_file, result)
                    self._write_csv_row(run_id, result)
                    self.on_complete(result)
        except Exception as e:
            self.on_log(f"Executor error: {e}", "error")
        finally:
            if log_file:
                log_file.close()
            self._running = False
            self._executor = None

        # Summary
        ok = sum(1 for r in results if r.success)
        fail = len(results) - ok
        self.on_log(f"{'═' * 50}", "info")
        self.on_log(
            f"  Done — {ok} succeeded, {fail} failed out of {len(results)} scripts",
            "success" if fail == 0 else "error",
        )
        self.on_log(f"{'═' * 50}", "info")

        self.on_all_done(results)

    def _run_single(self, script: dict) -> ScriptResult:
        """Run a single script in a subprocess."""
        result = ScriptResult(script["name"], script["path"])
        result.start_time = datetime.datetime.now()
        timeout = script.get("timeout", 300)
        result.timeout_setting = timeout

        timeout_label = f"timeout={timeout}s" if timeout > 0 else "no timeout"
        self.on_log(f"▶ Starting: {script['name']} ({timeout_label})", "running")

        if not os.path.isfile(script["path"]):
            result.end_time = datetime.datetime.now()
            result.error_message = f"File not found: {script['path']}"
            self.on_log(f"  ✗ {script['name']}: file not found", "error")
            return result

        try:
            # timeout <= 0 means no timeout
            effective_timeout = timeout if timeout > 0 else None
            proc = subprocess.run(
                [sys.executable, script["path"]],
                capture_output=True,
                text=True,
                timeout=effective_timeout,
                cwd=str(Path(script["path"]).parent),
            )
            result.return_code = proc.returncode
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            result.success = proc.returncode == 0
            if not result.success:
                result.error_message = proc.stderr[:500] if proc.stderr else f"Exit code {proc.returncode}"
        except subprocess.TimeoutExpired:
            result.timed_out = True
            result.error_message = f"Timed out after {timeout}s"
        except Exception as e:
            result.error_message = str(e)

        result.end_time = datetime.datetime.now()
        return result

    def _report_result(self, result: ScriptResult):
        """Log a single result to the GUI."""
        dur = f"{result.duration:.1f}s"
        if result.success:
            self.on_log(f"  ✓ {result.name} completed ({dur})", "success")
        elif result.timed_out:
            self.on_log(f"  ⏱ {result.name} TIMED OUT ({dur})", "error")
        else:
            self.on_log(f"  ✗ {result.name} FAILED ({dur})", "error")
            if result.error_message:
                # Truncate long errors for the GUI feed
                short = result.error_message[:200].replace("\n", " ")
                self.on_log(f"    └─ {short}", "error")

    def _open_log_file(self, now: datetime.datetime):
        """Open a log file for this execution run."""
        ensure_dirs()
        filename = now.strftime("run_%Y%m%d_%H%M%S.log")
        filepath = LOG_DIR / filename
        try:
            f = open(filepath, "w", encoding="utf-8")
            f.write(f"Script Scheduler — Run Log\n")
            f.write(f"Date: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'=' * 60}\n\n")
            self.on_log(f"  Log file: {filepath}", "info")
            return f
        except IOError:
            return None

    def _write_log(self, log_file, result: ScriptResult):
        """Write a result entry to the log file."""
        if not log_file:
            return
        try:
            log_file.write(f"Script: {result.name}\n")
            log_file.write(f"  Path: {result.path}\n")
            log_file.write(f"  Status: {result.status_label}\n")
            log_file.write(f"  Duration: {result.duration:.1f}s\n")
            if result.error_message:
                log_file.write(f"  Error: {result.error_message}\n")
            if result.stdout:
                log_file.write(f"  Stdout:\n{result.stdout[:1000]}\n")
            log_file.write(f"\n")
            log_file.flush()
        except IOError:
            pass

    def _write_csv_row(self, run_id: str, result: ScriptResult):
        """Append a row to the persistent CSV execution log."""
        ensure_dirs()
        file_exists = EXECUTION_LOG_CSV.exists()
        try:
            with open(EXECUTION_LOG_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(CSV_HEADERS)
                today = datetime.datetime.now().strftime("%A")
                writer.writerow([
                    run_id,
                    result.name,
                    result.path,
                    today,
                    result.start_time.strftime("%Y-%m-%d %H:%M:%S") if result.start_time else "",
                    result.end_time.strftime("%Y-%m-%d %H:%M:%S") if result.end_time else "",
                    f"{result.duration:.1f}",
                    result.status_label,
                    result.return_code if result.return_code is not None else "",
                    result.error_message,
                    result.timed_out,
                    result.timeout_setting if result.timeout_setting > 0 else "None",
                ])
        except IOError:
            pass
