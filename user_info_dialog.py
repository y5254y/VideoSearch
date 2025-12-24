# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Signal
from user_info_dialog_ui import Ui_UserInfoDialog

class UserInfoDialog(QDialog, Ui_UserInfoDialog):
    # 定义信号，用于通知父窗口登出事件
    logout_requested = Signal()
    # 定义信号，用于通知父窗口签到成功事件
    checkin_succeeded = Signal()
    
    def __init__(self, user_info, user_service, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        # 初始化数据
        self.user_info = user_info
        self.user_service = user_service
        
        # 连接信号槽
        self._connect_signals()
        
        # 更新用户信息和积分信息
        self.update_user_info()
        self.update_points_info()
        
        # 设置签到按钮状态
        self._set_checkin_button_state()
    
    def _connect_signals(self):
        """连接信号槽"""
        self.btn_checkin.clicked.connect(self._on_checkin)
        self.btn_logout.clicked.connect(self._on_logout)
        self.btn_close.clicked.connect(self.close)
    
    def update_user_info(self):
        """更新用户信息"""
        if self.user_info:
            username = self.user_info.get('username', 'N/A')
            email = self.user_info.get('email', 'N/A')
            self.label_username.setText(f"用户名: {username}")
            self.label_email.setText(f"邮箱: {email}")
    
    def update_points_info(self):
        """更新积分信息"""
        try:
            success, points_info = self.user_service.get_current_points()
            if success:
                current_points = points_info.get('current_points', 0)
                total_earned = points_info.get('total_earned', 0)
                total_spent = points_info.get('total_spent', 0)
                updated_at = points_info.get('updated_at', '')
                
                self.label_current_points.setText(f"当前积分: {current_points}")
                self.label_total_earned.setText(f"总获取积分: {total_earned}")
                self.label_total_spent.setText(f"总消耗积分: {total_spent}")
                
                if updated_at:
                    self.label_updated_at.setText(f"积分更新时间: {updated_at}")
                else:
                    self.label_updated_at.setText("积分更新时间: ")
            else:
                # 如果获取详细积分失败，显示基本积分
                points = self.user_info.get('points', 0)
                self.label_current_points.setText(f"当前积分: {points}")
                # 隐藏其他积分标签
                self.label_total_earned.setVisible(False)
                self.label_total_spent.setVisible(False)
                self.label_updated_at.setVisible(False)
        except Exception as e:
            QMessageBox.warning(self, "获取积分失败", f"无法获取积分信息: {str(e)}")
    
    def _set_checkin_button_state(self):
        """设置签到按钮状态"""
        try:
            if self.user_service.is_checked_in_today():
                self.btn_checkin.setEnabled(False)
                self.btn_checkin.setStyleSheet("color: gray;")
            else:
                self.btn_checkin.setEnabled(True)
                self.btn_checkin.setStyleSheet("")
        except Exception as e:
            print(f"检查签到状态失败: {e}")
    
    def _on_checkin(self):
        """处理签到事件"""
        try:
            success, message = self.user_service.check_in()
            if success:
                # 更新积分信息
                self.update_points_info()
                
                # 更新签到按钮状态
                self._set_checkin_button_state()
                
                # 发送签到成功信号
                self.checkin_succeeded.emit()
                
                QMessageBox.information(self, "签到成功", message)
            else:
                QMessageBox.warning(self, "签到失败", message)
        except Exception as e:
            QMessageBox.warning(self, "签到失败", f"签到过程中发生错误: {str(e)}")
    
    def _on_logout(self):
        """处理登出事件"""
        reply = QMessageBox.question(self, "登出确认", "确定要登出吗？", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 发送登出请求信号
            self.logout_requested.emit()
            
            # 关闭对话框
            self.close()
