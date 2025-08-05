@echo off
echo Fixing PowerShell ReadLine issues...

REM Remove PSReadLine module to force reset
powershell -Command "Remove-Module PSReadLine -Force -ErrorAction SilentlyContinue"

REM Clear PowerShell history that might be corrupted
del "%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" 2>nul

REM Reset PowerShell profile
powershell -Command "if (Test-Path $PROFILE) { Rename-Item $PROFILE ($PROFILE + '.backup.' + (Get-Date -Format 'yyyyMMdd')) }"

echo PowerShell reset complete. Try opening a new terminal in VS Code.
pause
