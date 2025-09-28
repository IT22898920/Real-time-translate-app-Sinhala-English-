@echo off
echo Installing SpeechRecognition...
py -m pip install SpeechRecognition
echo.
echo Installation complete!
echo Running the application...
python realtime_translator.py
pause