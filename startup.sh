#!/bin/bash

# IntelliSFIA AI Framework Startup Script
# =======================================
# 
# This script starts the complete IntelliSFIA AI Framework:
# 1. FastAPI backend with CrewAI multi-agent system
# 2. React frontend with enhanced AI integration
# 3. Ollama service for local LLM processing

set -e  # Exit on any error

echo "🚀 Starting IntelliSFIA AI Framework..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python is not installed. Please install Python 3.8+ and try again.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js and try again.${NC}"
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama is not installed. Please install Ollama for local LLM support.${NC}"
    echo "   Visit: https://ollama.ai"
fi

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    if [[ $BACKEND_PID ]]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✓ Backend stopped${NC}"
    fi
    if [[ $FRONTEND_PID ]]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    fi
    exit 0
}

# Trap Ctrl+C to cleanup processes
trap cleanup SIGINT SIGTERM

echo -e "${BLUE}📦 Setting up Python environment...${NC}"

# Install Python dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "Installing core Python dependencies..."
    pip install fastapi uvicorn pydantic crewai rdflib sparqlwrapper python-multipart
fi

echo -e "${GREEN}✓ Python environment ready${NC}"

echo -e "${BLUE}📦 Setting up Node.js environment...${NC}"

# Navigate to frontend directory and install dependencies
if [ -d "sfia_ai_framework/frontend" ]; then
    cd sfia_ai_framework/frontend
    
    if [ -f "package.json" ]; then
        echo "Installing Node.js dependencies..."
        npm install
    else
        echo -e "${YELLOW}⚠️  package.json not found in frontend directory${NC}"
    fi
    
    cd ../..
else
    echo -e "${YELLOW}⚠️  Frontend directory not found${NC}"
fi

echo -e "${GREEN}✓ Node.js environment ready${NC}"

# Start Ollama service if available
if command -v ollama &> /dev/null; then
    echo -e "${BLUE}🤖 Starting Ollama service...${NC}"
    ollama serve &
    OLLAMA_PID=$!
    sleep 3
    
    # Pull DeepSeek model if not already available
    echo "Checking for DeepSeek model..."
    if ! ollama list | grep -q "deepseek-coder"; then
        echo "Pulling DeepSeek Coder model (this may take a while)..."
        ollama pull deepseek-coder:6.7b
    fi
    
    echo -e "${GREEN}✓ Ollama service ready${NC}"
fi

echo -e "${BLUE}🚀 Starting FastAPI Backend...${NC}"

# Start the FastAPI backend
if [ -f "intellisfia_ai_api.py" ]; then
    python intellisfia_ai_api.py &
    BACKEND_PID=$!
    echo -e "${GREEN}✓ Backend started on http://localhost:8000${NC}"
else
    echo -e "${RED}❌ intellisfia_ai_api.py not found${NC}"
    exit 1
fi

# Wait for backend to start
sleep 5

echo -e "${BLUE}🌐 Starting React Frontend...${NC}"

# Start the React frontend
if [ -d "sfia_ai_framework/frontend" ]; then
    cd sfia_ai_framework/frontend
    npm start &
    FRONTEND_PID=$!
    cd ../..
    echo -e "${GREEN}✓ Frontend started on http://localhost:3000${NC}"
else
    echo -e "${RED}❌ Frontend directory not found${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 IntelliSFIA AI Framework is now running!${NC}"
echo "============================================="
echo -e "📊 Frontend:      ${BLUE}http://localhost:3000${NC}"
echo -e "🔧 Backend API:   ${BLUE}http://localhost:8000${NC}"
echo -e "📚 API Docs:      ${BLUE}http://localhost:8000/docs${NC}"
if command -v ollama &> /dev/null; then
    echo -e "🤖 Ollama:        ${BLUE}http://localhost:11434${NC}"
fi
echo ""
echo -e "${YELLOW}Features Available:${NC}"
echo "• CrewAI Multi-Agent System"
echo "• SFIA Semantic Ontology (RDF/OWL)"
echo "• Conversation Memory"
echo "• Evidence Validation"
echo "• AI-Powered Assessments"
echo "• Real-time Chat Interface"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for background processes
wait