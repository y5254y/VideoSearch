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
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(4)
        
        self.videoWidget = QVideoWidget(PlayerWidget)
        self.videoWidget.setObjectName(u"videoWidget")

        self.verticalLayout.addWidget(self.videoWidget)

        # 播放器控制区域 - 两排布局
        self.controlsContainer = QWidget(PlayerWidget)
        self.controlsContainer.setObjectName(u"controlsContainer")
        self.controlsContainer.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")
        self.controlsLayout = QVBoxLayout(self.controlsContainer)
        self.controlsLayout.setObjectName(u"controlsLayout")
        self.controlsLayout.setContentsMargins(8, 4, 8, 8)
        self.controlsLayout.setSpacing(4)
        
        # 上排：进度条
        self.progressRow = QWidget(self.controlsContainer)
        self.progressRow.setObjectName(u"progressRow")
        self.progressRowLayout = QHBoxLayout(self.progressRow)
        self.progressRowLayout.setObjectName(u"progressRowLayout")
        self.progressRowLayout.setContentsMargins(0, 0, 0, 0)
        self.progressRowLayout.setSpacing(8)
        
        self.playbackSlider = QSlider(self.progressRow)
        self.playbackSlider.setObjectName(u"playbackSlider")
        self.playbackSlider.setOrientation(Qt.Horizontal)
        self.playbackSlider.setMinimumHeight(20)
        self.progressRowLayout.addWidget(self.playbackSlider)
        self.progressRowLayout.setStretchFactor(self.playbackSlider, 1)
        
        self.controlsLayout.addWidget(self.progressRow)
        
        # 下排：控制按钮和信息
        self.buttonsRow = QWidget(self.controlsContainer)
        self.buttonsRow.setObjectName(u"buttonsRow")
        self.buttonsRowLayout = QHBoxLayout(self.buttonsRow)
        self.buttonsRowLayout.setObjectName(u"buttonsRowLayout")
        self.buttonsRowLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonsRowLayout.setSpacing(8)
        
        # 左侧：播放控制按钮
        self.leftButtonsLayout = QHBoxLayout()
        self.leftButtonsLayout.setSpacing(8)
        
        # 播放/暂停按钮
        self.playButton = QPushButton(self.buttonsRow)
        self.playButton.setObjectName(u"playButton")
        self.playButton.setFixedSize(28, 28)
        self.leftButtonsLayout.addWidget(self.playButton)
        
        # 暂停按钮 (可能会隐藏)
        self.pauseButton = QPushButton(self.buttonsRow)
        self.pauseButton.setObjectName(u"pauseButton")
        self.pauseButton.setFixedSize(28, 28)
        self.leftButtonsLayout.addWidget(self.pauseButton)
        
        # 停止按钮
        self.stopButton = QPushButton(self.buttonsRow)
        self.stopButton.setObjectName(u"stopButton")
        self.stopButton.setFixedSize(28, 28)
        self.leftButtonsLayout.addWidget(self.stopButton)
        
        self.buttonsRowLayout.addLayout(self.leftButtonsLayout)
        
        # 中间：播放时间
        self.playbackTimeLabel = QLabel(self.buttonsRow)
        self.playbackTimeLabel.setObjectName(u"playbackTimeLabel")
        self.playbackTimeLabel.setStyleSheet("color: white;")
        self.playbackTimeLabel.setAlignment(Qt.AlignCenter)
        self.buttonsRowLayout.addWidget(self.playbackTimeLabel)
        self.buttonsRowLayout.setStretchFactor(self.playbackTimeLabel, 1)
        
        # 右侧：速率选择和全屏按钮
        self.rightControlsLayout = QHBoxLayout()
        self.rightControlsLayout.setSpacing(8)
        
        # 播放速率选择器
        self.rateSelector = QComboBox(self.buttonsRow)
        self.rateSelector.setObjectName(u"rateSelector")
        self.rateSelector.setFixedSize(70, 24)  # 增加宽度以显示完整内容
        self.rateSelector.setStyleSheet("QComboBox { color: white; background-color: rgba(255, 255, 255, 0.1); border-radius: 4px; padding: 0 4px; }")
        self.rightControlsLayout.addWidget(self.rateSelector)
        
        # 缓冲标签
        self.bufferLabel = QLabel(self.buttonsRow)
        self.bufferLabel.setObjectName(u"bufferLabel")
        self.bufferLabel.setStyleSheet("color: white;")
        self.rightControlsLayout.addWidget(self.bufferLabel)
        
        # 全屏按钮
        self.fullscreenButton = QPushButton(self.buttonsRow)
        self.fullscreenButton.setObjectName(u"fullscreenButton")
        self.fullscreenButton.setFixedSize(28, 28)
        self.rightControlsLayout.addWidget(self.fullscreenButton)
        
        self.buttonsRowLayout.addLayout(self.rightControlsLayout)
        
        self.controlsLayout.addWidget(self.buttonsRow)
        
        self.verticalLayout.addWidget(self.controlsContainer)


        self.retranslateUi(PlayerWidget)

        QMetaObject.connectSlotsByName(PlayerWidget)
    # setupUi

    def retranslateUi(self, PlayerWidget):
        self.playButton.setText(QCoreApplication.translate("PlayerWidget", u"Play", None))
        self.pauseButton.setText(QCoreApplication.translate("PlayerWidget", u"Pause", None))
        self.stopButton.setText(QCoreApplication.translate("PlayerWidget", u"Stop", None))
        self.fullscreenButton.setText(QCoreApplication.translate("PlayerWidget", u"Fullscreen", None))
        self.playbackTimeLabel.setText(QCoreApplication.translate("PlayerWidget", u"00:00/00:00", None))
        self.bufferLabel.setText("")
        pass
    # retranslateUi

