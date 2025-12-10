# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt

class Card(QWidget):
    """Simple Card widget that sets a dynamic property for styling via QSS.

    Use by adding child widgets or setting layout.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty('card', True)
        # default layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(6)
        self.setLayout(self._layout)

    def add_widget(self, w: QWidget):
        self._layout.addWidget(w)

    def clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
