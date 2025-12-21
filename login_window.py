# -*- coding: utf-8 -*-
import sys
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Qt
from login_ui import Ui_LoginWindow
from user_service import UserService
from register_window import RegisterWindow

class LoginWindow(QDialog, Ui_LoginWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("视频搜索系统 - 登录")
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        # 初始化用户服务
        self.user_service = UserService()
        
        # 登录成功信号
        self.login_success = False
        self.user_info = None
        self.token = None
        
        # 连接信号槽
        self.login_button.clicked.connect(self.on_login_clicked)
        # 注册链接点击事件
        self.register_link.mousePressEvent = self.on_register_link_clicked
        
    def on_login_clicked(self):
        """处理登录按钮点击事件"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.status_label.setText("用户名和密码不能为空")
            return
        
        try:
            # 使用UserService进行登录
            success, data = self.user_service.login(username, password)
            
            if success:
                self.token = self.user_service.token
                self.user_info = self.user_service.user_info
                self.login_success = True
                self.close()
            else:
                self.status_label.setText(f"登录失败: {data}")
        except Exception as e:
            self.status_label.setText(f"登录失败: {str(e)}")
    
    def on_register_link_clicked(self, event):
        """处理注册链接点击事件"""
        # 打开注册窗口
        register_window = RegisterWindow(self)
        register_window.setWindowModality(Qt.ApplicationModal)  # 设置为模态窗口
        register_window.exec()
        
        # 如果注册成功，自动关闭登录窗口
        if register_window.register_success:
            self.login_success = False
            self.close()
    
    def get_user_info(self):
        """获取用户信息"""
        return self.user_info
    
    def get_token(self):
        """获取登录令牌"""
        return self.token
