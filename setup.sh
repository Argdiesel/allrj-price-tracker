#!/bin/bash

# This script automates the setup of a Python virtual environment and installs the necessary dependencies.

# Check if Python3 and pip are installed
if ! command -v python3 &> /dev/null || ! command -v pip3 &> /dev/null
then
    echo "Python3 and pip are required. Please install them to proceed."
    exit 1
fi

# Create a virtual environment
VENV_DIR="venv"
echo "Creating virtual environment in $VENV_DIR..."
python3 -m venv $VENV_DIR

# Activate the virtual environment
if [ "$OSTYPE" == "linux-gnu" ]; then
    # Linux
    source $VENV_DIR/bin/activate
elif [ "$OSTYPE" == "darwin" ]; then
    # macOS
    source $VENV_DIR/bin/activate
else
    echo "Unsupported operating system. Please activate the virtual environment manually."
    exit 1
fi

echo "Virtual environment activated. Installing dependencies..."

# Install requirements
pip install -r requirements.txt

echo "Setup complete! To activate the virtual environment later, run 'source $VENV_DIR/bin/activate'"