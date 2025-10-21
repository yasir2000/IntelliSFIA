#!/usr/bin/env python3
"""
Quick Production API Server for IntelliSFIA with Ollama
======================================================
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import uvicorn

app = FastAPI(title="IntelliSFIA Production API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatRequest(BaseModel):
    prompt: str
    provider: str = "ollama"
    max_tokens: int = 500

class ChatResponse(BaseModel):
    response: str
    model: str
    provider: str

# Ollama client
OLLAMA_BASE_URL = "http://localhost:11434"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "intellisfia-api"}

@app.get("/api/ollama/models")
async def get_ollama_models():
    """Get available Ollama models"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

@app.post("/api/ai/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with AI using Ollama"""
    try:
        # Use available model
        model = "deepseek-coder:latest"  # From your available models
        
        ollama_payload = {
            "model": model,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "num_predict": request.max_tokens,
                "temperature": 0.7
            }
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=ollama_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return ChatResponse(
                response=result.get("response", ""),
                model=model,
                provider="ollama"
            )
        else:
            raise HTTPException(status_code=500, detail="Ollama request failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/api/sfia9/statistics")
async def get_sfia_statistics():
    """Get SFIA statistics"""
    return {
        "total_skills": 102,
        "categories": 7,
        "levels": 7,
        "version": "SFIA 9",
        "status": "active"
    }

@app.get("/docs")
async def get_docs():
    """Redirect to OpenAPI docs"""
    return {"message": "API Documentation", "docs_url": "/docs"}

if __name__ == "__main__":
    print("Starting IntelliSFIA Production API Server")
    print("=" * 50)
    print("• API Server: http://localhost:8001")
    print("• API Docs:   http://localhost:8001/docs")
    print("• Health:     http://localhost:8001/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")