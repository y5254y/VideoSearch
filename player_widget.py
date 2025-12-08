# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from typing import Optional
from search import format_ms
from player_widget_ui import Ui_PlayerWidget
from PySide6.QtMultimediaWidgets import QVideoWidget

class PlayerWidget(QWidget, Ui_PlayerWidget):
    """PlayerWidget built from .ui; wiring lives here."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._pending_position_ms: Optional[int] = None
        self._slider_is_dragging = False

        # configure UI defaults similar to previous implementation
        try:
            self.videoWidget.setMinimumHeight(240)
        except Exception:
            pass

        self.playbackSlider.setRange(0, 1000)
        self.playbackSlider.setEnabled(False)

        # populate rate selector
        for r in [0.5, 1.0, 1.25, 1.5, 2.0]:
            self.rateSelector.addItem(f"{r}x", r)
        try:
            self.rateSelector.setCurrentIndex(1)
        except Exception:
            pass

        # connect signals
        try:
            self.playButton.clicked.connect(self._on_play_clicked)
            self.pauseButton.clicked.connect(self._on_pause_clicked)
            self.stopButton.clicked.connect(self._on_stop_clicked)

            self.playbackSlider.sliderPressed.connect(self._on_slider_pressed)
            self.playbackSlider.sliderReleased.connect(self._on_slider_released)
            self.playbackSlider.sliderMoved.connect(self._on_slider_moved)

            self.rateSelector.currentIndexChanged.connect(self._on_rate_changed)
        except Exception:
            pass

        # Media
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        try:
            self.player.setVideoOutput(self.videoWidget)
        except Exception:
            pass

        # connect player signals
        try:
            self.player.positionChanged.connect(self._on_player_position_changed)
            self.player.durationChanged.connect(self._on_player_duration_changed)
            self.player.mediaStatusChanged.connect(self._on_media_status_changed)
            try:
                self.player.bufferStatusChanged.connect(self._on_buffer_status_changed)
            except Exception:
                pass
        except Exception:
            pass

    # Public API
    def play_file(self, path: str):
        url = QUrl.fromLocalFile(path)
        self.player.setSource(url)
        self.player.play()

    def play_at(self, path: str, position_ms: int):
        try:
            self._pending_position_ms = int(position_ms)
        except Exception:
            self._pending_position_ms = None
        url = QUrl.fromLocalFile(path)
        self.player.setSource(url)
        self.player.play()

    def set_rate(self, rate: float):
        try:
            self.player.setPlaybackRate(rate)
        except Exception:
            try:
                self.player.setRate(rate)
            except Exception:
                pass

    # UI handlers
    def _on_play_clicked(self):
        try:
            self.player.play()
        except Exception:
            pass

    def _on_pause_clicked(self):
        try:
            self.player.pause()
        except Exception:
            pass

    def _on_stop_clicked(self):
        try:
            self.player.stop()
        except Exception:
            pass

    # Internal handlers (reusing previous logic)
    def _on_media_status_changed(self, status):
        try:
            if status == QMediaPlayer.MediaStatus.LoadedMedia and self._pending_position_ms is not None:
                try:
                    self.player.setPosition(int(self._pending_position_ms))
                except Exception:
                    pass
                self._pending_position_ms = None

            try:
                if status in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia, QMediaPlayer.MediaStatus.Buffered):
                    self.playbackSlider.setEnabled(True)
                else:
                    if status == QMediaPlayer.MediaStatus.NoMedia:
                        self.playbackSlider.setEnabled(False)
            except Exception:
                pass
        except Exception:
            pass

    def _on_player_position_changed(self, pos_ms: int):
        try:
            dur = self.player.duration() or 0
            self.playbackTimeLabel.setText(f"{format_ms(int(pos_ms))} / {format_ms(int(dur))}")
            if dur > 0 and not self._slider_is_dragging:
                val = int((pos_ms / dur) * 1000)
                self.playbackSlider.setValue(max(0, min(val, 1000)))
        except Exception:
            pass

    def _on_player_duration_changed(self, dur_ms: int):
        try:
            pos = self.player.position() or 0
            self.playbackTimeLabel.setText(f"{format_ms(int(pos))} / {format_ms(int(dur_ms))}")
            try:
                if dur_ms > 0:
                    self.playbackSlider.setEnabled(True)
                else:
                    self.playbackSlider.setEnabled(False)
            except Exception:
                pass
        except Exception:
            pass

    def _on_buffer_status_changed(self, percent: int):
        try:
            self.bufferLabel.setText(f"Buffer: {int(percent)}%")
        except Exception:
            pass

    def _on_rate_changed(self, idx: int):
        try:
            rate = float(self.rateSelector.currentData())
            self.set_rate(rate)
        except Exception:
            pass

    # Slider interactions
    def _on_slider_pressed(self):
        self._slider_is_dragging = True

    def _on_slider_released(self):
        try:
            self._slider_is_dragging = False
            val = self.playbackSlider.value()
            dur = self.player.duration() or 0
            if dur > 0:
                pos = int((val / 1000.0) * dur)
                self.player.setPosition(pos)
        except Exception:
            pass

    def _on_slider_moved(self, value: int):
        try:
            dur = self.player.duration() or 0
            if dur > 0:
                pos = int((value / 1000.0) * dur)
                self.playbackTimeLabel.setText(f"{format_ms(pos)} / {format_ms(int(dur))}")
        except Exception:
            pass
