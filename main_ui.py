# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QProgressBar, QPushButton, QRadioButton, QSizePolicy,
    QSlider, QSplitter, QTextBrowser, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 700)
        # 设置窗口最小大小
        MainWindow.setMinimumSize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        # 设置splitter的拉伸因子，让中间面板能够自适应伸缩
        self.splitter.setStretchFactor(0, 1)  # 左侧面板
        self.splitter.setStretchFactor(1, 2)  # 中间面板
        self.splitter.setStretchFactor(2, 2)  # 右侧面板
        # 设置左侧面板的最小宽度，确保能够完整显示单选按钮文本
        self.splitter.setSizes([280, 400, 400])
        self.leftPanel = QWidget(self.splitter)
        self.leftPanel.setObjectName(u"leftPanel")
        self.leftLayout = QVBoxLayout(self.leftPanel)
        self.leftLayout.setObjectName(u"leftLayout")
        self.leftLayout.setContentsMargins(0, 0, 0, 0)
        self.selectionLayout = QVBoxLayout()
        self.selectionLayout.setObjectName(u"selectionLayout")
        # 保持控件在顶部，不添加顶部拉伸
        self.modeLayout = QVBoxLayout()
        self.modeLayout.setObjectName(u"modeLayout")
        self.radioButtonsLayout = QVBoxLayout()
        self.radioButtonsLayout.setObjectName(u"radioButtonsLayout")
        self.radioButtonsLayout.setContentsMargins(4, 8, 8, 8)
        self.rb_image = QRadioButton(self.leftPanel)
        self.rb_image.setObjectName(u"rb_image")
        self.rb_image.setMinimumWidth(0)  # 允许按钮根据文本自动调整宽度

        self.radioButtonsLayout.addWidget(self.rb_image)

        self.rb_category = QRadioButton(self.leftPanel)
        self.rb_category.setObjectName(u"rb_category")
        self.rb_category.setMinimumWidth(0)  # 允许按钮根据文本自动调整宽度

        self.radioButtonsLayout.addWidget(self.rb_category)

        self.rb_text = QRadioButton(self.leftPanel)
        self.rb_text.setObjectName(u"rb_text")
        self.rb_text.setMinimumWidth(0)  # 允许按钮根据文本自动调整宽度

        self.radioButtonsLayout.addWidget(self.rb_text)


        self.modeLayout.addLayout(self.radioButtonsLayout)

        self.lbl_mode_hint = QLabel(self.leftPanel)
        self.lbl_mode_hint.setObjectName(u"lbl_mode_hint")
        self.lbl_mode_hint.setWordWrap(True)
        self.lbl_mode_hint.setStyleSheet(u"color: #666666; font-size: 12px;")

        self.modeLayout.addWidget(self.lbl_mode_hint)


        self.selectionLayout.addLayout(self.modeLayout)

        self.btn_select_videos = QPushButton(self.leftPanel)
        self.btn_select_videos.setObjectName(u"btn_select_videos")

        self.selectionLayout.addWidget(self.btn_select_videos)

        self.lbl_selected_videos = QLabel(self.leftPanel)
        self.lbl_selected_videos.setObjectName(u"lbl_selected_videos")

        self.selectionLayout.addWidget(self.lbl_selected_videos)

        self.list_videos = QListWidget(self.leftPanel)
        self.list_videos.setObjectName(u"list_videos")

        self.selectionLayout.addWidget(self.list_videos)

        self.btn_select_images = QPushButton(self.leftPanel)
        self.btn_select_images.setObjectName(u"btn_select_images")

        self.selectionLayout.addWidget(self.btn_select_images)

        self.lbl_query_images = QLabel(self.leftPanel)
        self.lbl_query_images.setObjectName(u"lbl_query_images")

        self.selectionLayout.addWidget(self.lbl_query_images)

        self.list_images = QListWidget(self.leftPanel)
        self.list_images.setObjectName(u"list_images")

        self.selectionLayout.addWidget(self.list_images)

        self.lbl_select_category = QLabel(self.leftPanel)
        self.lbl_select_category.setObjectName(u"lbl_select_category")

        self.selectionLayout.addWidget(self.lbl_select_category)

        self.combo_category = QComboBox(self.leftPanel)
        self.combo_category.setObjectName(u"combo_category")

        self.selectionLayout.addWidget(self.combo_category)

        self.lbl_text_query = QLabel(self.leftPanel)
        self.lbl_text_query.setObjectName(u"lbl_text_query")

        self.selectionLayout.addWidget(self.lbl_text_query)

        self.input_text = QLineEdit(self.leftPanel)
        self.input_text.setObjectName(u"input_text")

        self.selectionLayout.addWidget(self.input_text)

        self.sliderLayout = QHBoxLayout()
        self.sliderLayout.setObjectName(u"sliderLayout")
        self.lbl_score = QLabel(self.leftPanel)
        self.lbl_score.setObjectName(u"lbl_score")

        self.sliderLayout.addWidget(self.lbl_score)

        self.slider = QSlider(self.leftPanel)
        self.slider.setObjectName(u"slider")
        self.slider.setOrientation(Qt.Orientation.Horizontal)

        self.sliderLayout.addWidget(self.slider)


        self.selectionLayout.addLayout(self.sliderLayout)

        self.btnsLayout = QHBoxLayout()
        self.btnsLayout.setObjectName(u"btnsLayout")
        self.btn_search = QPushButton(self.leftPanel)
        self.btn_search.setObjectName(u"btn_search")

        self.btnsLayout.addWidget(self.btn_search)



        self.selectionLayout.addLayout(self.btnsLayout)
        # 在底部添加拉伸因子，将所有控件固定在顶部
        self.selectionLayout.addStretch(1)


        self.leftLayout.addLayout(self.selectionLayout)

        self.splitter.addWidget(self.leftPanel)
        self.centerPanel = QWidget(self.splitter)
        self.centerPanel.setObjectName(u"centerPanel")
        self.centerLayout = QVBoxLayout(self.centerPanel)
        self.centerLayout.setObjectName(u"centerLayout")
        self.centerLayout.setContentsMargins(0, 0, 0, 0)
        self.centerHeaderLayout = QHBoxLayout()
        self.centerHeaderLayout.setObjectName(u"centerHeaderLayout")
        self.lbl_results = QLabel(self.centerPanel)
        self.lbl_results.setObjectName(u"lbl_results")

        self.centerHeaderLayout.addWidget(self.lbl_results)


        self.centerLayout.addLayout(self.centerHeaderLayout)

        self.list_results = QListWidget(self.centerPanel)
        self.list_results.setObjectName(u"list_results")

        self.centerLayout.addWidget(self.list_results)

        self.splitter.addWidget(self.centerPanel)
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

        self.mainLayout.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.rb_image.setText(QCoreApplication.translate("MainWindow", u"Image", None))
        self.rb_category.setText(QCoreApplication.translate("MainWindow", u"Category", None))
        self.rb_text.setText(QCoreApplication.translate("MainWindow", u"Text", None))
        self.lbl_mode_hint.setText(QCoreApplication.translate("MainWindow", u"Select a search mode", None))
        self.btn_select_videos.setText(QCoreApplication.translate("MainWindow", u"Select Videos", None))
        self.lbl_selected_videos.setText(QCoreApplication.translate("MainWindow", u"Selected Videos", None))
        self.btn_select_images.setText(QCoreApplication.translate("MainWindow", u"Select Images", None))
        self.lbl_query_images.setText(QCoreApplication.translate("MainWindow", u"Query Images", None))
        self.lbl_select_category.setText(QCoreApplication.translate("MainWindow", u"Select Category", None))
        self.lbl_text_query.setText(QCoreApplication.translate("MainWindow", u"Text Query", None))
        self.lbl_score.setText(QCoreApplication.translate("MainWindow", u"Score Threshold: 0.25", None))
        self.btn_search.setText(QCoreApplication.translate("MainWindow", u"Search", None))
        self.lbl_results.setText(QCoreApplication.translate("MainWindow", u"Results", None))
        pass
    # retranslateUi



