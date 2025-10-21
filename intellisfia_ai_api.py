"""
IntelliSFIA AI Assessment API
============================

FastAPI backend service that integrates Multi-LLM providers with IntelliSFIA
for intelligent SFIA assessment, conversation memory, and evidence validation.

Features:
- Multi-LLM provider support (Ollama, OpenAI, Anthropic, Google, etc.)
- RESTful API endpoints for AI assessment
- Conversation memory and context tracking
- Evidence validation workflows
- Specialized assessment agents
- Real-time AI-powered insights
- Provider selection and fallback capabilities

Author: IntelliSFIA Development Team
License: Apache 2.0 (with SFIA Foundation attribution)
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import asyncio
import logging

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Multi-LLM Provider imports
from llm_providers import (
    MultiLLMManager, 
    LLMProvider, 
    LLMConfig, 
    create_llm_manager,
    DEFAULT_CONFIGS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our Multi-LLM service (with Ollama fallback)
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

try:
    # Try to use the new Multi-LLM system
    MULTI_LLM_AVAILABLE = True
    logger.info("Multi-LLM provider system available")
except ImportError as e:
    # Fallback to original Ollama service
    from ollama_service import OllamaService, OllamaConfig, IntelliSFIAAgent
    MULTI_LLM_AVAILABLE = False
    logger.warning(f"Multi-LLM system not available, using Ollama fallback: {e}")

# ========================
# Data Models
# ========================

class AssessmentRequest(BaseModel):
    skill_code: str = Field(..., description="SFIA skill code (e.g., 'PROG')")
    evidence: str = Field(..., description="Professional evidence text")
    context: str = Field(default="", description="Additional context")
    session_id: Optional[str] = Field(default=None, description="Conversation session ID")
    assessment_type: str = Field(default="standard", description="Type of assessment")

class AssessmentResponse(BaseModel):
    assessment_id: str
    skill_code: str
    skill_title: str
    recommended_level: Any
    confidence: float
    reasoning: str
    evidence_gaps: Optional[str] = None
    development_recommendations: Optional[str] = None
    assessment_method: str
    timestamp: datetime
    session_id: Optional[str] = None

class ConversationMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    message_type: str = Field(default="text", description="Message type")

class ConversationSession(BaseModel):
    session_id: str
    created_at: datetime
    last_activity: datetime
    messages: List[ConversationMessage] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    assessment_history: List[str] = Field(default_factory=list)

class EvidenceValidationRequest(BaseModel):
    evidence: str = Field(..., description="Evidence text to validate")
    skill_code: Optional[str] = Field(default=None, description="Target skill code")
    validation_level: str = Field(default="standard", description="Validation depth")

class EvidenceValidationResponse(BaseModel):
    validation_id: str
    evidence_quality_score: float
    authenticity_indicators: List[str]
    completeness_score: float
    relevance_score: float
    suggestions: List[str]
    validated_competencies: List[Dict[str, Any]]

class CareerGuidanceRequest(BaseModel):
    current_skills: Dict[str, int] = Field(..., description="Current skill levels")
    career_goals: str = Field(..., description="Career aspirations")
    experience_years: int = Field(..., description="Years of experience")
    industry: Optional[str] = Field(default=None, description="Industry context")
    session_id: Optional[str] = None

class CareerGuidanceResponse(BaseModel):
    guidance_id: str
    career_paths: List[Dict[str, Any]]
    skills_gap_analysis: Dict[str, Any]
    development_plan: Dict[str, Any]
    timeline_recommendations: Dict[str, Any]
    next_steps: List[str]

# ========================
# Multi-LLM Provider Models
# ========================

class LLMProviderRequest(BaseModel):
    provider: str = Field(default="auto", description="LLM provider (auto, ollama, openai, anthropic, google, cohere)")
    model: Optional[str] = Field(default=None, description="Specific model to use")
    fallback: bool = Field(default=True, description="Allow fallback to other providers")
    ensemble: bool = Field(default=False, description="Get responses from multiple providers")

class LLMProviderStatus(BaseModel):
    provider: str
    available: bool
    model: str
    request_count: int
    cache_size: int
    cost_per_token: float

class LLMProviderResponse(BaseModel):
    content: str
    provider: str
    model: str
    tokens_used: int
    cost: float
    response_time: float
    cached: bool = False
    error: Optional[str] = None

class MultiLLMResponse(BaseModel):
    responses: List[LLMProviderResponse]
    preferred_response: LLMProviderResponse
    total_cost: float
    comparison_analysis: Optional[str] = None

# Enhanced request models with LLM provider selection
class EnhancedAssessmentRequest(AssessmentRequest):
    llm_provider: LLMProviderRequest = Field(default_factory=LLMProviderRequest)

class EnhancedChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    llm_provider: LLMProviderRequest = Field(default_factory=LLMProviderRequest)

class EnhancedEvidenceRequest(EvidenceValidationRequest):
    llm_provider: LLMProviderRequest = Field(default_factory=LLMProviderRequest)

# ========================
# Memory and Session Management
# ========================

@dataclass
class ConversationMemory:
    """Manages conversation context and memory across sessions."""
    sessions: Dict[str, ConversationSession] = field(default_factory=dict)
    max_session_age: timedelta = field(default=timedelta(hours=24))
    
    def create_session(self) -> str:
        """Create a new conversation session."""
        session_id = str(uuid.uuid4())
        session = ConversationSession(
            session_id=session_id,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        self.sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get conversation session by ID."""
        session = self.sessions.get(session_id)
        if session:
            # Check if session is still valid
            if datetime.now() - session.last_activity < self.max_session_age:
                return session
            else:
                # Clean up expired session
                del self.sessions[session_id]
        return None
    
    def add_message(self, session_id: str, role: str, content: str, 
                   message_type: str = "text") -> bool:
        """Add message to conversation session."""
        session = self.get_session(session_id)
        if session:
            message = ConversationMessage(
                role=role,
                content=content,
                message_type=message_type
            )
            session.messages.append(message)
            session.last_activity = datetime.now()
            return True
        return False
    
    def get_conversation_context(self, session_id: str, 
                               last_n_messages: int = 5) -> str:
        """Get recent conversation context as formatted string."""
        session = self.get_session(session_id)
        if not session:
            return ""
        
        recent_messages = session.messages[-last_n_messages:]
        context_lines = []
        
        for msg in recent_messages:
            role_prefix = "User" if msg.role == "user" else "Assistant"
            context_lines.append(f"{role_prefix}: {msg.content}")
        
        return "\n".join(context_lines)
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions from memory."""
        current_time = datetime.now()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if current_time - session.last_activity > self.max_session_age
        ]
        for sid in expired_sessions:
            del self.sessions[sid]
        return len(expired_sessions)

# ========================
# Specialized Assessment Agents
# ========================

class SpecializedAgents:
    """Collection of specialized AI agents for different assessment aspects with multi-LLM support."""
    
    def __init__(self, llm_manager: MultiLLMManager = None, ollama_service = None):
        """Initialize with either multi-LLM manager or fallback to Ollama service."""
        self.llm_manager = llm_manager
        self.ollama = ollama_service
        self.use_multi_llm = llm_manager is not None
        
        if not self.use_multi_llm and ollama_service:
            from ollama_service import IntelliSFIAAgent
            self.base_agent = IntelliSFIAAgent(ollama_service)
    
    async def _generate_response(self, prompt: str, system_prompt: str, 
                                llm_provider: LLMProviderRequest, 
                                temperature: float = 0.3) -> str:
        """Generate response using multi-LLM or fallback to Ollama."""
        if self.use_multi_llm and self.llm_manager:
            # Use multi-LLM system
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Map provider name to enum
            provider_map = {
                "ollama": LLMProvider.OLLAMA,
                "openai": LLMProvider.OPENAI,
                "anthropic": LLMProvider.ANTHROPIC,
                "google": LLMProvider.GOOGLE,
                "cohere": LLMProvider.COHERE,
                "auto": None
            }
            
            preferred_provider = provider_map.get(llm_provider.provider.lower())
            
            response = await self.llm_manager.generate(
                full_prompt,
                preferred_provider=preferred_provider,
                fallback=llm_provider.fallback,
                temperature=temperature
            )
            
            return response.content
        else:
            # Fallback to Ollama
            return self.ollama.generate(prompt, system_prompt, temperature=temperature)
    
    async def evidence_validator_agent(self, evidence: str, skill_code: str, 
                                     llm_provider: LLMProviderRequest = None) -> Dict[str, Any]:
        """Specialized agent for evidence validation with multi-LLM support."""
        
        if llm_provider is None:
            llm_provider = LLMProviderRequest()
        
        system_prompt = """You are a specialized Evidence Validation Expert for SFIA assessments.
