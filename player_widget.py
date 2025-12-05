# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QComboBox, QSizePolicy
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from typing import Optional
from search import format_ms


class PlayerWidget(QWidget):
    """Encapsulates video playback UI and logic as a reusable QWidget."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._pending_position_ms: Optional[int] = None
        self._slider_is_dragging = False

        layout = QVBoxLayout(self)

        # Video display
        self.video_widget = QVideoWidget()
        # make video widget expand more: give it larger stretch and expanding policy
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_widget.setMinimumHeight(240)
        layout.addWidget(self.video_widget, 8)

        # Media player and audio
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        # Connect media signals
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

        # Controls row
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        self.btn_play = QPushButton("Play")
        self.btn_play.clicked.connect(self.player.play)
        controls_layout.addWidget(self.btn_play)
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self.player.pause)
        controls_layout.addWidget(self.btn_pause)
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.player.stop)
        controls_layout.addWidget(self.btn_stop)
        layout.addWidget(controls)

        # Playback time
        self.lbl_playback_time = QLabel("00:00/00:00")
        self.lbl_playback_time.setFixedHeight(20)
        self.lbl_playback_time.setSizePolicy(self.lbl_playback_time.sizePolicy().Policy.Preferred, self.lbl_playback_time.sizePolicy().Policy.Fixed)
        layout.addWidget(self.lbl_playback_time, 0)

        # Playback slider
        self.playback_slider = QSlider(Qt.Orientation.Horizontal)
        self.playback_slider.setRange(0, 1000)
        self.playback_slider.setEnabled(False)
        self.playback_slider.setFixedHeight(20)
        layout.addWidget(self.playback_slider, 0)

        # Rate selector
        self.rate_selector = QComboBox()
        for r in [0.5, 1.0, 1.25, 1.5, 2.0]:
            self.rate_selector.addItem(f"{r}x", r)
        self.rate_selector.setCurrentIndex(1 if self.rate_selector.count() > 1 else 0)
        self.rate_selector.currentIndexChanged.connect(self._on_rate_changed)
        # place rate selector and buffer label in a small row
        bottom_row = QWidget()
        bottom_layout = QHBoxLayout(bottom_row)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addWidget(self.rate_selector, 0)
        self.lbl_buffer = QLabel("")
        bottom_layout.addWidget(self.lbl_buffer, 1)
        bottom_row.setFixedHeight(28)
        layout.addWidget(bottom_row, 0)

        # Slider interactions
        self.playback_slider.sliderPressed.connect(self._on_slider_pressed)
        self.playback_slider.sliderReleased.connect(self._on_slider_released)
        self.playback_slider.sliderMoved.connect(self._on_slider_moved)

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

    # Internal handlers
    def _on_media_status_changed(self, status):
        try:
            # Seek when media is loaded
            if status == QMediaPlayer.MediaStatus.LoadedMedia and self._pending_position_ms is not None:
                try:
                    self.player.setPosition(int(self._pending_position_ms))
                except Exception:
                    pass
                self._pending_position_ms = None

            # enable slider when media available
            try:
                if status in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia, QMediaPlayer.MediaStatus.Buffered):
                    self.playback_slider.setEnabled(True)
                else:
                    if status == QMediaPlayer.MediaStatus.NoMedia:
                        self.playback_slider.setEnabled(False)
            except Exception:
                pass
        except Exception:
            pass

    def _on_player_position_changed(self, pos_ms: int):
        try:
            dur = self.player.duration() or 0
            self.lbl_playback_time.setText(f"{format_ms(int(pos_ms))} / {format_ms(int(dur))}")
            if dur > 0 and not self._slider_is_dragging:
                val = int((pos_ms / dur) * 1000)
                self.playback_slider.setValue(max(0, min(val, 1000)))
        except Exception:
            pass

    def _on_player_duration_changed(self, dur_ms: int):
        try:
            pos = self.player.position() or 0
            self.lbl_playback_time.setText(f"{format_ms(int(pos))} / {format_ms(int(dur_ms))}")
            try:
                if dur_ms > 0:
                    self.playback_slider.setEnabled(True)
                else:
                    self.playback_slider.setEnabled(False)
            except Exception:
                pass
        except Exception:
            pass

    def _on_buffer_status_changed(self, percent: int):
        try:
            self.lbl_buffer.setText(f"Buffer: {int(percent)}%")
        except Exception:
            pass

    def _on_rate_changed(self, idx: int):
        try:
            rate = float(self.rate_selector.currentData())
            self.set_rate(rate)
        except Exception:
            pass

    # Slider interactions
    def _on_slider_pressed(self):
        self._slider_is_dragging = True

    def _on_slider_released(self):
        try:
            self._slider_is_dragging = False
            val = self.playback_slider.value()
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
                self.lbl_playback_time.setText(f"{format_ms(pos)} / {format_ms(int(dur))}")
        except Exception:
            pass
