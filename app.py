# -*- coding: utf-8 -*-
import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QHBoxLayout, QVBoxLayout,
    QLineEdit, QComboBox, QMessageBox, QSizePolicy, QSplitter,
    QRadioButton, QButtonGroup, QSlider, QProgressBar, QTextBrowser
)
from PySide6.QtGui import QPixmap, QImage, QIcon
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from player_widget import PlayerWidget
from main_ui import Ui_MainWindow
from PySide6 import QtWidgets

# qt-material will be applied at application start if available
try:
    import qt_material
    _HAS_QT_MATERIAL = True
except Exception:
    qt_material = None
    _HAS_QT_MATERIAL = False

# import search utilities
from search import AISearchEngine, format_ms
# import translations
from translations import TRANSLATIONS
# import SearchWorker from separate module
from search_worker import SearchWorker


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # translations for Chinese (zh) and English (en)
        self.translations = TRANSLATIONS

        # default language
        self.lang = 'zh'

        # AI search engine instance
        self.search_engine = AISearchEngine()
        self.search_worker = None

        # Load config
        self.config_path = os.path.join(os.path.expanduser('~'), '.videosearch_config.json')
        self.config = self._load_config()

        # wire up UI elements to existing logic
        # language combo
        self.lang_combo.addItem('中文 (简体)')
        self.lang_combo.addItem('English')
        self.lang_combo.setCurrentIndex(0 if self.lang == 'zh' else 1)
        self.lang_combo.currentIndexChanged.connect(self.change_language)

        # radio buttons
        self.rb_image.toggled.connect(self.update_search_mode_ui)
        self.rb_category.toggled.connect(self.update_search_mode_ui)
        self.rb_text.toggled.connect(self.update_search_mode_ui)

        # list double clicks
        self.list_videos.itemDoubleClicked.connect(self.on_video_double_clicked)
        self.list_results.itemDoubleClicked.connect(self.on_result_double_clicked)

        # buttons
        self.btn_select_videos.clicked.connect(self.select_videos)
        self.btn_select_images.clicked.connect(self.select_images)
        self.btn_search.clicked.connect(self.on_search)
        self.btn_stop_search.clicked.connect(self.on_stop_search)

        # slider
        self.slider.setRange(0, 100)
        init_score = int(self.config.get('score', 85))
        self.slider.setValue(init_score)
        self.slider.setTickInterval(5)
        self.slider.valueChanged.connect(self._on_slider_changed)

        # results list
        # category combo editable
        self.combo_category.setEditable(True)
        for c in self._t('categories'):
            self.combo_category.addItem(c)

        # player: if main_ui promoted the widget, playerContainer will already be a PlayerWidget
        try:
            if isinstance(self.playerContainer, PlayerWidget):
                self.player_widget = self.playerContainer
            else:
                try:
                    self.player_widget = PlayerWidget(self.playerContainer)
                    layout = self.playerContainer.layout() or QtWidgets.QVBoxLayout(self.playerContainer)
                    layout.addWidget(self.player_widget)
                except Exception as e:
                    self.player_widget = None
                    self.playerContainer_layout_fallback = QtWidgets.QVBoxLayout(self.playerContainer)
                    self.playerContainer_layout_fallback.addWidget(QtWidgets.QLabel(f"Player unavailable: {e}"))
                    print("PlayerWidget initialization failed:", e)
        except Exception:
            self.player_widget = None

        # set initial UI states
        self.rb_image.setChecked(True)
        self.update_search_mode_ui()
        # apply translations for initial language
        try:
            self.change_language(self.lang_combo.currentIndex())
        except Exception:
            pass

    def _load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {'score': 85}

    def _save_config(self):
        try:
            # ensure parent directory exists
            parent = os.path.dirname(self.config_path)
            if parent and not os.path.exists(parent):
                try:
                    os.makedirs(parent, exist_ok=True)
                except Exception:
                    pass

            # write config (will create file if not exists)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f)
        except Exception:
            pass

    def _t(self, key):
        # helper to get translated string or list
        val = self.translations[self.lang].get(key)
        return val

    def change_language(self, index):
        self.lang = 'zh' if index == 0 else 'en'
        # update window title
        self.setWindowTitle(self._t('title'))
        # update labels and buttons
        self.btn_select_videos.setText(self._t('select_videos'))
        self.btn_select_images.setText(self._t('select_images'))
        self.btn_search.setText(self._t('search'))
        # player buttons live in player_widget; update if available
        if getattr(self, 'player_widget', None) is not None:
            try:
                self.player_widget.playButton.setText(self._t('play'))
                self.player_widget.pauseButton.setText(self._t('pause'))
                self.player_widget.stopButton.setText(self._t('stop'))
            except Exception:
                pass
        self.btn_stop_search.setText(self._t('stop_search'))

        self.lbl_lang.setText(self._t('language') + ':')
        self.lbl_selected_videos.setText(self._t('selected_videos'))
        self.lbl_query_images.setText(self._t('query_images'))
        self.lbl_select_category.setText(self._t('select_category'))
        self.lbl_text_query.setText(self._t('text_query'))
        self.lbl_results.setText(self._t('results'))

        # update category list
        self.combo_category.clear()
        for c in self._t('categories'):
            self.combo_category.addItem(c)

        # update radio labels
        self.rb_image.setText(self._t('search_mode_image'))
        self.rb_category.setText(self._t('search_mode_category'))
        self.rb_text.setText(self._t('search_mode_text'))

        # update score label
        self.lbl_score.setText(f"{self._t('score_threshold')}: {self.slider.value()/100:.2f}")

    def update_search_mode_ui(self):
        # enable only controls relevant to the selected search mode
        image_mode = self.rb_image.isChecked()
        category_mode = self.rb_category.isChecked()
        text_mode = self.rb_text.isChecked()

        # image controls
        self.btn_select_images.setEnabled(image_mode)
        self.list_images.setEnabled(image_mode)

        # category controls
        self.combo_category.setEnabled(category_mode)
        self.lbl_select_category.setEnabled(category_mode)

        # text controls
        self.input_text.setEnabled(text_mode)
        self.lbl_text_query.setEnabled(text_mode)

    def select_videos(self):
        files, _ = QFileDialog.getOpenFileNames(self, self._t('file_dialog_videos'), os.path.expanduser("~"),
                                                "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)")
        if files:
            self.videos = files
            self.list_videos.clear()
            for f in files:
                self.list_videos.addItem(f)

    def select_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, self._t('file_dialog_images'), os.path.expanduser("~"),
                                                "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)")
        if files:
            self.images = files
            self.list_images.clear()
            for f in files:
                self.list_images.addItem(f)

    def on_search(self):
        """Start AI-powered search in a background thread."""
        if not self.videos:
            QMessageBox.warning(self, self._t('no_videos'), self._t('no_videos_detail'))
            return

        # Determine active search mode and validate inputs
        if self.rb_image.isChecked():
            mode = 'image'
            if not self.images:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_images'))
                return
        elif self.rb_category.isChecked():
            mode = 'category'
            query_category = self.combo_category.currentText().strip()
            if not query_category:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_category'))
                return
        elif self.rb_text.isChecked():
            mode = 'text'
            query_text = self.input_text.text().strip()
            if not query_text:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_text'))
                return
        else:
            # This should never happen as one radio button should always be selected
            assert False, "No search mode selected"

        self.list_results.clear()
        self.txt_log.clear()
        self.progress_bar.setValue(0)

        # Disable search button while processing
        self.btn_search.setEnabled(False)
        self.btn_stop_search.setEnabled(True)

        # Create and start the search worker
        self.search_worker = SearchWorker(
            search_engine=self.search_engine,
            video_paths=self.videos,
            mode=mode,
            query_images=self.images if mode == 'image' else None,
            query_text=self.input_text.text().strip() if mode == 'text' else None,
            query_category=self.combo_category.currentText().strip() if mode == 'category' else None,
            score_threshold=self.slider.value()/100.0,
            parent=self
        )

        # Connect signals to slots
        self.search_worker.match_found.connect(self._on_match_found)
        self.search_worker.finished_search.connect(self._on_search_finished)
        self.search_worker.error.connect(self._on_search_error)
        self.search_worker.progress.connect(self._on_progress)
        self.search_worker.message.connect(self._on_message)

        # Start the search
        self.search_worker.start()

    def on_stop_search(self):
        if self.search_worker:
            # request worker to stop; do not force-close generator from UI thread
            self.search_worker.stop()
            self.btn_stop_search.setEnabled(False)
            # log that stop was requested
            try:
                self.txt_log.append('<span style="color:gray;">{}</span>'.format(self._t('stop_search')))
            except Exception:
                self.txt_log.append('<span style="color:gray;">Stopping search...</span>')

    def _on_slider_changed(self, val: int):
        self.lbl_score.setText(f"{self._t('score_threshold')}: {val/100:.2f}")
        # save to config
        try:
            self.config['score'] = int(val)
            self._save_config()
        except Exception:
            pass

    def closeEvent(self, event):
        # ensure config saved on exit
        try:
            # persist current slider value
            self.config['score'] = int(self.slider.value())
            self._save_config()
        except Exception:
            pass

        # stop background search worker if running and wait briefly for it to finish
        try:
            if getattr(self, 'search_worker', None) is not None:
                try:
                    self.search_worker.stop()
                except Exception:
                    pass
                try:
                    # wait up to 3 seconds for thread to finish
                    if self.search_worker.isRunning():
                        self.search_worker.wait(3000)
                except Exception:
                    pass
        except Exception:
            pass

        # stop and release media player to avoid background native resources keeping process alive
        try:
            if getattr(self, 'player_widget', None) is not None:
                try:
                    self.player_widget.player.stop()
                    # clear source if supported
                    try:
                        self.player_widget.player.setSource(QUrl())
                    except Exception:
                        pass
                except Exception:
                    pass
        except Exception:
            pass

        super().closeEvent(event)

    def _on_match_found(self, video_path: str, timestamp_ms: int, score: float):
        """Handle a match found signal from the search worker."""
        # filter by slider threshold just in case
        threshold = self.slider.value() / 100.0
        if score < threshold:
            return

        item = QListWidgetItem()
        item.setText(f"{os.path.basename(video_path)} -- {self._t('match_at')} {format_ms(timestamp_ms)} (score: {score:.2f})")
        item.setData(Qt.ItemDataRole.UserRole, (video_path, timestamp_ms))

        # Get thumbnail at the specific timestamp of the match
        thumb = self._get_video_thumbnail(video_path, timestamp_ms)
        if thumb is not None:
            item.setIcon(QIcon(thumb))

        self.list_results.addItem(item)

    def _on_search_finished(self):
        """Handle search finished signal."""
        self.btn_search.setEnabled(True)
        self.btn_stop_search.setEnabled(False)
        self.search_worker = None
        # append translated finished message
        msg = self._t('search_finished')
        self.txt_log.append(f"{msg}")

    def _on_search_error(self, error_msg: str):
        """Handle search error signal: show message box and append red log."""
        try:
            title = self._t('search_error_title') or 'Error'
        except Exception:
            title = 'Error'
        QMessageBox.warning(self, title, error_msg)
        # append red colored message to log
        self.txt_log.append(f"<span style=\"color:red;\">{error_msg}</span>")

    def _on_progress(self, info):
        """Handle structured progress emitted by SearchWorker.
        info is ('video', current, total) or ('frame', current, total).
        We prefer to show frame-level progress when available, otherwise video-level.
        """
        try:
            if not isinstance(info, (list, tuple)):
                return
            kind = info[0]

            if kind == 'frame':
                # expected format: ('frame', video_idx, processed, total_samples, total_videos)
                if len(info) < 4:
                    return
                processed = int(info[2])
                total_samples = int(info[3])
                if total_samples <= 0:
                    self.progress_bar.setMaximum(100)
                    self.progress_bar.setValue(0)
                    return
                # avoid showing 100% during frame-level updates; reserve 100% for video completion
                pct = int((processed / float(total_samples)) * 100)
                pct = max(0, min(pct, 99))
                self.progress_bar.setMaximum(100)
                self.progress_bar.setValue(pct)
                return

            if kind == 'video':
                # expected format: ('video', completed_count, total_videos)
                if len(info) < 3:
                    return
                completed = int(info[1])
                total_videos = int(info[2])
                if total_videos <= 0:
                    self.progress_bar.setMaximum(100)
                    self.progress_bar.setValue(0)
                    return
                pct = int((completed / float(total_videos)) * 100)
                self.progress_bar.setMaximum(100)
                self.progress_bar.setValue(max(0, min(pct, 100)))
                return
        except Exception:
            pass

    def _on_message(self, msg):
        # msg can be structured (key, params) or plain string
        try:
            if isinstance(msg, (list, tuple)) and len(msg) == 2:
                key, params = msg
                tpl = self._t(key) or ''
                try:
                    text = tpl.format(**params)
                except Exception:
                    text = tpl
            else:
                text = str(msg)

            # append as plain text / black color
            self.txt_log.append(f"<span style=\"color:black;\">{text}</span>")
        except Exception:
            try:
                self.txt_log.append(str(msg))
            except Exception:
                pass

    def on_video_double_clicked(self, item: QListWidgetItem):
        # play video when double-clicking an item in selected videos list
        path = item.text()
        # item text is full path; ensure exists
        if os.path.exists(path):
            url = QUrl.fromLocalFile(path)
            self.player_widget.play_file(path)
            # self.player.setSource(url)
            # self.player.play()

    def on_result_double_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        video_path, position_ms = data
        url = QUrl.fromLocalFile(video_path)
        # set pending position so we seek when media is ready
        try:
            # self._pending_position_ms = int(position_ms)
            self.player_widget.play_at(video_path, position_ms)
        except Exception:
            self.player_widget.play_at(video_path, position_ms)
        # set source and start playback; position will be set when loaded via mediaStatus handler
        # self.player.setSource(url)
        # self.player.play()

    def _get_video_thumbnail(self, path, timestamp_ms: int = 0):
        """Capture a frame at the specified timestamp using opencv if available."""
        try:
            import cv2
            cap = cv2.VideoCapture(path)
            if timestamp_ms > 0:
                cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
            ok, frame = cap.read()
            cap.release()
            if not ok or frame is None:
                return None
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pix = QPixmap.fromImage(qimg).scaled(120, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            return pix
        except Exception:
            return None


def main():
    app = QApplication(sys.argv)
    # apply qt-material theme if available
    try:
        if _HAS_QT_MATERIAL and qt_material is not None:
            qt_material.apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True)
    except Exception:
        pass
    w = MainWindow()
    w.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()

