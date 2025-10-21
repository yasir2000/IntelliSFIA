"""
IntelliSFIA Web Application Configuration
=========================================

Enhanced web application configuration supporting multi-LLM provider capabilities,
advanced UI features, and comprehensive assessment workflows.

This configuration file sets up:
1. Multi-LLM provider integration
2. Advanced React components
3. Enhanced API endpoints
4. Performance monitoring
5. Cost tracking and optimization
6. Ensemble response comparison
7. Real-time provider status monitoring
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class LLMProvider(Enum):
    AUTO = "auto"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    AZURE = "azure"

@dataclass
class WebAppConfig:
    """Configuration for IntelliSFIA web application."""
    
    # API Configuration
    api_base_url: str = "http://localhost:8000"
    api_timeout: int = 30
    max_retries: int = 3
    
    # Frontend Configuration
    frontend_port: int = 3000
    frontend_host: str = "localhost"
    enable_hot_reload: bool = True
    
    # Multi-LLM Configuration
    default_provider: LLMProvider = LLMProvider.AUTO
    enable_fallback: bool = True
    enable_ensemble: bool = True
    enable_cost_tracking: bool = True
    enable_performance_monitoring: bool = True
    
    # UI Features
    enable_provider_selector: bool = True
    enable_conversation_memory: bool = True
    enable_evidence_validation: bool = True
    enable_career_guidance: bool = True
    enable_real_time_insights: bool = True
    enable_dark_mode: bool = True
    
    # Performance Settings
    request_batching: bool = True
    response_caching: bool = True
    max_concurrent_requests: int = 5
    cache_ttl_seconds: int = 300
    
    # Cost Management
    cost_alerts_enabled: bool = True
    daily_cost_limit: float = 10.0
    cost_tracking_precision: int = 6
    
    # Security
    enable_api_key_auth: bool = False
    enable_cors: bool = True
    cors_origins: List[str] = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = [
                f"http://{self.frontend_host}:{self.frontend_port}",
                "http://localhost:3000",
                "http://localhost:3001"
            ]

# Default configuration instance
default_config = WebAppConfig()

# Environment-specific configurations
ENVIRONMENT_CONFIGS = {
    "development": WebAppConfig(
        enable_hot_reload=True,
        enable_cost_tracking=True,
        enable_performance_monitoring=True,
        daily_cost_limit=5.0
    ),
    
    "production": WebAppConfig(
        enable_hot_reload=False,
        api_timeout=60,
        max_retries=5,
        enable_api_key_auth=True,
        daily_cost_limit=100.0,
        cors_origins=["https://yourdomain.com"]
    ),
    
    "testing": WebAppConfig(
        api_base_url="http://localhost:8001",
        frontend_port=3001,
        enable_cost_tracking=False,
        daily_cost_limit=1.0
    )
}

def get_config(environment: str = None) -> WebAppConfig:
    """Get configuration for specified environment."""
    env = environment or os.getenv("INTELLISFIA_ENV", "development")
    return ENVIRONMENT_CONFIGS.get(env, default_config)

# Frontend Component Configuration
COMPONENT_CONFIG = {
    "AIAssessmentPanel": {
        "enabled": True,
        "features": {
            "provider_selection": True,
            "cost_display": True,
            "confidence_scoring": True,
            "evidence_validation": True,
            "development_recommendations": True
        }
    },
    
    "ConversationChat": {
        "enabled": True,
        "features": {
            "memory_persistence": True,
            "provider_switching": True,
            "message_export": True,
            "typing_indicators": True,
            "cost_per_message": True
        }
    },
    
    "EvidenceValidator": {
        "enabled": True,
        "features": {
            "quality_scoring": True,
            "improvement_suggestions": True,
            "batch_validation": True,
            "competency_mapping": True
        }
    },
    
    "CareerGuidanceDashboard": {
        "enabled": True,
        "features": {
            "skills_gap_analysis": True,
            "career_path_visualization": True,
            "development_timeline": True,
            "market_insights": True
        }
    },
    
    "ProviderPerformanceMonitor": {
        "enabled": True,
        "features": {
            "real_time_metrics": True,
            "cost_breakdown": True,
            "success_rate_tracking": True,
            "response_time_monitoring": True,
            "provider_comparison": True
        }
    },
    
    "EnsembleResponseComparator": {
        "enabled": True,
        "features": {
            "multi_provider_testing": True,
            "response_quality_scoring": True,
            "cost_benefit_analysis": True,
            "provider_recommendation": True
        }
    },
    
    "LLMProviderSelector": {
        "enabled": True,
        "features": {
            "provider_status_monitoring": True,
            "cost_estimation": True,
            "model_selection": True,
            "fallback_configuration": True,
            "ensemble_mode": True
        }
    }
}

# API Endpoint Configuration
API_ENDPOINTS = {
    # Core Assessment Endpoints
    "assess_skill": "/api/assess/skill",
    "validate_evidence": "/api/validate/evidence",
    "career_guidance": "/api/guidance/career",
    "chat": "/api/chat",
    
    # Multi-LLM Provider Endpoints
    "llm_providers": "/api/llm/providers",
    "llm_available": "/api/llm/available",
    "llm_test": "/api/llm/test",
    
    # Session Management
    "create_session": "/api/sessions/create",
    "session_history": "/api/sessions/{session_id}/history",
    
    # System Health
    "health": "/health",
    "metrics": "/api/metrics",
    "statistics": "/api/statistics"
}

# UI Theme Configuration
UI_THEME = {
    "primary_color": "#1976d2",
    "secondary_color": "#dc004e",
    "success_color": "#2e7d32",
    "warning_color": "#ed6c02",
    "error_color": "#d32f2f",
    "info_color": "#0288d1",
    
    "typography": {
        "fontFamily": "'Roboto', 'Helvetica', 'Arial', sans-serif",
        "h1": {"fontSize": "2.5rem", "fontWeight": 300},
        "h2": {"fontSize": "2rem", "fontWeight": 400},
        "h3": {"fontSize": "1.75rem", "fontWeight": 400},
        "h4": {"fontSize": "1.5rem", "fontWeight": 500},
        "h5": {"fontSize": "1.25rem", "fontWeight": 500},
        "h6": {"fontSize": "1rem", "fontWeight": 500},
        "body1": {"fontSize": "1rem", "lineHeight": 1.5},
        "body2": {"fontSize": "0.875rem", "lineHeight": 1.43}
    },
    
    "spacing": 8,
    "borderRadius": 4,
    
    "breakpoints": {
        "xs": 0,
        "sm": 600,
        "md": 900,
        "lg": 1200,
        "xl": 1536
    }
}

# Provider-Specific Configurations
PROVIDER_CONFIGS = {
    "ollama": {
        "display_name": "Ollama (Local)",
        "description": "Privacy-first local LLM processing",
        "icon": "🏠",
        "cost_per_token": 0.0,
        "features": ["Privacy", "Local Processing", "No Internet Required"],
        "limitations": ["Limited Model Variety", "Hardware Dependent"],
        "recommended_for": ["Privacy-sensitive", "Development", "Testing"]
    },
    
    "openai": {
        "display_name": "OpenAI GPT",
        "description": "Advanced conversational AI with broad knowledge",
        "icon": "🤖",
        "cost_per_token": 0.00003,
        "features": ["High Quality", "Broad Knowledge", "Creative Writing"],
        "limitations": ["Cost", "Rate Limits"],
        "recommended_for": ["General Purpose", "Creative Tasks", "Complex Analysis"]
    },
    
    "anthropic": {
        "display_name": "Anthropic Claude",
        "description": "Helpful, harmless, and honest AI assistant",
        "icon": "🧠",
        "cost_per_token": 0.000015,
        "features": ["Safety-focused", "Long Context", "Code Analysis"],
        "limitations": ["Newer Service", "Limited Availability"],
        "recommended_for": ["Code Review", "Technical Writing", "Analysis"]
    },
    
    "google": {
        "display_name": "Google Gemini",
        "description": "Multimodal AI with competitive performance",
        "icon": "🌟",
        "cost_per_token": 0.00001,
        "features": ["Cost Effective", "Fast", "Multimodal"],
        "limitations": ["Newer Service", "Limited Features"],
        "recommended_for": ["Cost-conscious", "Speed", "General Tasks"]
    },
    
    "cohere": {
        "display_name": "Cohere Command",
        "description": "Enterprise-focused language model",
        "icon": "🏢",
        "cost_per_token": 0.000025,
        "features": ["Enterprise Features", "Customizable", "API-first"],
        "limitations": ["Specialized Use Cases", "Learning Curve"],
        "recommended_for": ["Enterprise", "Specialized Tasks", "Custom Solutions"]
    }
}

# Feature Flags
FEATURE_FLAGS = {
    # Core Features
    "multi_llm_support": True,
    "conversation_memory": True,
    "evidence_validation": True,
    "career_guidance": True,
    
    # Advanced Features
    "ensemble_responses": True,
    "provider_fallback": True,
    "cost_optimization": True,
    "performance_monitoring": True,
    
    # Experimental Features
    "ai_powered_insights": True,
    "predictive_career_analysis": False,
    "automated_skill_mapping": False,
    "integration_webhooks": False,
    
    # UI Enhancements
    "dark_mode": True,
    "accessibility_features": True,
    "mobile_responsive": True,
    "offline_mode": False
}

# Performance Monitoring Configuration
MONITORING_CONFIG = {
    "enable_metrics": True,
    "metrics_retention_days": 30,
    "alert_thresholds": {
        "response_time_ms": 5000,
        "error_rate_percent": 5.0,
        "cost_per_day": 10.0,
        "provider_downtime_minutes": 5
    },
    "dashboard_refresh_interval_seconds": 30,
    "export_formats": ["json", "csv", "pdf"]
}

# Export configuration
__all__ = [
    'WebAppConfig',
    'get_config',
    'COMPONENT_CONFIG',
    'API_ENDPOINTS',
    'UI_THEME',
    'PROVIDER_CONFIGS',
    'FEATURE_FLAGS',
    'MONITORING_CONFIG'
]