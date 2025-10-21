"""
Multi-LLM Provider Support for SFIA AI Framework

This module provides comprehensive support for multiple LLM providers including
OpenAI, Ollama (local models), Anthropic, Azure OpenAI, and others.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
import httpx
import json
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    PALM = "palm"


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 120
    extra_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
    
    @abstractmethod
    async def initialize(self):
        """Initialize the LLM client"""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy"""
        pass
    
    async def close(self):
        """Close the client connection"""
        if hasattr(self.client, 'close'):
            await self.client.close()


class OpenAIClient(BaseLLMClient):
    """OpenAI LLM client"""
    
    async def initialize(self):
        """Initialize OpenAI client"""
        try:
            from openai import AsyncOpenAI
            
            self.client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout
            )
            logger.info("OpenAI client initialized")
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI"""
        try:
            response = await self.client.completions.create(
                model=self.config.model,
                prompt=prompt,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens or 1000,
                **kwargs
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens or 1000,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check OpenAI API health"""
        try:
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False


class OllamaClient(BaseLLMClient):
    """Ollama local LLM client"""
    
    async def initialize(self):
        """Initialize Ollama client"""
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )
        logger.info(f"Ollama client initialized with base URL: {self.config.base_url}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama"""
        try:
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens or 1000,
                    **self.config.extra_params
                }
            }
            
            response = await self.client.post("/api/generate", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion using Ollama"""
        try:
            payload = {
                "model": self.config.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens or 1000,
                    **self.config.extra_params
                }
            }
            
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "").strip()
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Ollama server health"""
        try:
            response = await self.client.get("/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            
            result = response.json()
            models = [model["name"] for model in result.get("models", [])]
            return models
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            payload = {"name": model_name}
            response = await self.client.post("/api/pull", json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error pulling Ollama model {model_name}: {e}")
            return False


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude LLM client"""
    
    async def initialize(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            
            self.client = anthropic.AsyncAnthropic(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            logger.info("Anthropic client initialized")
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Anthropic"""
        try:
            response = await self.client.completions.create(
                model=self.config.model,
                prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
                temperature=self.config.temperature,
                max_tokens_to_sample=self.config.max_tokens or 1000,
                **kwargs
            )
            return response.completion.strip()
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion using Anthropic"""
        try:
            # Convert messages to Anthropic format
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = await self.client.messages.create(
                model=self.config.model,
                system=system_message,
                messages=user_messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens or 1000,
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Anthropic API health"""
        try:
            # Simple test request
            await self.generate("Hello", max_tokens_to_sample=10)
            return True
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return False


class AzureOpenAIClient(BaseLLMClient):
    """Azure OpenAI LLM client"""
    
    async def initialize(self):
        """Initialize Azure OpenAI client"""
        try:
            from openai import AsyncAzureOpenAI
            
            self.client = AsyncAzureOpenAI(
                api_key=self.config.api_key,
                azure_endpoint=self.config.base_url,
                api_version=self.config.extra_params.get("api_version", "2024-02-15-preview"),
                timeout=self.config.timeout
            )
            logger.info("Azure OpenAI client initialized")
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Azure OpenAI"""
        try:
            response = await self.client.completions.create(
                model=self.config.model,
                prompt=prompt,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens or 1000,
                **kwargs
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logger.error(f"Azure OpenAI generation error: {e}")
            raise
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion using Azure OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens or 1000,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Azure OpenAI chat error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Azure OpenAI API health"""
        try:
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"Azure OpenAI health check failed: {e}")
            return False


class HuggingFaceClient(BaseLLMClient):
    """Hugging Face Inference API client"""
    
    async def initialize(self):
        """Initialize Hugging Face client"""
        self.client = httpx.AsyncClient(
            base_url="https://api-inference.huggingface.co",
            headers={"Authorization": f"Bearer {self.config.api_key}"},
            timeout=self.config.timeout
        )
        logger.info("Hugging Face client initialized")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Hugging Face"""
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": self.config.temperature,
                    "max_new_tokens": self.config.max_tokens or 1000,
                    **self.config.extra_params
                }
            }
            
            response = await self.client.post(f"/models/{self.config.model}", json=payload)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            return ""
        except Exception as e:
            logger.error(f"Hugging Face generation error: {e}")
            raise
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion using Hugging Face"""
        # Convert messages to a single prompt
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"System: {content}\n"
            elif role == "user":
                prompt += f"User: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"
        
        prompt += "Assistant:"
        return await self.generate(prompt, **kwargs)
    
    async def health_check(self) -> bool:
        """Check Hugging Face API health"""
        try:
            response = await self.client.get("/")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Hugging Face health check failed: {e}")
            return False


class LLMManager:
    """Manager for multiple LLM providers"""
    
    def __init__(self):
        self.clients: Dict[str, BaseLLMClient] = {}
        self.default_provider: Optional[str] = None
    
    async def add_provider(self, name: str, config: LLMConfig) -> bool:
        """Add a new LLM provider"""
        try:
            # Create client based on provider type
            if config.provider == LLMProvider.OPENAI:
                client = OpenAIClient(config)
            elif config.provider == LLMProvider.OLLAMA:
                client = OllamaClient(config)
            elif config.provider == LLMProvider.ANTHROPIC:
                client = AnthropicClient(config)
            elif config.provider == LLMProvider.AZURE_OPENAI:
                client = AzureOpenAIClient(config)
            elif config.provider == LLMProvider.HUGGINGFACE:
                client = HuggingFaceClient(config)
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")
            
            # Initialize the client
            await client.initialize()
            
            # Test the client
            if await client.health_check():
                self.clients[name] = client
                if self.default_provider is None:
                    self.default_provider = name
                logger.info(f"Provider {name} added successfully")
                return True
            else:
                logger.error(f"Provider {name} failed health check")
                return False
        
        except Exception as e:
            logger.error(f"Error adding provider {name}: {e}")
            return False
    
    async def remove_provider(self, name: str):
        """Remove a provider"""
        if name in self.clients:
            await self.clients[name].close()
            del self.clients[name]
            
            if self.default_provider == name:
                self.default_provider = next(iter(self.clients.keys())) if self.clients else None
            
            logger.info(f"Provider {name} removed")
    
    def set_default_provider(self, name: str):
        """Set the default provider"""
        if name in self.clients:
            self.default_provider = name
            logger.info(f"Default provider set to {name}")
        else:
            raise ValueError(f"Provider {name} not found")
    
    def get_provider(self, name: Optional[str] = None) -> BaseLLMClient:
        """Get a specific provider or the default one"""
        provider_name = name or self.default_provider
        
        if provider_name is None:
            raise ValueError("No providers available")
        
        if provider_name not in self.clients:
            raise ValueError(f"Provider {provider_name} not found")
        
        return self.clients[provider_name]
    
    async def generate(self, prompt: str, provider: Optional[str] = None, **kwargs) -> str:
        """Generate text using specified provider"""
        client = self.get_provider(provider)
        return await client.generate(prompt, **kwargs)
    
    async def chat(self, messages: List[Dict[str, str]], provider: Optional[str] = None, **kwargs) -> str:
        """Chat completion using specified provider"""
        client = self.get_provider(provider)
        return await client.chat(messages, **kwargs)
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all providers"""
        results = {}
        for name, client in self.clients.items():
            results[name] = await client.health_check()
        return results
    
    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all providers with their configurations"""
        providers = {}
        for name, client in self.clients.items():
            providers[name] = {
                "provider": client.config.provider.value,
                "model": client.config.model,
                "is_default": name == self.default_provider,
                "base_url": client.config.base_url
            }
        return providers
    
    async def close_all(self):
        """Close all provider connections"""
        for client in self.clients.values():
            await client.close()
        self.clients.clear()
        self.default_provider = None


# Factory function for easy setup
async def create_llm_manager_from_config(config: Dict[str, Any]) -> LLMManager:
    """Create LLM manager from configuration dictionary"""
    manager = LLMManager()
    
    default_provider = config.get("default_provider", "openai")
    providers_config = config.get("providers", {})
    
    for name, provider_config in providers_config.items():
        try:
            # Map provider name to enum
            provider_type = LLMProvider(provider_config.get("provider", name))
            
            llm_config = LLMConfig(
                provider=provider_type,
                model=provider_config.get("model", "gpt-3.5-turbo"),
                api_key=provider_config.get("api_key"),
                base_url=provider_config.get("base_url"),
                temperature=provider_config.get("temperature", 0.7),
                max_tokens=provider_config.get("max_tokens"),
                timeout=provider_config.get("timeout", 120),
                extra_params=provider_config.get("extra_params", {})
            )
            
            success = await manager.add_provider(name, llm_config)
            if not success:
                logger.warning(f"Failed to add provider {name}")
        
        except Exception as e:
            logger.error(f"Error configuring provider {name}: {e}")
    
    # Set default provider
    if default_provider in manager.clients:
        manager.set_default_provider(default_provider)
    
    return manager


# Utility functions for common LLM operations
async def quick_chat(message: str, provider_config: Dict[str, Any]) -> str:
    """Quick chat function for testing"""
    manager = await create_llm_manager_from_config(provider_config)
    
    try:
        messages = [{"role": "user", "content": message}]
        response = await manager.chat(messages)
        return response
    finally:
        await manager.close_all()


async def compare_providers(prompt: str, providers_config: Dict[str, Any]) -> Dict[str, str]:
    """Compare responses from multiple providers"""
    manager = await create_llm_manager_from_config(providers_config)
    
    try:
        results = {}
        for provider_name in manager.clients.keys():
            try:
                response = await manager.generate(prompt, provider=provider_name)
                results[provider_name] = response
            except Exception as e:
                results[provider_name] = f"Error: {e}"
        
        return results
    finally:
        await manager.close_all()


# Example configuration
EXAMPLE_CONFIG = {
    "default_provider": "ollama",
    "providers": {
        "openai": {
            "provider": "openai",
            "model": "gpt-4",
            "api_key": "sk-...",
            "temperature": 0.7
        },
        "ollama": {
            "provider": "ollama",
            "model": "llama2",
            "base_url": "http://localhost:11434",
            "temperature": 0.7
        },
        "anthropic": {
            "provider": "anthropic",
            "model": "claude-3-sonnet-20240229",
            "api_key": "sk-ant-...",
            "temperature": 0.7
        },
        "azure": {
            "provider": "azure",
            "model": "gpt-4",
            "api_key": "...",
            "base_url": "https://your-resource.openai.azure.com/",
            "extra_params": {
                "api_version": "2024-02-15-preview"
            }
        }
    }
}