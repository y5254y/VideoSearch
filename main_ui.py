# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QProgressBar, QRadioButton, QSizePolicy, QSlider,
    QSplitter, QTextBrowser, QVBoxLayout, QWidget, QPushButton)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 700)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.leftPanel = QWidget(self.splitter)
        self.leftPanel.setObjectName(u"leftPanel")
        self.leftLayout = QVBoxLayout(self.leftPanel)
        self.leftLayout.setObjectName(u"leftLayout")
        self.leftLayout.setContentsMargins(0, 0, 0, 0)
        self.langLayout = QHBoxLayout()
        self.langLayout.setObjectName(u"langLayout")
        self.lbl_lang = QLabel(self.leftPanel)
        self.lbl_lang.setObjectName(u"lbl_lang")

        self.langLayout.addWidget(self.lbl_lang)

        self.lang_combo = QComboBox(self.leftPanel)
        self.lang_combo.setObjectName(u"lang_combo")

        self.langLayout.addWidget(self.lang_combo)


        self.leftLayout.addLayout(self.langLayout)

        self.modeLayout = QHBoxLayout()
        self.modeLayout.setObjectName(u"modeLayout")
        self.rb_image = QRadioButton(self.leftPanel)
        self.rb_image.setObjectName(u"rb_image")

        self.modeLayout.addWidget(self.rb_image)

        self.rb_category = QRadioButton(self.leftPanel)
        self.rb_category.setObjectName(u"rb_category")

        self.modeLayout.addWidget(self.rb_category)

        self.rb_text = QRadioButton(self.leftPanel)
        self.rb_text.setObjectName(u"rb_text")

        self.modeLayout.addWidget(self.rb_text)


        self.leftLayout.addLayout(self.modeLayout)

        self.btn_select_videos = QPushButton(self.leftPanel)
        self.btn_select_videos.setObjectName(u"btn_select_videos")

        self.leftLayout.addWidget(self.btn_select_videos)

        self.lbl_selected_videos = QLabel(self.leftPanel)
        self.lbl_selected_videos.setObjectName(u"lbl_selected_videos")

        self.leftLayout.addWidget(self.lbl_selected_videos)

        self.list_videos = QListWidget(self.leftPanel)
        self.list_videos.setObjectName(u"list_videos")

        self.leftLayout.addWidget(self.list_videos)

        self.btn_select_images = QPushButton(self.leftPanel)
        self.btn_select_images.setObjectName(u"btn_select_images")

        self.leftLayout.addWidget(self.btn_select_images)

        self.lbl_query_images = QLabel(self.leftPanel)
        self.lbl_query_images.setObjectName(u"lbl_query_images")

        self.leftLayout.addWidget(self.lbl_query_images)

        self.list_images = QListWidget(self.leftPanel)
        self.list_images.setObjectName(u"list_images")

        self.leftLayout.addWidget(self.list_images)

        self.lbl_select_category = QLabel(self.leftPanel)
        self.lbl_select_category.setObjectName(u"lbl_select_category")

        self.leftLayout.addWidget(self.lbl_select_category)

        self.combo_category = QComboBox(self.leftPanel)
        self.combo_category.setObjectName(u"combo_category")

        self.leftLayout.addWidget(self.combo_category)

        self.lbl_text_query = QLabel(self.leftPanel)
        self.lbl_text_query.setObjectName(u"lbl_text_query")

        self.leftLayout.addWidget(self.lbl_text_query)

        self.input_text = QLineEdit(self.leftPanel)
        self.input_text.setObjectName(u"input_text")

        self.leftLayout.addWidget(self.input_text)

        self.sliderLayout = QHBoxLayout()
        self.sliderLayout.setObjectName(u"sliderLayout")
        self.lbl_score = QLabel(self.leftPanel)
        self.lbl_score.setObjectName(u"lbl_score")

        self.sliderLayout.addWidget(self.lbl_score)

        self.slider = QSlider(self.leftPanel)
        self.slider.setObjectName(u"slider")
        self.slider.setOrientation(Qt.Orientation.Horizontal)

        self.sliderLayout.addWidget(self.slider)


        self.leftLayout.addLayout(self.sliderLayout)

        self.btnsLayout = QHBoxLayout()
        self.btnsLayout.setObjectName(u"btnsLayout")
        self.btn_search = QPushButton(self.leftPanel)
        self.btn_search.setObjectName(u"btn_search")

        self.btnsLayout.addWidget(self.btn_search)

        self.btn_stop_search = QPushButton(self.leftPanel)
        self.btn_stop_search.setObjectName(u"btn_stop_search")

        self.btnsLayout.addWidget(self.btn_stop_search)


        self.leftLayout.addLayout(self.btnsLayout)

        self.lbl_results = QLabel(self.leftPanel)
        self.lbl_results.setObjectName(u"lbl_results")

        self.leftLayout.addWidget(self.lbl_results)

        self.list_results = QListWidget(self.leftPanel)
        self.list_results.setObjectName(u"list_results")

        self.leftLayout.addWidget(self.list_results)

        self.splitter.addWidget(self.leftPanel)
        self.rightPanel = QWidget(self.splitter)
        self.rightPanel.setObjectName(u"rightPanel")
        self.rightLayout = QVBoxLayout(self.rightPanel)
        self.rightLayout.setObjectName(u"rightLayout")
        self.rightLayout.setContentsMargins(0, 0, 0, 0)
        self.playerContainer = QWidget(self.rightPanel)
        self.playerContainer.setObjectName(u"playerContainer")

        self.rightLayout.addWidget(self.playerContainer)

        self.progress_bar = QProgressBar(self.rightPanel)
        self.progress_bar.setObjectName(u"progress_bar")

        self.rightLayout.addWidget(self.progress_bar)

        self.txt_log = QTextBrowser(self.rightPanel)
        self.txt_log.setObjectName(u"txt_log")

        self.rightLayout.addWidget(self.txt_log)

        self.splitter.addWidget(self.rightPanel)

        self.horizontalLayout.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.lbl_lang.setText(QCoreApplication.translate("MainWindow", u"Language:", None))
        self.rb_image.setText(QCoreApplication.translate("MainWindow", u"Image", None))
        self.rb_category.setText(QCoreApplication.translate("MainWindow", u"Category", None))
        self.rb_text.setText(QCoreApplication.translate("MainWindow", u"Text", None))
        self.btn_select_videos.setText(QCoreApplication.translate("MainWindow", u"Select Videos", None))
        self.lbl_selected_videos.setText(QCoreApplication.translate("MainWindow", u"Selected Videos", None))
        self.btn_select_images.setText(QCoreApplication.translate("MainWindow", u"Select Images", None))
        self.lbl_query_images.setText(QCoreApplication.translate("MainWindow", u"Query Images", None))
        self.lbl_select_category.setText(QCoreApplication.translate("MainWindow", u"Select Category", None))
        self.lbl_text_query.setText(QCoreApplication.translate("MainWindow", u"Text Query", None))
        self.lbl_score.setText(QCoreApplication.translate("MainWindow", u"Score Threshold: 0.25", None))
        self.btn_search.setText(QCoreApplication.translate("MainWindow", u"Search", None))
        self.btn_stop_search.setText(QCoreApplication.translate("MainWindow", u"Stop Search", None))
        self.lbl_results.setText(QCoreApplication.translate("MainWindow", u"Results", None))
        pass
    # retranslateUi

