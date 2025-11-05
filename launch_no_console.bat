@echo off
REM NextAstroTarget - Launch without console window
REM This batch file runs the application using pythonw.exe to avoid showing the console

cd /d "%~dp0"
start "" pythonw main_pyside6.py
