@echo off
echo Setting up Python virtual environment...

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not found in PATH. Please install Python and try again.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo Setup complete! Virtual environment is activated.
echo You can now run your script.

:: Uncomment the line below to automatically run your script after setup
:: python your_script_name.py

:: Keep the window open
pause