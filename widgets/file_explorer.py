"""
File Explorer widget — QTreeView backed by QFileSystemModel,
filtered to show only directories and .py files.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QComboBox,
    QPushButton, QLabel, QFileDialog, QHeaderView, QFileSystemModel
)
from PySide6.QtCore import Qt, Signal, QDir


class FileExplorer(QWidget):
    """
    Left panel file browser for selecting Python scripts.
    Emits `script_selected(path)` when the user picks a .py file.
    """

    script_selected = Signal(str)  # full path to a .py file

    def __init__(self, initial_dir: str = "", parent=None):
        super().__init__(parent)
        self._build_ui(initial_dir)

    def _build_ui(self, initial_dir: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Title
        title = QLabel("FILE EXPLORER")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        # Browse bar
        browse_row = QHBoxLayout()
        browse_row.setSpacing(4)
        self._path_combo = QComboBox()
        self._path_combo.setEditable(True)
        self._path_combo.setMinimumWidth(120)
        self._path_combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        browse_row.addWidget(self._path_combo, 1)

        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("smallButton")
        browse_btn.clicked.connect(self._browse_folder)
        browse_row.addWidget(browse_btn)
        layout.addLayout(browse_row)

        # Tree view
        self._model = QFileSystemModel()
        self._model.setNameFilters(["*.py"])
        self._model.setNameFilterDisables(False)
        self._model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)

        self._tree = QTreeView()
        self._tree.setModel(self._model)
        self._tree.setAnimated(True)
        self._tree.setIndentation(16)
        self._tree.setSortingEnabled(True)
        self._tree.setHeaderHidden(False)

        # Only show Name column
        for col in range(1, self._model.columnCount()):
            self._tree.hideColumn(col)

        header = self._tree.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        self._tree.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self._tree, 1)

        # Select button
        select_btn = QPushButton("Select Script")
        select_btn.setObjectName("addButton")
        select_btn.clicked.connect(self._on_select_clicked)
        layout.addWidget(select_btn)

        # Set initial directory
        start = initial_dir or str(Path.home())
        self._set_root(start)
        self._path_combo.currentTextChanged.connect(self._on_path_changed)

    def _set_root(self, path: str):
        """Set the file explorer root to a directory."""
        if Path(path).is_dir():
            root_index = self._model.setRootPath(path)
            self._tree.setRootIndex(root_index)
            if self._path_combo.findText(path) == -1:
                self._path_combo.addItem(path)
            self._path_combo.setCurrentText(path)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Scripts Directory", self._path_combo.currentText()
        )
        if folder:
            self._set_root(folder)

    def _on_path_changed(self, text: str):
        if Path(text).is_dir():
            self._set_root(text)

    def _on_double_click(self, index):
        path = self._model.filePath(index)
        if path.endswith(".py"):
            self.script_selected.emit(path)

    def _on_select_clicked(self):
        indexes = self._tree.selectedIndexes()
        if indexes:
            path = self._model.filePath(indexes[0])
            if path.endswith(".py"):
                self.script_selected.emit(path)

    def get_current_dir(self) -> str:
        return self._path_combo.currentText()