Your role is to analyze professional evidence for quality, authenticity, and completeness.

Focus on:
- Quantifiable achievements and metrics
- Specific examples with context
- Evidence of impact and outcomes
- Consistency and credibility
- Alignment with SFIA competency levels

Provide detailed analysis with confidence scores."""

        prompt = f"""
Analyze this professional evidence for SFIA skill {skill_code}:

EVIDENCE:
{evidence}

Provide validation analysis:

1. QUALITY_SCORE (0-100): Overall evidence quality
2. AUTHENTICITY_INDICATORS: Signs of genuine experience
3. COMPLETENESS_SCORE (0-100): How complete the evidence is
4. RELEVANCE_SCORE (0-100): Relevance to {skill_code} skill
5. SPECIFIC_COMPETENCIES: Which SFIA competencies are demonstrated
6. IMPROVEMENT_SUGGESTIONS: How to strengthen the evidence

Format as JSON.
"""
        
        response = self.ollama.generate(prompt, system_prompt, temperature=0.2)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result.update({
                    "validation_method": "Specialized Evidence Validator Agent",
                    "skill_code": skill_code
                })
                return result
        except Exception as e:
            logger.error(f"Evidence validation parsing error: {e}")
        
        return {
            "validation_method": "Specialized Evidence Validator Agent",
            "skill_code": skill_code,
            "error": "Could not parse validation results",
            "raw_response": response
        }
    
    async def career_strategy_agent(self, profile: Dict[str, Any], 
                                   conversation_context: str = "",
                                   llm_provider: LLMProviderRequest = None) -> Dict[str, Any]:
        """Specialized agent for strategic career guidance with multi-LLM support."""
        
        if llm_provider is None:
            llm_provider = LLMProviderRequest()
        
        system_prompt = """You are a Senior Career Strategy Advisor specializing in technology careers.
