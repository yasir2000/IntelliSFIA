"""
IntelliSFIA Python SDK - Multi-LLM SFIA Assessment SDK
======================================================

A comprehensive Python SDK for integrating SFIA skills assessment with multi-LLM
provider support into applications, workflows, and automation systems.

Features:
- Multi-LLM provider management (Ollama, OpenAI, Anthropic, Google, Cohere)
- Async and sync API support
- Conversation memory and context management
- Evidence validation and quality scoring
- Career guidance and skill mapping
- Batch processing capabilities
- Custom provider configuration
- Retry mechanisms and error handling
- Type hints and comprehensive documentation

Example Usage:
    from intellisfia_sdk import IntelliSFIAClient, LLMProviderConfig
    
    # Initialize client
    client = IntelliSFIAClient(base_url="http://localhost:8000")
    
    # Assess a skill
    assessment = await client.assess_skill(
        skill_code="PROG",
        evidence="5 years of Python development...",
        provider="anthropic"
    )
    
    # Validate evidence
    validation = await client.validate_evidence(evidence_text)
    
    # Get career guidance
    guidance = await client.get_career_guidance("Senior Developer", experience)
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

# HTTP client imports
try:
    import aiohttp
    import requests
except ImportError:
    raise ImportError("Please install aiohttp and requests: pip install aiohttp requests")

# Optional dependencies
try:
    from pydantic import BaseModel, Field
except ImportError:
    BaseModel = object
    Field = lambda **kwargs: None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers."""
    AUTO = "auto"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    BEDROCK = "bedrock"

class AssessmentLevel(Enum):
    """SFIA assessment levels."""
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7

@dataclass
class LLMProviderConfig:
    """Configuration for LLM provider."""
    provider: LLMProvider
    model: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 2000
    fallback: bool = True
    ensemble: bool = False
    cost_limit: Optional[float] = None
    timeout: int = 30

@dataclass
class AssessmentRequest:
    """SFIA skill assessment request."""
    skill_code: str
    evidence: str
    context: Optional[str] = None
    llm_provider: Optional[LLMProviderConfig] = None
    session_id: Optional[str] = None

@dataclass
class AssessmentResponse:
    """SFIA skill assessment response."""
    skill_code: str
    skill_name: str
    recommended_level: int
    confidence: float
    assessment: str
    evidence_quality_score: Optional[float] = None
    evidence_feedback: Optional[str] = None
    development_recommendations: Optional[str] = None
    provider_used: Optional[str] = None
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None

@dataclass
class EvidenceValidation:
    """Evidence validation result."""
    evidence_quality_score: float
    completeness: float
    relevance: float
    authenticity: float
    feedback: str
    suggestions: List[str]
    validation_id: str
    timestamp: datetime

@dataclass
class ProviderStatus:
    """LLM provider status information."""
    provider: str
    available: bool
    model: str
    request_count: int
    cache_size: int
    cost_per_token: float
    last_used: Optional[datetime] = None

