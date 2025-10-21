"""
IntelliSFIA + Ollama Integration Service
=====================================

A comprehensive service for integrating local Ollama LLMs with IntelliSFIA
for intelligent SFIA assessment, skills gap analysis, and career guidance.

This service provides:
- Privacy-first local LLM inference
- SFIA-aware intelligent assessment agents
- Evidence-based skill level evaluation
- Career path recommendations
- Skills gap analysis

Author: IntelliSFIA Development Team
License: Apache 2.0 (with SFIA Foundation attribution)
"""

import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OllamaConfig:
    """Configuration for Ollama LLM service."""
    model: str = "deepseek-coder:latest"  # Using available model
    host: str = "localhost"
    port: int = 11434
    temperature: float = 0.3
    max_tokens: int = 2048
    timeout: int = 60

class OllamaService:
    """
    Service for interacting with local Ollama LLM instance.
    
    Provides a simple interface for generating responses using
    locally hosted large language models through Ollama.
    """
    
    def __init__(self, config: OllamaConfig):
        self.config = config
        self.base_url = f"http://{config.host}:{config.port}"
        
    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama service not available: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=self.config.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate response using Ollama model.
        
        Args:
            prompt: User prompt/question
            system_prompt: Optional system instructions
            temperature: Override default temperature
            
        Returns:
            Generated response text
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature or self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('message', {}).get('content', '')
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""

