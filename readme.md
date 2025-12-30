# VideoSearch - 本地视频内容搜索工具

<div align="center">
  <img src="resources/icon.png" alt="VideoSearch Logo" width="100">
  <p>一款基于AI的本地视频内容搜索工具，支持图像搜索和类别搜索</p>
  <p>
    <a href="#功能特性">功能特性</a> •
    <a href="#安装说明">安装说明</a> •
    <a href="#使用方法">使用方法</a> •
    <a href="#许可证">许可证</a> •
    <a href="#联系方式">联系方式</a>
  </p>
</div>

## 项目介绍

VideoSearch是一款本地视频内容搜索工具，利用先进的AI模型（CLIP和YOLO）帮助用户快速搜索本地视频中的特定内容。用户可以通过上传参考图像或选择类别，在视频库中找到相似的内容片段。

## 功能特性

### 🔍 搜索功能
- **图像搜索**：上传一张参考图像，在视频中找到相似的内容
- **类别搜索**：选择预设类别（如人、车、狗等），搜索相关内容
- **高分阈值过滤**：可调整分数阈值，过滤搜索结果
- **实时搜索进度显示**：可视化搜索进度和结果数量

### 📺 视频播放
- **智能定位播放**：点击搜索结果，自动跳转到对应时间点
- **流畅播放体验**：基于Qt多媒体框架，支持多种视频格式
- **播放控制**：支持播放、暂停、停止等基本操作

### 🌐 多语言支持
- 中文（简体）
- English
- 动态切换语言，无需重启

### 👤 用户系统
- 登录功能
- 每日签到
- 用户信息管理

### 🎨 其他特性
- 现代化UI设计
- 响应式布局，适配不同屏幕尺寸
- 自定义主题样式
- 清晰的搜索结果展示

## 技术栈

- **框架**：PySide6 (GUI)
- **AI模型**：PyTorch, CLIP, YOLOv8
- **开发语言**：Python 3.10+
- **打包工具**：PyInstaller

## 安装说明

### 选项1：使用预编译的EXE文件

