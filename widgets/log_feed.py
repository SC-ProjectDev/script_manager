"""
Log Feed widget — scrolling, color-coded execution telemetry panel.
Mimics a terminal / ops-console output with timestamps.
"""

import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QTextCursor

from theme import LOG_COLORS


class LogFeed(QWidget):
    """
    Scrolling log panel with color-coded entries.
    Call `log(message, level)` to append entries.
    Levels: 'info', 'success', 'error', 'warning', 'running'
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Header row
        header_row = QHBoxLayout()
        title = QLabel("EXECUTION LOG")
        title.setObjectName("sectionTitle")
        header_row.addWidget(title)
        header_row.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("smallButton")
        clear_btn.clicked.connect(self.clear)
        header_row.addWidget(clear_btn)
        layout.addLayout(header_row)

        # Log text area
        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setLineWrapMode(QTextEdit.NoWrap)
        layout.addWidget(self._text, 1)

    @Slot(str, str)
    def log(self, message: str, level: str = "info"):
        """Append a log entry with timestamp and color."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        color = LOG_COLORS.get(level, LOG_COLORS["info"])

        # Escape HTML in message
        safe_msg = (
            message.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        html = (
            f'<span style="color: #555d6b;">[{timestamp}]</span> '
            f'<span style="color: {color};">{safe_msg}</span>'
        )

        self._text.append(html)
        # Auto-scroll to bottom
        cursor = self._text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self._text.setTextCursor(cursor)

    def clear(self):
        """Clear all log entries."""
        self._text.clear()

    def log_separator(self):
        """Add a visual separator line."""
        self.log("─" * 50, "info")
