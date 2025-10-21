@echo off
REM Production Deployment Script for IntelliSFIA with Ollama (Windows)
REM ==================================================================

echo 🚀 IntelliSFIA Production Deployment with Ollama
echo =================================================

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Stop existing containers
echo 🛑 Stopping existing containers...
docker-compose -f docker-compose.prod-ollama.yml down 2>nul

REM Ask about cleaning up
set /p cleanup="🗑️  Remove old Docker images? (y/N): "
if /i "%cleanup%"=="y" (
    echo 🗑️  Removing old images...
    docker system prune -f
    docker volume prune -f
)

REM Build and start services
echo 🔨 Building and starting services...
docker-compose -f docker-compose.prod-ollama.yml up --build -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)

REM Wait for services
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

echo.
echo 🌐 Access Points:
echo =================
echo • Frontend:      http://localhost:3000
echo • API:           http://localhost:8000
echo • API Docs:      http://localhost:8000/docs
echo • Ollama API:    http://localhost:11434
echo • Nginx Proxy:   http://localhost:80

echo.
echo 🧪 Running tests...
python test_production.py

echo.
echo 🔧 Management Commands:
echo ======================
echo • View logs:       docker-compose -f docker-compose.prod-ollama.yml logs -f
echo • Stop services:   docker-compose -f docker-compose.prod-ollama.yml down
echo • Restart:         docker-compose -f docker-compose.prod-ollama.yml restart

echo.
echo ✅ Deployment Complete!
echo.
echo 💡 Note: Model downloads may take some time on first run.
echo    Check progress with: docker logs intellisfia-model-init

pause