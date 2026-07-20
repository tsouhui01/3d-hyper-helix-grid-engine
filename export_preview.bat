@echo off
chcp 65001 >nul
cd /d "%~dp0"
python hyper_helix.py --export-svg preview.svg
if errorlevel 1 pause
