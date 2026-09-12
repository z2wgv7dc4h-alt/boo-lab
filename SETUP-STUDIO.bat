@echo off
setlocal EnableExtensions
title boo-lab studio
cd /d "%~dp0"

if exist "tools\boo-lab\pyproject.toml" (
  cd /d "%~dp0tools\boo-lab"
) else if exist "pyproject.toml" (
  cd /d "%~dp0"
) else (
  echo Put this bat in Desktop\god-tier-metal  OR  in tools\boo-lab
  echo Missing pyproject.toml
  pause
  exit /b 1
)

set "ROOT=%CD%"
set "FLAC=C:\Users\RIGGUSPIG\Desktop\god-tier-metal\reference\audio-corpus\born_of_osiris"
set "GP=C:\Users\RIGGUSPIG\Desktop\god-tier-metal\reference\gp-tabs"

if not exist "%FLAC%" (
  echo FLAC folder missing:
  echo   %FLAC%
  pause
  exit /b 1
)

if not exist "%GP%" (
  mkdir "%GP%" 2>nul
  echo.
  echo Unzip your tab archive into:
  echo   %GP%
  echo Then run this bat again.
  explorer "%GP%"
  pause
  exit /b 1
)

(
  echo BOO_FLAC_ROOT=%FLAC%
  echo BOO_GP_ROOT=%GP%
) > "%ROOT%\.env"

if not exist "%ROOT%\data" mkdir "%ROOT%\data"
if exist "%~dp0data\map.csv" copy /Y "%~dp0data\map.csv" "%ROOT%\data\map.csv" >nul

where py >nul 2>&1 && (set "PY=py -3") || (set "PY=python")
if not exist "%ROOT%\.venv\Scripts\python.exe" (
  echo Creating venv...
  %PY% -m venv "%ROOT%\.venv"
  if errorlevel 1 (
    echo Need Python 3.11+ on PATH
    pause
    exit /b 1
  )
)
call "%ROOT%\.venv\Scripts\activate.bat"
python -m pip install -q -U pip
python -m pip install -q -e "%ROOT%"
if errorlevel 1 (
  echo pip install failed
  pause
  exit /b 1
)

echo.
echo UI  http://127.0.0.1:8765
echo 1 riff  2 hook  3 breakdown  4 solo  S save  N next
echo.
start "" http://127.0.0.1:8765
boo-lab studio --port 8765
pause
