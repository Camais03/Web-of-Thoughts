@echo off

:: Install the required Python packages
pip install -r requirements.txt

:: Build the executable using PyInstaller
pyinstaller --onefile app.py

pause