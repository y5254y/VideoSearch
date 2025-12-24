# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QWidget, QSizePolicy)
from PySide6.QtCore import Qt

class Ui_UserInfoDialog:
    def setupUi(self, UserInfoDialog):
        UserInfoDialog.setObjectName("UserInfoDialog")
        UserInfoDialog.resize(350, 300)
        UserInfoDialog.setWindowTitle("用户信息")
        
        # 创建主布局
        self.main_layout = QVBoxLayout(UserInfoDialog)
        self.main_layout.setObjectName("main_layout")
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        
        # 用户信息部分
        self.user_info_widget = QWidget(UserInfoDialog)
        self.user_info_widget.setObjectName("user_info_widget")
        self.user_info_layout = QVBoxLayout(self.user_info_widget)
        self.user_info_layout.setObjectName("user_info_layout")
        self.user_info_layout.setContentsMargins(0, 0, 0, 0)
        self.user_info_layout.setSpacing(8)
        
        # 用户名标签
        self.label_username = QLabel(self.user_info_widget)
        self.label_username.setObjectName("label_username")
        self.label_username.setText("用户名: N/A")
        self.user_info_layout.addWidget(self.label_username)
        
        # 邮箱标签
        self.label_email = QLabel(self.user_info_widget)
        self.label_email.setObjectName("label_email")
        self.label_email.setText("邮箱: N/A")
        self.user_info_layout.addWidget(self.label_email)
        
        self.main_layout.addWidget(self.user_info_widget)
        
        # 积分信息部分
        self.points_widget = QWidget(UserInfoDialog)
        self.points_widget.setObjectName("points_widget")
        self.points_layout = QVBoxLayout(self.points_widget)
        self.points_layout.setObjectName("points_layout")
        self.points_layout.setContentsMargins(0, 0, 0, 0)
        self.points_layout.setSpacing(8)
        
        # 当前积分标签
        self.label_current_points = QLabel(self.points_widget)
        self.label_current_points.setObjectName("label_current_points")
        self.label_current_points.setText("当前积分: 0")
        self.points_layout.addWidget(self.label_current_points)
        
        # 总获取积分标签
        self.label_total_earned = QLabel(self.points_widget)
        self.label_total_earned.setObjectName("label_total_earned")
        self.label_total_earned.setText("总获取积分: 0")
        self.points_layout.addWidget(self.label_total_earned)
        
        # 总消耗积分标签
        self.label_total_spent = QLabel(self.points_widget)
        self.label_total_spent.setObjectName("label_total_spent")
        self.label_total_spent.setText("总消耗积分: 0")
        self.points_layout.addWidget(self.label_total_spent)
        
        # 积分更新时间标签
        self.label_updated_at = QLabel(self.points_widget)
        self.label_updated_at.setObjectName("label_updated_at")
        self.label_updated_at.setText("积分更新时间: ")
        self.points_layout.addWidget(self.label_updated_at)
        
        self.main_layout.addWidget(self.points_widget)
        
        # 按钮部分
        self.buttons_widget = QWidget(UserInfoDialog)
        self.buttons_widget.setObjectName("buttons_widget")
        self.buttons_layout = QHBoxLayout(self.buttons_widget)
        self.buttons_layout.setObjectName("buttons_layout")
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(10)
        self.buttons_layout.addStretch()
        
        # 签到按钮
        self.btn_checkin = QPushButton(self.buttons_widget)
        self.btn_checkin.setObjectName("btn_checkin")
        self.btn_checkin.setText("签到")
        self.btn_checkin.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_checkin.setMinimumWidth(80)
        self.buttons_layout.addWidget(self.btn_checkin)
        
        # 登出按钮
        self.btn_logout = QPushButton(self.buttons_widget)
        self.btn_logout.setObjectName("btn_logout")
        self.btn_logout.setText("登出")
        self.btn_logout.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_logout.setMinimumWidth(80)
        self.buttons_layout.addWidget(self.btn_logout)
        
        # 关闭按钮
        self.btn_close = QPushButton(self.buttons_widget)
        self.btn_close.setObjectName("btn_close")
        self.btn_close.setText("关闭")
        self.btn_close.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_close.setMinimumWidth(80)
        self.buttons_layout.addWidget(self.btn_close)
        
        self.main_layout.addWidget(self.buttons_widget)
        
        # 设置布局
        UserInfoDialog.setLayout(self.main_layout)
