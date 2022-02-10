#!/bin/sh
rm -rf build dist *.spec *.zip
wine C:/Python36-32/Scripts/pyinstaller.exe --onefile ../k1921vkx_flasher.py
zip -j k1921vkx_flasher_v$1_win.zip dist/k1921vkx_flasher.exe