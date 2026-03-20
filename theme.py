"""
Dark theme stylesheet for Script Scheduler GUI.
Inspired by terminal/ops-console aesthetic — dark backgrounds,
monospace accents, sharp accent colors for status.
"""

# ── Color palette ──
BG_PRIMARY = "#0e1117"       # Main background
BG_SECONDARY = "#161b22"     # Panel backgrounds
BG_TERTIARY = "#1c2333"      # Card / elevated surfaces
BG_INPUT = "#0d1117"         # Input fields
BORDER = "#2a3142"           # Subtle borders
BORDER_FOCUS = "#4a9eff"     # Focus ring
TEXT_PRIMARY = "#e6edf3"     # Main text
TEXT_SECONDARY = "#8b949e"   # Muted text
TEXT_MUTED = "#555d6b"       # Very muted
ACCENT = "#4a9eff"           # Primary accent (blue)
ACCENT_HOVER = "#6db3ff"     # Accent hover
SUCCESS = "#3fb950"          # Green
WARNING = "#d29922"          # Amber
ERROR = "#f85149"            # Red
RUNNING = "#a371f7"          # Purple for running state
HEADER_BG = "#1a2030"        # Column header bg
SELECTION = "#1a3a5c"        # Selected row

DARK_STYLESHEET = f"""
/* ═══════════════════════════════════════════════════════
   GLOBAL
   ═══════════════════════════════════════════════════════ */
QMainWindow, QWidget {{
    background-color: {BG_PRIMARY};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 13px;
}}

/* ═══════════════════════════════════════════════════════
   SPLITTERS & FRAMES
   ═══════════════════════════════════════════════════════ */
QSplitter::handle {{
    background-color: {BORDER};
    width: 1px;
    height: 1px;
}}
QFrame#panelFrame {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}

/* ═══════════════════════════════════════════════════════
   GROUP BOXES (panels)
   ═══════════════════════════════════════════════════════ */
QGroupBox {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding: 16px 10px 10px 10px;
    font-weight: 600;
    font-size: 12px;
    color: {TEXT_SECONDARY};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    color: {TEXT_SECONDARY};
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ═══════════════════════════════════════════════════════
   LABELS
   ═══════════════════════════════════════════════════════ */
QLabel {{
    color: {TEXT_PRIMARY};
    background: transparent;
}}
QLabel#sectionTitle {{
    font-size: 11px;
    font-weight: 700;
    color: {TEXT_SECONDARY};
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 4px 0;
}}
QLabel#dayHeader {{
    font-size: 12px;
    font-weight: 700;
    color: {ACCENT};
    padding: 6px 8px;
    background-color: {HEADER_BG};
    border-radius: 4px;
}}
QLabel#dayHeaderToday {{
    font-size: 12px;
    font-weight: 700;
    color: {BG_PRIMARY};
    padding: 6px 8px;
    background-color: {ACCENT};
    border-radius: 4px;
}}
QLabel#statusBar {{
    font-size: 12px;
    color: {TEXT_SECONDARY};
    padding: 6px 12px;
    background-color: {BG_SECONDARY};
    border-top: 1px solid {BORDER};
}}

/* ═══════════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════════ */
QPushButton {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 600;
    font-size: 12px;
}}
QPushButton:hover {{
    background-color: {BORDER};
    border-color: {TEXT_MUTED};
}}
QPushButton:pressed {{
    background-color: {BG_INPUT};
}}
QPushButton:disabled {{
    color: {TEXT_MUTED};
    background-color: {BG_SECONDARY};
    border-color: {BORDER};
}}
QPushButton#runButton {{
    background-color: {SUCCESS};
    color: #ffffff;
    border: none;
    font-size: 13px;
    padding: 8px 24px;
    font-weight: 700;
}}
QPushButton#runButton:hover {{
    background-color: #2ea043;
}}
QPushButton#runButton:disabled {{
    background-color: {TEXT_MUTED};
    color: {BG_PRIMARY};
}}
QPushButton#stopButton {{
    background-color: {ERROR};
    color: #ffffff;
    border: none;
    font-size: 13px;
    padding: 8px 24px;
    font-weight: 700;
}}
QPushButton#stopButton:hover {{
    background-color: #da3633;
}}
QPushButton#addButton {{
    background-color: {ACCENT};
    color: #ffffff;
    border: none;
    padding: 6px 14px;
    font-weight: 700;
}}
QPushButton#addButton:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton#removeButton {{
    background-color: transparent;
    color: {ERROR};
    border: 1px solid {ERROR};
    padding: 4px 10px;
    font-size: 11px;
}}
QPushButton#removeButton:hover {{
    background-color: {ERROR};
    color: #ffffff;
}}
QPushButton#smallButton {{
    padding: 4px 10px;
    font-size: 11px;
}}

/* ═══════════════════════════════════════════════════════
   TREE VIEW (file explorer)
   ═══════════════════════════════════════════════════════ */
QTreeView {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px;
    font-size: 12px;
    outline: none;
}}
QTreeView::item {{
    padding: 4px 6px;
    border-radius: 3px;
}}
QTreeView::item:hover {{
    background-color: {BG_TERTIARY};
}}
QTreeView::item:selected {{
    background-color: {SELECTION};
    color: {TEXT_PRIMARY};
}}
QTreeView::branch {{
    background: transparent;
}}
QHeaderView::section {{
    background-color: {BG_SECONDARY};
    color: {TEXT_SECONDARY};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 5px 8px;
    font-size: 11px;
    font-weight: 600;
}}

/* ═══════════════════════════════════════════════════════
   LIST WIDGET (scripts in day columns)
   ═══════════════════════════════════════════════════════ */
QListWidget {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px;
    font-size: 12px;
    outline: none;
}}
QListWidget::item {{
    padding: 5px 8px;
    border-radius: 4px;
    margin: 1px 0;
}}
QListWidget::item:hover {{
    background-color: {BG_TERTIARY};
}}
QListWidget::item:selected {{
    background-color: {SELECTION};
    color: {TEXT_PRIMARY};
}}

/* ═══════════════════════════════════════════════════════
   TEXT EDIT (log feed)
   ═══════════════════════════════════════════════════════ */
QTextEdit {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px;
    font-family: "Cascadia Code", "Fira Code", "JetBrains Mono", "Consolas", monospace;
    font-size: 12px;
    selection-background-color: {SELECTION};
}}

/* ═══════════════════════════════════════════════════════
   CHECKBOXES
   ═══════════════════════════════════════════════════════ */
QCheckBox {{
    color: {TEXT_PRIMARY};
    spacing: 8px;
    font-size: 12px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {BORDER};
    border-radius: 4px;
    background-color: {BG_INPUT};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}
QCheckBox::indicator:hover {{
    border-color: {TEXT_MUTED};
}}

/* ═══════════════════════════════════════════════════════
   COMBO BOX
   ═══════════════════════════════════════════════════════ */
QComboBox {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
}}
QComboBox:hover {{
    border-color: {TEXT_MUTED};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    selection-background-color: {SELECTION};
    outline: none;
}}

/* ═══════════════════════════════════════════════════════
   TIME EDIT
   ═══════════════════════════════════════════════════════ */
QTimeEdit {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
}}
QTimeEdit:disabled {{
    color: {TEXT_MUTED};
    background-color: {BG_SECONDARY};
}}

/* ═══════════════════════════════════════════════════════
   SPIN BOX
   ═══════════════════════════════════════════════════════ */
QSpinBox {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
}}

/* ═══════════════════════════════════════════════════════
   SCROLLBAR
   ═══════════════════════════════════════════════════════ */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    height: 0;
    background: transparent;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 4px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {TEXT_MUTED};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    width: 0;
    background: transparent;
}}

/* ═══════════════════════════════════════════════════════
   TOOLTIPS
   ═══════════════════════════════════════════════════════ */
QToolTip {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ═══════════════════════════════════════════════════════
   TAB WIDGET (settings)
   ═══════════════════════════════════════════════════════ */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    background-color: {BG_SECONDARY};
}}
QTabBar::tab {{
    background-color: {BG_TERTIARY};
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 6px 16px;
    margin-right: 2px;
    font-size: 12px;
}}
QTabBar::tab:selected {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    font-weight: 600;
}}
QTabBar::tab:hover {{
    color: {TEXT_PRIMARY};
}}

/* ═══════════════════════════════════════════════════════
   DIALOG
   ═══════════════════════════════════════════════════════ */
QDialog {{
    background-color: {BG_PRIMARY};
}}
QMessageBox {{
    background-color: {BG_PRIMARY};
}}
"""

# Colors for the log feed (used with QTextEdit HTML formatting)
LOG_COLORS = {
    "info": TEXT_SECONDARY,
    "success": SUCCESS,
    "error": ERROR,
    "warning": WARNING,
    "running": RUNNING,
}
