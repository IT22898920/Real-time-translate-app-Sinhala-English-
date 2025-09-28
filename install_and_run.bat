@echo off
echo ========================================
echo Real-time Voice Translator Setup
echo ========================================
echo.

echo Installing required packages...
echo.

REM Install SpeechRecognition
echo Installing SpeechRecognition...
py -m pip install SpeechRecognition

REM Try to install PyAudio
echo.
echo Installing PyAudio (this might fail on some systems)...
py -m pip install pyaudio

REM If PyAudio fails, provide instructions
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo PyAudio installation failed!
    echo.
    echo For Windows, you can:
    echo 1. Download the .whl file from:
    echo    https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    echo 2. Install it with: py -m pip install downloaded_file.whl
    echo.
    echo The app will still work with text input mode!
    echo ========================================
    echo.
)

echo.
echo Starting the application...
echo.
py voice_translator.py

pause