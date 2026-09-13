@echo off
setlocal EnableExtensions
title boo-lab setup
cd /d "%~dp0"

set "METAL=C:\Users\RIGGUSPIG\Desktop\god-tier-metal"
set "LAB=%METAL%\tools\boo-lab"
set "FLAC=%METAL%\reference\audio-corpus\born_of_osiris"
set "GP=%METAL%\reference\gp-tabs"

echo === boo-lab ===
echo LAB   %LAB%
echo FLAC  %FLAC%
echo GP    %GP%

if not exist "%METAL%" (
  echo Missing %METAL%
  pause & exit /b 1
)
if not exist "%FLAC%" (
  echo Missing FLACs: %FLAC%
  pause & exit /b 1
)

if not exist "%LAB%" mkdir "%LAB%"

where git >nul 2>&1
if not errorlevel 1 (
  if exist "%LAB%\.git" (
    echo Pulling boo-lab...
    git -C "%LAB%" pull --ff-only
  ) else if exist "%~dp0.git" (
    echo This folder is the repo.
  )
) else (
  echo git not on PATH — skip pull. Copy this repo into %LAB% if needed.
)

if exist "%~dp0pyproject.toml" if /I not "%~dp0"=="%LAB%\" (
  echo Syncing files from this folder into tools\boo-lab
  xcopy /E /I /Y "%~dp0src" "%LAB%\src" >nul
  copy /Y "%~dp0pyproject.toml" "%LAB%\pyproject.toml" >nul
  if exist "%~dp0data\map.csv" (
    if not exist "%LAB%\data" mkdir "%LAB%\data"
    copy /Y "%~dp0data\map.csv" "%LAB%\data\map.csv" >nul
  )
)

(
  echo BOO_FLAC_ROOT=%FLAC%
  echo BOO_GP_ROOT=%GP%
) > "%LAB%\.env"

where py >nul 2>&1 && (set "PY=py -3") || (set "PY=python")
if not exist "%LAB%\.venv\Scripts\python.exe" (
  echo Creating venv...
  %PY% -m venv "%LAB%\.venv" || (echo Need Python 3.11+ & pause & exit /b 1)
)

call "%LAB%\.venv\Scripts\activate.bat"
python -m pip install -q -U pip
python -m pip install -q -e "%LAB%"
echo Installing librosa + demucs (first time is slow)...
python -m pip install -q "librosa" "soundfile" "numpy<2" "demucs"

echo.
echo http://127.0.0.1:8765
echo First Guess on a song can take several minutes (Demucs). After that it is cached.
echo Ctrl+F5 in the browser after this starts.
echo.
start "" http://127.0.0.1:8765
boo-lab studio --port 8765
pause
