"""
Week Calendar widget — 5-column (Mon–Fri) schedule grid.
Each column lists scripts assigned to that day with enable/disable checkboxes.
"""

import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QMenu, QMessageBox,
)
from PySide6.QtCore import Qt, Signal

from config import WEEKDAYS


class DayColumn(QWidget):
    """Single day column in the week calendar."""

    script_removed = Signal(str, str)       # day, script_path
    script_toggled = Signal(str, str)       # day, script_path
    script_reorder = Signal(str, list)      # day, list of script_paths

    def __init__(self, day_name: str, is_today: bool = False, parent=None):
        super().__init__(parent)
        self.day_name = day_name
        self._build_ui(is_today)

    def _build_ui(self, is_today: bool):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(4)

        # Day header
        self._header = QLabel(self.day_name[:3].upper())
        self._header.setObjectName("dayHeaderToday" if is_today else "dayHeader")
        self._header.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._header)

        # Script list
        self._list = QListWidget()
        self._list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._show_context_menu)
        self._list.setToolTip(f"Scripts scheduled for {self.day_name}")
        layout.addWidget(self._list, 1)

        # Script count
        self._count_label = QLabel("0 scripts")
        self._count_label.setAlignment(Qt.AlignCenter)
        self._count_label.setStyleSheet("font-size: 10px; color: #555d6b;")
        layout.addWidget(self._count_label)

    def load_scripts(self, scripts: list[dict]):
        """Populate the list from config data."""
        self._list.clear()
        for s in scripts:
            self._add_item(s)
        self._update_count()

    def add_script(self, script: dict):
        """Add a single script entry."""
        # Check for duplicate
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.UserRole) == script["path"]:
                return
        self._add_item(script)
        self._update_count()

    def _add_item(self, script: dict):
        name = script.get("name", Path(script["path"]).stem)
        timeout = script.get("timeout", 300)
        item = QListWidgetItem()
        item.setText(name)
        item.setData(Qt.UserRole, script["path"])
        item.setData(Qt.UserRole + 1, timeout)  # store per-script timeout
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if script.get("enabled", True) else Qt.Unchecked)
        timeout_label = f"(no timeout)" if timeout <= 0 else f"(timeout: {timeout}s)"
        item.setToolTip(f"{script['path']} {timeout_label}")
        self._list.addItem(item)
        # Connect checkbox changes
        self._list.itemChanged.connect(self._on_item_changed)

    def _on_item_changed(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if path:
            self.script_toggled.emit(self.day_name, path)

    def _show_context_menu(self, pos):
        item = self._list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        remove_action = menu.addAction("Remove from " + self.day_name)
        action = menu.exec_(self._list.mapToGlobal(pos))
        if action == remove_action:
            path = item.data(Qt.UserRole)
            row = self._list.row(item)
            self._list.takeItem(row)
            self._update_count()
            self.script_removed.emit(self.day_name, path)

    def _update_count(self):
        n = self._list.count()
        self._count_label.setText(f"{n} script{'s' if n != 1 else ''}")

    def get_script_paths(self) -> list[str]:
        """Return list of script paths in order."""
        paths = []
        for i in range(self._list.count()):
            paths.append(self._list.item(i).data(Qt.UserRole))
        return paths


class WeekCalendar(QWidget):
    """
    Five-column Mon–Fri calendar grid.
    Each column shows scripts scheduled for that day.
    """

    config_changed = Signal()  # emitted when scripts are added/removed/toggled

    def __init__(self, parent=None):
        super().__init__(parent)
        today_name = datetime.datetime.now().strftime("%A")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Title
        title = QLabel("WEEKLY SCHEDULE")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        # Day columns
        cols_layout = QHBoxLayout()
        cols_layout.setSpacing(6)

        self._columns: dict[str, DayColumn] = {}
        for day in WEEKDAYS:
            col = DayColumn(day, is_today=(day == today_name))
            col.script_removed.connect(self._on_script_removed)
            col.script_toggled.connect(self._on_script_toggled)
            self._columns[day] = col
            cols_layout.addWidget(col, 1)

        layout.addLayout(cols_layout, 1)

    def load_from_config(self, config: dict):
        """Populate all columns from config data."""
        for day in WEEKDAYS:
            scripts = config.get("schedules", {}).get(day, [])
            self._columns[day].load_scripts(scripts)

    def add_script_to_day(self, day: str, script: dict):
        """Add a script to a specific day column."""
        if day in self._columns:
            self._columns[day].add_script(script)
            self.config_changed.emit()

    def _on_script_removed(self, day: str, path: str):
        self.config_changed.emit()

    def _on_script_toggled(self, day: str, path: str):
        self.config_changed.emit()

    def get_column(self, day: str) -> DayColumn:
        return self._columns.get(day)
