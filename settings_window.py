import requests
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QWidget, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, Signal
from config import API_BASE_URL, APP_ID

class VersionCheckThread(QThread):
    version_checked = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.app_id = APP_ID
        self._stop_flag = False
        self.session = requests.Session()  # 使用会话以方便关闭

    def stop(self):
        """停止线程执行"""
        self._stop_flag = True
        # 关闭会话以终止可能的网络请求
        self.session.close()
        self.quit()

    def run(self):
        try:
            if self._stop_flag:
                return
                
            url = f"{API_BASE_URL}/version/{self.app_id}/latest"
            response = self.session.get(url, timeout=5)  # 添加超时
            
            if self._stop_flag:
                return
                
            if response.status_code == 200:
                self.version_checked.emit(response.json())
            else:
                self.error_occurred.emit(f"请求失败: {response.status_code}")
        except requests.exceptions.RequestException as e:
            if not self._stop_flag:  # 只有在非停止状态下才报告错误
                self.error_occurred.emit(f"网络错误: {str(e)}")
        except Exception as e:
            if not self._stop_flag:  # 只有在非停止状态下才报告错误
                self.error_occurred.emit(f"未知错误: {str(e)}")
        finally:
            self.session.close()

class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.current_version = "1.0.0"
        self.version_thread = None

        self.setup_ui()
        self.setup_connections()
        self.load_data()

    def setup_ui(self):
        self.setWindowTitle("设置")
        self.setFixedSize(400, 300)
        self.setModal(True)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # 联系我页面
        self.contact_page = QWidget()
        self.contact_layout = QVBoxLayout()
        self.contact_page.setLayout(self.contact_layout)

        self.qrcode_label = QLabel()
        self.qrcode_label.setAlignment(Qt.AlignCenter)
        self.contact_layout.addWidget(self.qrcode_label)

        self.contact_text = QLabel("关注我们，不迷路")
        self.contact_text.setAlignment(Qt.AlignCenter)
        self.contact_text.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.contact_layout.addWidget(self.contact_text)

        # 关于页面
        self.about_page = QWidget()
        self.about_layout = QVBoxLayout()
        self.about_page.setLayout(self.about_layout)

        self.current_version_label = QLabel()
        self.current_version_label.setAlignment(Qt.AlignCenter)
        self.current_version_label.setStyleSheet("font-size: 14px;")
        self.about_layout.addWidget(self.current_version_label)

        self.latest_version_label = QLabel()
        self.latest_version_label.setAlignment(Qt.AlignCenter)
        self.latest_version_label.setStyleSheet("font-size: 14px; color: #0078d4;")
        self.about_layout.addWidget(self.latest_version_label)

        self.version_description_label = QLabel()
        self.version_description_label.setAlignment(Qt.AlignCenter)
        self.version_description_label.setWordWrap(True)
        self.version_description_label.setStyleSheet("font-size: 12px; color: #666;")
        self.about_layout.addWidget(self.version_description_label)

        # 添加标签页
        self.tab_widget.addTab(self.contact_page, "联系我")
        self.tab_widget.addTab(self.about_page, "关于")

        # 设置当前版本
        self.current_version_label.setText(f"当前版本: {self.current_version}")

    def setup_connections(self):
        pass

    def load_data(self):
        # 加载二维码
        self.qrcode_label.setPixmap(QPixmap(":/icons/resources/code.jpg").scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # 检查最新版本
        self.check_latest_version()

    def check_latest_version(self):
        self.version_thread = VersionCheckThread()
        self.version_thread.version_checked.connect(self.on_version_checked)
        self.version_thread.error_occurred.connect(self.on_version_check_error)
        self.version_thread.start()

    def on_version_checked(self, version_data):
        latest_version = version_data.get("version", "未知")
        version_description = version_data.get("version_description", "")

        self.latest_version_label.setText(f"最新版本: {latest_version}")
        if version_description:
            self.version_description_label.setText(version_description)

    def on_version_check_error(self, error_msg):
        self.latest_version_label.setText(f"最新版本: 检查失败")
        self.version_description_label.setText(error_msg)

    def closeEvent(self, event):
        """窗口关闭事件处理，确保线程被正确终止"""
        if hasattr(self, 'version_thread') and self.version_thread is not None and self.version_thread.isRunning():
            self.version_thread.stop()
            self.version_thread.wait(2000)  # 等待最多2秒
        event.accept()
