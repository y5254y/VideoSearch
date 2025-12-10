# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

class Badge(QLabel):
    """Small badge label for counts or status. Exposes set_accent to change background."""
    def __init__(self, text: str = "", parent=None, accent: str = "#0078D4"):
        super().__init__(text, parent)
        self.setProperty('badge', True)
        self.setAlignment(Qt.AlignCenter)
        self._accent = accent
        self._apply_style()

    def _apply_style(self):
        try:
            self.setStyleSheet(f"background:{self._accent}; color:white; padding:2px 6px; border-radius:8px;")
        except Exception:
            pass

    def set_accent(self, color: str):
        self._accent = color
        self._apply_style()
