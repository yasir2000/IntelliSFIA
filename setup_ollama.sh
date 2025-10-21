#!/bin/bash
# IntelliSFIA + Ollama Setup Script
# =================================
# This script helps set up the complete environment for IntelliSFIA with local Ollama LLM integration

echo "🚀 IntelliSFIA + Ollama Integration Setup"
echo "======================================="

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install Ollama first:"
    echo "   Visit: https://ollama.ai"
    echo "   Or use: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo "✅ Ollama found: $(ollama --version)"

# Check if Ollama service is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "🔄 Starting Ollama service..."
    ollama serve &
    OLLAMA_PID=$!
    echo "⏳ Waiting for Ollama to start..."
    sleep 5
    
    if ! curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "❌ Failed to start Ollama service"
        exit 1
    fi
    echo "✅ Ollama service started (PID: $OLLAMA_PID)"
else
    echo "✅ Ollama service already running"
fi

# List available models
echo "📚 Available models:"
ollama list

# Download recommended models if not available
RECOMMENDED_MODELS=("llama3.1:8b" "llama3.1:13b" "codellama:7b")

for model in "${RECOMMENDED_MODELS[@]}"; do
    if ! ollama list | grep -q "$model"; then
        echo "📥 Would you like to download $model? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "⬇️ Downloading $model (this may take a while)..."
            ollama pull "$model"
            echo "✅ $model downloaded successfully"
        fi
    else
        echo "✅ $model already available"
    fi
done

# Install Python dependencies
if [ -f "requirements-ollama.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements-ollama.txt
    echo "✅ Dependencies installed"
fi

# Process SFIA data if needed
if [ ! -d "sfia_ai_framework/sfia_ai_framework/data/sfia9" ] || [ -z "$(ls -A sfia_ai_framework/sfia_ai_framework/data/sfia9 2>/dev/null)" ]; then
    echo "🔄 Processing SFIA 9 data..."
    python sfia_ai_framework/sfia_ai_framework/data/sfia9_data_processor.py
    echo "✅ SFIA data processed"
else
    echo "✅ SFIA data already processed"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "🚀 Ready to run the demo:"
echo "   python demo_ollama_integration.py"
echo ""
echo "📋 Quick test:"
echo "   curl http://localhost:11434/api/tags"
echo ""
echo "🛠️ Available models:"
ollama list
echo ""
echo "💡 Tips:"
echo "   • Use llama3.1:8b for balanced performance and quality"
echo "   • Use llama3.1:13b for better quality (requires more RAM)"
echo "   • Use codellama:7b for code-focused tasks"
echo ""
echo "🔧 Troubleshooting:"
echo "   • If Ollama fails: killall ollama && ollama serve"
echo "   • Check service: curl http://localhost:11434/api/tags"
echo "   • View logs: tail -f ~/.ollama/logs/server.log"