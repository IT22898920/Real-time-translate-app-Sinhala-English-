#!/bin/bash

echo "Installing Real-time Voice Translator..."
echo "========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required. Current version: $python_version"
    exit 1
fi

echo "Python version: $python_version ✓"

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Platform-specific PyAudio installation
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing PyAudio for Linux..."
    sudo apt-get update
    sudo apt-get install -y python3-pyaudio portaudio19-dev
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing PyAudio for Mac..."
    brew install portaudio
    pip install pyaudio
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    echo "Installing PyAudio for Windows..."
    pip install pyaudio
fi

echo "========================================="
echo "Installation complete!"
echo "Run 'python realtime_translator.py' to start the application"