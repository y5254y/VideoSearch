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
        RegisterWindow.resize(420, 600)
        RegisterWindow.setMinimumSize(420, 450)
        RegisterWindow.setMaximumSize(420, 600)
        self.centralwidget = QWidget(RegisterWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(30, 30, 30, 30)
        self.mainLayout.setSpacing(20)
        
        # 标题
        # self.title_label = QLabel(self.centralwidget)
        # self.title_label.setObjectName(u"title_label")
        # self.title_label.setText("视频搜索系统")
        # self.title_label.setAlignment(Qt.AlignCenter)
        # self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2196F3;")
        # self.title_label.setMinimumHeight(50)
        
        # self.mainLayout.addWidget(self.title_label)
        
        # 用户名输入框
        self.username_label = QLabel(self.centralwidget)
        self.username_label.setObjectName(u"username_label")
        self.username_label.setText("用户名")
        self.username_label.setStyleSheet("font-size: 14px;")
        self.username_label.setMinimumHeight(25)
        self.username_label.setFixedWidth(80)
        
        self.username_input = QLineEdit(self.centralwidget)
        self.username_input.setObjectName(u"username_input")
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setStyleSheet("padding: 6px; border: 1px solid #ddd; border-radius: 4px;")
        self.username_input.setMinimumHeight(25)
        self.username_input.setMinimumWidth(200)
        
        # 创建水平布局
        self.username_layout = QHBoxLayout()
        self.username_layout.addWidget(self.username_label)
        self.username_layout.addWidget(self.username_input)
        self.username_layout.setContentsMargins(0, 0, 0, 0)
        self.username_layout.setSpacing(10)
        
        self.mainLayout.addLayout(self.username_layout)
        
        # 密码输入框
        self.password_label = QLabel(self.centralwidget)
        self.password_label.setObjectName(u"password_label")
        self.password_label.setText("密码")
        self.password_label.setStyleSheet("font-size: 14px;")
        self.password_label.setMinimumHeight(25)
        self.password_label.setMinimumWidth(80)  # 密码输入框
        self.password_input = QLineEdit(self.centralwidget)
        self.password_input.setObjectName(u"password_input")
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px; background-color: white;")
        self.password_input.setMinimumHeight(30)
        
        # 密码显示/隐藏按钮
        self.password_toggle = QPushButton(self.centralwidget)
        self.password_toggle.setObjectName(u"password_toggle")
        self.password_toggle.setText("👁")
        self.password_toggle.setStyleSheet("background-color: transparent; border: none; color: #666; padding: 8px; margin: 0; border-radius: 0 4px 4px 0; position: relative; left: -1px;")
        self.password_toggle.setCursor(QCursor(Qt.PointingHandCursor))
        self.password_toggle.setMinimumHeight(30)
        self.password_toggle.setMaximumWidth(40)  # 增加宽度以提供更好的点击区域
        
        # 创建密码输入框和显示/隐藏按钮的水平布局
        self.password_field_layout = QHBoxLayout()
        self.password_field_layout.addWidget(self.password_input)
        self.password_field_layout.addWidget(self.password_toggle)
        self.password_field_layout.setContentsMargins(0, 0, 0, 0)
        self.password_field_layout.setSpacing(0)
        
        # 创建包含label和密码输入框的主水平布局
        self.password_layout = QHBoxLayout()
        self.password_layout.addWidget(self.password_label)
        self.password_layout.addLayout(self.password_field_layout)
        self.password_layout.setContentsMargins(0, 0, 0, 0)
        self.password_layout.setSpacing(10)
        
        self.mainLayout.addLayout(self.password_layout)
        
        # 确认密码输入框
        self.confirm_password_label = QLabel(self.centralwidget)
        self.confirm_password_label.setObjectName(u"confirm_password_label")
        self.confirm_password_label.setText("确认密码")
        self.confirm_password_label.setStyleSheet("font-size: 14px;")
        self.confirm_password_label.setMinimumHeight(25)
        self.confirm_password_label.setFixedWidth(80)
        
        self.confirm_password_input = QLineEdit(self.centralwidget)
        self.confirm_password_input.setObjectName(u"confirm_password_input")
        self.confirm_password_input.setPlaceholderText("请再次输入密码")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px; background-color: white;")
        self.confirm_password_input.setMinimumHeight(30)
        
        # 确认密码显示/隐藏按钮
        self.confirm_password_toggle = QPushButton(self.centralwidget)
        self.confirm_password_toggle.setObjectName(u"confirm_password_toggle")
        self.confirm_password_toggle.setText("👁")
        self.confirm_password_toggle.setStyleSheet("background-color: transparent; border: none; color: #666; padding: 8px; margin: 0; border-radius: 0 4px 4px 0; position: relative; left: -1px;")
        self.confirm_password_toggle.setCursor(QCursor(Qt.PointingHandCursor))
        self.confirm_password_toggle.setMinimumHeight(30)
        self.confirm_password_toggle.setMaximumWidth(40)
        
        # 创建确认密码输入框和显示/隐藏按钮的水平布局
        self.confirm_password_field_layout = QHBoxLayout()
        self.confirm_password_field_layout.addWidget(self.confirm_password_input)
        self.confirm_password_field_layout.addWidget(self.confirm_password_toggle)
        self.confirm_password_field_layout.setContentsMargins(0, 0, 0, 0)
        self.confirm_password_field_layout.setSpacing(0)
        
        # 创建包含label和确认密码输入框的主水平布局
        self.confirm_password_layout = QHBoxLayout()
        self.confirm_password_layout.addWidget(self.confirm_password_label)
        self.confirm_password_layout.addLayout(self.confirm_password_field_layout)
        self.confirm_password_layout.setContentsMargins(0, 0, 0, 0)
        self.confirm_password_layout.setSpacing(10)
        
        self.mainLayout.addLayout(self.confirm_password_layout)
        
        # 邮箱输入框（可选）
        self.email_label = QLabel(self.centralwidget)
        self.email_label.setObjectName(u"email_label")
        self.email_label.setText("邮箱（可选）")
        self.email_label.setStyleSheet("font-size: 14px;")
        self.email_label.setMinimumHeight(25)
        self.email_label.setFixedWidth(80)
        
        self.email_input = QLineEdit(self.centralwidget)
        self.email_input.setObjectName(u"email_input")
        self.email_input.setPlaceholderText("请输入邮箱地址")
        self.email_input.setStyleSheet("padding: 6px; border: 1px solid #ddd; border-radius: 4px;")
        self.email_input.setMinimumHeight(25)
        self.email_input.setMinimumWidth(200)
        
        # 创建水平布局
        self.email_layout = QHBoxLayout()
        self.email_layout.addWidget(self.email_label)
        self.email_layout.addWidget(self.email_input)
        self.email_layout.setContentsMargins(0, 0, 0, 0)
        self.email_layout.setSpacing(10)
        
        self.mainLayout.addLayout(self.email_layout)
        
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

