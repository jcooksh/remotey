@echo off
REM Remotey - one-click: expose this Windows machine's SSH over the internet.
REM Double-click this file. It self-elevates (admin needed first run to install sshd).

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator access...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0tunnel_host.ps1"
