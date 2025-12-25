# -*- coding: utf-8 -*-
import sys
import os
import json
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QHBoxLayout, QVBoxLayout,
    QLineEdit, QComboBox, QMessageBox, QSizePolicy, QSplitter,
    QRadioButton, QButtonGroup, QSlider, QProgressBar, QTextBrowser, QListView,
    QDialog
)
from PySide6.QtGui import QPixmap, QImage, QIcon, QAction, QPainter, QPolygon, QColor
from PySide6.QtCore import QPoint, Qt, QUrl, QSize, QTimer, QEvent
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

# 导入自定义组件
from player_widget import PlayerWidget
from main_ui import Ui_MainWindow
from widgets.result_card import ResultCard
from login_window import LoginWindow

# 导入搜索和工具模块
from search import AISearchEngine, format_ms
from translations import TRANSLATIONS
from search_worker import SearchWorker
from category_mappings import translate_category, get_translated_categories
from user_service import UserService

# 确保资源文件被加载
try:
    import resources_rc
except Exception:
    pass

class VideoSearchApp(QMainWindow, Ui_MainWindow):
    def __init__(self, token=None, user_info=None):
        super().__init__()
        self.setupUi(self)
        
        # 设置窗口初始大小为屏幕的3/4
        screen_geometry = QApplication.primaryScreen().geometry()
        width = int(screen_geometry.width() * 3 / 4)
        height = int(screen_geometry.height() * 3 / 4)
        self.resize(width, height)
        
        # 允许窗口大小调整
        self.setMinimumSize(800, 600)
        
        # 使用自定义标题栏，去掉默认标题栏
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 初始化用户服务
        self.user_service = UserService()
        
        # 用户认证状态
        self.is_logged_in = token is not None and user_info is not None
        self.token = token
        self.user_info = user_info
        from config import API_BASE_URL
        self.api_base_url = API_BASE_URL
        
        # 初始化应用状态
        self.lang = 'zh'  # 默认语言
        self.videos = []  # 选中的视频列表
        self.images = []  # 选中的图像列表
        self.search_worker = None  # 搜索工作线程
        self.search_engine = AISearchEngine()  # AI搜索引擎实例
        
        # 初始化翻译
        self.translations = TRANSLATIONS
        
        # 加载配置
        self.config_path = os.path.join(os.path.expanduser('~'), '.videosearch_config.json')
        self.config = self._load_config()
        
        # 初始化UI组件
        self._init_ui()
        
        # 连接信号槽
        self._connect_signals()
        
        # 应用初始设置
        self._apply_initial_settings()
    
    def _init_ui(self):
        """初始化UI组件"""
        # 创建自定义标题栏
        self._create_custom_title_bar()
        
        # 创建语言选择组合框
        self.lang_combo = QComboBox()
        self.lang_combo.addItem('中文 (简体)')
        self.lang_combo.addItem('English')
        self.lang_combo.setCurrentIndex(0)
        self.lang_combo.setToolTip(self._t('language'))
        
        # 将语言选择组合框添加到自定义标题栏
        self.title_bar.layout().insertWidget(2, self.lang_combo)
        
        # 样式已移至QSS文件中
        
        # 搜索模式选择
        self.rb_image.setChecked(True)
        
        # 滑块设置
        self.slider.setRange(0, 100)
        self.slider.setTickInterval(5)
        
        # 分类选择框设置为可编辑
        self.combo_category.setEditable(True)
        # 为combo_category安装事件过滤器，实现获得焦点时自动打开下拉列表
        self.combo_category.installEventFilter(self)
        # 添加分类提示功能
        self._init_category_hint()
        
        # 移除了清除按钮以简化界面
        
        # 设置列表视图为列表模式，仅显示文本
        self.list_videos.setViewMode(QListWidget.ListMode)
        self.list_videos.setSpacing(2)
        
        self.list_images.setViewMode(QListWidget.IconMode)
        self.list_images.setIconSize(QSize(80, 60))
        self.list_images.setResizeMode(QListWidget.Adjust)
        self.list_images.setSpacing(12)
        
        # 优化左侧面板布局和控件样式
        self._optimize_left_panel_layout()
        
        # 播放器初始化
        self._init_player()
        
        # 搜索按钮状态初始化
        self._spinner_timer = None
        self._spinner_chars = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
        self._spinner_idx = 0
        
        
        # 初始化响应式布局
        self._init_responsive_layout()
        
        # 添加排序选项
        self._init_sorting_options()
    
    def _create_custom_title_bar(self):
        """创建自定义标题栏"""
        # 创建标题栏容器
        self.title_bar = QWidget()
        self.title_bar.setObjectName("title_bar")
        
        # 设置标题栏高度
        self.title_bar.setFixedHeight(60)
        
        # 创建标题栏布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建标题标签
        self.title_label = QLabel(self._t('title'))
        self.title_label.setObjectName("title_label")
        
        # 创建最小化按钮
        self.btn_minimize = QPushButton("-")
        self.btn_minimize.setObjectName("title_btn")
        
        # 创建最大化按钮
        self.btn_maximize = QPushButton("□")
        self.btn_maximize.setObjectName("title_btn")
        
        # 创建关闭按钮
        self.btn_close = QPushButton("×")
        self.btn_close.setObjectName("title_btn_close")
        
        # 添加控件到布局
        layout.addWidget(self.title_label)
        layout.addStretch(1)
        
        # 创建用户按钮，放在窗口控制按钮之前
        self.user_button = QPushButton('登录')  # 直接在创建时设置文本
        self.user_button.setObjectName("userButton")
        
        # 设置简单明确的样式
        self.user_button.setStyleSheet(
            "QPushButton {" 
            "    color: white;" 
            "    background-color: #4285F4;" 
            "    border: none;" 
            "    border-radius: 4px;" 
            "    padding: 8px 16px;" 
            "    font-size: 14px;" 
            "    font-weight: bold;" 
            "    margin-right: 10px;" 
            "    min-width: 80px;" 
            "    min-height: 30px;" 
            "}" 
            "QPushButton:hover {" 
            "    background-color: #3367D6;" 
            "}"
        )
        
        self.user_button.setCursor(Qt.PointingHandCursor)
        
        # 根据登录状态和签到状态更新按钮文本
        if self.is_logged_in and self.user_info:
            username = self.user_info.get('username', '用户')
            # 检查是否已经签到
            if hasattr(self, 'user_service') and self.user_service.is_logged_in():
                if not self.user_service.is_checked_in_today():
                    username = f"🎁 {username}"
            self.user_button.setText(username)
        
        # 连接点击事件
        self.user_button.clicked.connect(self._on_user_button_clicked)
        
        # 将用户按钮添加到标题栏
        layout.addWidget(self.user_button)
        
        # 添加窗口控制按钮
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_maximize)
        layout.addWidget(self.btn_close)
        
        # 设置标题栏布局
        self.title_bar.setLayout(layout)
        
        # 将标题栏添加到主窗口布局
        main_layout = self.centralwidget.layout()
        main_layout.insertWidget(0, self.title_bar)
        
        # 连接窗口控制按钮信号
        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_maximize.clicked.connect(self._toggle_maximize)
        self.btn_close.clicked.connect(self.close)
        
        # 添加窗口拖动功能
        self.title_bar.mousePressEvent = self._title_bar_mouse_press_event
        self.title_bar.mouseMoveEvent = self._title_bar_mouse_move_event
        self.title_bar.mouseReleaseEvent = self._title_bar_mouse_release_event
        
        # 初始化拖动状态
        self._drag_pos = None
    
    def _toggle_maximize(self):
        """切换窗口最大化/还原状态"""
        if self.isMaximized():
            self.showNormal()
            self.btn_maximize.setText("□")
        else:
            self.showMaximized()
            self.btn_maximize.setText("◱")
    
    def _title_bar_mouse_press_event(self, event):
        """标题栏鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def _title_bar_mouse_move_event(self, event):
        """标题栏鼠标移动事件"""
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    
    def _title_bar_mouse_release_event(self, event):
        """标题栏鼠标释放事件"""
        self._drag_pos = None
    
    def _init_player(self):
        """初始化播放器组件"""
        try:
            if isinstance(self.playerContainer, PlayerWidget):
                self.player_widget = self.playerContainer
            else:
                self.player_widget = PlayerWidget(self.playerContainer)
                layout = self.playerContainer.layout() or QVBoxLayout(self.playerContainer)
                layout.addWidget(self.player_widget)
                # self.player_widget.pauseButton.setVisible(False)
        except Exception as e:
            self.player_widget = None
            self.playerContainer_layout_fallback = QVBoxLayout(self.playerContainer)
            self.playerContainer_layout_fallback.addWidget(QLabel(f"Player unavailable: {e}"))
            print(f"PlayerWidget initialization failed: {e}")
        
        # 加载图标
        self._load_icons()
    
    def _load_icons(self):
        """优化后的图标加载机制，集中管理所有图标"""
        
        # 集中存储所有图标
        self.icons = {}
        
        def load_icon(icon_name):
            """加载单个图标，直接使用文件系统路径"""
            import os
            base = os.path.abspath(os.path.dirname(__file__))
            icon_path = os.path.join(base, 'resources', f'{icon_name}.svg')
            
            if os.path.exists(icon_path):
                return QIcon(icon_path)
            
            # 如果文件不存在，返回一个空图标
            return QIcon()
        
        # 定义并加载所有需要的图标
        icon_names = ['play', 'pause', 'stop', 'folder_open', 'search', 'stop_search']
        
        for icon_name in icon_names:
            self.icons[icon_name] = load_icon(icon_name)
        
        # 设置播放器图标
        if self.player_widget:
            self.player_widget.set_icons(
                self.icons['play'], 
                self.icons['pause'], 
                self.icons['stop']
            )
        
        # 设置按钮图标
        self.btn_select_videos.setIcon(self.icons['folder_open'])
        self.btn_select_videos.setIconSize(QSize(16, 16))
        
        self.btn_select_images.setIcon(self.icons['folder_open'])
        self.btn_select_images.setIconSize(QSize(16, 16))
        
        self.btn_search.setIcon(self.icons['search'])
        self.btn_search.setIconSize(QSize(16, 16))
        
        

    
    def _optimize_left_panel_layout(self):
        """优化左侧面板的布局和控件样式"""
        
        # 为各个控件组添加更好的间距
        for layout in [self.modeLayout, self.selectionLayout]:
            if hasattr(layout, 'setSpacing'):
                layout.setSpacing(8)
            if hasattr(layout, 'setContentsMargins'):
                layout.setContentsMargins(8, 8, 8, 8)
        
        # 优化单选按钮组的布局，改为紧凑的水平布局
        self.modeLayout.setContentsMargins(12, 8, 12, 8)
        
        # 将单选按钮组设置为水平布局，使用紧凑的样式
        self.radioButtonsLayout.setDirection(QHBoxLayout.LeftToRight)
        self.radioButtonsLayout.setSpacing(12)
        
        # 调整单选按钮的样式已移至QSS文件中
        
        # 调整按钮大小策略
        for btn in [self.btn_select_videos, self.btn_select_images, self.btn_search]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # 设置优化标签样式已移至QSS文件中
                
    def _init_category_hint(self):
        """初始化分类提示功能，将YOLO支持的类别直接添加到下拉框中"""
        try:
            # 获取支持的类别
            categories = self.search_engine.get_supported_categories()
            
            # 清空下拉框
            self.combo_category.clear()
            
            # 根据当前语言翻译类别并添加到下拉框中
            for category in categories:
                translated_category = translate_category(category, self.lang)
                self.combo_category.addItem(translated_category)
        except Exception as e:
            # 如果加载类别失败，不影响程序运行
            print(f"无法加载类别列表：{str(e)}")
    
    def _show_supported_categories(self):
        """显示YOLO支持的所有类别"""
        try:
            # 获取支持的类别
            categories = self.search_engine.get_supported_categories()
            
            # 创建一个对话框来显示类别
            category_dialog = QDialog(self)
            category_dialog.setWindowTitle("支持的类别")
            category_dialog.resize(400, 500)
            
            # 创建布局
            layout = QVBoxLayout(category_dialog)
            
            # 添加说明文本
            label = QLabel("YOLO模型支持以下检测类别：")
            label.setWordWrap(True)
            layout.addWidget(label)
            
            # 创建列表视图显示类别
            category_list = QListWidget()
            category_list.addItems(categories)
            category_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
            layout.addWidget(category_list)
            
            # 添加关闭按钮
            btn_close = QPushButton("关闭")
            btn_close.clicked.connect(category_dialog.close)
            layout.addWidget(btn_close)
            
            # 显示对话框
            category_dialog.exec()
        except Exception as e:
            # 如果加载模型失败，显示错误信息
            QMessageBox.warning(self, "提示", f"无法加载类别列表：{str(e)}")
    
    def _init_responsive_layout(self):
        """初始化响应式布局"""
        # 设置splitter的拉伸因子
        self.splitter.setSizes([300, 600, 400])
        
        # 设置splitter的拉伸策略
        self.splitter.setStretchFactor(0, 1)   # leftPanel - 最小拉伸
        self.splitter.setStretchFactor(1, 3)   # centerPanel - 主要拉伸区域
        self.splitter.setStretchFactor(2, 2)   # rightPanel - 中等拉伸
        
        # 设置最小尺寸约束
        self.leftPanel.setMinimumWidth(250)
        self.leftPanel.setMaximumWidth(450)
        self.centerPanel.setMinimumWidth(500)
        self.rightPanel.setMinimumWidth(350)
        self.rightPanel.setMaximumWidth(700)
        
        # 设置窗口大小策略
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 设置搜索结果列表的自适应行为
        self.list_results.setFlow(QListView.LeftToRight)
        self.list_results.setWrapping(True)
        self.list_results.setResizeMode(QListWidget.Adjust)
        self.list_results.setMovement(QListView.Static)
        self.list_results.setSelectionMode(QListWidget.SingleSelection)
        
        # 设置结果列表样式已移至QSS文件中
        
        # 初始化搜索结果列表的图标大小
        self._update_result_icon_size()
    
    def resizeEvent(self, event):
        """重写窗口大小变化事件，实现响应式布局"""
        # 调用父类的resizeEvent
        super(VideoSearchApp, self).resizeEvent(event)
        
        # 更新搜索结果列表的图标大小
        self._update_result_icon_size()
    
    def _update_result_icon_size(self):
        """根据窗口宽度更新搜索结果卡片的大小和排列"""
        window_width = self.width()
        center_width = self.centerPanel.width()
        
        # 计算卡片宽度和行数，确保合理的排列
        if center_width < 800:
            # 小窗口时每行显示2个卡片
            card_width = min(320, center_width // 2 - 20)
            self.list_results.setGridSize(QSize(card_width, 160))
        elif center_width < 1200:
            # 中等窗口时每行显示3个卡片
            card_width = min(320, center_width // 3 - 20)
            self.list_results.setGridSize(QSize(card_width, 160))
        else:
            # 大窗口时每行显示4个卡片
            card_width = min(320, center_width // 4 - 20)
            self.list_results.setGridSize(QSize(card_width, 170))
        
        # 设置间距，确保卡片之间有足够的空间
        self.list_results.setSpacing(16)
    
    def _init_sorting_options(self):
        """初始化排序选项UI"""
        # 创建排序标签
        self.lbl_sort = QLabel(self._t('sort_by'))
        
        # 创建排序下拉框
        self.combo_sort = QComboBox()
        self.combo_sort.addItem(self._t('sort_by_score'), 'score')
        self.combo_sort.addItem(self._t('sort_by_time'), 'time')
        
        # 设置默认排序为按评分排序
        self.combo_sort.setCurrentIndex(0)
        
        # 连接排序选择信号
        self.combo_sort.currentIndexChanged.connect(self._on_sort_changed)
        
        # 获取lbl_results的父布局
        layout = self.lbl_results.parent().layout()
        if layout:
            # 在lbl_results之后添加排序控件
            index = layout.indexOf(self.lbl_results)
            if index >= 0:
                layout.insertWidget(index + 1, self.lbl_sort)
                layout.insertWidget(index + 2, self.combo_sort)
        
        # 初始排序（默认按评分从高到低）
        self._sort_results('score', reverse=True)
    
    def _on_sort_changed(self, index):
        """处理排序选择变化"""
        sort_by = self.combo_sort.currentData()
        # 按评分排序默认从高到低，按时间排序默认从低到高（时间顺序）
        reverse = (sort_by == 'score')
        self._sort_results(sort_by, reverse)
    
    def _sort_results(self, sort_by, reverse=False):
        """对搜索结果进行排序"""
        if self.list_results.count() <= 1:
            return
        
        # 获取所有结果项的数据（保存创建Widget所需的数据）
        items_data = []
        for i in range(self.list_results.count()):
            item = self.list_results.item(i)
            if not item:
                continue
            
            # 获取UserRole数据（视频路径和时间戳）
            user_data = item.data(Qt.ItemDataRole.UserRole)
            if not user_data:
                continue
            
            # 获取Widget和分数
            widget = self.list_results.itemWidget(item)
            score = widget.score if (widget and hasattr(widget, 'score')) else 0.0
            
            # 获取排序键
            if sort_by == 'score':
                sort_key = score
            else:  # 'time'
                sort_key = user_data[1]  # timestamp_ms
            
            # 保存创建Widget所需的所有数据（不包括缩略图，排序时重新生成）
            video_path, timestamp_ms = user_data
            items_data.append((sort_key, video_path, timestamp_ms, score))
        
        # 如果没有找到任何有效的项，直接返回
        if not items_data:
            return
        
        # 排序
        items_data.sort(key=lambda x: x[0], reverse=reverse)
        
        # 清空列表
        self.list_results.clear()
        
        # 获取当前网格大小
        grid_size = self.list_results.gridSize()
        
        # 重新添加所有项
        for sort_key, video_path, timestamp_ms, score in items_data:
            try:
                # 重新生成视频缩略图
                thumb = self._get_video_thumbnail(video_path, timestamp_ms)
                
                # 创建结果卡片
                card = ResultCard(video_path=video_path, timestamp_ms=timestamp_ms, score=score, thumbnail=thumb)
                
                # 根据网格大小调整卡片大小
                card.setFixedWidth(grid_size.width())
                
                # 创建列表项
                lw_item = QListWidgetItem()
                
                # 设置项目大小与卡片大小匹配
                item_height = max(150, grid_size.height())
                lw_item.setSizeHint(QSize(grid_size.width(), item_height))
                
                # 设置UserRole数据
                lw_item.setData(Qt.ItemDataRole.UserRole, (video_path, timestamp_ms))
                
                # 添加结果到列表
                self.list_results.addItem(lw_item)
                self.list_results.setItemWidget(lw_item, card)
                
                # 连接卡片点击事件
                card.clicked.connect(self.on_result_card_clicked)
            except Exception as e:
                print(f"Error creating result card during sort: {e}")
                import traceback
                traceback.print_exc()
        
        # 更新搜索结果数量显示
        self.lbl_results.setText(f"{self._t('results')} ({self.list_results.count()})")
    
    def _connect_signals(self):
        """连接UI信号和槽函数"""
        # 语言选择
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        
        # 搜索模式切换
        self.rb_image.toggled.connect(self.update_search_mode_ui)
        self.rb_category.toggled.connect(self.update_search_mode_ui)
        
        # 列表双击事件
        self.list_videos.itemDoubleClicked.connect(self.on_video_double_clicked)
        self.list_results.itemDoubleClicked.connect(self.on_result_double_clicked)
        
        # 按钮点击事件
        self.btn_select_videos.clicked.connect(self.select_videos)
        self.btn_select_images.clicked.connect(self.select_images)
        self.btn_search.clicked.connect(self._on_search_toggle)
        
        # 滑块值变化
        self.slider.valueChanged.connect(self._on_slider_changed)
        
        # 分类选择完成后切换焦点到搜索按钮
        self.combo_category.activated.connect(self._on_category_selected)
    
    def _apply_initial_settings(self):
        """应用初始设置"""
        # 设置滑块初始值
        init_score = int(self.config.get('score', 85))
        self.slider.setValue(init_score)
        
        # 更新搜索模式UI
        self.update_search_mode_ui()
        
        # 应用初始语言
        self.change_language(0)
    
    def eventFilter(self, obj, event):
        """事件过滤器，用于处理combo_category的焦点事件"""
        if obj is self.combo_category:
            if event.type() == QEvent.FocusIn:
                # 只在用户主动点击或通过键盘聚焦时才打开下拉列表，避免自动触发
                if event.reason() in [Qt.MouseFocusReason, Qt.TabFocusReason, Qt.BacktabFocusReason]:
                    # 当获得焦点时，延迟打开下拉列表，确保焦点已完全切换
                    QTimer.singleShot(100, lambda: self.combo_category.showPopup())
        return super().eventFilter(obj, event)
    
    def _on_category_selected(self):
        """当选择类别后，关闭下拉框并将焦点切换到搜索按钮"""
        # 先关闭下拉框，再切换焦点
        self.combo_category.hidePopup()
        # 将焦点切换到搜索按钮
        self.btn_search.setFocus()
        
    
    # -------------- UI控制方法 --------------
    def update_search_mode_ui(self):
        """根据选择的搜索模式更新UI控件的可见性和可用性"""
        # 检查单选按钮状态
        image_mode = self.rb_image.isChecked()
        category_mode = self.rb_category.isChecked()
        text_mode = False  # 文字搜索功能已隐藏
        
        # 隐藏文字搜索单选按钮
        self.rb_text.setVisible(False)
        
        # 根据搜索模式隐藏/显示相关控件
        # 图片搜索模式: 显示视频选择、图片选择；隐藏类别选择、文字查询
        # 类别搜索模式: 显示视频选择、类别选择；隐藏图片选择、文字查询
        # 文字搜索模式: 显示视频选择、文字查询；隐藏图片选择、类别选择
        
        # 视频选择相关控件 - 所有模式都显示
        self.btn_select_videos.setVisible(True)
        self.lbl_selected_videos.setVisible(True)
        self.list_videos.setVisible(True)
        
        # 图像搜索相关控件
        image_controls = [self.btn_select_images, self.list_images, self.lbl_query_images]
        for control in image_controls:
            control.setVisible(image_mode)
            control.setEnabled(image_mode)
        
        # 分类搜索相关控件
        category_controls = [self.combo_category, self.lbl_select_category]
        for control in category_controls:
            control.setVisible(category_mode)
            control.setEnabled(category_mode)
        
        # 当切换到类别搜索模式时，确保下拉框中有类别项
        if category_mode and self.combo_category.count() == 0:
            try:
                # 获取支持的类别
                categories = self.search_engine.get_supported_categories()
                
                # 将类别添加到下拉框中
                for category in categories:
                    self.combo_category.addItem(category)
            except Exception as e:
                # 如果加载类别失败，不影响程序运行
                print(f"无法加载类别列表：{str(e)}")
        
        # 移除可能影响下拉按钮显示的自定义样式
        if hasattr(self.combo_category, 'setStyleSheet'):
            # 设置明确的下拉框样式，确保下拉按钮和箭头可见
            self.combo_category.setStyleSheet("""
                QComboBox {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 6px;
                    background-color: white;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left: 1px solid #e0e0e0;
                    border-top-right-radius: 4px;
                    border-bottom-right-radius: 4px;
                    background-color: transparent;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-style: solid;
                    border-width: 5px 4px 0 4px;
                    border-color: #999999 transparent transparent transparent;
                    width: 0;
                    height: 0;
                    margin: 6px;
                }
                QComboBox::down-arrow:hover {
                    border-color: #555555 transparent transparent transparent;
                }
                QComboBox QAbstractItemView {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    background-color: white;
                    selection-background-color: #e3f2fd;
                    selection-color: #202124;
                }
            """)
        
        # 确保QComboBox处于可下拉状态
        self.combo_category.setEditable(True)
        self.combo_category.setFocusPolicy(Qt.StrongFocus)
        self.combo_category.setDisabled(False)
        
        # 确保下拉框视图正确设置
        view = self.combo_category.view()
        view.setFixedWidth(self.combo_category.width())
        view.setMaximumHeight(200)
        view.setStyleSheet("background-color: white;")
        
        # 确保模型数据正确
        if self.combo_category.count() > 0:
            self.combo_category.setCurrentIndex(0)
        
        # 显式触发下拉框的显示
        self.combo_category.view().setVisible(True)
        
        # 文本搜索相关控件（始终隐藏）
        text_controls = [self.input_text, self.lbl_text_query]
        for control in text_controls:
            control.setVisible(False)
            control.setEnabled(False)
        

        
        # Update mode hint
        mode = self._get_search_mode()
        mode_hints = {
            'image': self._t('mode_hint_image'),
            'category': self._t('mode_hint_category')
        }
        self.lbl_mode_hint.setText(mode_hints.get(mode, self._t('mode_hint_select')))
    
    def change_language(self, index):
        """切换界面语言"""
        self.lang = 'zh' if index == 0 else 'en'
        
        # 更新窗口标题
        self.setWindowTitle(self._t('title'))
        
        # 更新标题栏标题
        self.title_label.setText(self._t('title'))
        
        # 更新按钮文本
        self.btn_select_videos.setText(self._t('select_videos'))
        self.btn_select_images.setText(self._t('select_images'))
        # 清除按钮已被移除
        # self.btn_clear_videos.setText(self._t('clear_videos'))
        # self.btn_clear_images.setText(self._t('clear_images'))
        self.btn_search.setText(self._t('search'))
        
        
        
        # 更新标签文本
        self.lbl_selected_videos.setText(self._t('selected_videos'))
        self.lbl_query_images.setText(self._t('query_images'))
        self.lbl_select_category.setText(self._t('select_category'))
        self.lbl_text_query.setText(self._t('text_query'))
        self.lbl_results.setText(self._t('results'))
        
        # 更新语言选择组合框的工具提示
        self.lang_combo.setToolTip(self._t('language'))
        
        # 不再从翻译文件更新分类列表，而是保持显示所有YOLO支持的类别
        # 这确保了combo_category始终显示完整的YOLO类别列表
        
        # 更新搜索模式标签
        self.rb_image.setText(self._t('search_mode_image'))
        self.rb_category.setText(self._t('search_mode_category'))
        self.rb_text.setText(self._t('search_mode_text'))
        
        # 更新分数标签
        self._update_score_label()
        
        # 更新类别下拉框的显示，根据新的语言翻译类别
        # 保存当前选择的类别
        current_category = self.combo_category.currentText()
        # 重新初始化类别下拉框
        self._init_category_hint()
        # 尝试重新选择之前的类别（如果存在的话）
        index = self.combo_category.findText(current_category)
        if index >= 0:
            self.combo_category.setCurrentIndex(index)
    
    def _update_score_label(self):
        """更新分数标签，显示为百分数"""
        self.lbl_score.setText(f"{self._t('score_threshold')}: {self.slider.value()}%")
    
    # -------------- 文件选择方法 --------------
    def select_videos(self):
        """选择视频文件"""
        files, _ = QFileDialog.getOpenFileNames(self, self._t('file_dialog_videos'), os.path.expanduser("~"),
                                               "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)")
        if files:
            self.videos = files
            self.list_videos.clear()
            for f in files:
                filename = os.path.basename(f)  # 只显示文件名
                
                # 创建文本项，不使用图标
                item = QListWidgetItem(filename)
                
                item.setToolTip(f)  # 鼠标悬停显示完整路径
                self.list_videos.addItem(item)
    
    def select_images(self):
        """选择图像文件"""
        files, _ = QFileDialog.getOpenFileNames(self, self._t('file_dialog_images'), os.path.expanduser("~"),
                                               "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)")
        if files:
            self.images = files
            self.list_images.clear()
            for f in files:
                filename = os.path.basename(f)  # 只显示文件名
                
                # 加载图像作为缩略图
                try:
                    pixmap = QPixmap(f)
                    if not pixmap.isNull():
                        # 缩放图像到合适大小
                        pixmap = pixmap.scaled(80, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        item = QListWidgetItem(QIcon(pixmap), filename)
                    else:
                        item = QListWidgetItem(filename)
                except Exception as e:
                    item = QListWidgetItem(filename)
                
                item.setToolTip(f)  # 鼠标悬停显示完整路径
                item.setTextAlignment(Qt.AlignCenter)
                self.list_images.addItem(item)
    
    # def clear_videos(self):
    #     """清除所有选择的视频"""
    #     self.videos = []
    #     self.list_videos.clear()
    
    # def clear_images(self):
    #     """清除所有选择的图片"""
    #     self.images = []
    #     self.list_images.clear()
    
    # -------------- 搜索相关方法 --------------
    def _on_search_toggle(self):
        """切换搜索/停止搜索状态"""
        print("_on_search_toggle method called")
        print(f"Current search_worker: {self.search_worker}")
        
        if self.search_worker:
            # 当前正在搜索，停止搜索
            print("Stopping search...")
            self.on_stop_search()
        else:
            # 检查用户是否已登录
            if not self.is_logged_in:
                QMessageBox.warning(self, "未登录", "请先登录后再使用搜索功能")
                return
            
            # 立即更新按钮状态为停止搜索，然后再开始搜索
            print("Starting search...")
            # 保存原始按钮文本
            self._btn_search_orig_text = self.btn_search.text()
            print(f"Original button text saved: {self._btn_search_orig_text}")
            # 更新按钮状态
            self.btn_search.setText(self._t('stop_search'))
            self.btn_search.setIcon(self.icons['stop_search'])
            
            # 当前未搜索，开始搜索
            print("Calling on_search...")
            self.on_search()
    
    def on_search(self):
        """开始搜索"""
        print("on_search method called")
        
        # 验证视频选择
        print(f"Videos selected: {self.videos}")
        if not self.videos:
            QMessageBox.warning(self, self._t('no_videos'), self._t('no_videos_detail'))
            return
        
        # 确定搜索模式并验证输入
        mode = self._get_search_mode()
        print(f"Search mode: {mode}")
        if mode is None:
            return
        
        # 准备搜索参数
        search_params = self._prepare_search_params(mode)
        print(f"Search params: {search_params}")
        if search_params is None:
            return
        
        # 禁用搜索模式切换按钮
        self.rb_image.setEnabled(False)
        self.rb_category.setEnabled(False)
        
        # 初始化搜索状态
        self._init_search_state()
        
        # 开始按钮旋转动画并保存原始按钮文本
        self._start_button_spinner()
        
        # 创建并启动搜索工作线程
        print("Starting search worker...")
        self._start_search_worker(search_params)
        print("Search worker started")
    
    def _get_search_mode(self):
        """获取当前选择的搜索模式"""
        if self.rb_image.isChecked():
            return 'image'
        elif self.rb_category.isChecked():
            return 'category'
        return None
    
    def _prepare_search_params(self, mode):
        """准备搜索参数"""
        params = {
            'mode': mode,
            'score_threshold': self.slider.value()/100.0
        }
        
        if mode == 'image':
            if not self.images:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_images'))
                return None
            params['query_images'] = self.images
        elif mode == 'category':
            query_category = self.combo_category.currentText().strip()
            if not query_category:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_category'))
                return None
            # 将用户选择的类别转换为英文，因为模型只支持英文
            english_category = translate_category(query_category, 'en')
            params['query_category'] = english_category
        elif mode == 'text':
            query_text = self.input_text.text().strip()
            if not query_text:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_text'))
                return None
            params['query_text'] = query_text
        
        return params
    
    def _init_search_state(self):
        """初始化搜索状态"""
        self.list_results.clear()
        self.txt_log.clear()
        self.progress_bar.setValue(0)
        
        # 更新搜索按钮状态已在_on_search_toggle中完成
        pass
    
    def _start_search_worker(self, params):
        """启动搜索工作线程"""
        try:
            print("Creating SearchWorker instance...")
            self.search_worker = SearchWorker(
                search_engine=self.search_engine,
                video_paths=self.videos,
                mode=params['mode'],
                query_images=params.get('query_images'),
                query_text=params.get('query_text'),
                query_category=params.get('query_category'),
                score_threshold=params['score_threshold'],
                parent=self
            )
            
            print("Connecting worker signals...")
            # 连接工作线程信号
            self.search_worker.match_found.connect(self._on_match_found)
            self.search_worker.finished_search.connect(self._on_search_finished)
            self.search_worker.error.connect(self._on_search_error)
            self.search_worker.progress.connect(self._on_progress)
            self.search_worker.message.connect(self._on_message)
            
            print("Starting worker thread...")
            # 启动搜索
            self.search_worker.start()
            print(f"Worker thread started: {self.search_worker.isRunning()}")
        except Exception as e:
            print(f"Error in _start_search_worker: {e}")
            import traceback
            traceback.print_exc()
    
    def on_stop_search(self):
        """停止搜索"""
        if self.search_worker:
            print("on_stop_search method called")
            self.search_worker.stop()
            
            # 重置搜索工作线程引用
            self.search_worker = None
            print("Search worker stopped and reset to None")
            
            # 更新日志
            self.txt_log.append(f'<span style="color:gray;">{self._t("stop_search")}</span>')
            
            # 停止按钮旋转动画
            self._stop_button_spinner()
            
            # 启用搜索模式切换按钮
            self.rb_image.setEnabled(True)
            self.rb_category.setEnabled(True)
            
            # 直接更新搜索按钮状态
            try:
                self.btn_search.setText(self._t('search'))
                self.btn_search.setIcon(self.icons['search'])
            except Exception as e:
                print(f"Error updating button state: {e}")
    
    # -------------- 搜索结果处理 --------------
    def _on_match_found(self, video_path, timestamp_ms, score):
        """处理找到的匹配结果"""
        # 过滤低于阈值的结果
        threshold = self.slider.value() / 100.0
        
        if score < threshold:
            return
        
        try:
            # 获取视频缩略图
            thumb = self._get_video_thumbnail(video_path, timestamp_ms)
            
            # 创建结果卡片
            card = ResultCard(video_path=video_path, timestamp_ms=timestamp_ms, score=score, thumbnail=thumb)
            
            # 根据网格大小调整卡片大小
            grid_size = self.list_results.gridSize()
            card.setFixedWidth(grid_size.width())
            
            lw_item = QListWidgetItem()
            # 设置项目大小与卡片大小匹配
            item_height = max(150, grid_size.height())
            lw_item.setSizeHint(QSize(grid_size.width(), item_height))
            lw_item.setData(Qt.ItemDataRole.UserRole, (video_path, timestamp_ms))
            
            # 添加结果到列表
            self.list_results.addItem(lw_item)
            self.list_results.setItemWidget(lw_item, card)
            
            # 连接卡片点击事件
            card.clicked.connect(self.on_result_card_clicked)
            
            # 更新搜索结果数量显示
            self.lbl_results.setText(f"{self._t('results')} ({self.list_results.count()})")
        except Exception as e:
            # 失败时使用简单列表项作为回退
            item = QListWidgetItem()
            item.setText(f"{os.path.basename(video_path)} -- {self._t('match_at')} {format_ms(timestamp_ms)} (score: {score:.2f})")
            item.setData(Qt.ItemDataRole.UserRole, (video_path, timestamp_ms))
            self.list_results.addItem(item)
            
            # 更新搜索结果数量显示
            self.lbl_results.setText(f"{self._t('results')} ({self.list_results.count()})")
    
    def _on_search_finished(self):
        """搜索完成处理"""
        # 搜索完成后自动排序（默认按评分从高到低）
        self._sort_results('score', reverse=True)
        
        # 重置搜索状态（不重置结果数量显示）
        self.btn_search.setEnabled(True)
        self.search_worker = None
        self._stop_button_spinner()
        
        # 启用搜索模式切换按钮
        self.rb_image.setEnabled(True)
        self.rb_category.setEnabled(True)
        
        # 确保按钮文本恢复为"搜索"
        try:
            self.btn_search.setText(self._t('search'))
            self.btn_search.setIcon(self.icons['search'])
            print("Search button text reset to 'search'")
        except Exception as e:
            print(f"Error resetting search button: {e}")
        
        # 更新UI
        self.txt_log.append(f"{self._t('search_finished')}")
    
    def _on_search_error(self, error_msg):
        """搜索错误处理"""
        title = self._t('search_error_title') or 'Error'
        QMessageBox.warning(self, title, error_msg)
        self.txt_log.append(f"<span style=\"color:red;\">{error_msg}</span>")
    
    def _on_progress(self, info):
        """处理搜索进度"""
        try:
            if not isinstance(info, (list, tuple)):
                return
            
            kind = info[0]
            if kind == 'frame' and len(info) >= 4:
                processed = int(info[2])
                total_samples = int(info[3])
                if total_samples > 0:
                    pct = int((processed / float(total_samples)) * 100)
                    self.progress_bar.setValue(max(0, min(pct, 99)))
            elif kind == 'video' and len(info) >= 3:
                completed = int(info[1])
                total_videos = int(info[2])
                if total_videos > 0:
                    pct = int((completed / float(total_videos)) * 100)
                    self.progress_bar.setValue(max(0, min(pct, 100)))
        except Exception:
            pass
    
    def _on_message(self, msg):
        """处理搜索消息"""
        try:
            if isinstance(msg, (list, tuple)) and len(msg) == 2:
                key, params = msg
                
                # 优化不同类型消息的显示格式
                if key == 'downloading_model':
                    text = f"<span style=\"color:blue;\">{self._t('downloading_model')}</span>"
                elif key == 'searching_video':
                    text = f"<span style=\"color:green;\">{self._t('processing_video')}</span>: {params['name']} ({params['idx']}/{params['total']})"
                elif key == 'found_match':
                    # 使用翻译模板格式化内容
                    tpl = self._t('found_match')
                    text = tpl.format(**params)
                    text = f"<span style=\"color:green;\">{text}</span>"
                else:
                    # 其他类型消息使用默认格式
                    tpl = self._t(key) or ''
                    text = tpl.format(**params)
                    text = f"<span style=\"color:black;\">{text}</span>"
            else:
                # 字符串消息，尝试识别并优化
                msg_str = str(msg)
                if 'download' in msg_str.lower():
                    text = f"<span style=\"color:blue;\">{msg_str}</span>"
                elif 'process' in msg_str.lower() or 'search' in msg_str.lower():
                    text = f"<span style=\"color:green;\">{msg_str}</span>"
                else:
                    text = f"<span style=\"color:black;\">{msg_str}</span>"
            
            self.txt_log.append(text)
        except Exception as e:
            self.txt_log.append(f"<span style=\"color:red;\">Error processing message: {e}</span>")
    
    # -------------- 视频播放处理 --------------
    def on_video_double_clicked(self, item):
        """双击视频列表项播放视频"""
        path = item.toolTip()  # 从toolTip获取完整路径
        if os.path.exists(path) and self.player_widget:
            self.player_widget.play_file(path)
    
    def on_result_double_clicked(self, item):
        """双击搜索结果播放视频"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if data and self.player_widget:
            video_path, position_ms = data
            self.player_widget.play_at(video_path, position_ms)
            
    def on_result_card_clicked(self, video_path, timestamp_ms):
        """处理结果卡片的点击事件"""
        if video_path and timestamp_ms is not None and self.player_widget:
            self.player_widget.play(video_path, timestamp_ms)
    
    # -------------- 辅助方法 --------------
    def _t(self, key):
        """获取翻译文本"""
        return self.translations[self.lang].get(key, key)
    
    def _on_slider_changed(self, val):
        """滑块值变化处理"""
        self._update_score_label()
        self.config['score'] = val
        self._save_config()
    
    def on_check_in_clicked(self):
        """处理签到按钮点击事件"""
        try:
            success, message = self.user_service.check_in()
            if success:
                QMessageBox.information(self, "签到成功", message)
                # 更新用户信息
                self.update_user_info()
                
                # 如果有用户信息标签，更新显示
                if hasattr(self, 'user_info_label'):
                    # 获取最新的详细积分信息
                    points_success, points_info = self.user_service.get_current_points()
                    if points_success:
                        username = self.user_info.get('username', '用户')
                        current_points = points_info.get('current_points', 0)
                        self.user_info_label.setText(f"{username} - {current_points} 积分")
                    else:
                        # 如果获取详细积分失败，使用基本积分
                        username = self.user_info.get('username', '用户')
                        points = self.user_info.get('points', 0)
                        self.user_info_label.setText(f"{username} - {points} 积分")
            else:
                QMessageBox.warning(self, "签到失败", message)
        except Exception as e:
            QMessageBox.warning(self, "签到失败", f"签到过程中发生错误: {str(e)}")
    
    def update_user_button_text(self):
        if hasattr(self, 'user_button'):
            if self.is_logged_in and self.user_info:
                username = self.user_info.get('username', '用户')
                # 检查是否已经签到
                if hasattr(self, 'user_service') and self.user_service.is_logged_in():
                    if not self.user_service.is_checked_in_today():
                        username = f"🎁 {username}"
                self.user_button.setText(username)
            else:
                self.user_button.setText(self._t('login'))
    
    def _show_user_info_dialog(self):
        """显示用户信息对话框"""
        # 确保获取最新的用户信息
        self.update_user_info()
        
        # 创建并显示新的用户信息对话框
        from user_info_dialog import UserInfoDialog
        dialog = UserInfoDialog(self.user_info, self.user_service, self)
        
        # 连接信号
        dialog.logout_requested.connect(self._handle_logout_request)
        dialog.checkin_succeeded.connect(self._handle_checkin_succeeded)
        
        # 显示对话框
        dialog.exec()
        
    def _handle_logout_request(self):
        """处理来自用户信息对话框的登出请求"""
        self._on_logout()
        
    def _handle_checkin_succeeded(self):
        """处理来自用户信息对话框的签到成功事件"""
        # 更新用户信息
        self.update_user_info()
        
        # 更新标题栏用户按钮文本（包括礼物盒图标）
        self.update_user_button_text()
    
    def _on_user_button_clicked(self):
        """处理用户按钮点击事件"""
        if self.is_logged_in:
            # 显示用户信息窗口
            self._show_user_info_dialog()
        else:
            # 显示登录窗口
            from login_window import LoginWindow
            login_window = LoginWindow()
            if login_window.exec():
                # 登录成功后更新状态
                self.token = login_window.get_token()
                self.user_info = login_window.get_user_info()
                self.is_logged_in = True
                
                # 更新用户按钮文本
                self.update_user_button_text()
                
                # 更新用户服务的状态
                self.user_service.save_login_state(self.token, self.user_info)
    
    def _on_logout(self, dialog=None):
        """处理登出事件"""
        # 清除登录状态
        self.is_logged_in = False
        self.token = None
        self.user_info = None
        
        # 更新用户按钮文本
        self.update_user_button_text()
        
        # 更新用户服务的状态
        self.user_service.clear_login_state()
        
        # 如果提供了对话框参数，则关闭对话框
        if dialog:
            dialog.close()
    
    def update_user_info(self):
        """更新用户信息显示"""
        if self.is_logged_in:
            # 获取最新用户信息
            success, user_info = self.user_service.get_user_info()
            if success:
                self.user_info = user_info
                # 更新用户按钮文本
                self.update_user_button_text()
    
    def _get_video_thumbnail(self, path, timestamp_ms=0):
        """获取视频缩略图"""
        try:
            import cv2
            cap = cv2.VideoCapture(path)
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
            ok, frame = cap.read()
            cap.release()
            
            if ok and frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pix = QPixmap.fromImage(qimg).scaled(120, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                return pix
        except Exception:
            pass
        return None
    
    def _reset_search_state(self):
        """重置搜索状态"""
        print("_reset_search_state method called")
        self.btn_search.setEnabled(True)
        
        self.search_worker = None
        print("Search worker reset to None")
        self._stop_button_spinner()
        
        # 直接更新搜索按钮状态
        try:
            self.btn_search.setText(self._t('search'))
            self.btn_search.setIcon(self.icons['search'])
        except Exception as e:
            print(f"Error updating search button: {e}")
        
        # 重置搜索结果数量显示
        self.lbl_results.setText(self._t('results'))
    
    def _start_button_spinner(self):
        """开始搜索按钮的旋转动画"""
        try:
            # 保存原始按钮文本
            self._btn_search_orig_text = self.btn_search.text()
            # 保持按钮可用，以便用户可以点击停止搜索
            self.btn_search.setEnabled(True)
            
            if self._spinner_timer is None:
                self._spinner_timer = QTimer(self)
                self._spinner_timer.setInterval(100)
                self._spinner_timer.timeout.connect(self._update_spinner)
                self._spinner_timer.start()
                print("Spinner timer started")
        except Exception as e:
            print(f"Error starting button spinner: {e}")
    
    def _stop_button_spinner(self):
        """停止搜索按钮的旋转动画"""
        try:
            if self._spinner_timer:
                self._spinner_timer.stop()
                self._spinner_timer.deleteLater()
                self._spinner_timer = None
            
            # 确保按钮文本重置为原始文本
            if hasattr(self, '_btn_search_orig_text'):
                self.btn_search.setText(self._btn_search_orig_text)
            else:
                # 如果原始文本未保存，直接设置为"搜索"
                self.btn_search.setText(self._t('search'))
                self.btn_search.setIcon(self.icons['search'])
            
            self.btn_search.setEnabled(True)
        except Exception:
            pass
    
    def _update_spinner(self):
        """更新旋转动画"""
        try:
            self._spinner_idx = (self._spinner_idx + 1) % len(self._spinner_chars)
            self.btn_search.setText(f"{self._spinner_chars[self._spinner_idx]} {self._t('stop_search')}")
            # 确保按钮保持可用状态
            self.btn_search.setEnabled(True)
        except Exception as e:
            print(f"Error updating spinner: {e}")
            pass
    
    def _load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {'score': 85}
    
    def _save_config(self):
        """保存配置"""
        try:
            parent = os.path.dirname(self.config_path)
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f)
        except Exception:
            pass
    
    def _init_search_state(self):
        """初始化搜索状态"""
        self.list_results.clear()
        self.txt_log.clear()
        self.progress_bar.setValue(0)
        
        try:
            #self.btn_search.set_accent('#FF5722')
            self.btn_search.setText(self._t('stop_search'))
            self.btn_search.set_loading(True)
        except Exception:
            pass
    
    def _prepare_search_params(self, mode):
        """准备搜索参数"""
        params = {
            'mode': mode,
            'video_paths': self.videos,
            'score_threshold': self.slider.value()/100.0
        }
        
        if mode == 'image':
            params['query_images'] = self.images
        elif mode == 'category':
            query_category = self.combo_category.currentText().strip()
            if not query_category:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_category'))
                return None
            # 将用户选择的类别转换为英文，因为模型只支持英文
            english_category = translate_category(query_category, 'en')
            params['query_category'] = english_category
        elif mode == 'text':
            query_text = self.input_text.text().strip()
            if not query_text:
                QMessageBox.warning(self, self._t('no_videos'), self._t('need_text'))
                return None
            params['query_text'] = query_text
        
        return params
    
    # -------------- 窗口事件处理 --------------
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        # 保存配置
        try:
            self.config['score'] = int(self.slider.value())
            self._save_config()
        except Exception:
            pass
        
        # 停止搜索工作线程
        try:
            if self.search_worker:
                self.search_worker.stop()
                if self.search_worker.isRunning():
                    self.search_worker.wait(3000)
        except Exception:
            pass
        
        # 停止播放器
        try:
            if self.player_widget:
                self.player_widget.player.stop()
                self.player_widget.player.setSource(QUrl())
        except Exception:
            pass
        
        super().closeEvent(event)

