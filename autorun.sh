#!/bin/bash

echo "Setting up and running meta0.1.py..."

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Please install Python3."
    exit 1
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install selenium webdriver-manager

# Ensure script permissions
chmod +x "$0"

# Run meta0.1.py
echo "Running meta0.1.py..."
python3 meta0.1.py

# Deactivate venv
deactivate