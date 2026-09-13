@echo off
call "C:\Users\RIGGUSPIG\Desktop\god-tier-metal\tools\boo-lab\.venv\Scripts\activate.bat"
echo Installing librosa + demucs (one time). Then Guess will cache drums.
python -m pip install "librosa" "soundfile" "numpy<2" "demucs"
python -c "import librosa, demucs; print('ok')"
pause