You excel at:
- Strategic career planning and progression paths
- Industry trend analysis and market insights
- Skills gap identification and development planning
- Timeline estimation and milestone setting
- Personalized guidance based on individual goals

Provide actionable, strategic advice with specific timelines and next steps."""

        context_section = f"\nPREVIOUS CONVERSATION:\n{conversation_context}\n" if conversation_context else ""

        prompt = f"""
Provide strategic career guidance for this professional:

PROFILE:
Current Skills: {profile.get('current_skills', {})}
Career Goals: {profile.get('career_goals', 'Not specified')}
Experience: {profile.get('experience_years', 0)} years
Industry: {profile.get('industry', 'Technology')}
{context_section}

Provide strategic analysis:

1. CAREER_PATHS: 3 viable progression paths with timelines
2. SKILLS_GAP_ANALYSIS: Priority development areas
3. DEVELOPMENT_PLAN: Structured learning approach
4. MARKET_INSIGHTS: Industry trends and opportunities
5. TIMELINE_MILESTONES: Key checkpoints and goals
6. IMMEDIATE_ACTIONS: Next 30/60/90 day steps

Format as JSON with detailed explanations.
"""
        
        response = self.ollama.generate(prompt, system_prompt, temperature=0.4)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result.update({
                    "guidance_method": "Specialized Career Strategy Agent",
                    "profile": profile
                })
                return result
        except Exception as e:
            logger.error(f"Career guidance parsing error: {e}")
        
        return {
            "guidance_method": "Specialized Career Strategy Agent",
            "profile": profile,
            "error": "Could not parse guidance results",
            "raw_response": response
        }
    
    async def conversation_agent(self, user_message: str, context: str, 
                               session_data: Dict[str, Any],
                               llm_provider: LLMProviderRequest = None) -> str:
        """Specialized agent for natural conversation about SFIA and careers with multi-LLM support."""
        
        if llm_provider is None:
            llm_provider = LLMProviderRequest()
        
        system_prompt = """You are an intelligent SFIA Career Advisor Assistant.
You engage in natural conversations about:
- SFIA skills and competency levels
- Career development and progression
- Skills assessment and evidence
- Professional development planning

Maintain conversation context and provide helpful, personalized responses.
Be conversational but professional. Ask follow-up questions when appropriate."""

        prompt = f"""
Continue this conversation about SFIA and career development:

CONVERSATION CONTEXT:
{context}

SESSION DATA:
- Previous assessments: {len(session_data.get('assessment_history', []))}
- User context: {session_data.get('context', {})}

USER MESSAGE:
{user_message}

