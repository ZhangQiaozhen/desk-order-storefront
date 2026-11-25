@echo off
cd /d "%~dp0"
python store\launch.py
if errorlevel 1 pause

