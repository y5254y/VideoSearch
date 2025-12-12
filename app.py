# -*- coding: utf-8 -*-
import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QHBoxLayout, QVBoxLayout,
    QLineEdit, QComboBox, QMessageBox, QSizePolicy, QSplitter,
    QRadioButton, QButtonGroup, QSlider, QProgressBar, QTextBrowser, QListView
)
from PySide6.QtGui import QPixmap, QImage, QIcon, QAction, QPainter, QPolygon, QColor
from PySide6.QtCore import QPoint
from PySide6.QtCore import Qt, QUrl, QSize, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

# 导入自定义组件
from player_widget import PlayerWidget
from main_ui import Ui_MainWindow
from widgets.result_card import ResultCard

# 导入搜索和工具模块
from search import AISearchEngine, format_ms
from translations import TRANSLATIONS
from search_worker import SearchWorker

# 确保资源文件被加载
try:
    import resources_rc
except Exception:
    pass

class VideoSearchApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 设置窗口初始大小为屏幕的3/4
        screen_geometry = QApplication.primaryScreen().geometry()
        width = int(screen_geometry.width() * 3 / 4)
        height = int(screen_geometry.height() * 3 / 4)
        self.resize(width, height)
        
        # 允许窗口大小调整
        self.setMinimumSize(800, 600)
        
        # 隐藏默认标题栏，使用自定义标题栏
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
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
        self.title_bar.layout().insertWidget(1, self.lang_combo)
        
        # 样式已移至QSS文件中
        
        # 搜索模式选择
        self.rb_image.setChecked(True)
        
        # 滑块设置
        self.slider.setRange(0, 100)
        self.slider.setTickInterval(5)
        
        # 分类选择框设置为可编辑
        self.combo_category.setEditable(True)
        
        # 移除了清除按钮以简化界面
        
        # 设置列表视图为图标模式，支持缩略图显示
        self.list_videos.setViewMode(QListWidget.IconMode)
        self.list_videos.setIconSize(QSize(80, 60))
        self.list_videos.setResizeMode(QListWidget.Adjust)
        self.list_videos.setSpacing(12)
        
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
    
    def _create_custom_title_bar(self):
        """创建自定义标题栏"""
        # 创建标题栏容器
        self.title_bar = QWidget()
        self.title_bar.setObjectName("title_bar")
        
        # 设置标题栏高度
        self.title_bar.setFixedHeight(50)
        
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
    
    def _connect_signals(self):
        """连接UI信号和槽函数"""
        # 语言选择
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        
        # 搜索模式切换
        self.rb_image.toggled.connect(self.update_search_mode_ui)
        self.rb_category.toggled.connect(self.update_search_mode_ui)
        self.rb_text.toggled.connect(self.update_search_mode_ui)
        
        # 列表双击事件
        self.list_videos.itemDoubleClicked.connect(self.on_video_double_clicked)
        self.list_results.itemDoubleClicked.connect(self.on_result_double_clicked)
        
        # 按钮点击事件
        self.btn_select_videos.clicked.connect(self.select_videos)
        self.btn_select_images.clicked.connect(self.select_images)
        self.btn_search.clicked.connect(self._on_search_toggle)
        
        # 滑块值变化
        self.slider.valueChanged.connect(self._on_slider_changed)
    
    def _apply_initial_settings(self):
        """应用初始设置"""
        # 设置滑块初始值
        init_score = int(self.config.get('score', 85))
        self.slider.setValue(init_score)
        
        # 更新搜索模式UI
        self.update_search_mode_ui()
        
        # 应用初始语言
        self.change_language(0)
    
    # -------------- UI控制方法 --------------
    def update_search_mode_ui(self):
        """根据选择的搜索模式更新UI控件的可见性和可用性"""
        # 检查单选按钮状态
        image_mode = self.rb_image.isChecked()
        category_mode = self.rb_category.isChecked()
        text_mode = self.rb_text.isChecked()
        
        # 使用分组方式更新控件状态，提高代码可读性
        # 图像搜索相关控件
        image_controls = [self.btn_select_images, self.list_images, self.lbl_query_images]
        for control in image_controls:
            control.setEnabled(image_mode)
        
        # 分类搜索相关控件
        category_controls = [self.combo_category, self.lbl_select_category]
        for control in category_controls:
            control.setEnabled(category_mode)
        
        # 文本搜索相关控件
        text_controls = [self.input_text, self.lbl_text_query]
        for control in text_controls:
            control.setEnabled(text_mode)
        
        # Update mode hint
        mode = self._get_search_mode()
        mode_hints = {
            'image': self._t('mode_hint_image'),
            'category': self._t('mode_hint_category'),
            'text': self._t('mode_hint_text')
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
        
        # 更新播放器按钮文本
        if self.player_widget:
            try:
                self.player_widget.playButton.setText(self._t('play'))
                # self.player_widget.pauseButton.setText(self._t('pause'))
                self.player_widget.stopButton.setText(self._t('stop'))
            except Exception:
                pass
        
        # 更新标签文本
        self.lbl_selected_videos.setText(self._t('selected_videos'))
        self.lbl_query_images.setText(self._t('query_images'))
        self.lbl_select_category.setText(self._t('select_category'))
        self.lbl_text_query.setText(self._t('text_query'))
        self.lbl_results.setText(self._t('results'))
        
        # 更新语言选择组合框的工具提示
        self.lang_combo.setToolTip(self._t('language'))
        
        # 更新分类列表
        self.combo_category.clear()
        for c in self._t('categories'):
            self.combo_category.addItem(c)
        
        # 更新搜索模式标签
        self.rb_image.setText(self._t('search_mode_image'))
        self.rb_category.setText(self._t('search_mode_category'))
        self.rb_text.setText(self._t('search_mode_text'))
        
        # 更新分数标签
        self._update_score_label()
    
    def _update_score_label(self):
        """更新分数标签"""
        self.lbl_score.setText(f"{self._t('score_threshold')}: {self.slider.value()/100:.2f}")
    
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
                
                # 尝试从视频中提取缩略图
                try:
                    # 创建临时图像用于存储缩略图
                    thumbnail = QImage()
                    
                    # 使用QPixmap创建一个简单的视频图标作为备用
                    pixmap = QPixmap(80, 60)
                    pixmap.fill(QColor(41, 111, 246))  # 使用应用主题色
                    
                    # 在图标上绘制播放符号
                    painter = QPainter(pixmap)
                    painter.setBrush(QColor(255, 255, 255))  # 白色播放符号
                    painter.drawPolygon(
                        QPolygon([
                            QPoint(30, 20),
                            QPoint(55, 30),
                            QPoint(30, 40)
                        ])
                    )
                    painter.end()
                    
                    item = QListWidgetItem(QIcon(pixmap), filename)
                except Exception as e:
                    # 如果提取失败，使用默认图标
                    item = QListWidgetItem(filename)
                
                item.setToolTip(f)  # 鼠标悬停显示完整路径
                item.setTextAlignment(Qt.AlignCenter)
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
        elif self.rb_text.isChecked():
            return 'text'
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
            params['query_category'] = query_category
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
        # 重置搜索状态
        self._reset_search_state()
        
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
                tpl = self._t(key) or ''
                text = tpl.format(**params)
            else:
                text = str(msg)
            
            self.txt_log.append(f"<span style=\"color:black;\">{text}</span>")
        except Exception:
            self.txt_log.append(str(msg))
    
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
            params['query_category'] = query_category
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
    app = QApplication(sys.argv)
    
    # 应用样式
    _apply_styles(app)
    
    # 创建并显示主窗口
    window = VideoSearchApp()
    window.show()
    
    # 设置初始分屏大小
    _set_initial_splitter_sizes(window)
    
    # 运行应用
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


