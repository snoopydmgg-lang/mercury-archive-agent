@echo off
REM 习惯打卡快捷命令
REM 用法: habit_done.bat ^<习惯名^>
REM 示例: habit_done.bat 戒手机
REM       habit_done.bat 戒手机 --note 开会刷手机

set PYTHON=C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe
set SCRIPT=%~dp0habit_tracker.py

if "%1"=="" (
    echo 用法: habit_done.bat ^<习惯名^>
    exit /b 1
)

%PYTHON% "%SCRIPT%" log %*
