#!/usr/bin/env python3
"""
Simple IntelliSFIA API Server with Ollama Integration
====================================================

A simplified version that works directly with Ollama for testing production setup.
"""

import asyncio
import json
import logging
import os
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="User prompt/question")
    provider: str = Field(default="ollama", description="LLM provider")
    max_tokens: int = Field(default=500, description="Maximum tokens in response")
    temperature: float = Field(default=0.7, description="Temperature for randomness")


class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]


class SFIASkill(BaseModel):
    code: str
    name: str
    description: str
    category: str
    levels: List[int]


class IntelliSFIASimpleAPI:
    """Simple IntelliSFIA API with Ollama integration"""
    
    def __init__(self):
        self.app = FastAPI(
            title="IntelliSFIA Simple API",
            description="Production-ready IntelliSFIA API with Ollama integration",
            version="1.0.0"
        )
        
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = os.getenv("OLLAMA_MODEL", "deepseek-coder:latest")
        
        self.setup_middleware()
        self.setup_routes()
        
        # Load SFIA data
        self.sfia_data = self.load_sfia_data()
    
    def setup_middleware(self):
        """Setup CORS and other middleware"""
        cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def load_sfia_data(self) -> Dict[str, Any]:
        """Load SFIA data from JSON files"""
        data_dir = Path("data")
        sfia_data = {
            "skills": [],
            "levels": [],
            "attributes": []
        }
        
        # Try to load SFIA 9 data
        for data_type in ["skills", "levels", "attributes"]:
            file_path = data_dir / f"sfia9_{data_type}.json"
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        sfia_data[data_type] = json.load(f)
                    logger.info(f"Loaded {len(sfia_data[data_type])} SFIA {data_type}")
                except Exception as e:
                    logger.warning(f"Failed to load {file_path}: {e}")
        
        return sfia_data
    
    async def call_ollama(self, prompt: str, model: str = None) -> Dict[str, Any]:
        """Call Ollama API for chat completion"""
        if model is None:
            model = self.default_model
        
        try:
            # Check if Ollama is available
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise HTTPException(status_code=503, detail="Ollama service not available")
            
            # Prepare chat request
            chat_payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
            
            start_time = datetime.now()
            
            # Make the API call
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=chat_payload,
                timeout=60
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                result = response.json()
                message_content = result.get('message', {}).get('content', 'No response')
                
                return {
                    "response": message_content,
                    "model": model,
                    "processing_time": processing_time,
                    "tokens_used": len(message_content.split())  # Rough estimate
                }
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Ollama API error: {response.status_code} - {response.text}"
                )
                
        except requests.RequestException as e:
            raise HTTPException(status_code=503, detail=f"Connection to Ollama failed: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/", response_model=dict)
        async def root():
            return {
                "name": "IntelliSFIA Simple API",
                "version": "1.0.0",
                "description": "Production-ready SFIA assessment API with Ollama",
                "endpoints": {
                    "health": "/health",
                    "docs": "/docs",
                    "chat": "/api/ai/chat",
                    "sfia_skills": "/api/sfia9/skills",
                    "sfia_statistics": "/api/sfia9/statistics"
                }
            }
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            services = {}
            
            # Check Ollama
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
                services["ollama"] = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                services["ollama"] = "unavailable"
            
            return HealthResponse(
                status="healthy",
                timestamp=datetime.now().isoformat(),
                version="1.0.0",
                services=services
            )
        
        @self.app.post("/api/ai/chat", response_model=ChatResponse)
        async def ai_chat(request: ChatRequest):
            """AI chat endpoint using Ollama"""
            try:
                result = await self.call_ollama(request.prompt, self.default_model)
                
                return ChatResponse(
                    response=result["response"],
                    provider="ollama",
                    model=result["model"],
                    tokens_used=result.get("tokens_used"),
                    processing_time=result.get("processing_time")
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Chat error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/sfia9/skills", response_model=List[SFIASkill])
        async def get_sfia_skills():
            """Get SFIA 9 skills"""
            skills = []
            for skill in self.sfia_data.get("skills", []):
                skills.append(SFIASkill(
                    code=skill.get("code", ""),
                    name=skill.get("name", ""),
                    description=skill.get("description", ""),
                    category=skill.get("category", ""),
                    levels=list(range(1, 8))  # SFIA levels 1-7
                ))
            return skills
        
        @self.app.get("/api/sfia9/statistics")
        async def get_sfia_statistics():
            """Get SFIA 9 statistics"""
            skills_count = len(self.sfia_data.get("skills", []))
            levels_count = len(self.sfia_data.get("levels", []))
            attributes_count = len(self.sfia_data.get("attributes", []))
            
            # Get available models from Ollama
            ollama_models = []
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    ollama_models = [model["name"] for model in models]
            except:
                pass
            
            return {
                "sfia_framework": {
                    "version": "9.0",
                    "skills_count": skills_count,
                    "levels_count": levels_count,
                    "attributes_count": attributes_count
                },
                "llm_integration": {
                    "provider": "ollama",
                    "base_url": self.ollama_url,
                    "default_model": self.default_model,
                    "available_models": ollama_models
                },
                "api_info": {
                    "version": "1.0.0",
                    "status": "production",
                    "timestamp": datetime.now().isoformat()
                }
            }
        
        @self.app.post("/api/sfia9/assess")
        async def assess_skill(request: dict):
            """SFIA skill assessment endpoint"""
            skill_code = request.get("skill_code")
            evidence = request.get("evidence", "")
            
            if not skill_code or not evidence:
                raise HTTPException(status_code=400, detail="skill_code and evidence are required")
            
            # Find the skill
            skill = None
            for s in self.sfia_data.get("skills", []):
                if s.get("code") == skill_code:
                    skill = s
                    break
            
            if not skill:
                raise HTTPException(status_code=404, detail=f"Skill {skill_code} not found")
            
            # Create assessment prompt
            prompt = f"""
As an expert SFIA assessor, please evaluate the following evidence for the SFIA skill "{skill.get('name', skill_code)}":

Skill Description: {skill.get('description', 'No description available')}

Evidence provided:
{evidence}

Please assess:
1. What SFIA level (1-7) does this evidence demonstrate?
2. What specific indicators support this assessment?
3. What additional evidence would strengthen the assessment?

Respond in JSON format with: level, reasoning, confidence_score (0-1), recommendations.
"""
            
            try:
                result = await self.call_ollama(prompt, self.default_model)
                
                return {
                    "skill_code": skill_code,
                    "skill_name": skill.get("name"),
                    "evidence": evidence,
                    "assessment": result["response"],
                    "model_used": result["model"],
                    "processing_time": result.get("processing_time"),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Assessment error: {e}")
                raise HTTPException(status_code=500, detail=str(e))


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    api = IntelliSFIASimpleAPI()
    return api.app


# Create the app instance
app = create_app()


def main():
    """Run the development server"""
    uvicorn.run(
        "simple_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()