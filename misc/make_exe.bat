del /q *.spec *.zip
rd /s /q dist build
pyinstaller --onefile -w -c ../k1921vkx_flasher.py
