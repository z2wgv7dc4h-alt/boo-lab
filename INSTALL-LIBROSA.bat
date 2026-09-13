@echo off
call "C:\Users\RIGGUSPIG\Desktop\god-tier-metal\tools\boo-lab\.venv\Scripts\activate.bat"
python -m pip install "librosa" "soundfile" "numpy<2"
python -c "import librosa; print('librosa', librosa.__version__)"
pause
