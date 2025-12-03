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
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

# import search utilities
from search import compute_query_descriptors, image_search_for_video, format_ms
# import translations
from translations import TRANSLATIONS


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
        # Placeholder search implementation
        if not self.videos:
            QMessageBox.warning(self, self._t('no_videos'), self._t('no_videos_detail'))
            return

        # Determine active search mode and validate inputs
        if self.rb_image.isChecked():
            if not self.images:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_images'))
                return
        elif self.rb_category.isChecked():
            query_category = self.combo_category.currentText().strip()
            if not query_category:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_category'))
                return
        elif self.rb_text.isChecked():
            query_text = self.input_text.text().strip()
            if not query_text:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_text'))
                return

        query_images = self.images
        query_category = self.combo_category.currentText().strip()
        query_text = self.input_text.text().strip()

        self.list_results.clear()

        # If image mode, perform simple ORB-based image search in videos
        if self.rb_image.isChecked():
            try:
                import cv2
            except Exception:
                QMessageBox.warning(self, "OpenCV missing", "OpenCV (cv2) is required for image search. Please install opencv-python.")
                return

            # compute descriptors for query images
            query_descs = compute_query_descriptors(self.images)
            if not query_descs:
                QMessageBox.warning(self, "No valid query images", self._t('need_images'))
                return

            # disable search button while processing
            self.btn_search.setEnabled(False)
            try:
                for video_path in self.videos:
                    matches = image_search_for_video(video_path, query_descs)
                    if matches:
                        # take earliest match
                        pos_ms = matches[0][0]
                        item = QListWidgetItem()
                        item.setText(f"{os.path.basename(video_path)} -- {self._t('match_at')} {format_ms(pos_ms)}")
                        item.setData(Qt.ItemDataRole.UserRole, (video_path, pos_ms))

                        thumb = self._get_video_thumbnail(video_path)
                        if thumb is not None:
                            item.setIcon(QIcon(thumb))
                        self.list_results.addItem(item)
                    else:
                        # optionally show no-match entry (commented out)
                        pass
            finally:
                self.btn_search.setEnabled(True)
            return

        # Mock results for other modes: for each video return a fake hit at 10 seconds
        for video_path in self.videos:
            item = QListWidgetItem()
            item.setText(f"{os.path.basename(video_path)} -- {self._t('match_at')} 00:00:10")
            item.setData(Qt.ItemDataRole.UserRole, (video_path, 10_000))

            # try to add a small thumbnail if opencv is available
            thumb = self._get_video_thumbnail(video_path)
            if thumb is not None:
                item.setIcon(QIcon(thumb))

            self.list_results.addItem(item)

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

    def _get_video_thumbnail(self, path):
        # Attempt to capture the first frame using opencv if available
        try:
            import cv2
            cap = cv2.VideoCapture(path)
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
