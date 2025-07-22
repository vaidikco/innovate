@echo off
echo.
echo Configuring environment to run Innovate CLI
echo Hang on tight!
echo Installing dependencies from Python...
pip install -q -U google-genai  
pip install fade
pip install python-dotenv
cls

echo Welcome to Innovate CLI Configuration!
echo This script will help you set up the necessary configurations for Innovate CLI, for a smooth experience.
echo To begin with, enter your Gemini API key. This can be obtained from Google AI Studio or via Google Cloud Console.
echo.

:: Prompt for API key
set /p API_KEY=Enter your Gemini API Key: 

:: Create .env file with the entered key
(
    echo GEMINI_API_KEY=%API_KEY%
) > .env

:: Add current directory to USER PATH (no admin required)
set "CURRENT_DIR=%cd%"

:: Check if it's already in PATH
echo Checking if current directory is already in user PATH...
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "OLD_PATH=%%b"

echo %OLD_PATH% | find /I "%CURRENT_DIR%" >nul
if %errorlevel%==0 (
    echo Current directory is already in user PATH.
) else (
    echo Adding %CURRENT_DIR% to user PATH...
    set "NEW_PATH=%OLD_PATH%;%CURRENT_DIR%"
    reg add "HKCU\Environment" /v Path /t REG_EXPAND_SZ /d "%NEW_PATH%" /f
    echo Done! You may need to restart your terminal or log out and back in for changes to apply.
)

echo.
echo Innovate CLI has now been successfully configured!
echo You can run it by typing 'innovate' in your terminal.
pause
