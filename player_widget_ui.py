# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'player.ui'
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

        self.controlsRow = QWidget(PlayerWidget)
        self.controlsRow.setObjectName(u"controlsRow")
        self.controlsLayout = QHBoxLayout(self.controlsRow)
        self.controlsLayout.setObjectName(u"controlsLayout")
        self.controlsLayout.setContentsMargins(0, 0, 0, 0)
        self.playButton = QPushButton(self.controlsRow)
        self.playButton.setObjectName(u"playButton")

        self.controlsLayout.addWidget(self.playButton)

        self.pauseButton = QPushButton(self.controlsRow)
        self.pauseButton.setObjectName(u"pauseButton")

        self.controlsLayout.addWidget(self.pauseButton)

        self.stopButton = QPushButton(self.controlsRow)
        self.stopButton.setObjectName(u"stopButton")

        self.controlsLayout.addWidget(self.stopButton)


        self.verticalLayout.addWidget(self.controlsRow)

        self.playbackTimeLabel = QLabel(PlayerWidget)
        self.playbackTimeLabel.setObjectName(u"playbackTimeLabel")

        self.verticalLayout.addWidget(self.playbackTimeLabel)

        self.playbackSlider = QSlider(PlayerWidget)
        self.playbackSlider.setObjectName(u"playbackSlider")
        self.playbackSlider.setOrientation(Qt.Horizontal)

        self.verticalLayout.addWidget(self.playbackSlider)

        self.bottomRow = QWidget(PlayerWidget)
        self.bottomRow.setObjectName(u"bottomRow")
        self.bottomLayout = QHBoxLayout(self.bottomRow)
        self.bottomLayout.setObjectName(u"bottomLayout")
        self.bottomLayout.setContentsMargins(0, 0, 0, 0)
        self.rateSelector = QComboBox(self.bottomRow)
        self.rateSelector.setObjectName(u"rateSelector")

        self.bottomLayout.addWidget(self.rateSelector)

        self.bufferLabel = QLabel(self.bottomRow)
        self.bufferLabel.setObjectName(u"bufferLabel")

        self.bottomLayout.addWidget(self.bufferLabel)


        self.verticalLayout.addWidget(self.bottomRow)


        self.retranslateUi(PlayerWidget)

        QMetaObject.connectSlotsByName(PlayerWidget)
    # setupUi

    def retranslateUi(self, PlayerWidget):
        self.playButton.setText(QCoreApplication.translate("PlayerWidget", u"Play", None))
        self.pauseButton.setText(QCoreApplication.translate("PlayerWidget", u"Pause", None))
        self.stopButton.setText(QCoreApplication.translate("PlayerWidget", u"Stop", None))
        self.playbackTimeLabel.setText(QCoreApplication.translate("PlayerWidget", u"00:00/00:00", None))
        self.bufferLabel.setText("")
        pass
    # retranslateUi

