#!/bin/bash
# Small helper to regenerate Python UI modules from .ui and .qrc files
set -e

# Paths
UI_DIR="."
# regenerate player_widget_ui.py and main_ui.py from .ui files
pyside6-uic "$UI_DIR/player.ui" -o "$UI_DIR/player_widget_ui.py"
pyside6-uic "$UI_DIR/main.ui" -o "$UI_DIR/main_ui.py"

# If you use resources.qrc, uncomment below and adjust path
# pyrcc6 "$UI_DIR/resources.qrc" -o "$UI_DIR/resources_rc.py"

echo "UI build complete."
