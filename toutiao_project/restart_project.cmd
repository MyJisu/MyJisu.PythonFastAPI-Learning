@echo off
title Restart Project
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0restart_generic.ps1" -BackendRoot "%~dp0"
echo.
pause