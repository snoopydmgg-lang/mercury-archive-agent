# MiMo Docs Crawler - One-click run
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Installing dependencies..." -ForegroundColor Cyan
& "C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe" -m pip install -q playwright markdownify

Write-Host "Checking Playwright browsers..." -ForegroundColor Cyan
& "C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe" -m playwright install chromium --with-deps 2>&1 | Out-Null

Write-Host "Running crawler..." -ForegroundColor Cyan
& "C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe" crawl_mimo_docs.py

Write-Host "`nDone. Check output/ folder for results." -ForegroundColor Green
