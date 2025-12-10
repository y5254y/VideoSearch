# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal
from widgets.fluent_card import Card
from widgets.fluent_badge import Badge
import os

class ResultCard(Card):
    clicked = Signal(str, int)  # video_path, timestamp_ms
    def __init__(self, video_path: str, timestamp_ms: int, score: float, thumbnail: QPixmap = None, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.timestamp_ms = int(timestamp_ms)
        self.score = float(score)

        # Build layout: HBox with thumbnail and right-side VBox
        container = QWidget()
        h = QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        # Thumbnail
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(120, 90)
        self.thumb_label.setObjectName('thumbnail')
        if thumbnail is not None:
            pix = thumbnail.scaled(self.thumb_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.thumb_label.setPixmap(pix)
        h.addWidget(self.thumb_label)

        # Right side: title, details
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(6)

        title = QLabel(os.path.basename(video_path))
        title.setObjectName('result_title')
        rv.addWidget(title)

        # details row: time and score badge aligned right
        details = QWidget()
        dv = QHBoxLayout(details)
        dv.setContentsMargins(0, 0, 0, 0)
        dv.setSpacing(6)

        time_label = QLabel(self._format_ms(self.timestamp_ms))
        time_label.setObjectName('result_time')
        dv.addWidget(time_label)
        dv.addStretch()

        score_badge = Badge(f"{score:.2f}")
        score_badge.setFixedHeight(20)
        dv.addWidget(score_badge)

        rv.addWidget(details)

        h.addWidget(right, 1)

        # action buttons
        actions = QWidget()
        av = QHBoxLayout(actions)
        av.setContentsMargins(0, 0, 0, 0)
        av.setSpacing(6)
        btn_open = QPushButton('Open')
        btn_open.setObjectName('action_open')
        btn_open.setFixedHeight(24)
        btn_open.clicked.connect(self._on_open)
        btn_download = QPushButton('Download')
        btn_download.setObjectName('action_download')
        btn_download.setFixedHeight(24)
        btn_download.clicked.connect(self._on_download)
        av.addStretch()
        av.addWidget(btn_open)
        av.addWidget(btn_download)

        rv.addWidget(actions)

        # put container into Card
        self.add_widget(container)

    def _format_ms(self, ms: int) -> str:
        s = ms // 1000
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        return f"{h:02d}:{m:02d}:{sec:02d}"

    def set_thumbnail(self, pix: QPixmap):
        scaled = pix.scaled(self.thumb_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.thumb_label.setPixmap(scaled)

    def enterEvent(self, e):
        self.setProperty('hover', True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.setProperty('hover', False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        self.clicked.emit(self.video_path, self.timestamp_ms)
        super().mousePressEvent(e)

    def _on_open(self):
        # open the video in system file explorer or play
        if os.path.exists(self.video_path):
            try:
                os.startfile(self.video_path)
            except Exception:
                # Handle specific exceptions that might occur
                pass

    def _on_download(self):
        # placeholder: in real app, implement export logic
        if os.path.exists(self.video_path):
            try:
                # simply copy to desktop as demo
                import shutil
                dst = os.path.join(os.path.expanduser('~'), 'Desktop', os.path.basename(self.video_path))
                shutil.copy(self.video_path, dst)
            except Exception:
                # Handle specific exceptions that might occur
                pass
