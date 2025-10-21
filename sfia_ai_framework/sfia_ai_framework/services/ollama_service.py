"""
Ollama LLM Integration Service for IntelliSFIA
============================================

This service integrates local Ollama LLMs with IntelliSFIA for intelligent
SFIA assessment, career guidance, and skills analysis.

Features:
- Local LLM inference for privacy
- SFIA-aware intelligent assessment
- Career progression recommendations
- Skills gap analysis
- Evidence evaluation
"""

import json
import requests
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class OllamaConfig:
    """Configuration for Ollama service"""
    host: str = "localhost"
    port: int = 11434
    model: str = "llama3.1:8b"  # Default model
    temperature: float = 0.7
    max_tokens: int = 2048
    
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

class OllamaService:
    """Service for interacting with local Ollama LLM"""
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.session = requests.Session()
        
    def is_available(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = self.session.get(f"{self.config.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = self.session.get(f"{self.config.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
        return []
    
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Generate text using Ollama"""
        try:
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens)
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
                
            response = self.session.post(
                f"{self.config.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return ""
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with Ollama using conversation format"""
        try:
            payload = {
                "model": self.config.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens)
                }
            }
            
            response = self.session.post(
                f"{self.config.base_url}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "")
            else:
                logger.error(f"Ollama chat API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return ""

class IntelliSFIAAgent:
    """Intelligent SFIA assessment agent using local Ollama LLM"""
    
    def __init__(self, ollama_service: OllamaService, sfia_data_path: str = None):
        self.ollama = ollama_service
        self.sfia_data_path = Path(sfia_data_path) if sfia_data_path else Path(__file__).parent.parent / "data" / "sfia9"
        self.sfia_data = self._load_sfia_data()
        
    def _load_sfia_data(self) -> Dict[str, Any]:
        """Load SFIA 9 data for intelligent processing"""
        data = {}
        
        try:
            # Load skills
            skills_file = self.sfia_data_path / "sfia9_skills.json"
            if skills_file.exists():
                with open(skills_file, 'r', encoding='utf-8') as f:
                    data['skills'] = json.load(f)
            
            # Load attributes
            attributes_file = self.sfia_data_path / "sfia9_attributes.json"
            if attributes_file.exists():
                with open(attributes_file, 'r', encoding='utf-8') as f:
                    data['attributes'] = json.load(f)
                    
            # Load levels
            levels_file = self.sfia_data_path / "sfia9_levels.json"
            if levels_file.exists():
                with open(levels_file, 'r', encoding='utf-8') as f:
                    data['levels'] = json.load(f)
                    
            logger.info(f"Loaded SFIA data: {len(data.get('skills', []))} skills, {len(data.get('attributes', []))} attributes")
            
        except Exception as e:
            logger.error(f"Error loading SFIA data: {e}")
            
        return data
    
    def assess_skill_level(self, skill_code: str, evidence: str, context: str = "") -> Dict[str, Any]:
        """Intelligently assess SFIA skill level based on evidence"""
        
        # Find the skill
        skill = next((s for s in self.sfia_data.get('skills', []) if s.get('code') == skill_code), None)
        if not skill:
            return {"error": f"Skill {skill_code} not found"}
        
        system_prompt = f"""You are an expert SFIA (Skills Framework for the Information Age) assessor. 
Your role is to evaluate evidence against SFIA skill levels objectively and professionally.

SFIA Skill: {skill.get('name', '')} ({skill_code})
Description: {skill.get('description', '')}

SFIA Level Guidelines:
- Level 1: Follow - Basic understanding, works under guidance
- Level 2: Assist - Some experience, assists in activities  
- Level 3: Apply - Good practical knowledge, works independently
- Level 4: Enable - Broad knowledge, enables others, some leadership
- Level 5: Ensure - Extensive knowledge, ensures delivery, manages complexity
- Level 6: Initiate - Expert knowledge, initiates strategy, influences others
- Level 7: Set strategy - Authority across organization, sets direction

Analyze the evidence and provide:
1. Recommended SFIA level (1-7)
2. Confidence score (0-100%)
3. Key evidence points that support the level
4. Areas for improvement to reach next level
5. Specific examples from the evidence

Be objective, evidence-based, and constructive."""

        user_prompt = f"""Please assess the following evidence for SFIA skill {skill_code} ({skill.get('name', '')}):

EVIDENCE:
{evidence}

CONTEXT:
{context}

Provide your assessment in this JSON format:
{{
    "skill_code": "{skill_code}",
    "skill_name": "{skill.get('name', '')}",
    "recommended_level": <number 1-7>,
    "confidence": <percentage 0-100>,
    "evidence_points": ["point1", "point2", "point3"],
    "improvement_areas": ["area1", "area2"],
    "specific_examples": ["example1", "example2"],
    "reasoning": "Brief explanation of the assessment",
    "next_level_requirements": "What's needed for the next level"
}}"""

        try:
            response = self.ollama.generate(user_prompt, system_prompt)
            
            # Try to parse JSON response
            try:
                # Extract JSON from response if it's wrapped in text
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = response[start:end]
                    result = json.loads(json_str)
                    return result
                else:
                    # Fallback: create structured response from text
                    return {
                        "skill_code": skill_code,
                        "skill_name": skill.get('name', ''),
                        "assessment": response,
                        "status": "text_response"
                    }
            except json.JSONDecodeError:
                return {
                    "skill_code": skill_code,
                    "skill_name": skill.get('name', ''),
                    "assessment": response,
                    "status": "text_response"
                }
                
        except Exception as e:
            logger.error(f"Error in skill assessment: {e}")
            return {"error": str(e)}
    
    def analyze_skills_gap(self, current_skills: Dict[str, int], target_role: str) -> Dict[str, Any]:
        """Analyze skills gap for career progression"""
        
        system_prompt = """You are a career development expert specializing in SFIA-based skill assessment. 
Analyze the skills gap between current capabilities and target role requirements.
Provide actionable recommendations for professional development."""
        
        skills_summary = []
        for skill_code, level in current_skills.items():
            skill = next((s for s in self.sfia_data.get('skills', []) if s.get('code') == skill_code), None)
            if skill:
                skills_summary.append(f"- {skill.get('name')} ({skill_code}): Level {level}")
        
        user_prompt = f"""Analyze the skills gap for career progression:

TARGET ROLE: {target_role}

CURRENT SKILLS:
{chr(10).join(skills_summary)}

AVAILABLE SFIA SKILLS (for reference):
{json.dumps([{'code': s.get('code'), 'name': s.get('name'), 'category': s.get('category')} for s in self.sfia_data.get('skills', [])[:20]], indent=2)}

Provide analysis in JSON format:
{{
    "target_role": "{target_role}",
    "skills_gap_analysis": {{
        "strengths": ["skill1", "skill2"],
        "gaps": ["skill1", "skill2"],
        "priority_skills": ["skill1", "skill2"]
    }},
    "recommendations": {{
        "immediate_actions": ["action1", "action2"],
        "learning_path": ["step1", "step2", "step3"],
        "timeline": "6-12 months"
    }},
    "role_readiness": {{
        "current_readiness": "percentage",
        "key_blockers": ["blocker1", "blocker2"]
    }}
}}"""

        try:
            response = self.ollama.generate(user_prompt, system_prompt)
            
            # Parse JSON response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                return {"analysis": response, "status": "text_response"}
                
        except Exception as e:
            logger.error(f"Error in skills gap analysis: {e}")
            return {"error": str(e)}
    
    def recommend_career_path(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Provide intelligent career path recommendations"""
        
        system_prompt = """You are a senior career advisor with deep expertise in SFIA framework and technology careers.
Provide thoughtful, realistic career progression recommendations based on the person's profile and interests."""
        
        user_prompt = f"""Based on this professional profile, recommend career progression paths:

PROFILE:
{json.dumps(profile, indent=2)}

SFIA FRAMEWORK CONTEXT:
- 147 digital skills across 6 categories
- 7 responsibility levels (Follow → Assist → Apply → Enable → Ensure → Initiate → Set strategy)
- Evidence-based competency assessment

Provide recommendations in JSON format:
{{
    "career_paths": [
        {{
            "role_title": "Target Role 1",
            "timeline": "1-2 years",
            "key_skills_needed": ["SFIA_CODE1", "SFIA_CODE2"],
            "description": "Role description and why it fits"
        }}
    ],
    "immediate_development": {{
        "priority_skills": ["skill1", "skill2"],
        "learning_activities": ["activity1", "activity2"],
        "timeframe": "3-6 months"
    }},
    "long_term_vision": {{
        "senior_roles": ["Senior Role 1", "Senior Role 2"],
        "leadership_path": "description",
        "specialist_path": "description"
    }}
}}"""

        try:
            response = self.ollama.generate(user_prompt, system_prompt)
            
            # Parse JSON response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                return {"recommendations": response, "status": "text_response"}
                
        except Exception as e:
            logger.error(f"Error in career path recommendation: {e}")
            return {"error": str(e)}

# Example usage and testing
if __name__ == "__main__":
    # Test the integration
    config = OllamaConfig(model="llama3.1:8b")  # Adjust model as needed
    ollama = OllamaService(config)
    
    if ollama.is_available():
        print("✅ Ollama service is available")
        print(f"Available models: {ollama.list_models()}")
        
        # Create intelligent agent
        agent = IntelliSFIAAgent(ollama)
        print(f"✅ IntelliSFIA Agent initialized with {len(agent.sfia_data.get('skills', []))} skills")
        
    else:
        print("❌ Ollama service not available. Please start Ollama first:")
        print("   ollama serve")
        print("   ollama pull llama3.1:8b")