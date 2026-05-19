# DeepSeek Docs Crawler - One-click run
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Installing dependencies..." -ForegroundColor Cyan
& "C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe" -m pip install -q requests beautifulsoup4 markdownify

Write-Host "Running crawler..." -ForegroundColor Cyan
& "C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe" crawl_deepseek_docs.py

Write-Host "`nDone. Check output/ folder for results." -ForegroundColor Green