Provide a helpful, conversational response. If the user is asking about skills assessment,
evidence validation, or career guidance, guide them appropriately.
"""
        
        response = self.ollama.generate(prompt, system_prompt, temperature=0.6)
        return response.strip()

# ========================
# Application Setup
# ========================

# ========================
# Application Setup
# ========================

# Initialize Multi-LLM Manager or fallback to Ollama
if MULTI_LLM_AVAILABLE:
    logger.info("Initializing Multi-LLM Manager with multiple providers")
    llm_manager = create_llm_manager()
    available_providers = llm_manager.get_available_providers()
    logger.info(f"Available LLM providers: {[p.value for p in available_providers]}")
    
    # Initialize services with Multi-LLM support
    conversation_memory = ConversationMemory()
    specialized_agents = SpecializedAgents(llm_manager=llm_manager)
    ollama_service = None  # Not needed with multi-LLM
else:
    logger.info("Falling back to Ollama-only configuration")
    from ollama_service import OllamaService, OllamaConfig
    ollama_config = OllamaConfig(model="deepseek-coder:latest", temperature=0.3)
    ollama_service = OllamaService(ollama_config)
    conversation_memory = ConversationMemory()
    specialized_agents = SpecializedAgents(ollama_service=ollama_service)
    llm_manager = None

# Initialize FastAPI app
app = FastAPI(
    title="IntelliSFIA AI Assessment API",
    description="Intelligent SFIA assessment with conversation memory and specialized agents",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Dependency Functions
# ========================

# ========================
# Dependency Functions
# ========================

def get_llm_manager() -> Optional[MultiLLMManager]:
    """Dependency to get Multi-LLM manager."""
    return llm_manager

def get_ollama_service():
    """Dependency to get Ollama service (fallback)."""
    if ollama_service and not ollama_service.is_available():
        raise HTTPException(status_code=503, detail="Ollama service not available")
    return ollama_service

def get_conversation_memory() -> ConversationMemory:
    """Dependency to get conversation memory."""
    return conversation_memory

def get_specialized_agents() -> SpecializedAgents:
    """Dependency to get specialized agents."""
    return specialized_agents

# ========================
# API Endpoints
# ========================

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "IntelliSFIA AI Assessment API",
        "version": "2.0.0",
        "features": [
            "Multi-LLM provider support",
            "AI-powered SFIA assessment", 
            "Conversation memory",
            "Evidence validation",
            "Specialized assessment agents",
            "Career guidance",
            "Provider selection and fallback"
        ],
        "multi_llm_enabled": MULTI_LLM_AVAILABLE
    }

# ========================
# LLM Provider Management Endpoints
# ========================

@app.get("/api/llm/providers", response_model=List[LLMProviderStatus])
async def get_llm_providers(llm_mgr: Optional[MultiLLMManager] = Depends(get_llm_manager)):
    """Get status of all LLM providers."""
    if not llm_mgr:
        # Fallback to Ollama status
        ollama_available = ollama_service and ollama_service.is_available()
        return [
            LLMProviderStatus(
                provider="ollama",
                available=ollama_available,
                model="deepseek-coder:latest",
                request_count=0,
                cache_size=0,
                cost_per_token=0.0
            )
        ]
    
    stats = llm_mgr.get_provider_stats()
    return [
        LLMProviderStatus(
            provider=provider,
            available=stat["available"],
            model=stat["model"],
            request_count=stat["request_count"],
            cache_size=stat["cache_size"],
            cost_per_token=stat["cost_per_token"]
        )
        for provider, stat in stats.items()
    ]

@app.get("/api/llm/available")
async def get_available_providers(llm_mgr: Optional[MultiLLMManager] = Depends(get_llm_manager)):
    """Get list of currently available LLM providers."""
    if not llm_mgr:
        return {"providers": ["ollama"], "count": 1}
    
    available = llm_mgr.get_available_providers()
    return {
        "providers": [p.value for p in available],
        "count": len(available)
    }

@app.post("/api/llm/test")
async def test_llm_provider(
    request: LLMProviderRequest,
    llm_mgr: Optional[MultiLLMManager] = Depends(get_llm_manager)
):
    """Test a specific LLM provider with a simple prompt."""
    test_prompt = "Explain SFIA in one sentence."
    
    if not llm_mgr:
        # Fallback to Ollama
        if ollama_service and ollama_service.is_available():
            response = ollama_service.generate(test_prompt, "You are a helpful assistant.", temperature=0.3)
            return {
                "provider": "ollama",
                "response": response,
                "success": True
            }
        else:
            raise HTTPException(status_code=503, detail="No LLM providers available")
    
    # Test with multi-LLM system
    provider_map = {
        "ollama": LLMProvider.OLLAMA,
        "openai": LLMProvider.OPENAI,
        "anthropic": LLMProvider.ANTHROPIC,
        "google": LLMProvider.GOOGLE,
        "cohere": LLMProvider.COHERE,
        "auto": None
    }
    
    preferred_provider = provider_map.get(request.provider.lower())
    
    try:
        response = await llm_mgr.generate(
            test_prompt,
            preferred_provider=preferred_provider,
            fallback=request.fallback
        )
        
        return {
            "provider": response.provider.value,
            "model": response.model,
            "response": response.content,
            "tokens": response.tokens_used,
            "cost": response.cost,
            "response_time": response.response_time,
            "success": not bool(response.error),
            "error": response.error
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Provider test failed: {str(e)}")

@app.get("/health")
async def health_check(llm_mgr: Optional[MultiLLMManager] = Depends(get_llm_manager)):
    """Health check endpoint with multi-LLM status."""
    if llm_mgr:
        available_providers = llm_mgr.get_available_providers()
        provider_stats = llm_mgr.get_provider_stats()
        
        return {
            "status": "healthy" if available_providers else "degraded",
            "multi_llm_enabled": True,
            "available_providers": [p.value for p in available_providers],
            "provider_count": len(available_providers),
            "provider_stats": provider_stats,
            "active_sessions": len(conversation_memory.sessions),
            "timestamp": datetime.now().isoformat()
        }
    else:
        # Fallback to Ollama status
        ollama_status = ollama_service and ollama_service.is_available()
        return {
            "status": "healthy" if ollama_status else "degraded",
            "multi_llm_enabled": False,
            "ollama_available": ollama_status,
            "active_sessions": len(conversation_memory.sessions),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/sessions/create")
async def create_session(memory: ConversationMemory = Depends(get_conversation_memory)):
    """Create a new conversation session."""
    session_id = memory.create_session()
    return {"session_id": session_id, "created_at": datetime.now().isoformat()}

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str, memory: ConversationMemory = Depends(get_conversation_memory)):
    """Get conversation session details."""
    session = memory.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.post("/api/assess/skill")
async def assess_skill(
    request: AssessmentRequest,
    background_tasks: BackgroundTasks,
    ollama: OllamaService = Depends(get_ollama_service),
    memory: ConversationMemory = Depends(get_conversation_memory)
) -> AssessmentResponse:
    """Perform AI-powered SFIA skill assessment with conversation context."""
    
    assessment_id = str(uuid.uuid4())
    
    # Get conversation context if session provided
    conversation_context = ""
    if request.session_id:
        conversation_context = memory.get_conversation_context(request.session_id)
        # Add user message to conversation
        memory.add_message(request.session_id, "user", 
                          f"Assess {request.skill_code}: {request.evidence[:100]}...")
    
    # Create enhanced agent with conversation context
    agent = IntelliSFIAAgent(ollama)
    
    # Enhanced system prompt with conversation awareness
    enhanced_prompt = f"""You are an expert SFIA assessor with conversation memory.
    