1. 从[Releases](https://github.com/y5254y/VideoSearch/releases)页面下载最新的`VideoSearch.zip`
2. 解压到任意目录
3. 将模型文件放入同一目录：
   - `clip-vit-base-patch32` 文件夹
   - `yolov8n.pt` 文件
4. 双击 `VideoSearch.exe` 运行

### 选项2：从源码运行

#### 环境要求
- Python 3.10+
- Git

#### 安装步骤

1. 克隆仓库
   ```bash
git clone https://github.com/y5254y/VideoSearch.git
cd VideoSearch
   ```

2. 安装依赖
   ```bash
pip install -r requirements.txt
   ```

3. 下载模型文件（可选，如果没有提前下载，运行过程中会自动下载）
   - 下载CLIP模型：[clip-vit-base-patch32](https://huggingface.co/openai/clip-vit-base-patch32)
   - 下载YOLOv8模型：[yolov8n.pt](https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt)
   - 将模型文件放入项目根目录

4. 运行应用
   ```bash
python app.py
   ```

## 使用方法

### 1. 准备视频

- 点击「选择视频」按钮，选择一个或多个要搜索的视频文件
- 支持的视频格式：MP4, AVI, MOV, MKV等

### 2. 选择搜索模式

#### 图像搜索模式
- 选择「图像搜索」单选按钮
- 点击「选择图像」按钮，上传一张参考图像
- 点击「搜索」按钮开始搜索

#### 类别搜索模式
- 选择「类别搜索」单选按钮
- 从下拉列表中选择一个类别
- 点击「搜索」按钮开始搜索

### 3. 查看搜索结果

- 搜索结果将以卡片形式显示，包含：
  - 视频缩略图
  - 匹配时间点
  - 匹配分数
- 点击卡片可在播放器中观看对应片段
- 支持按分数或时间排序

### 4. 调整搜索参数

- **分数阈值**：拖动滑块调整匹配分数的最低阈值
- **语言切换**：在右上角选择界面语言

## 模型文件说明

本项目依赖两个AI模型：

1. **CLIP模型** (`clip-vit-base-patch32`)
   - 用途：图像与文本的相似度匹配
   - 大小：约600MB
   - 下载地址：[Hugging Face](https://huggingface.co/openai/clip-vit-base-patch32)

2. **YOLOv8模型** (`yolov8n.pt`)
   - 用途：目标检测和类别识别
   - 大小：约6.5MB
   - 下载地址：[Ultralytics](https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt)

### 模型放置位置

- 直接将模型文件放在与`VideoSearch.exe`或`app.py`同一目录下
- 程序将自动从当前目录加载模型

## 打包说明

### 使用PyInstaller打包

1. 安装PyInstaller
   ```bash
pip install pyinstaller
   ```

2. 执行打包命令
   ```bash
pyinstaller videosearch.spec
   ```

3. 打包后文件
   - 生成的EXE文件位于`dist`目录
   - 模型文件不会被打包到EXE中，需单独提供

### 分发说明

- 可将`VideoSearch.exe`与模型文件一起打包分发
- 确保用户了解模型文件的正确放置位置

## 许可证

### 主要许可证

本项目采用**MIT许可证**开源，但有以下附加条款：

1. **非商业用途**：个人用户可自由修改和使用本软件
2. **商业用途**：需获得作者授权
3. **保留标识信息**：
   - 任何基于本项目修改的版本，在打包发布给他人使用时，**不得移除**：
     - 软件界面上的二维码
     - QQ群信息（451636267）
     - 用户登录功能
     - 版权标识
   - 这些信息是作者的推广渠道，修改版本必须保留

### 第三方库许可证

- PySide6：LGPL v3
- PyTorch：BSD-3-Clause
- CLIP：MIT License
- YOLOv8：AGPL-3.0 License

## 贡献指南

欢迎对本项目进行贡献！贡献前请阅读以下指南：

1. Fork本仓库
2. 创建新的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

### 贡献规范

- 遵循现有的代码风格
- 添加适当的注释
- 确保代码可以正常运行
- 不要修改许可证相关内容
- 保留所有标识信息

## 联系方式

- **作者**：VideoSearch开发团队
- **QQ群**：451636267
- **公众号**：[视频搜索工具]
- **GitHub**：[https://github.com/yourusername/VideoSearch](https://github.com/yourusername/VideoSearch)

## 常见问题

### Q: 为什么搜索速度很慢？
A: 搜索速度取决于视频长度和计算机性能。建议：
- 缩短视频长度
- 提高分数阈值
- 使用性能更好的计算机

### Q: 为什么找不到匹配结果？
A: 可能原因：
- 参考图像与视频内容差异过大
- 分数阈值设置过高
- 模型文件未正确放置

### Q: 支持哪些视频格式？
A: 理论上支持所有Qt多媒体框架支持的格式，包括：
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)

### Q: 可以在Mac或Linux上运行吗？
A: 本项目基于跨平台框架开发，但目前主要针对Windows优化。
可以尝试从源码运行，可能需要调整一些依赖和配置。

## 更新日志

### v1.0.0 (2025-12-30)
- 初始版本发布
- 支持图像搜索和类别搜索
- 中英文界面切换
- 用户登录系统
- 智能视频播放定位

## 致谢

感谢以下开源项目的支持：

- [PySide6](https://www.qt.io/qt-for-python)
- [PyTorch](https://pytorch.org/)
- [CLIP](https://github.com/openai/CLIP)
- [YOLOv8](https://github.com/ultralytics/ultralytics)
- [PyInstaller](https://pyinstaller.org/)

---

<div align="center">
  <p>🎬 享受使用VideoSearch搜索视频内容的乐趣！</p>
  <p>📢 欢迎加入QQ群交流：451636267</p>
</div>