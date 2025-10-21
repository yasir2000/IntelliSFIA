"""
IntelliSFIA: Intelligent SFIA Framework with Multi-LLM Support

A comprehensive framework for SFIA (Skills Framework for the Information Age) 
skill assessment, RDF data conversion, and AI-powered analysis.
"""

__version__ = "1.0.0"
__author__ = "Yasir Ahmed"
__email__ = "yasir@intellisfia.com"

from .api import IntelliSFIAAPI
from .cli import IntelliSFIACLI
from .sdk import IntelliSFIAClient
from .llm_providers import MultiLLMManager, LLMProvider
from .sfia_converter import SFIAConverter

__all__ = [
    "IntelliSFIAAPI",
    "IntelliSFIACLI", 
    "IntelliSFIAClient",
    "MultiLLMManager",
    "LLMProvider",
    "SFIAConverter",
]