@echo off
REM Context:
REM Windows Startup-folder launcher for AFD-Thermonuklear.
REM
REM Responsibilities:
REM - Start the printer controller on user logon (when placed in shell:startup).
REM - Launch via the PowerShell launcher (which can go fullscreen in Windows Terminal).
REM
REM IMPORTANT:
REM - Edit REPO to your repo folder.
REM - Then copy THIS .bat into: Win+R -> shell:startup

set "REPO=C:\Users\thermo\Documents\GitHub\AFD-Thermonuklear"

if not exist "%REPO%\scripts\start_printer_fullscreen.ps1" (
  echo ERROR: Cannot find "%REPO%\scripts\start_printer_fullscreen.ps1"
  echo Fix the REPO path in this .bat file.
  pause
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%REPO%\scripts\start_printer_fullscreen.ps1"
