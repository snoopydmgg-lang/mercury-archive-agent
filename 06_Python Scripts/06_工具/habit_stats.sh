#!/bin/bash
# habit_stats - 查看习惯统计（Git Bash / WSL）
# 用法: habit_stats [习惯名]

PYTHON="/c/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe"
SCRIPT="$(dirname "$0")/habit_tracker.py"

"$PYTHON" "$SCRIPT" stats "$@"
