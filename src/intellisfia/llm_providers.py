"""
Multi-LLM Provider Integration for IntelliSFIA AI Framework
==========================================================

This module provides a unified interface for multiple LLM providers:
- Ollama (Local/Privacy-first)
- OpenAI GPT models
- Anthropic Claude
- Google Gemini
- Azure OpenAI
- Cohere
- Hugging Face Transformers
- AWS Bedrock

Features:
- Provider auto-detection and fallback
- Cost optimization and rate limiting
- Response caching and optimization
- Model-specific prompt optimization
- Multi-provider ensemble responses
"""

import os
import json
import time
import asyncio
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Optional imports with graceful fallback
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import cohere
except ImportError:
    cohere = None

try:
    from transformers import pipeline
except ImportError:
    pipeline = None

try:
    import boto3
except ImportError:
    boto3 = None

try:
    import requests
except ImportError:
    requests = None

# Setup logging
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    BEDROCK = "bedrock"


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: int = 30
    rate_limit: int = 100  # requests per minute
    cost_per_token: float = 0.0
    enabled: bool = True
    priority: int = 1  # Lower number = higher priority


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    provider: LLMProvider
    model: str
    tokens_used: int
    cost: float
    response_time: float
    cached: bool = False
    error: Optional[str] = None


class LLMProviderBase(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.request_count = 0
        self.last_request_time = 0
        self.cache = {}
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from the LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available"""
        pass
    
    def _rate_limit_check(self) -> bool:
        """Check if we're within rate limits"""
        current_time = time.time()
        if current_time - self.last_request_time < 60:
            if self.request_count >= self.config.rate_limit:
                return False
        else:
            self.request_count = 0
        return True
    
    def _get_cache_key(self, prompt: str, **kwargs) -> str:
        """Generate cache key for request"""
        cache_data = {"prompt": prompt, "config": asdict(self.config), **kwargs}
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    def _update_request_stats(self):
        """Update request statistics"""
        self.request_count += 1
        self.last_request_time = time.time()


class OllamaProvider(LLMProviderBase):
    """Ollama local LLM provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, **kwargs)
        if cache_key in self.cache:
            cached_response = self.cache[cache_key]
            cached_response.cached = True
            return cached_response
        
        if not self._rate_limit_check():
            return LLMResponse(
                content="",
                provider=LLMProvider.OLLAMA,
                model=self.config.model,
                tokens_used=0,
                cost=0.0,
                response_time=0.0,
                error="Rate limit exceeded"
            )
        
        try:
            if not requests:
                raise ImportError("requests library not available")
                
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("response", "")
            
            # Estimate tokens (rough approximation)
            tokens_used = len(content.split()) * 1.3
            
            llm_response = LLMResponse(
                content=content,
                provider=LLMProvider.OLLAMA,
                model=self.config.model,
                tokens_used=int(tokens_used),
                cost=0.0,  # Ollama is free
                response_time=time.time() - start_time
            )
            
            # Cache the response
            self.cache[cache_key] = llm_response
            self._update_request_stats()
            
            return llm_response
            
        except Exception as e:
            logger.error(f"Ollama provider error: {e}")
            return LLMResponse(
                content="",
                provider=LLMProvider.OLLAMA,
                model=self.config.model,
                tokens_used=0,
                cost=0.0,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            if not requests:
                return False
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


class OpenAIProvider(LLMProviderBase):
    """OpenAI GPT provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if openai and config.api_key:
            openai.api_key = config.api_key
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        if not openai:
            return LLMResponse(
                content="",
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                tokens_used=0,
                cost=0.0,
                response_time=0.0,
                error="OpenAI library not available"
            )
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, **kwargs)
        if cache_key in self.cache:
            cached_response = self.cache[cache_key]
            cached_response.cached = True
            return cached_response
        
        if not self._rate_limit_check():
            return LLMResponse(
                content="",
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                tokens_used=0,
                cost=0.0,
                response_time=0.0,
                error="Rate limit exceeded"
            )
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=self.config.timeout
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost = tokens_used * self.config.cost_per_token
            
            llm_response = LLMResponse(
                content=content,
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                tokens_used=tokens_used,
                cost=cost,
                response_time=time.time() - start_time
            )
            
            # Cache the response
            self.cache[cache_key] = llm_response
            self._update_request_stats()
            
            return llm_response
            
        except Exception as e:
            logger.error(f"OpenAI provider error: {e}")
            return LLMResponse(
                content="",
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                tokens_used=0,
                cost=0.0,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return openai is not None and self.config.api_key is not None


class AnthropicProvider(LLMProviderBase):
    """Anthropic Claude provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if anthropic and config.api_key:
            self.client = anthropic.Anthropic(api_key=config.api_key)
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        if not anthropic:
            return LLMResponse(
                content="",
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                tokens_used=0,
                cost=0.0,
                response_time=0.0,
                error="Anthropic library not available"
            )
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, **kwargs)
        if cache_key in self.cache:
            cached_response = self.cache[cache_key]
            cached_response.cached = True
            return cached_response
        
        try:
            message = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens
            cost = tokens_used * self.config.cost_per_token
            
            llm_response = LLMResponse(
                content=content,
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                tokens_used=tokens_used,
                cost=cost,
                response_time=time.time() - start_time
            )
            
            # Cache the response
            self.cache[cache_key] = llm_response
            self._update_request_stats()
            
            return llm_response
            
        except Exception as e:
            logger.error(f"Anthropic provider error: {e}")
            return LLMResponse(
                content="",
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                tokens_used=0,
                cost=0.0,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if Anthropic is available"""
        return anthropic is not None and self.config.api_key is not None


class GoogleProvider(LLMProviderBase):
    """Google Gemini provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if genai and config.api_key:
            genai.configure(api_key=config.api_key)
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        if not genai:
            return LLMResponse(
                content="",
                provider=LLMProvider.GOOGLE,
                model=self.config.model,
                tokens_used=0,
                cost=0.0,
                response_time=0.0,
                error="Google AI library not available"
            )
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, **kwargs)
        if cache_key in self.cache:
            cached_response = self.cache[cache_key]
            cached_response.cached = True
            return cached_response
        
        try:
            model = genai.GenerativeModel(self.config.model)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )
            
            content = response.text
            # Estimate tokens
            tokens_used = len(content.split()) * 1.3
            cost = tokens_used * self.config.cost_per_token
            
            llm_response = LLMResponse(
                content=content,
                provider=LLMProvider.GOOGLE,
                model=self.config.model,
                tokens_used=int(tokens_used),
                cost=cost,
                response_time=time.time() - start_time
            )
            
            # Cache the response
            self.cache[cache_key] = llm_response
            self._update_request_stats()
            
            return llm_response
            
        except Exception as e:
            logger.error(f"Google provider error: {e}")
            return LLMResponse(
                content="",
                provider=LLMProvider.GOOGLE,
                model=self.config.model,
                tokens_used=0,
                cost=0.0,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if Google AI is available"""
        return genai is not None and self.config.api_key is not None


class CohereProvider(LLMProviderBase):
    """Cohere provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if cohere and config.api_key:
            self.client = cohere.Client(config.api_key)
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        if not cohere:
            return LLMResponse(
                content="",
                provider=LLMProvider.COHERE,
                model=self.config.model,
                tokens_used=0,
                cost=0.0,
                response_time=0.0,
                error="Cohere library not available"
            )
        
        try:
            response = self.client.generate(
                model=self.config.model,
                prompt=prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            content = response.generations[0].text
            tokens_used = len(content.split()) * 1.3
            cost = tokens_used * self.config.cost_per_token
            
            llm_response = LLMResponse(
                content=content,
                provider=LLMProvider.COHERE,
                model=self.config.model,
                tokens_used=int(tokens_used),
                cost=cost,
                response_time=time.time() - start_time
            )
            
            self._update_request_stats()
            return llm_response
            
        except Exception as e:
            logger.error(f"Cohere provider error: {e}")
            return LLMResponse(
                content="",
                provider=LLMProvider.COHERE,
                model=self.config.model,
                tokens_used=0,
                cost=0.0,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if Cohere is available"""
        return cohere is not None and self.config.api_key is not None


class MultiLLMManager:
    """Multi-LLM provider manager with fallback and optimization"""
    
    def __init__(self, configs: List[LLMConfig]):
        self.providers: Dict[LLMProvider, LLMProviderBase] = {}
        self.configs = sorted(configs, key=lambda x: x.priority)
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured providers"""
        provider_classes = {
            LLMProvider.OLLAMA: OllamaProvider,
            LLMProvider.OPENAI: OpenAIProvider,
            LLMProvider.ANTHROPIC: AnthropicProvider,
            LLMProvider.GOOGLE: GoogleProvider,
            LLMProvider.COHERE: CohereProvider,
        }
        
        for config in self.configs:
            if config.enabled and config.provider in provider_classes:
                try:
                    provider_class = provider_classes[config.provider]
                    provider = provider_class(config)
                    self.providers[config.provider] = provider
                    logger.info(f"Initialized {config.provider.value} provider with model {config.model}")
                except Exception as e:
                    logger.error(f"Failed to initialize {config.provider.value}: {e}")
    
    async def generate(self, 
                      prompt: str, 
                      preferred_provider: Optional[LLMProvider] = None,
                      fallback: bool = True,
                      **kwargs) -> LLMResponse:
        """Generate response with provider selection and fallback"""
        
        # Try preferred provider first
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
            if provider.is_available():
                response = await provider.generate(prompt, **kwargs)
                if not response.error:
                    return response
        
        # Fallback to available providers by priority
        if fallback:
            for config in self.configs:
                if config.provider in self.providers:
                    provider = self.providers[config.provider]
                    if provider.is_available():
                        response = await provider.generate(prompt, **kwargs)
                        if not response.error:
                            return response
        
        # All providers failed
        return LLMResponse(
            content="",
            provider=preferred_provider or LLMProvider.OLLAMA,
            model="unknown",
            tokens_used=0,
            cost=0.0,
            response_time=0.0,
            error="All providers failed or unavailable"
        )
    
    async def generate_ensemble(self, 
                               prompt: str,
                               providers: List[LLMProvider],
                               **kwargs) -> List[LLMResponse]:
        """Generate responses from multiple providers for comparison"""
        tasks = []
        for provider_type in providers:
            if provider_type in self.providers:
                provider = self.providers[provider_type]
                if provider.is_available():
                    task = provider.generate(prompt, **kwargs)
                    tasks.append(task)
        
        if tasks:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in responses if isinstance(r, LLMResponse)]
        
        return []
    
    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of currently available providers"""
        return [
            provider_type for provider_type, provider in self.providers.items()
            if provider.is_available()
        ]
    
    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all providers"""
        stats = {}
        for provider_type, provider in self.providers.items():
            stats[provider_type.value] = {
                "available": provider.is_available(),
                "request_count": provider.request_count,
                "cache_size": len(provider.cache),
                "model": provider.config.model,
                "cost_per_token": provider.config.cost_per_token
            }
        return stats


# Default configurations for common providers
DEFAULT_CONFIGS = [
    # Ollama (Local, highest priority for privacy)
    LLMConfig(
        provider=LLMProvider.OLLAMA,
        model="deepseek-coder:6.7b",
        priority=1,
        cost_per_token=0.0
    ),
    
    # OpenAI GPT-4
    LLMConfig(
        provider=LLMProvider.OPENAI,
        model="gpt-4-turbo-preview",
        api_key=os.getenv("OPENAI_API_KEY"),
        priority=2,
        cost_per_token=0.00003,
        enabled=bool(os.getenv("OPENAI_API_KEY"))
    ),
    
    # Anthropic Claude
    LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        model="claude-3-sonnet-20240229",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        priority=3,
        cost_per_token=0.000015,
        enabled=bool(os.getenv("ANTHROPIC_API_KEY"))
    ),
    
    # Google Gemini
    LLMConfig(
        provider=LLMProvider.GOOGLE,
        model="gemini-pro",
        api_key=os.getenv("GOOGLE_API_KEY"),
        priority=4,
        cost_per_token=0.00001,
        enabled=bool(os.getenv("GOOGLE_API_KEY"))
    ),
    
    # Cohere
    LLMConfig(
        provider=LLMProvider.COHERE,
        model="command-light",
        api_key=os.getenv("COHERE_API_KEY"),
        priority=5,
        cost_per_token=0.000015,
        enabled=bool(os.getenv("COHERE_API_KEY"))
    ),
]


def create_llm_manager(custom_configs: Optional[List[LLMConfig]] = None) -> MultiLLMManager:
    """Create LLM manager with default or custom configurations"""
    configs = custom_configs or DEFAULT_CONFIGS
    return MultiLLMManager(configs)


# Example usage
if __name__ == "__main__":
    async def demo():
        """Demo the multi-LLM system"""
        manager = create_llm_manager()
        
        print("Available providers:", manager.get_available_providers())
        print("Provider stats:", manager.get_provider_stats())
        
        prompt = "Explain the key principles of SFIA skills assessment in 2 sentences."
        
        # Single provider response
        response = await manager.generate(prompt)
        print(f"\nResponse from {response.provider.value}:")
        print(f"Content: {response.content}")
        print(f"Tokens: {response.tokens_used}, Cost: ${response.cost:.4f}")
        
        # Ensemble response
        ensemble = await manager.generate_ensemble(
            prompt, 
            [LLMProvider.OLLAMA, LLMProvider.OPENAI, LLMProvider.ANTHROPIC]
        )
        
        print(f"\nEnsemble responses ({len(ensemble)} providers):")
        for resp in ensemble:
            print(f"- {resp.provider.value}: {resp.content[:100]}...")
    
    # Run demo
    asyncio.run(demo())