@dataclass
class ChatMessage:
    """Chat message structure."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    provider: Optional[str] = None
    tokens_used: Optional[int] = None

@dataclass
class ConversationSession:
    """Conversation session with memory."""
    session_id: str
    created_at: datetime
    last_activity: datetime
    messages: List[ChatMessage]
    context: Dict[str, Any]
    assessment_history: List[str]

class IntelliSFIAError(Exception):
    """Base exception for IntelliSFIA SDK."""
    pass

class APIConnectionError(IntelliSFIAError):
    """API connection error."""
    pass

class ProviderError(IntelliSFIAError):
    """LLM provider error."""
    pass

class ValidationError(IntelliSFIAError):
    """Validation error."""
    pass

class IntelliSFIAClient:
    """
    IntelliSFIA Python SDK Client with Multi-LLM Support
    
    This client provides comprehensive access to the IntelliSFIA AI assessment
    system with support for multiple LLM providers, conversation memory,
    evidence validation, and career guidance.
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize IntelliSFIA client.
        
        Args:
            base_url: IntelliSFIA API base URL
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session_id: Optional[str] = None
        
        # HTTP session for connection pooling
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            
        Returns:
            Response data
            
        Raises:
            APIConnectionError: Connection failed
            IntelliSFIAError: API error
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                if not self._session:
                    self._session = aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    )
                
                async with self._session.request(
                    method,
                    url,
                    json=data,
                    params=params,
                    headers=self._get_headers()
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 503:
                        error_data = await response.json()
                        raise ProviderError(error_data.get("detail", "Provider unavailable"))
                    else:
                        error_data = await response.json()
                        raise IntelliSFIAError(error_data.get("detail", f"HTTP {response.status}"))
            
            except aiohttp.ClientError as e:
                if attempt == self.max_retries:
                    raise APIConnectionError(f"Connection failed after {self.max_retries} retries: {e}")
                
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
    
    def _make_sync_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make synchronous HTTP request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            
        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = requests.get(
                        url, 
                        params=params, 
                        headers=self._get_headers(),
                        timeout=self.timeout
                    )
                else:
                    response = requests.post(
                        url, 
                        json=data, 
                        params=params,
                        headers=self._get_headers(),
                        timeout=self.timeout
                    )
                
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    raise APIConnectionError(f"Connection failed: {e}")
                
                time.sleep(self.retry_delay * (2 ** attempt))
    
    # Health and Status Methods
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health and status."""
        return await self._make_request("GET", "/health")
    
    def health_check_sync(self) -> Dict[str, Any]:
        """Check API health and status (synchronous)."""
        return self._make_sync_request("GET", "/health")
    
    async def get_providers(self) -> List[ProviderStatus]:
        """Get list of available LLM providers."""
        providers_data = await self._make_request("GET", "/api/llm/providers")
        return [
            ProviderStatus(
                provider=p["provider"],
                available=p["available"],
                model=p["model"],
                request_count=p["request_count"],
                cache_size=p["cache_size"],
                cost_per_token=p["cost_per_token"]
            )
            for p in providers_data
        ]
    
    def get_providers_sync(self) -> List[ProviderStatus]:
        """Get list of available LLM providers (synchronous)."""
        providers_data = self._make_sync_request("GET", "/api/llm/providers")
        return [
            ProviderStatus(
                provider=p["provider"],
                available=p["available"],
                model=p["model"],
                request_count=p["request_count"],
                cache_size=p["cache_size"],
                cost_per_token=p["cost_per_token"]
            )
            for p in providers_data
        ]
    
    async def test_provider(self, provider: str = "auto", fallback: bool = True) -> Dict[str, Any]:
        """Test a specific LLM provider."""
        test_data = {
            "provider": provider,
            "fallback": fallback
        }
        return await self._make_request("POST", "/api/llm/test", test_data)
    
    # Assessment Methods
    
    async def assess_skill(
        self,
        skill_code: str,
        evidence: str,
        context: Optional[str] = None,
        provider: Union[str, LLMProviderConfig] = "auto",
        session_id: Optional[str] = None
    ) -> AssessmentResponse:
        """
        Perform AI-powered SFIA skill assessment.
        
        Args:
            skill_code: SFIA skill code (e.g., "PROG")
            evidence: Professional evidence text
            context: Additional context for assessment
            provider: LLM provider configuration
            session_id: Session ID for conversation memory
            
        Returns:
            Assessment response with recommendations
        """
        # Convert provider config
        if isinstance(provider, str):
            llm_config = {"provider": provider, "fallback": True}
        else:
            llm_config = asdict(provider)
            llm_config["provider"] = provider.provider.value
        
        assessment_data = {
            "skill_code": skill_code.upper(),
            "evidence": evidence,
            "context": context or f"SDK assessment for {skill_code}",
            "llm_provider": llm_config
        }
        
        if session_id or self.session_id:
            assessment_data["session_id"] = session_id or self.session_id
        
        response = await self._make_request("POST", "/api/assess/skill", assessment_data)
        
        # Store session ID
        if "session_id" in response:
            self.session_id = response["session_id"]
        
        return AssessmentResponse(
            skill_code=response.get("skill_code", skill_code),
            skill_name=response.get("skill_name", "Unknown"),
            recommended_level=response.get("recommended_level", 0),
            confidence=response.get("confidence", 0.0),
            assessment=response.get("assessment", ""),
            evidence_quality_score=response.get("evidence_quality_score"),
            evidence_feedback=response.get("evidence_feedback"),
            development_recommendations=response.get("development_recommendations"),
            provider_used=response.get("provider_used"),
            timestamp=datetime.now(),
            session_id=response.get("session_id")
        )
    
    def assess_skill_sync(
        self,
        skill_code: str,
        evidence: str,
        context: Optional[str] = None,
        provider: str = "auto"
    ) -> AssessmentResponse:
        """Perform SFIA skill assessment (synchronous)."""
        assessment_data = {
            "skill_code": skill_code.upper(),
            "evidence": evidence,
            "context": context or f"SDK assessment for {skill_code}",
            "llm_provider": {"provider": provider, "fallback": True}
        }
        
        response = self._make_sync_request("POST", "/api/assess/skill", assessment_data)
        
        return AssessmentResponse(
            skill_code=response.get("skill_code", skill_code),
            skill_name=response.get("skill_name", "Unknown"),
            recommended_level=response.get("recommended_level", 0),
            confidence=response.get("confidence", 0.0),
            assessment=response.get("assessment", ""),
            evidence_quality_score=response.get("evidence_quality_score"),
            evidence_feedback=response.get("evidence_feedback"),
            development_recommendations=response.get("development_recommendations"),
            provider_used=response.get("provider_used"),
            timestamp=datetime.now()
        )
    
    async def batch_assess(
        self,
        assessments: List[AssessmentRequest],
        max_concurrent: int = 5
    ) -> List[AssessmentResponse]:
        """
        Perform batch skill assessments with concurrency control.
        
        Args:
            assessments: List of assessment requests
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of assessment responses
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def assess_single(request: AssessmentRequest) -> AssessmentResponse:
            async with semaphore:
                return await self.assess_skill(
                    skill_code=request.skill_code,
                    evidence=request.evidence,
                    context=request.context,
                    provider=request.llm_provider or "auto",
                    session_id=request.session_id
                )
        
        tasks = [assess_single(req) for req in assessments]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    # Evidence Validation Methods
    
    async def validate_evidence(
        self,
        evidence: str,
        context: Optional[str] = None
    ) -> EvidenceValidation:
        """
        Validate professional evidence quality.
        
        Args:
            evidence: Evidence text to validate
            context: Additional context for validation
            
        Returns:
            Evidence validation results
        """
        validation_data = {
            "evidence": evidence,
            "context": context or "SDK evidence validation"
        }
        
        response = await self._make_request("POST", "/api/validate/evidence", validation_data)
        
        return EvidenceValidation(
            evidence_quality_score=response.get("evidence_quality_score", 0.0),
            completeness=response.get("completeness", 0.0),
            relevance=response.get("relevance", 0.0),
            authenticity=response.get("authenticity", 0.0),
            feedback=response.get("feedback", ""),
            suggestions=response.get("suggestions", []),
            validation_id=response.get("validation_id", ""),
            timestamp=datetime.now()
        )
    
    # Conversation and Chat Methods
    
    async def send_message(
        self,
        message: str,
        provider: str = "auto",
        session_id: Optional[str] = None
    ) -> ChatMessage:
        """
        Send a chat message to AI assistant.
        
        Args:
            message: User message
            provider: LLM provider to use
            session_id: Session ID for conversation memory
            
        Returns:
            AI response message
        """
        chat_data = {
            "message": message,
            "provider": provider,
            "session_id": session_id or self.session_id
        }
        
        response = await self._make_request("POST", "/api/chat", chat_data)
        
        # Update session ID
        if "session_id" in response:
            self.session_id = response["session_id"]
        
        return ChatMessage(
            role="assistant",
            content=response.get("response", ""),
            timestamp=datetime.now(),
            provider=response.get("provider_used"),
            tokens_used=response.get("tokens_used")
        )
    
    async def get_conversation_history(
        self,
        session_id: Optional[str] = None
    ) -> ConversationSession:
        """Get conversation history for a session."""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID available")
        
        response = await self._make_request("GET", f"/api/sessions/{sid}/history")
        
        messages = [
            ChatMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
                provider=msg.get("provider")
            )
            for msg in response.get("messages", [])
        ]
        
        return ConversationSession(
            session_id=sid,
            created_at=datetime.fromisoformat(response["created_at"]),
            last_activity=datetime.fromisoformat(response["last_activity"]),
            messages=messages,
            context=response.get("context", {}),
            assessment_history=response.get("assessment_history", [])
        )
    
    # Career Guidance Methods
    
    async def get_career_guidance(
        self,
        target_role: str,
        current_experience: str,
        provider: str = "auto"
    ) -> Dict[str, Any]:
        """
        Get AI-powered career guidance.
        
        Args:
            target_role: Desired career role
            current_experience: Current experience description
            provider: LLM provider to use
            
        Returns:
            Career guidance recommendations
        """
        guidance_data = {
            "target_role": target_role,
            "current_experience": current_experience,
            "context": "SDK career guidance request",
            "provider": provider
        }
        
        return await self._make_request("POST", "/api/guidance/career", guidance_data)
    
    # Utility Methods
    
    async def create_session(self) -> str:
        """Create a new conversation session."""
        response = await self._make_request("POST", "/api/sessions/create")
        session_id = response.get("session_id")
        self.session_id = session_id
        return session_id
    
    def set_session(self, session_id: str):
        """Set the current session ID."""
        self.session_id = session_id
    
    async def close(self):
        """Close the client and cleanup resources."""
        if self._session:
            await self._session.close()