def main():
    """应用入口"""
    print("启动应用程序...")
    # 启用高DPI支持（针对PySide6 6.x版本的最佳实践）
    # 在PySide6 6.x中，高DPI缩放和高DPI像素图已经是默认启用的
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    print("创建QApplication实例成功")
    
    # 应用样式
    _apply_styles(app)
    print("应用样式成功")
    
    # 检查是否已登录
    user_service = UserService()
    
    if user_service.is_logged_in():
        # 使用已保存的令牌和用户信息
        token = user_service.token
        user_info = user_service.user_info
    else:
        # 未登录状态，使用None
        token = None
        user_info = None
    
    # 创建并显示主窗口
    window = VideoSearchApp(token=token, user_info=user_info)
    print("创建主窗口实例成功")
    window.show()
    print("显示主窗口成功")
    
    # 设置初始分屏大小
    _set_initial_splitter_sizes(window)
    print("设置初始分屏大小成功")
    
    # 运行应用
    print("开始运行应用程序事件循环...")
    sys.exit(app.exec())

def _apply_styles(app):
    """应用样式"""
    # 尝试应用qt-material主题
    try:
        from qt_material import apply_stylesheet
        apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True)
    except ImportError:
        pass
    
    # 加载自定义Fluent样式
    try:
        qss_path = os.path.join(os.path.dirname(__file__), 'styles', 'fluent_simple.qss')
        if os.path.exists(qss_path):
            with open(qss_path, 'r', encoding='utf-8') as f:
                qss_content = f.read()
                # 尝试应用样式表并捕获详细错误
                try:
                    app.setStyleSheet(qss_content)
                    print(f"成功加载样式表: {qss_path}")
                except Exception as e:
                    print(f"应用样式表失败: {e}")
                    import traceback
                    traceback.print_exc()
    except Exception as e:
        print(f"读取样式表文件失败: {e}")

def _set_initial_splitter_sizes(window):
    """设置初始分屏大小"""
    try:
        total_w = window.width() or 1000
        window.splitter.setSizes([int(total_w*0.25), int(total_w*0.5), int(total_w*0.25)])
    except Exception:
        try:
            window.splitter.setSizes([250, 500, 250])
        except Exception:
            pass

if __name__ == "__main__":
    main()


