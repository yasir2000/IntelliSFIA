"""
Enterprise Integration Module

Provides comprehensive integration capabilities with enterprise systems
for real-time SFIA analysis and workforce intelligence.
"""

from .connectors import (
    BaseSystemConnector,
    SAPConnector,
    PowerBIConnector,
    DatabaseConnector,
    KafkaConnector,
    MongoDBConnector,
    SystemCredentials,
    TaskActivity,
    PerformanceMetrics,
    SFIALevelSuggestion,
    create_connector
)

from .real_time_engine import (
    RealTimeAnalysisEngine,
    ActivityWeights,
    SFIALevelCriteria
)

from .integration_manager import (
    EnterpriseIntegrationManager,
    IntegrationConfig
)

__all__ = [
    # Connectors
    'BaseSystemConnector',
    'SAPConnector',
    'PowerBIConnector',
    'DatabaseConnector',
    'KafkaConnector',
    'MongoDBConnector',
    'SystemCredentials',
    'TaskActivity',
    'PerformanceMetrics',
    'SFIALevelSuggestion',
    'create_connector',
    
    # Analysis Engine
    'RealTimeAnalysisEngine',
    'ActivityWeights',
    'SFIALevelCriteria',
    
    # Integration Manager
    'EnterpriseIntegrationManager',
    'IntegrationConfig'
]