# Convenience Functions for Quick Usage

async def quick_assess(
    skill_code: str,
    evidence: str,
    provider: str = "auto",
    api_url: str = "http://localhost:8000"
) -> AssessmentResponse:
    """
    Quick skill assessment with default settings.
    
    Args:
        skill_code: SFIA skill code
        evidence: Professional evidence
        provider: LLM provider
        api_url: API base URL
        
    Returns:
        Assessment response
    """
    async with IntelliSFIAClient(api_url) as client:
        return await client.assess_skill(skill_code, evidence, provider=provider)

def quick_assess_sync(
    skill_code: str,
    evidence: str,
    provider: str = "auto",
    api_url: str = "http://localhost:8000"
) -> AssessmentResponse:
    """Quick skill assessment (synchronous)."""
    client = IntelliSFIAClient(api_url)
    return client.assess_skill_sync(skill_code, evidence, provider=provider)

async def quick_validate(
    evidence: str,
    api_url: str = "http://localhost:8000"
) -> EvidenceValidation:
    """
    Quick evidence validation.
    
    Args:
        evidence: Evidence text to validate
        api_url: API base URL
        
    Returns:
        Validation results
    """
    async with IntelliSFIAClient(api_url) as client:
        return await client.validate_evidence(evidence)

# Context Managers for Resource Management

class IntelliSFIASession:
    """Context manager for IntelliSFIA sessions with automatic cleanup."""
    
    def __init__(self, client: IntelliSFIAClient):
        self.client = client
        self.session_id: Optional[str] = None
    
    async def __aenter__(self) -> str:
        self.session_id = await self.client.create_session()
        return self.session_id
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Session cleanup would go here if needed
        pass

# Export main classes and functions
__all__ = [
    "IntelliSFIAClient",
    "LLMProvider",
    "LLMProviderConfig", 
    "AssessmentRequest",
    "AssessmentResponse",
    "EvidenceValidation",
    "ProviderStatus",
    "ChatMessage",
    "ConversationSession",
    "IntelliSFIASession",
    "IntelliSFIAError",
    "APIConnectionError",
    "ProviderError",
    "ValidationError",
    "quick_assess",
    "quick_assess_sync",
    "quick_validate"
]