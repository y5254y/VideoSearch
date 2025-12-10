#!/usr/bin/env bash
# Generate Python resources module from resources.qrc using pyside6-rcc
pyside6-rcc resources.qrc -o resources_rc.py
echo "Generated resources_rc.py"
