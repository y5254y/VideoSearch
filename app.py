# -*- coding: utf-8 -*-
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QHBoxLayout, QVBoxLayout,
    QLineEdit, QComboBox, QMessageBox, QSizePolicy, QSplitter,
    QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

# import search utilities
from search import compute_query_descriptors, image_search_for_video, format_ms, AISearchEngine
# import translations
from translations import TRANSLATIONS


class SearchWorker(QThread):
    """
    Worker thread for running AI-powered video search in the background.
    This prevents the UI from freezing during long search operations.
    """
    match_found = pyqtSignal(str, int, float)  # video_path, timestamp_ms, score
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, search_engine: AISearchEngine, video_paths: list,
                 query_data, mode: str, parent=None):
        super().__init__(parent)
        self.search_engine = search_engine
        self.video_paths = video_paths
        self.query_data = query_data
        self.mode = mode

    def run(self):
        try:
            for video_path, timestamp_ms, score in self.search_engine.search(
                self.video_paths, self.query_data, self.mode
            ):
                self.match_found.emit(video_path, timestamp_ms, score)
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            self.finished_signal.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # translations for Chinese (zh) and English (en)
        self.translations = TRANSLATIONS

        # default language
        self.lang = 'zh'

        self.setWindowTitle(self._t('title'))
        self.resize(1000, 700)

        self.videos = []  # list of video file paths
        self.images = []  # list of image file paths

        # Initialize AI search engine
        self.search_engine = AISearchEngine()
        self.search_worker = None

        # Main layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Left: controls and results
        left = QWidget()
        left_layout = QVBoxLayout(left)

        # Language selector
        lang_layout = QHBoxLayout()
        lbl_lang = QLabel(self._t('language') + ':')
        self.lang_combo = QComboBox()
        # order: zh, en
        self.lang_combo.addItem('中文 (简体)')
        self.lang_combo.addItem('English')
        self.lang_combo.setCurrentIndex(0 if self.lang == 'zh' else 1)
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(lbl_lang)
        lang_layout.addWidget(self.lang_combo)
        left_layout.addLayout(lang_layout)
        self.lbl_lang = lbl_lang

        # Search mode (only one of image/category/text allowed)
        mode_layout = QHBoxLayout()
        self.rb_image = QRadioButton(self._t('search_mode_image'))
        self.rb_category = QRadioButton(self._t('search_mode_category'))
        self.rb_text = QRadioButton(self._t('search_mode_text'))
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.rb_image)
        self.mode_group.addButton(self.rb_category)
        self.mode_group.addButton(self.rb_text)
        self.rb_image.toggled.connect(self.update_search_mode_ui)
        mode_layout.addWidget(self.rb_image)
        mode_layout.addWidget(self.rb_category)
        mode_layout.addWidget(self.rb_text)
        left_layout.addLayout(mode_layout)


        # Video selection
        self.btn_select_videos = QPushButton(self._t('select_videos'))
        self.btn_select_videos.clicked.connect(self.select_videos)
        left_layout.addWidget(self.btn_select_videos)

        self.list_videos = QListWidget()
        left_layout.addWidget(QLabel(self._t('selected_videos')))
        # keep reference to the label so it can be updated on language change
        self.lbl_selected_videos = left_layout.itemAt(left_layout.count()-1).widget()
        left_layout.addWidget(self.list_videos)

        # Image selection
        self.btn_select_images = QPushButton(self._t('select_images'))
        self.btn_select_images.clicked.connect(self.select_images)
        left_layout.addWidget(self.btn_select_images)

        self.list_images = QListWidget()
        left_layout.addWidget(QLabel(self._t('query_images')))
        self.lbl_query_images = left_layout.itemAt(left_layout.count()-1).widget()
        left_layout.addWidget(self.list_images)

        # Category and text inputs
        left_layout.addWidget(QLabel(self._t('select_category')))
        self.lbl_select_category = left_layout.itemAt(left_layout.count()-1).widget()
        self.combo_category = QComboBox()
        self.combo_category.setEditable(True)
        # example categories (will be populated by change_language)
        for c in self._t('categories'):
            self.combo_category.addItem(c)
        left_layout.addWidget(self.combo_category)

        left_layout.addWidget(QLabel(self._t('text_query')))
        self.lbl_text_query = left_layout.itemAt(left_layout.count()-1).widget()
        self.input_text = QLineEdit()
        left_layout.addWidget(self.input_text)

        # Search button
        self.btn_search = QPushButton(self._t('search'))
        self.btn_search.clicked.connect(self.on_search)
        left_layout.addWidget(self.btn_search)

        # Results
        left_layout.addWidget(QLabel(self._t('results')))
        self.lbl_results = left_layout.itemAt(left_layout.count()-1).widget()
        self.list_results = QListWidget()
        self.list_results.itemDoubleClicked.connect(self.on_result_double_clicked)
        left_layout.addWidget(self.list_results)

        # Right: video player
        right = QWidget()
        right_layout = QVBoxLayout(right)

        self.video_widget = QVideoWidget()
        right_layout.addWidget(self.video_widget)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        # Playback controls
        controls = QWidget()
        c_layout = QHBoxLayout(controls)
        self.btn_play = QPushButton(self._t('play'))
        self.btn_play.clicked.connect(self.player.play)
        c_layout.addWidget(self.btn_play)
        self.btn_pause = QPushButton(self._t('pause'))
        self.btn_pause.clicked.connect(self.player.pause)
        c_layout.addWidget(self.btn_pause)
        self.btn_stop = QPushButton(self._t('stop'))
        self.btn_stop.clicked.connect(self.player.stop)
        c_layout.addWidget(self.btn_stop)
        right_layout.addWidget(controls)

        # Put left and right in splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)
        # default search mode: image
        self.rb_image.setChecked(True)
        # apply initial UI state for search modes
        self.update_search_mode_ui()

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
        self.btn_play.setText(self._t('play'))
        self.btn_pause.setText(self._t('pause'))
        self.btn_stop.setText(self._t('stop'))

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
        # Validate inputs
        if not self.videos:
            QMessageBox.warning(self, self._t('no_videos'), self._t('no_videos_detail'))
            return

        # Determine active search mode and validate inputs
        mode = None
        query_data = None

        if self.rb_image.isChecked():
            if not self.images:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_images'))
                return
            mode = 'image'
            query_data = self.images
        elif self.rb_category.isChecked():
            query_category = self.combo_category.currentText().strip()
            if not query_category:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_category'))
                return
            mode = 'category'
            query_data = query_category
        elif self.rb_text.isChecked():
            query_text = self.input_text.text().strip()
            if not query_text:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_text'))
                return
            mode = 'text'
            query_data = query_text

        # Clear previous results
        self.list_results.clear()

        # Disable search button while processing
        self.btn_search.setEnabled(False)

        # Create and start the search worker thread
        self.search_worker = SearchWorker(
            self.search_engine,
            self.videos,
            query_data,
            mode,
            parent=self
        )
        self.search_worker.match_found.connect(self.on_match_found)
        self.search_worker.finished_signal.connect(self.on_search_finished)
        self.search_worker.error_signal.connect(self.on_search_error)
        self.search_worker.start()

    def on_match_found(self, video_path: str, timestamp_ms: int, score: float):
        """Slot to handle match results from the search worker."""
        item = QListWidgetItem()
        item.setText(f"{os.path.basename(video_path)} -- {self._t('match_at')} {format_ms(timestamp_ms)} (score: {score:.2f})")
        item.setData(Qt.ItemDataRole.UserRole, (video_path, timestamp_ms))

        # Generate thumbnail
        thumb = self._get_video_thumbnail(video_path, timestamp_ms)
        if thumb is not None:
            item.setIcon(QIcon(thumb))

        self.list_results.addItem(item)

    def on_search_finished(self):
        """Slot to handle search completion."""
        self.btn_search.setEnabled(True)
        self.search_worker = None

    def on_search_error(self, error_message: str):
        """Slot to handle search errors."""
        self.btn_search.setEnabled(True)
        self.search_worker = None
        QMessageBox.warning(self, "Search Error", error_message)

    def on_result_double_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        video_path, position_ms = data
        url = QUrl.fromLocalFile(video_path)
        self.player.setSource(url)
        # set position after media is loaded; simple approach: setPosition with slight delay
        self.player.play()
        self.player.setPosition(position_ms)

    def _get_video_thumbnail(self, path, timestamp_ms: int = 0):
        # Attempt to capture a frame at the specified timestamp using opencv if available
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
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
