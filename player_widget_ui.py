# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSlider, QVBoxLayout,
    QWidget)

class Ui_PlayerWidget(object):
    def setupUi(self, PlayerWidget):
        if not PlayerWidget.objectName():
            PlayerWidget.setObjectName(u"PlayerWidget")
        PlayerWidget.resize(640, 480)
        self.verticalLayout = QVBoxLayout(PlayerWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.videoWidget = QVideoWidget(PlayerWidget)
        self.videoWidget.setObjectName(u"videoWidget")

        self.verticalLayout.addWidget(self.videoWidget)

        self.controlsContainer = QWidget(PlayerWidget)
        self.controlsContainer.setObjectName(u"controlsContainer")
        self.controlsContainer.setStyleSheet(u"background-color: rgba(255, 255, 255, 0.9);")
        self.controlsLayout = QVBoxLayout(self.controlsContainer)
        self.controlsLayout.setObjectName(u"controlsLayout")
        self.controlsLayout.setContentsMargins(0, 0, 0, 0)
        self.progressRow = QWidget(self.controlsContainer)
        self.progressRow.setObjectName(u"progressRow")
        self.progressRowLayout = QHBoxLayout(self.progressRow)
        self.progressRowLayout.setObjectName(u"progressRowLayout")
        self.progressRowLayout.setContentsMargins(0, 0, 0, 0)
        self.playbackSlider = QSlider(self.progressRow)
        self.playbackSlider.setObjectName(u"playbackSlider")
        self.playbackSlider.setOrientation(Qt.Orientation.Horizontal)

        self.progressRowLayout.addWidget(self.playbackSlider)


        self.controlsLayout.addWidget(self.progressRow)

        self.buttonsRow = QWidget(self.controlsContainer)
        self.buttonsRow.setObjectName(u"buttonsRow")
        self.buttonsRowLayout = QHBoxLayout(self.buttonsRow)
        self.buttonsRowLayout.setObjectName(u"buttonsRowLayout")
        self.buttonsRowLayout.setContentsMargins(0, 0, 0, 0)
        self.leftButtonsLayout = QHBoxLayout()
        self.leftButtonsLayout.setObjectName(u"leftButtonsLayout")
        self.playButton = QPushButton(self.buttonsRow)
        self.playButton.setObjectName(u"playButton")

        self.leftButtonsLayout.addWidget(self.playButton)

        self.stopButton = QPushButton(self.buttonsRow)
        self.stopButton.setObjectName(u"stopButton")

        self.leftButtonsLayout.addWidget(self.stopButton)


        self.buttonsRowLayout.addLayout(self.leftButtonsLayout)

        self.playbackTimeLabel = QLabel(self.buttonsRow)
        self.playbackTimeLabel.setObjectName(u"playbackTimeLabel")
        self.playbackTimeLabel.setAlignment(Qt.AlignCenter)

        self.buttonsRowLayout.addWidget(self.playbackTimeLabel)

        self.rightControlsLayout = QHBoxLayout()
        self.rightControlsLayout.setObjectName(u"rightControlsLayout")
        self.rateSelector = QComboBox(self.buttonsRow)
        self.rateSelector.setObjectName(u"rateSelector")

        self.rightControlsLayout.addWidget(self.rateSelector)

        self.bufferLabel = QLabel(self.buttonsRow)
        self.bufferLabel.setObjectName(u"bufferLabel")

        self.rightControlsLayout.addWidget(self.bufferLabel)

        self.fullscreenButton = QPushButton(self.buttonsRow)
        self.fullscreenButton.setObjectName(u"fullscreenButton")

        self.rightControlsLayout.addWidget(self.fullscreenButton)


        self.buttonsRowLayout.addLayout(self.rightControlsLayout)


        self.controlsLayout.addWidget(self.buttonsRow)


        self.verticalLayout.addWidget(self.controlsContainer)


        self.retranslateUi(PlayerWidget)

        QMetaObject.connectSlotsByName(PlayerWidget)
    # setupUi

    def retranslateUi(self, PlayerWidget):
        self.playButton.setText(QCoreApplication.translate("PlayerWidget", u"Play", None))
        self.stopButton.setText(QCoreApplication.translate("PlayerWidget", u"Stop", None))
        self.playbackTimeLabel.setText(QCoreApplication.translate("PlayerWidget", u"00:00/00:00", None))
        self.bufferLabel.setText("")
        self.fullscreenButton.setText(QCoreApplication.translate("PlayerWidget", u"Fullscreen", None))
        pass
    # retranslateUi