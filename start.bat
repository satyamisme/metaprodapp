@echo off
echo Activating virtual environment...

:: Check if venv exists
if not exist "venv" (
    echo Virtual environment not found. Please run setup_venv.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Run the script
echo Running meta0.1.py...
python meta0.1.py

:: Keep the window open
pause