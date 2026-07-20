@echo off
chcp 65001 >nul
cd /d "%~dp0"
python hyper_helix.py
if errorlevel 1 pause
