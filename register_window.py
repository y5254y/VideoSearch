# -*- coding: utf-8 -*-
import sys
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Qt
from register_ui import Ui_RegisterWindow
from user_service import UserService

class RegisterWindow(QDialog, Ui_RegisterWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("视频搜索系统 - 注册")
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        
        # 初始化用户服务
        self.user_service = UserService()
        
        # 注册成功信号
        self.register_success = False
        
        # 连接信号槽
        self.register_button.clicked.connect(self.on_register_clicked)
        self.login_button.clicked.connect(self.on_login_clicked)
    
    def on_register_clicked(self):
        """处理注册按钮点击事件"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        email = self.email_input.text().strip()
        
        # 验证输入
        if not username:
            self.status_label.setText("用户名不能为空")
            return
        
        if not password:
            self.status_label.setText("密码不能为空")
            return
        
        if password != confirm_password:
            self.status_label.setText("两次输入的密码不一致")
            return
        
        if len(password) < 6:
            self.status_label.setText("密码长度不能少于6位")
            return
        
        try:
            # 调用注册API
            success, message = self.user_service.register(username, password, email)
            
            if success:
                QMessageBox.information(self, "注册成功", message)
                self.register_success = True
                self.close()
            else:
                self.status_label.setText(message)
        except Exception as e:
            self.status_label.setText(f"注册失败: {str(e)}")
    
    def on_login_clicked(self):
        """处理返回登录按钮点击事件"""
        self.register_success = False
        self.close()
