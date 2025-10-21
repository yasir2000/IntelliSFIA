@echo off
REM IntelliSFIA AI Framework Startup Script for Windows
REM ===================================================
REM 
REM This script starts the complete IntelliSFIA AI Framework:
REM 1. FastAPI backend with CrewAI multi-agent system
REM 2. React frontend with enhanced AI integration
REM 3. Ollama service for local LLM processing

setlocal enabledelayedexpansion

echo 🚀 Starting IntelliSFIA AI Framework...
echo ======================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js and try again.
    pause
    exit /b 1
)

REM Check if Ollama is installed
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama is not installed. Please install Ollama for local LLM support.
    echo    Visit: https://ollama.ai
)

echo 📦 Setting up Python environment...

REM Install Python dependencies
if exist requirements.txt (
    echo Installing Python dependencies...
    pip install -r requirements.txt
) else (
    echo Installing core Python dependencies...
    pip install fastapi uvicorn pydantic crewai rdflib sparqlwrapper python-multipart
)

echo ✓ Python environment ready

echo 📦 Setting up Node.js environment...

REM Navigate to frontend directory and install dependencies
if exist "sfia_ai_framework\frontend" (
    cd sfia_ai_framework\frontend
    
    if exist package.json (
        echo Installing Node.js dependencies...
        call npm install
    ) else (
        echo ⚠️  package.json not found in frontend directory
    )
    
    cd ..\..
) else (
    echo ⚠️  Frontend directory not found
)

echo ✓ Node.js environment ready

REM Start Ollama service if available
ollama --version >nul 2>&1
if not errorlevel 1 (
    echo 🤖 Starting Ollama service...
    start /B ollama serve
    timeout /t 3 /nobreak >nul
    
    REM Check for DeepSeek model
    echo Checking for DeepSeek model...
    ollama list | findstr "deepseek-coder" >nul 2>&1
    if errorlevel 1 (
        echo Pulling DeepSeek Coder model (this may take a while)...
        ollama pull deepseek-coder:6.7b
    )
    
    echo ✓ Ollama service ready
)

echo 🚀 Starting FastAPI Backend...

REM Start the FastAPI backend
if exist intellisfia_ai_api.py (
    start /B python intellisfia_ai_api.py
    echo ✓ Backend started on http://localhost:8000
) else (
    echo ❌ intellisfia_ai_api.py not found
    pause
    exit /b 1
)

REM Wait for backend to start
timeout /t 5 /nobreak >nul

echo 🌐 Starting React Frontend...

REM Start the React frontend
if exist "sfia_ai_framework\frontend" (
    cd sfia_ai_framework\frontend
    start /B npm start
    cd ..\..
    echo ✓ Frontend started on http://localhost:3000
) else (
    echo ❌ Frontend directory not found
    pause
    exit /b 1
)

echo.
echo 🎉 IntelliSFIA AI Framework is now running!
echo =============================================
echo 📊 Frontend:      http://localhost:3000
echo 🔧 Backend API:   http://localhost:8000
echo 📚 API Docs:      http://localhost:8000/docs
ollama --version >nul 2>&1
if not errorlevel 1 (
    echo 🤖 Ollama:        http://localhost:11434
)
echo.
echo Features Available:
echo • CrewAI Multi-Agent System
echo • SFIA Semantic Ontology (RDF/OWL)
echo • Conversation Memory
echo • Evidence Validation
echo • AI-Powered Assessments
echo • Real-time Chat Interface
echo.
echo Press any key to open the application in your browser...
pause >nul

REM Open the application in the default browser
start http://localhost:3000

echo.
echo Press any key to stop all services...
pause >nul

REM Stop services (simplified - in real scenario you'd track PIDs)
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM ollama.exe >nul 2>&1

echo Services stopped.
pause