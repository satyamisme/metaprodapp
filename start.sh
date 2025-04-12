#!/bin/bash
echo "Activating virtual environment..."

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run setup_venv.sh first."
    exit 1
fi

source venv/bin/activate

echo "Running meta0.1.py..."
python3 meta0.1.py