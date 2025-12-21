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

class Ui_RegisterWindow(object):
    def setupUi(self, RegisterWindow):
        if not RegisterWindow.objectName():
            RegisterWindow.setObjectName(u"RegisterWindow")
        RegisterWindow.resize(420, 700)
        RegisterWindow.setMinimumSize(420, 500)
        RegisterWindow.setMaximumSize(420, 700)
        self.centralwidget = QWidget(RegisterWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(30, 30, 30, 30)
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
        self.username_label.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
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
        self.password_label.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
        self.password_label.setMinimumHeight(25)
        
        self.mainLayout.addWidget(self.password_label)
        
        self.password_input = QLineEdit(self.centralwidget)
        self.password_input.setObjectName(u"password_input")
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;")
        self.password_input.setMinimumHeight(30)
        
        self.mainLayout.addWidget(self.password_input)
        
        # 确认密码输入框
        self.confirm_password_label = QLabel(self.centralwidget)
        self.confirm_password_label.setObjectName(u"confirm_password_label")
        self.confirm_password_label.setText("确认密码")
        self.confirm_password_label.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
        self.confirm_password_label.setMinimumHeight(25)
        
        self.mainLayout.addWidget(self.confirm_password_label)
        
        self.confirm_password_input = QLineEdit(self.centralwidget)
        self.confirm_password_input.setObjectName(u"confirm_password_input")
        self.confirm_password_input.setPlaceholderText("请再次输入密码")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;")
        self.confirm_password_input.setMinimumHeight(30)
        
        self.mainLayout.addWidget(self.confirm_password_input)
        
        # 邮箱输入框（可选）
        self.email_label = QLabel(self.centralwidget)
        self.email_label.setObjectName(u"email_label")
        self.email_label.setText("邮箱（可选）")
        self.email_label.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
        self.email_label.setMinimumHeight(25)
        
        self.mainLayout.addWidget(self.email_label)
        
        self.email_input = QLineEdit(self.centralwidget)
        self.email_input.setObjectName(u"email_input")
        self.email_input.setPlaceholderText("请输入邮箱地址")
        self.email_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;")
        self.email_input.setMinimumHeight(30)
        
        self.mainLayout.addWidget(self.email_input)
        
        # 注册按钮
        self.register_button = QPushButton(self.centralwidget)
        self.register_button.setObjectName(u"register_button")
        self.register_button.setText("注册")
        self.register_button.setStyleSheet("padding: 10px; background-color: #2196F3; color: white; border: none; border-radius: 4px; font-size: 16px;")
        self.register_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.register_button.setMinimumHeight(40)
        
        self.mainLayout.addWidget(self.register_button)
        
        # 返回登录按钮
        self.login_button = QPushButton(self.centralwidget)
        self.login_button.setObjectName(u"login_button")
        self.login_button.setText("返回登录")
        self.login_button.setStyleSheet("padding: 10px; background-color: #e0e0e0; color: #333; border: none; border-radius: 4px; font-size: 16px;")
        self.login_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.login_button.setMinimumHeight(40)
        
        self.mainLayout.addWidget(self.login_button)
        
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
        
        QMetaObject.connectSlotsByName(RegisterWindow)

