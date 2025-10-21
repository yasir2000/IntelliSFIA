"""
Enterprise Integration Module for IntelliSFIA Framework

This module provides comprehensive integration capabilities with enterprise systems
including ERP, HRMS, BI, BPM, and other business systems for real-time SFIA analysis.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import httpx
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import pymongo
from confluent_kafka import Consumer, Producer
import redis.asyncio as redis
from pydantic import BaseModel, Field
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


@dataclass
class SystemCredentials:
    """Credentials for enterprise system access"""
    system_type: str
    endpoint: str
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    token: Optional[str] = None
    connection_string: Optional[str] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskActivity:
    """Represents a task or activity from enterprise systems"""
    task_id: str
    employee_id: str
    role: str
    department: str
    task_type: str
    complexity_level: int  # 1-10
    skills_required: List[str]
    time_spent: float  # hours
    completion_quality: float  # 0-1
    business_impact: str  # low, medium, high, critical
    timestamp: datetime
    system_source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMetrics(BaseModel):
    """Performance metrics from business systems"""
    employee_id: str
    role: str
    department: str
    kpi_scores: Dict[str, float]
    productivity_metrics: Dict[str, float]
    quality_metrics: Dict[str, float]
    collaboration_score: float
    innovation_score: float
    technical_proficiency: Dict[str, float]
    leadership_indicators: Dict[str, float]
    period_start: datetime
    period_end: datetime
    system_source: str


class SFIALevelSuggestion(BaseModel):
    """SFIA level suggestion for an employee"""
    employee_id: str
    current_role: str
    skill_code: str
    skill_name: str
    current_level: Optional[int]
    suggested_level: int
    confidence_score: float
    reasoning: str
    supporting_evidence: List[str]
    improvement_areas: List[str]
    timeline_estimate: str
    business_justification: str
    timestamp: datetime


class BaseSystemConnector(ABC):
    """Abstract base class for enterprise system connectors"""
    
    def __init__(self, credentials: SystemCredentials, config: Dict[str, Any] = None):
        self.credentials = credentials
        self.config = config or {}
        self.is_connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the system"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the system"""
        pass
    
    @abstractmethod
    async def get_employee_data(self, employee_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Retrieve employee data"""
        pass
    
    @abstractmethod
    async def get_task_activities(self, date_range: tuple = None) -> List[TaskActivity]:
        """Retrieve task and activity data"""
        pass
    
    @abstractmethod
    async def get_performance_metrics(self, employee_ids: Optional[List[str]] = None) -> List[PerformanceMetrics]:
        """Retrieve performance metrics"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Check system connectivity and health"""
        try:
            await self.connect()
            return {
                "status": "healthy",
                "system_type": self.credentials.system_type,
                "endpoint": self.credentials.endpoint,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "system_type": self.credentials.system_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


class SAPConnector(BaseSystemConnector):
    """SAP ERP system connector"""
    
    async def connect(self) -> bool:
        """Connect to SAP system"""
        try:
            # SAP RFC or REST API connection
            self.client = httpx.AsyncClient(
                base_url=self.credentials.endpoint,
                auth=(self.credentials.username, self.credentials.password),
                timeout=30.0
            )
            
            # Test connection
            response = await self.client.get("/sap/bc/rest/test")
            self.is_connected = response.status_code == 200
            return self.is_connected
        except Exception as e:
            logger.error(f"SAP connection failed: {e}")
            return False
    
    async def disconnect(self) -> None:
        if hasattr(self, 'client'):
            await self.client.aclose()
        self.is_connected = False
    
    async def get_employee_data(self, employee_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get employee data from SAP HR module"""
        try:
            params = {}
            if employee_ids:
                params['employee_ids'] = ','.join(employee_ids)
            
            response = await self.client.get("/sap/hr/employees", params=params)
            response.raise_for_status()
            
            return response.json().get('employees', [])
        except Exception as e:
            logger.error(f"Failed to get SAP employee data: {e}")
            return []
    
    async def get_task_activities(self, date_range: tuple = None) -> List[TaskActivity]:
        """Get task activities from SAP project systems"""
        try:
            params = {}
            if date_range:
                params['start_date'] = date_range[0].isoformat()
                params['end_date'] = date_range[1].isoformat()
            
            response = await self.client.get("/sap/ps/activities", params=params)
            response.raise_for_status()
            
            activities = []
            for item in response.json().get('activities', []):
                activities.append(TaskActivity(
                    task_id=item['task_id'],
                    employee_id=item['employee_id'],
                    role=item['role'],
                    department=item['department'],
                    task_type=item['task_type'],
                    complexity_level=item.get('complexity', 5),
                    skills_required=item.get('skills', []),
                    time_spent=item.get('hours', 0),
                    completion_quality=item.get('quality_score', 0.8),
                    business_impact=item.get('impact', 'medium'),
                    timestamp=datetime.fromisoformat(item['timestamp']),
                    system_source='SAP',
                    metadata=item.get('metadata', {})
                ))
            
            return activities
        except Exception as e:
            logger.error(f"Failed to get SAP activities: {e}")
            return []
    
    async def get_performance_metrics(self, employee_ids: Optional[List[str]] = None) -> List[PerformanceMetrics]:
        """Get performance metrics from SAP SuccessFactors"""
        try:
            params = {}
            if employee_ids:
                params['employee_ids'] = ','.join(employee_ids)
            
            response = await self.client.get("/sap/sf/performance", params=params)
            response.raise_for_status()
            
            metrics = []
            for item in response.json().get('performance_data', []):
                metrics.append(PerformanceMetrics(
                    employee_id=item['employee_id'],
                    role=item['role'],
                    department=item['department'],
                    kpi_scores=item.get('kpis', {}),
                    productivity_metrics=item.get('productivity', {}),
                    quality_metrics=item.get('quality', {}),
                    collaboration_score=item.get('collaboration', 0.5),
                    innovation_score=item.get('innovation', 0.5),
                    technical_proficiency=item.get('technical_skills', {}),
                    leadership_indicators=item.get('leadership', {}),
                    period_start=datetime.fromisoformat(item['period_start']),
                    period_end=datetime.fromisoformat(item['period_end']),
                    system_source='SAP'
                ))
            
            return metrics
        except Exception as e:
            logger.error(f"Failed to get SAP performance metrics: {e}")
            return []


class PowerBIConnector(BaseSystemConnector):
    """Microsoft Power BI connector"""
    
    async def connect(self) -> bool:
        """Connect to Power BI REST API"""
        try:
            self.client = httpx.AsyncClient(
                base_url="https://api.powerbi.com/v1.0/myorg",
                headers={"Authorization": f"Bearer {self.credentials.token}"},
                timeout=30.0
            )
            
            # Test connection
            response = await self.client.get("/groups")
            self.is_connected = response.status_code == 200
            return self.is_connected
        except Exception as e:
            logger.error(f"Power BI connection failed: {e}")
            return False
    
    async def disconnect(self) -> None:
        if hasattr(self, 'client'):
            await self.client.aclose()
        self.is_connected = False
    
    async def get_employee_data(self, employee_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get employee data from Power BI datasets"""
        try:
            # Query Power BI dataset for employee information
            dataset_id = self.config.get('employee_dataset_id')
            query = {
                "queries": [{
                    "query": f"EVALUATE FILTER(Employees, Employees[Status] = \"Active\")"
                }]
            }
            
            if employee_ids:
                ids_filter = "', '".join(employee_ids)
                query["queries"][0]["query"] = f"EVALUATE FILTER(Employees, Employees[EmployeeID] IN {{'{ids_filter}'}})"
            
            response = await self.client.post(f"/datasets/{dataset_id}/executeQueries", json=query)
            response.raise_for_status()
            
            return response.json().get('results', [{}])[0].get('tables', [{}])[0].get('rows', [])
        except Exception as e:
            logger.error(f"Failed to get Power BI employee data: {e}")
            return []
    
    async def get_task_activities(self, date_range: tuple = None) -> List[TaskActivity]:
        """Get task activities from Power BI datasets"""
        try:
            dataset_id = self.config.get('activities_dataset_id')
            date_filter = ""
            if date_range:
                date_filter = f" AND Activities[Date] >= DATE({date_range[0].year}, {date_range[0].month}, {date_range[0].day}) AND Activities[Date] <= DATE({date_range[1].year}, {date_range[1].month}, {date_range[1].day})"
            
            query = {
                "queries": [{
                    "query": f"EVALUATE FILTER(Activities, Activities[Status] = \"Completed\"{date_filter})"
                }]
            }
            
            response = await self.client.post(f"/datasets/{dataset_id}/executeQueries", json=query)
            response.raise_for_status()
            
            activities = []
            for row in response.json().get('results', [{}])[0].get('tables', [{}])[0].get('rows', []):
                activities.append(TaskActivity(
                    task_id=str(row.get('Activities[TaskID]', '')),
                    employee_id=str(row.get('Activities[EmployeeID]', '')),
                    role=row.get('Activities[Role]', ''),
                    department=row.get('Activities[Department]', ''),
                    task_type=row.get('Activities[TaskType]', ''),
                    complexity_level=int(row.get('Activities[Complexity]', 5)),
                    skills_required=row.get('Activities[Skills]', '').split(',') if row.get('Activities[Skills]') else [],
                    time_spent=float(row.get('Activities[Hours]', 0)),
                    completion_quality=float(row.get('Activities[Quality]', 0.8)),
                    business_impact=row.get('Activities[Impact]', 'medium'),
                    timestamp=datetime.fromisoformat(row.get('Activities[Date]', datetime.now().isoformat())),
                    system_source='PowerBI',
                    metadata={'source_dataset': dataset_id}
                ))
            
            return activities
        except Exception as e:
            logger.error(f"Failed to get Power BI activities: {e}")
            return []
    
    async def get_performance_metrics(self, employee_ids: Optional[List[str]] = None) -> List[PerformanceMetrics]:
        """Get performance metrics from Power BI dashboards"""
        try:
            dataset_id = self.config.get('performance_dataset_id')
            
            employee_filter = ""
            if employee_ids:
                ids_filter = "', '".join(employee_ids)
                employee_filter = f" AND Performance[EmployeeID] IN {{'{ids_filter}'}}"
            
            query = {
                "queries": [{
                    "query": f"EVALUATE FILTER(Performance, Performance[Period] = \"Current\"{employee_filter})"
                }]
            }
            
            response = await self.client.post(f"/datasets/{dataset_id}/executeQueries", json=query)
            response.raise_for_status()
            
            metrics = []
            for row in response.json().get('results', [{}])[0].get('tables', [{}])[0].get('rows', []):
                metrics.append(PerformanceMetrics(
                    employee_id=str(row.get('Performance[EmployeeID]', '')),
                    role=row.get('Performance[Role]', ''),
                    department=row.get('Performance[Department]', ''),
                    kpi_scores=json.loads(row.get('Performance[KPIs]', '{}')),
                    productivity_metrics=json.loads(row.get('Performance[Productivity]', '{}')),
                    quality_metrics=json.loads(row.get('Performance[Quality]', '{}')),
                    collaboration_score=float(row.get('Performance[Collaboration]', 0.5)),
                    innovation_score=float(row.get('Performance[Innovation]', 0.5)),
                    technical_proficiency=json.loads(row.get('Performance[TechnicalSkills]', '{}')),
                    leadership_indicators=json.loads(row.get('Performance[Leadership]', '{}')),
                    period_start=datetime.fromisoformat(row.get('Performance[PeriodStart]', datetime.now().isoformat())),
                    period_end=datetime.fromisoformat(row.get('Performance[PeriodEnd]', datetime.now().isoformat())),
                    system_source='PowerBI'
                ))
            
            return metrics
        except Exception as e:
            logger.error(f"Failed to get Power BI performance metrics: {e}")
            return []


class DatabaseConnector(BaseSystemConnector):
    """Generic database connector for SQL databases"""
    
    async def connect(self) -> bool:
        """Connect to database"""
        try:
            self.engine = create_async_engine(self.credentials.connection_string)
            
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    async def disconnect(self) -> None:
        if hasattr(self, 'engine'):
            await self.engine.dispose()
        self.is_connected = False
    
    async def get_employee_data(self, employee_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get employee data from database"""
        try:
            query = "SELECT * FROM employees WHERE status = 'active'"
            params = {}
            
            if employee_ids:
                placeholders = ','.join([f':id_{i}' for i in range(len(employee_ids))])
                query += f" AND employee_id IN ({placeholders})"
                params.update({f'id_{i}': emp_id for i, emp_id in enumerate(employee_ids)})
            
            async with self.engine.begin() as conn:
                result = await conn.execute(text(query), params)
                rows = result.fetchall()
                
                return [dict(row._mapping) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get database employee data: {e}")
            return []
    
    async def get_task_activities(self, date_range: tuple = None) -> List[TaskActivity]:
        """Get task activities from database"""
        try:
            query = "SELECT * FROM task_activities WHERE status = 'completed'"
            params = {}
            
            if date_range:
                query += " AND created_date BETWEEN :start_date AND :end_date"
                params.update({
                    'start_date': date_range[0],
                    'end_date': date_range[1]
                })
            
            async with self.engine.begin() as conn:
                result = await conn.execute(text(query), params)
                rows = result.fetchall()
                
                activities = []
                for row in rows:
                    row_dict = dict(row._mapping)
                    activities.append(TaskActivity(
                        task_id=str(row_dict.get('task_id', '')),
                        employee_id=str(row_dict.get('employee_id', '')),
                        role=row_dict.get('role', ''),
                        department=row_dict.get('department', ''),
                        task_type=row_dict.get('task_type', ''),
                        complexity_level=int(row_dict.get('complexity_level', 5)),
                        skills_required=row_dict.get('skills_required', '').split(',') if row_dict.get('skills_required') else [],
                        time_spent=float(row_dict.get('time_spent', 0)),
                        completion_quality=float(row_dict.get('completion_quality', 0.8)),
                        business_impact=row_dict.get('business_impact', 'medium'),
                        timestamp=row_dict.get('created_date', datetime.now()),
                        system_source='Database',
                        metadata={'table': 'task_activities'}
                    ))
                
                return activities
        except Exception as e:
            logger.error(f"Failed to get database activities: {e}")
            return []
    
    async def get_performance_metrics(self, employee_ids: Optional[List[str]] = None) -> List[PerformanceMetrics]:
        """Get performance metrics from database"""
        try:
            query = "SELECT * FROM performance_metrics WHERE period_end >= :current_period"
            params = {'current_period': datetime.now() - timedelta(days=90)}
            
            if employee_ids:
                placeholders = ','.join([f':id_{i}' for i in range(len(employee_ids))])
                query += f" AND employee_id IN ({placeholders})"
                params.update({f'id_{i}': emp_id for i, emp_id in enumerate(employee_ids)})
            
            async with self.engine.begin() as conn:
                result = await conn.execute(text(query), params)
                rows = result.fetchall()
                
                metrics = []
                for row in rows:
                    row_dict = dict(row._mapping)
                    metrics.append(PerformanceMetrics(
                        employee_id=str(row_dict.get('employee_id', '')),
                        role=row_dict.get('role', ''),
                        department=row_dict.get('department', ''),
                        kpi_scores=json.loads(row_dict.get('kpi_scores', '{}')),
                        productivity_metrics=json.loads(row_dict.get('productivity_metrics', '{}')),
                        quality_metrics=json.loads(row_dict.get('quality_metrics', '{}')),
                        collaboration_score=float(row_dict.get('collaboration_score', 0.5)),
                        innovation_score=float(row_dict.get('innovation_score', 0.5)),
                        technical_proficiency=json.loads(row_dict.get('technical_proficiency', '{}')),
                        leadership_indicators=json.loads(row_dict.get('leadership_indicators', '{}')),
                        period_start=row_dict.get('period_start', datetime.now()),
                        period_end=row_dict.get('period_end', datetime.now()),
                        system_source='Database'
                    ))
                
                return metrics
        except Exception as e:
            logger.error(f"Failed to get database performance metrics: {e}")
            return []


class KafkaConnector(BaseSystemConnector):
    """Apache Kafka connector for real-time data streaming"""
    
    async def connect(self) -> bool:
        """Connect to Kafka cluster"""
        try:
            self.consumer = Consumer({
                'bootstrap.servers': self.credentials.endpoint,
                'group.id': self.config.get('group_id', 'intellisfia-consumer'),
                'auto.offset.reset': 'latest'
            })
            
            self.producer = Producer({
                'bootstrap.servers': self.credentials.endpoint
            })
            
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Kafka connection failed: {e}")
            return False
    
    async def disconnect(self) -> None:
        if hasattr(self, 'consumer'):
            self.consumer.close()
        if hasattr(self, 'producer'):
            self.producer.flush()
        self.is_connected = False
    
    async def consume_real_time_data(self, topics: List[str], callback: Callable) -> None:
        """Consume real-time data from Kafka topics"""
        try:
            self.consumer.subscribe(topics)
            
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                
                if msg.error():
                    logger.error(f"Kafka consumer error: {msg.error()}")
                    continue
                
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    await callback(data, msg.topic())
                except Exception as e:
                    logger.error(f"Error processing Kafka message: {e}")
        except Exception as e:
            logger.error(f"Kafka consumption error: {e}")
    
    async def get_employee_data(self, employee_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Not applicable for Kafka - real-time streaming only"""
        return []
    
    async def get_task_activities(self, date_range: tuple = None) -> List[TaskActivity]:
        """Not applicable for Kafka - real-time streaming only"""
        return []
    
    async def get_performance_metrics(self, employee_ids: Optional[List[str]] = None) -> List[PerformanceMetrics]:
        """Not applicable for Kafka - real-time streaming only"""
        return []


class MongoDBConnector(BaseSystemConnector):
    """MongoDB connector for document-based data"""
    
    async def connect(self) -> bool:
        """Connect to MongoDB"""
        try:
            self.client = pymongo.MongoClient(
                self.credentials.connection_string,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.config.get('database', 'intellisfia')]
            
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False
    
    async def disconnect(self) -> None:
        if hasattr(self, 'client'):
            self.client.close()
        self.is_connected = False
    
    async def get_employee_data(self, employee_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get employee data from MongoDB"""
        try:
            collection = self.db[self.config.get('employees_collection', 'employees')]
            
            query = {'status': 'active'}
            if employee_ids:
                query['employee_id'] = {'$in': employee_ids}
            
            cursor = collection.find(query)
            return list(cursor)
        except Exception as e:
            logger.error(f"Failed to get MongoDB employee data: {e}")
            return []
    
    async def get_task_activities(self, date_range: tuple = None) -> List[TaskActivity]:
        """Get task activities from MongoDB"""
        try:
            collection = self.db[self.config.get('activities_collection', 'task_activities')]
            
            query = {'status': 'completed'}
            if date_range:
                query['timestamp'] = {
                    '$gte': date_range[0],
                    '$lte': date_range[1]
                }
            
            activities = []
            for doc in collection.find(query):
                activities.append(TaskActivity(
                    task_id=str(doc.get('task_id', '')),
                    employee_id=str(doc.get('employee_id', '')),
                    role=doc.get('role', ''),
                    department=doc.get('department', ''),
                    task_type=doc.get('task_type', ''),
                    complexity_level=int(doc.get('complexity_level', 5)),
                    skills_required=doc.get('skills_required', []),
                    time_spent=float(doc.get('time_spent', 0)),
                    completion_quality=float(doc.get('completion_quality', 0.8)),
                    business_impact=doc.get('business_impact', 'medium'),
                    timestamp=doc.get('timestamp', datetime.now()),
                    system_source='MongoDB',
                    metadata=doc.get('metadata', {})
                ))
            
            return activities
        except Exception as e:
            logger.error(f"Failed to get MongoDB activities: {e}")
            return []
    
    async def get_performance_metrics(self, employee_ids: Optional[List[str]] = None) -> List[PerformanceMetrics]:
        """Get performance metrics from MongoDB"""
        try:
            collection = self.db[self.config.get('performance_collection', 'performance_metrics')]
            
            query = {'period_end': {'$gte': datetime.now() - timedelta(days=90)}}
            if employee_ids:
                query['employee_id'] = {'$in': employee_ids}
            
            metrics = []
            for doc in collection.find(query):
                metrics.append(PerformanceMetrics(
                    employee_id=str(doc.get('employee_id', '')),
                    role=doc.get('role', ''),
                    department=doc.get('department', ''),
                    kpi_scores=doc.get('kpi_scores', {}),
                    productivity_metrics=doc.get('productivity_metrics', {}),
                    quality_metrics=doc.get('quality_metrics', {}),
                    collaboration_score=float(doc.get('collaboration_score', 0.5)),
                    innovation_score=float(doc.get('innovation_score', 0.5)),
                    technical_proficiency=doc.get('technical_proficiency', {}),
                    leadership_indicators=doc.get('leadership_indicators', {}),
                    period_start=doc.get('period_start', datetime.now()),
                    period_end=doc.get('period_end', datetime.now()),
                    system_source='MongoDB'
                ))
            
            return metrics
        except Exception as e:
            logger.error(f"Failed to get MongoDB performance metrics: {e}")
            return []


# Factory function for creating connectors
def create_connector(system_type: str, credentials: SystemCredentials, config: Dict[str, Any] = None) -> BaseSystemConnector:
    """Factory function to create appropriate system connector"""
    connectors = {
        'sap': SAPConnector,
        'powerbi': PowerBIConnector,
        'database': DatabaseConnector,
        'sql': DatabaseConnector,
        'postgresql': DatabaseConnector,
        'mysql': DatabaseConnector,
        'oracle': DatabaseConnector,
        'kafka': KafkaConnector,
        'mongodb': MongoDBConnector,
        'mongo': MongoDBConnector
    }
    
    connector_class = connectors.get(system_type.lower())
    if not connector_class:
        raise ValueError(f"Unsupported system type: {system_type}")
    
    return connector_class(credentials, config)