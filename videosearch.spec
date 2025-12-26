# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 定义资源文件和目录
datas = [
    ('resources', 'resources'),
    ('styles', 'styles'),
    ('widgets', 'widgets'),
    ('yolov8n.pt', '.'),
]

# 定义要包含的Python模块
hiddenimports = [
    'PySide6.QtMultimediaWidgets',
    'PySide6.QtMultimedia',
    'cv2',
    'requests',
    'qt_material',
]

# 主程序配置
a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 收集所有资源并生成可执行文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoSearch',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 暂时设置为True以便调试
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # 设置程序图标
    icon='resources/logo.png',
)

# 生成目录模式的可执行文件
dist = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoSearch',
)
