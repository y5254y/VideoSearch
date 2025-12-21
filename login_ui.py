# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox)

class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        if not LoginWindow.objectName():
            LoginWindow.setObjectName(u"LoginWindow")
        LoginWindow.resize(400, 500)
        LoginWindow.setMinimumSize(400, 400)
        LoginWindow.setMaximumSize(400, 500)
        self.centralwidget = QWidget(LoginWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        #self.mainLayout.setContentsMargins(30, 30, 30, 30)
        self.mainLayout.setSpacing(20)
        
        # 标题
        self.title_label = QLabel(self.centralwidget)
        self.title_label.setObjectName(u"title_label")
        self.title_label.setText("视频搜索系统")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2196F3;")
        self.title_label.setMinimumHeight(50)
        
        self.mainLayout.addWidget(self.title_label)
        
        # 用户名输入框
        self.username_label = QLabel(self.centralwidget)
        self.username_label.setObjectName(u"username_label")
        self.username_label.setText("用户名")
        #self.username_label.setStyleSheet("font-size: 14px; margin-bottom: 1px;")
        self.username_label.setMinimumHeight(25)
        
        self.mainLayout.addWidget(self.username_label)
        
        self.username_input = QLineEdit(self.centralwidget)
        self.username_input.setObjectName(u"username_input")
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;")
        self.username_input.setMinimumHeight(30)
        
        self.mainLayout.addWidget(self.username_input)
        
        # 密码输入框
        self.password_label = QLabel(self.centralwidget)
        self.password_label.setObjectName(u"password_label")
        self.password_label.setText("密码")
        self.password_label.setStyleSheet("font-size: 14px; margin-bottom: 1px;")
        self.password_label.setMinimumHeight(25)
        
        self.mainLayout.addWidget(self.password_label)
        
        self.password_input = QLineEdit(self.centralwidget)
        self.password_input.setObjectName(u"password_input")
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;")
        self.password_input.setMinimumHeight(30)
        
        self.mainLayout.addWidget(self.password_input)
        
        # 登录按钮
        self.login_button = QPushButton(self.centralwidget)
        self.login_button.setObjectName(u"login_button")
        self.login_button.setText("登录")
        self.login_button.setStyleSheet("padding: 10px; background-color: #2196F3; color: white; border: none; border-radius: 4px; font-size: 16px;")
        self.login_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.login_button.setMinimumHeight(40)
        
        self.mainLayout.addWidget(self.login_button)
        
        # 注册链接
        self.register_link = QLabel(self.centralwidget)
        self.register_link.setObjectName(u"register_link")
        self.register_link.setText("没有账号？点击注册")
        self.register_link.setAlignment(Qt.AlignCenter)
        self.register_link.setStyleSheet("font-size: 12px; color: #2196F3;")
        self.register_link.setCursor(Qt.PointingHandCursor)
        self.register_link.setMinimumHeight(25)
        
        self.mainLayout.addWidget(self.register_link)
        
        # 状态标签
        self.status_label = QLabel(self.centralwidget)
        self.status_label.setObjectName(u"status_label")
        self.status_label.setText("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; color: #f44336;")
        self.status_label.setMinimumHeight(25)
        
        self.mainLayout.addWidget(self.status_label)
        
        # QDialog不需要setCentralWidget，直接设置布局
        self.setLayout(self.mainLayout)
        
        QMetaObject.connectSlotsByName(LoginWindow)

