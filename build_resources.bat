@echo off
REM Build Qt resource file into Python module using rcc
setlocal
if not exist "%~dp0\pyside6-rcc.exe" (
    echo Please ensure pyside6-rcc is in PATH or adjust path in script.
)
REM Generate resources_rc.py
pyside6-rcc resources.qrc -o resources_rc.py
endlocal
