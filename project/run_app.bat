@echo off
setlocal
cd /d "%~dp0.."
set PYTHONPATH=%CD%\src
python project\desktop_entry.py
endlocal
