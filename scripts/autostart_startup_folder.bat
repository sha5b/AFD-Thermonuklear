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

set "REPO="
set "SCRIPT_REL=scripts\start_printer_fullscreen.ps1"

if exist "%USERPROFILE%\Documents\GitHub\AFD-Thermonuklear\%SCRIPT_REL%" set "REPO=%USERPROFILE%\Documents\GitHub\AFD-Thermonuklear"
if not defined REPO if exist "%USERPROFILE%\OneDrive\Documents\GitHub\AFD-Thermonuklear\%SCRIPT_REL%" set "REPO=%USERPROFILE%\OneDrive\Documents\GitHub\AFD-Thermonuklear"
if not defined REPO if exist "%USERPROFILE%\Documents\AFD-Thermonuklear\%SCRIPT_REL%" set "REPO=%USERPROFILE%\Documents\AFD-Thermonuklear"
if not defined REPO if exist "%USERPROFILE%\OneDrive\Documents\AFD-Thermonuklear\%SCRIPT_REL%" set "REPO=%USERPROFILE%\OneDrive\Documents\AFD-Thermonuklear"

if not defined REPO (
  echo ERROR: Cannot find AFD-Thermonuklear repo.
  echo Looked for:
  echo   %USERPROFILE%\Documents\GitHub\AFD-Thermonuklear\%SCRIPT_REL%
  echo   %USERPROFILE%\OneDrive\Documents\GitHub\AFD-Thermonuklear\%SCRIPT_REL%
  echo   %USERPROFILE%\Documents\AFD-Thermonuklear\%SCRIPT_REL%
  echo   %USERPROFILE%\OneDrive\Documents\AFD-Thermonuklear\%SCRIPT_REL%
  pause
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%REPO%\%SCRIPT_REL%"
