"""
Add-to-Day dialog — lets the user choose which day(s) to assign a script to.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QLineEdit, QSpinBox, QGroupBox,
)
from PySide6.QtCore import Qt

from config import WEEKDAYS


class AddScriptDialog(QDialog):
    """
    Modal dialog: pick display name, timeout, and target days for a script.
    """

    def __init__(self, script_path: str, default_timeout: int = 300, parent=None):
        super().__init__(parent)
        self.script_path = script_path
        self.setWindowTitle("Add Script to Schedule")
        self.setMinimumWidth(380)
        self._result_days: list[str] = []
        self._result_name: str = ""
        self._result_timeout: int = default_timeout
        self._build_ui(script_path, default_timeout)

    def _build_ui(self, script_path: str, default_timeout: int):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Script info
        info_label = QLabel(f"<b>Script:</b> {Path(script_path).name}")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        path_label = QLabel(f"<small>{script_path}</small>")
        path_label.setWordWrap(True)
        path_label.setStyleSheet("color: #8b949e;")
        layout.addWidget(path_label)

        # Display name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Display Name:"))
        self._name_input = QLineEdit(Path(script_path).stem)
        name_layout.addWidget(self._name_input, 1)
        layout.addLayout(name_layout)

        # Timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout (seconds):"))
        self._timeout_spin = QSpinBox()
        self._timeout_spin.setRange(10, 7200)
        self._timeout_spin.setValue(default_timeout)
        self._timeout_spin.setSingleStep(30)
        timeout_layout.addWidget(self._timeout_spin)

        self._no_timeout_check = QCheckBox("No timeout")
        self._no_timeout_check.setToolTip("Let script run indefinitely (for long-running reports)")
        self._no_timeout_check.toggled.connect(self._on_no_timeout_toggled)
        timeout_layout.addWidget(self._no_timeout_check)

        timeout_layout.addStretch()
        layout.addLayout(timeout_layout)

        # Day selection
        days_group = QGroupBox("Schedule On:")
        days_layout = QVBoxLayout(days_group)

        # Quick select buttons
        quick_row = QHBoxLayout()
        all_btn = QPushButton("All (Mon–Fri)")
        all_btn.setObjectName("smallButton")
        all_btn.clicked.connect(self._select_all)
        quick_row.addWidget(all_btn)

        mwf_btn = QPushButton("Mon/Wed/Fri")
        mwf_btn.setObjectName("smallButton")
        mwf_btn.clicked.connect(lambda: self._select_specific(["Monday", "Wednesday", "Friday"]))
        quick_row.addWidget(mwf_btn)

        tt_btn = QPushButton("Tue/Thu")
        tt_btn.setObjectName("smallButton")
        tt_btn.clicked.connect(lambda: self._select_specific(["Tuesday", "Thursday"]))
        quick_row.addWidget(tt_btn)

        quick_row.addStretch()
        days_layout.addLayout(quick_row)

        # Individual checkboxes
        self._day_checks: dict[str, QCheckBox] = {}
        checks_row = QHBoxLayout()
        for day in WEEKDAYS:
            cb = QCheckBox(day[:3])
            cb.setToolTip(day)
            self._day_checks[day] = cb
            checks_row.addWidget(cb)
        days_layout.addLayout(checks_row)

        layout.addWidget(days_group)

        # OK / Cancel
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        ok_btn = QPushButton("Add to Schedule")
        ok_btn.setObjectName("addButton")
        ok_btn.clicked.connect(self._accept)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

    def _select_all(self):
        for cb in self._day_checks.values():
            cb.setChecked(True)

    def _select_specific(self, days: list[str]):
        for day, cb in self._day_checks.items():
            cb.setChecked(day in days)

    def _on_no_timeout_toggled(self, checked: bool):
        self._timeout_spin.setEnabled(not checked)

    def _accept(self):
        self._result_days = [
            day for day, cb in self._day_checks.items() if cb.isChecked()
        ]
        self._result_name = self._name_input.text().strip() or Path(self.script_path).stem
        self._result_timeout = 0 if self._no_timeout_check.isChecked() else self._timeout_spin.value()
        if self._result_days:
            self.accept()

    @property
    def selected_days(self) -> list[str]:
        return self._result_days

    @property
    def display_name(self) -> str:
        return self._result_name

    @property
    def timeout(self) -> int:
        return self._result_timeout
