@echo off
REM Clash for Windows CLI Launcher
REM Usage: clash.bat <command>

set SCRIPT_DIR=%~dp0
set PYTHON=C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe

%PYTHON% "%SCRIPT_DIR%clash_cli.py" %*