class IntelliSFIAAgent:
    """
    Intelligent SFIA assessment agent using local LLM.
    
    Provides AI-powered capabilities for:
    - Skill level assessment based on evidence
    - Skills gap analysis for target roles
    - Career path recommendations
    - Learning path planning
    """
    
    def __init__(self, ollama_service: OllamaService):
        self.ollama = ollama_service
        self.sfia_data = self._load_sfia_data()
        
    def _load_sfia_data(self) -> Dict[str, Any]:
        """Load processed SFIA 9 data."""
        data = {}
        
        # Define expected data files
        data_files = {
            'skills': 'sfia9_skills.json',
            'attributes': 'sfia9_attributes.json', 
            'levels': 'sfia9_levels.json'
        }
        
        for key, filename in data_files.items():
            file_path = Path(filename)
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data[key] = json.load(f)
                    logger.info(f"Loaded {len(data[key])} {key}")
                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")
                    data[key] = {}
            else:
                logger.warning(f"SFIA data file not found: {filename}")
                data[key] = {}
        
        return data
    
    def assess_skill_level(
        self, 
        skill_code: str, 
        evidence: str, 
        context: str = "",
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assess skill level based on provided evidence.
        
        Args:
            skill_code: SFIA skill code (e.g., 'PROG')
            evidence: Professional evidence/experience description
            context: Additional context (role, industry, etc.)
            system_prompt: Optional custom system prompt
            
        Returns:
            Assessment results with recommended level and reasoning
        """
        
        # Get skill information
        skill_info = self._get_skill_info(skill_code)
        if not skill_info:
            return {
                "error": f"Skill code '{skill_code}' not found in SFIA data",
                "skill_code": skill_code
            }
        
        # Default system prompt for skill assessment
        if not system_prompt:
            system_prompt = f"""You are an expert SFIA assessor with deep knowledge of the Skills Framework for the Information Age (SFIA 9).

Your task is to assess someone's skill level based on their evidence against SFIA competency levels.

SFIA Levels Overview:
- Level 1-2: Follow/Assist - Learning and following guidance
- Level 3: Apply - Working independently with guidance
- Level 4: Enable - Influencing others, leading small teams
- Level 5: Ensure/Advise - Managing people and resources
- Level 6: Initiate/Influence - Strategic thinking and management
- Level 7: Set Strategy/Inspire - Senior leadership and vision

IMPORTANT: Be conservative and evidence-based in your assessment. Only recommend a level if there is clear evidence of competency at that level."""

        # Build assessment prompt
        prompt = f"""
SKILL TO ASSESS: {skill_info['title']} ({skill_code})

SKILL DESCRIPTION:
{skill_info['description']}

SFIA LEVEL DETAILS:
{self._format_skill_levels(skill_info)}

EVIDENCE PROVIDED:
{evidence}

CONTEXT:
{context if context else 'No additional context provided'}

Please assess this evidence and provide:

1. RECOMMENDED_LEVEL: The highest SFIA level (1-7) that this evidence clearly demonstrates
2. CONFIDENCE: Your confidence percentage (0-100%) in this assessment
3. REASONING: Detailed explanation of why this level is appropriate
4. EVIDENCE_GAPS: What additional evidence would be needed for the next level
5. DEVELOPMENT_RECOMMENDATIONS: Specific suggestions for skill development

Format your response as JSON:
{{
    "recommended_level": X,
    "confidence": Y,
    "reasoning": "...",
    "evidence_gaps": "...",
    "development_recommendations": "..."
}}
"""
        
        # Generate assessment
        response = self.ollama.generate(prompt, system_prompt)
        
        try:
            # Try to parse as JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                assessment = json.loads(json_match.group())
                assessment.update({
                    "skill_code": skill_code,
                    "skill_title": skill_info['title'],
                    "assessment_method": "AI + SFIA Framework"
                })
                return assessment
            else:
                # Fallback if JSON parsing fails
                return {
                    "skill_code": skill_code,
                    "skill_title": skill_info['title'],
                    "recommended_level": "Unable to parse",
                    "confidence": 0,
                    "reasoning": response,
                    "assessment_method": "AI + SFIA Framework"
                }
        except Exception as e:
            logger.error(f"Error parsing assessment response: {e}")
            return {
                "skill_code": skill_code,
                "skill_title": skill_info['title'],
                "error": "Failed to parse assessment",
                "raw_response": response
            }
    
    def analyze_skills_gap(
        self, 
        current_skills: Dict[str, int], 
        target_role: str
    ) -> Dict[str, Any]:
        """
        Analyze skills gap between current capabilities and target role.
        
        Args:
            current_skills: Dictionary of skill_code -> current_level
            target_role: Target role/position description
            
        Returns:
            Gap analysis with recommendations
        """
        
        system_prompt = """You are a career development expert with deep SFIA knowledge. 
Analyze skills gaps and provide actionable career development advice."""
        
        # Format current skills
        skills_summary = []
        for skill_code, level in current_skills.items():
            skill_info = self._get_skill_info(skill_code)
            skill_title = skill_info['title'] if skill_info else skill_code
            skills_summary.append(f"- {skill_title} ({skill_code}): Level {level}")
        
        prompt = f"""
CURRENT SKILLS PROFILE:
{chr(10).join(skills_summary)}

TARGET ROLE: {target_role}

Based on typical requirements for "{target_role}" and the current skills profile, provide a comprehensive gap analysis.

Please analyze:
1. STRENGTHS: Current skills that align well with the target role
2. GAPS: Skills that need development for the target role
3. PRIORITY_SKILLS: Top 3-5 skills to focus on first
4. LEARNING_PATH: Structured approach to bridge the gaps
5. TIMELINE: Realistic timeframe for development

Format as JSON:
{{
    "strengths": ["skill1", "skill2"],
    "gaps": [
        {{"skill": "skill_code", "current_level": X, "target_level": Y, "priority": "high/medium/low"}}
    ],
    "recommendations": {{
        "priority_skills": ["skill1", "skill2", "skill3"],
        "learning_path": "...",
        "timeline": "...",
        "next_steps": "..."
    }}
}}
"""
        
        response = self.ollama.generate(prompt, system_prompt)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                analysis.update({
                    "target_role": target_role,
                    "analysis_method": "AI + SFIA Framework"
                })
                return analysis
            else:
                return {
                    "target_role": target_role,
                    "error": "Unable to parse analysis",
                    "raw_response": response
                }
        except Exception as e:
            logger.error(f"Error parsing gap analysis: {e}")
            return {
                "target_role": target_role,
                "error": "Failed to parse analysis",
                "raw_response": response
            }
    
    def recommend_career_path(
        self, 
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate personalized career path recommendations.
        
        Args:
            profile: Professional profile with experience, interests, etc.
            
        Returns:
            Career path recommendations with progression timelines
        """
        
        system_prompt = """You are a senior career advisor specializing in technology careers. 
Use SFIA framework to provide structured, realistic career progression advice."""
        
        prompt = f"""
PROFESSIONAL PROFILE:
Current Role: {profile.get('current_role', 'Not specified')}
Years Experience: {profile.get('years_experience', 'Not specified')}
Interests: {profile.get('interests', 'Not specified')}
Industry: {profile.get('industry', 'Not specified')}
Additional Context: {profile.get('additional_context', 'None')}

Based on this profile, recommend 3 potential career paths with:

1. CAREER_PATHS: Different progression options
2. SKILLS_REQUIRED: Key SFIA skills for each path
3. TIMELINE: Realistic progression timeline
4. DEVELOPMENT_STRATEGY: How to prepare for each path

Format as JSON:
{{
    "career_paths": [
        {{
            "role_title": "...",
            "timeline": "...",
            "key_skills_needed": ["skill1", "skill2"],
            "progression_steps": "...",
            "suitability_score": "high/medium/low"
        }}
    ],
    "general_recommendations": "...",
    "next_immediate_steps": "..."
}}
"""
        
        response = self.ollama.generate(prompt, system_prompt)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                recommendations.update({
                    "profile": profile,
                    "recommendation_method": "AI + SFIA Framework"
                })
                return recommendations
            else:
                return {
                    "profile": profile,
                    "error": "Unable to parse recommendations",
                    "raw_response": response
                }
        except Exception as e:
            logger.error(f"Error parsing career recommendations: {e}")
            return {
                "profile": profile,
                "error": "Failed to parse recommendations",
                "raw_response": response
            }
    
    def _get_skill_info(self, skill_code: str) -> Optional[Dict[str, Any]]:
        """Get skill information from SFIA data."""
        if 'skills' not in self.sfia_data:
            return None
            
        for skill in self.sfia_data['skills']:
            if skill.get('code') == skill_code:
                return skill
        return None
    
    def _format_skill_levels(self, skill_info: Dict[str, Any]) -> str:
        """Format skill level descriptions for prompt."""
        if 'levels' not in skill_info:
            return "No level information available"
        
        formatted_levels = []
        for level_info in skill_info['levels']:
            level_num = level_info.get('level', 'Unknown')
            description = level_info.get('description', 'No description')
            formatted_levels.append(f"Level {level_num}: {description}")
        
        return "\n".join(formatted_levels)

# Example usage and testing functions
def test_ollama_connection() -> bool:
    """Test connection to Ollama service."""
    config = OllamaConfig()
    ollama = OllamaService(config)
    return ollama.is_available()

def create_demo_agent() -> IntelliSFIAAgent:
    """Create a demo agent for testing."""
    config = OllamaConfig(model="llama3.1:8b", temperature=0.3)
    ollama = OllamaService(config)
    return IntelliSFIAAgent(ollama)

if __name__ == "__main__":
    # Quick test
    print("🔌 Testing Ollama Integration...")
    
    if test_ollama_connection():
        print("✅ Ollama service is available")
        
        agent = create_demo_agent()
        print("✅ IntelliSFIA agent created successfully")
        
        # Test skill assessment
        test_evidence = "I have developed Python applications for 3 years and led a small development team."
        assessment = agent.assess_skill_level("PROG", test_evidence, "Software Developer")
        
        if assessment and 'error' not in assessment:
            print("✅ Skill assessment working")
        else:
            print("❌ Skill assessment failed")
            
    else:
        print("❌ Ollama service not available")
        print("   Please start Ollama: ollama serve")
        print("   Download a model: ollama pull llama3.1:8b")