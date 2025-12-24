# -*- coding: utf-8 -*-
import sys
import os
import json
from PySide6.QtWidgets import QDialog, QMessageBox, QLineEdit
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
        
        # 密码显示状态
        self.password_visible = False
        
        # 配置文件路径
        self.config_path = os.path.join(os.path.expanduser('~'), '.videosearch_config.json')
        
        # 连接信号槽
        self.login_button.clicked.connect(self.on_login_clicked)
        # 密码显示/隐藏按钮点击事件
        self.password_toggle.clicked.connect(self.toggle_password_visibility)
        # 注册链接点击事件
        self.register_link.mousePressEvent = self.on_register_link_clicked
        
        # 加载并填充保存的登录信息
        self._load_saved_login_info()
        
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
                
                # 保存登录信息到配置文件
                self._save_login_info(username, password)
                
                self.accept()  # 使用accept()而不是close()，这样exec()会返回QDialog.Accepted
            else:
                self.status_label.setText(f"登录失败: {data}")
        except Exception as e:
            self.status_label.setText(f"登录失败: {str(e)}")
    
    def _save_login_info(self, username, password):
        """保存登录信息到配置文件"""
        try:
            # 加载现有配置
            config = self._load_config()
            
            # 更新登录信息
            config['login_info'] = {
                'username': username,
                'password': password
            }
            
            # 保存配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"保存登录信息失败: {e}")
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
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
    
    def toggle_password_visibility(self):
        """切换密码显示/隐藏状态"""
        self.password_visible = not self.password_visible
        
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.password_toggle.setText("👁‍🗨")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_toggle.setText("👁")
            
    def _load_saved_login_info(self):
        """加载保存的登录信息并填充到输入框"""
        try:
            config = self._load_config()
            if 'login_info' in config:
                login_info = config['login_info']
                username = login_info.get('username', '')
                password = login_info.get('password', '')
                
                # 填充到输入框
                self.username_input.setText(username)
                self.password_input.setText(password)
        except Exception as e:
            print(f"加载登录信息失败: {e}")
