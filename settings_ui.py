from PySide6.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class SettingsUI(QDialog):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_tabs()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle("设置")
        self.setFixedSize(400, 300)
        self.setModal(True)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

    def setup_tabs(self):
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

    def setup_connections(self):
        pass

    def set_qrcode_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.qrcode_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def set_current_version(self, version):
        self.current_version_label.setText(f"当前版本: {version}")

    def set_latest_version(self, version):
        self.latest_version_label.setText(f"最新版本: {version}")

    def set_version_description(self, description):
        self.version_description_label.setText(description)
