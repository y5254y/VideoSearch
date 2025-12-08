@echo off
REM Helper to regenerate Python UI modules from .ui and .qrc files (Windows)
set UI_DIR=.
pyside6-uic %UI_DIR%\player.ui -o %UI_DIR%\player_widget_ui.py
pyside6-uic %UI_DIR%\main.ui -o %UI_DIR%\main_ui.py
REM If you use resources.qrc, uncomment below and adjust path
REM pyrcc6 %UI_DIR%\resources.qrc -o %UI_DIR%\resources_rc.py
echo UI build complete.
pause
