@echo off
echo Starting Groundwater AI System...

:: Start the FastAPI Backend in a new window
echo Starting Backend API...
start cmd /k "venv\Scripts\activate && python backend\api.py"

:: Wait for a few seconds for the API to initialize
timeout /t 5 /nobreak > nul

:: Open the Frontend in the default browser
echo Opening Frontend...
start "" "frontend\index.html"

echo.
echo System launched! 
echo Keep the Backend window open while using the chat.
pause
