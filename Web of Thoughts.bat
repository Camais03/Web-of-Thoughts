@echo off

:: Read the OpenAI API key from config.json
for /f "usebackq tokens=2 delims=: " %%a in (config.json) do set OPENAI_API_KEY=%%a

:: Run the Flask app in the background
start "Web of Thoughts" python app.py

:: Wait for a few seconds to allow the Flask app to start up
ping -n 2 127.0.0.1 > nul

:: Open the web browser to localhost:5000
start "" http://localhost:5000