Previous conversation context:
{conversation_context}

Consider this context when making your assessment, but focus primarily on the current evidence."""
    
    # Perform assessment
    try:
        assessment_result = agent.assess_skill_level(
            request.skill_code,
            request.evidence,
            request.context,
            system_prompt=enhanced_prompt if conversation_context else None
        )
        
        # Create response
        response = AssessmentResponse(
            assessment_id=assessment_id,
            skill_code=request.skill_code,
            skill_title=assessment_result.get('skill_title', 'Unknown'),
            recommended_level=assessment_result.get('recommended_level', 'N/A'),
            confidence=float(assessment_result.get('confidence', 0)),
            reasoning=assessment_result.get('reasoning', ''),
            evidence_gaps=assessment_result.get('evidence_gaps'),
            development_recommendations=assessment_result.get('development_recommendations'),
            assessment_method=assessment_result.get('assessment_method', 'AI + SFIA Framework'),
            timestamp=datetime.now(),
            session_id=request.session_id
        )
        
        # Add response to conversation if session exists
        if request.session_id:
            memory.add_message(request.session_id, "assistant", 
                              f"Assessment complete: {request.skill_code} Level {response.recommended_level}")
            
            # Update session context
            session = memory.get_session(request.session_id)
            if session:
                session.assessment_history.append(assessment_id)
                session.context['last_assessment'] = {
                    'skill_code': request.skill_code,
                    'level': response.recommended_level,
                    'timestamp': datetime.now().isoformat()
                }
        
        return response
        
    except Exception as e:
        logger.error(f"Assessment error: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@app.post("/api/validate/evidence")
async def validate_evidence(
    request: EvidenceValidationRequest,
    ollama: OllamaService = Depends(get_ollama_service)
) -> EvidenceValidationResponse:
    """Validate professional evidence using specialized agent."""
    
    validation_id = str(uuid.uuid4())
    
    # Use specialized evidence validator agent
    validation_result = specialized_agents.evidence_validator_agent(
        request.evidence,
        request.skill_code or "GENERAL"
    )
    
    response = EvidenceValidationResponse(
        validation_id=validation_id,
        evidence_quality_score=float(validation_result.get('QUALITY_SCORE', 0)),
        authenticity_indicators=validation_result.get('AUTHENTICITY_INDICATORS', []),
        completeness_score=float(validation_result.get('COMPLETENESS_SCORE', 0)),
        relevance_score=float(validation_result.get('RELEVANCE_SCORE', 0)),
        suggestions=validation_result.get('IMPROVEMENT_SUGGESTIONS', []),
        validated_competencies=validation_result.get('SPECIFIC_COMPETENCIES', [])
    )
    
    return response

@app.post("/api/guidance/career")
async def get_career_guidance(
    request: CareerGuidanceRequest,
    memory: ConversationMemory = Depends(get_conversation_memory)
) -> CareerGuidanceResponse:
    """Get strategic career guidance using specialized agent."""
    
    guidance_id = str(uuid.uuid4())
    
    # Get conversation context if available
    conversation_context = ""
    if request.session_id:
        conversation_context = memory.get_conversation_context(request.session_id)
    
    # Prepare profile for agent
    profile = {
        'current_skills': request.current_skills,
        'career_goals': request.career_goals,
        'experience_years': request.experience_years,
        'industry': request.industry
    }
    
    # Use specialized career strategy agent
    guidance_result = specialized_agents.career_strategy_agent(profile, conversation_context)
    
    response = CareerGuidanceResponse(
        guidance_id=guidance_id,
        career_paths=guidance_result.get('CAREER_PATHS', []),
        skills_gap_analysis=guidance_result.get('SKILLS_GAP_ANALYSIS', {}),
        development_plan=guidance_result.get('DEVELOPMENT_PLAN', {}),
        timeline_recommendations=guidance_result.get('TIMELINE_MILESTONES', {}),
        next_steps=guidance_result.get('IMMEDIATE_ACTIONS', [])
    )
    
    return response

@app.post("/api/chat")
async def chat_message(
    message: str,
    session_id: str,
    memory: ConversationMemory = Depends(get_conversation_memory)
):
    """Handle conversational messages about SFIA and careers."""
    
    # Get or create session
    session = memory.get_session(session_id)
    if not session:
        session_id = memory.create_session()
        session = memory.get_session(session_id)
    
    # Add user message
    memory.add_message(session_id, "user", message)
    
    # Get conversation context
    context = memory.get_conversation_context(session_id)
    
    # Generate response using conversation agent
    response = specialized_agents.conversation_agent(
        message, context, session.context
    )
    
    # Add assistant response
    memory.add_message(session_id, "assistant", response)
    
    return {
        "response": response,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/sessions/{session_id}/history")
async def get_session_history(
    session_id: str,
    memory: ConversationMemory = Depends(get_conversation_memory)
):
    """Get conversation history for a session."""
    session = memory.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "messages": session.messages,
        "assessment_history": session.assessment_history,
        "context": session.context
    }

@app.post("/api/admin/cleanup")
async def cleanup_sessions(memory: ConversationMemory = Depends(get_conversation_memory)):
    """Cleanup expired sessions (admin endpoint)."""
    cleaned_count = memory.cleanup_expired_sessions()
    return {
        "cleaned_sessions": cleaned_count,
        "active_sessions": len(memory.sessions)
    }

# ========================
# Background Tasks
# ========================

@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("IntelliSFIA AI Assessment API starting up...")
    
    # Check Ollama availability
    if ollama_service.is_available():
        models = ollama_service.list_models()
        logger.info(f"Ollama available with models: {models}")
    else:
        logger.warning("Ollama service not available - API will have limited functionality")
    
    logger.info("API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("IntelliSFIA AI Assessment API shutting down...")
    # Cleanup any resources if needed
    logger.info("Shutdown complete")

# ========================
# Main Application
# ========================

if __name__ == "__main__":
    uvicorn.run(
        "intellisfia_ai_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )