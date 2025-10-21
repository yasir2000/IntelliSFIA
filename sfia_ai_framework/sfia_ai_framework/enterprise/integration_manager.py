"""
Enterprise Integration Manager

This module orchestrates the integration with multiple enterprise systems
and provides a unified interface for real-time SFIA analysis.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import json
import yaml
from pathlib import Path

from .connectors import (
    BaseSystemConnector, create_connector, SystemCredentials,
    TaskActivity, PerformanceMetrics, SFIALevelSuggestion
)
from .real_time_engine import RealTimeAnalysisEngine

logger = logging.getLogger(__name__)


@dataclass
class IntegrationConfig:
    """Configuration for enterprise integration"""
    systems: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    real_time_enabled: bool = True
    batch_interval: int = 3600  # seconds
    cache_ttl: int = 1800  # seconds
    max_concurrent_connections: int = 10
    retry_attempts: int = 3
    retry_delay: int = 5  # seconds
    analysis_config: Dict[str, Any] = field(default_factory=dict)


class EnterpriseIntegrationManager:
    """Manages integration with multiple enterprise systems"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = IntegrationConfig()
        self.connectors: Dict[str, BaseSystemConnector] = {}
        self.analysis_engine = None
        self.is_running = False
        self.background_tasks: Set[asyncio.Task] = set()
        self.data_callbacks: List[Callable] = []
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """Load configuration from file"""
        try:
            path = Path(config_path)
            if path.suffix.lower() in ['.yaml', '.yml']:
                with open(path, 'r') as f:
                    config_data = yaml.safe_load(f)
            else:
                with open(path, 'r') as f:
                    config_data = json.load(f)
            
            self.config = IntegrationConfig(**config_data)
            logger.info(f"Loaded configuration from {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    async def initialize(self, redis_url: str = "redis://localhost:6379"):
        """Initialize the integration manager"""
        try:
            # Initialize analysis engine
            self.analysis_engine = RealTimeAnalysisEngine(redis_url)
            await self.analysis_engine.initialize()
            
            # Initialize system connectors
            await self._initialize_connectors()
            
            # Start background tasks if real-time is enabled
            if self.config.real_time_enabled:
                await self._start_background_tasks()
            
            self.is_running = True
            logger.info("Enterprise integration manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize integration manager: {e}")
            raise
    
    async def _initialize_connectors(self):
        """Initialize all configured system connectors"""
        semaphore = asyncio.Semaphore(self.config.max_concurrent_connections)
        
        async def init_connector(system_name: str, system_config: Dict[str, Any]):
            async with semaphore:
                try:
                    credentials = SystemCredentials(**system_config['credentials'])
                    connector_config = system_config.get('config', {})
                    
                    connector = create_connector(
                        system_config['type'],
                        credentials,
                        connector_config
                    )
                    
                    # Test connection with retry logic
                    for attempt in range(self.config.retry_attempts):
                        try:
                            if await connector.connect():
                                self.connectors[system_name] = connector
                                logger.info(f"Connected to {system_name}")
                                break
                        except Exception as e:
                            if attempt == self.config.retry_attempts - 1:
                                logger.error(f"Failed to connect to {system_name} after {self.config.retry_attempts} attempts: {e}")
                            else:
                                logger.warning(f"Connection attempt {attempt + 1} failed for {system_name}: {e}")
                                await asyncio.sleep(self.config.retry_delay)
                
                except Exception as e:
                    logger.error(f"Failed to initialize connector for {system_name}: {e}")
        
        tasks = [init_connector(name, config) for name, config in self.config.systems.items()]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _start_background_tasks(self):
        """Start background tasks for real-time processing"""
        # Batch processing task
        batch_task = asyncio.create_task(self._batch_processing_loop())
        self.background_tasks.add(batch_task)
        batch_task.add_done_callback(self.background_tasks.discard)
        
        # Health monitoring task
        health_task = asyncio.create_task(self._health_monitoring_loop())
        self.background_tasks.add(health_task)
        health_task.add_done_callback(self.background_tasks.discard)
        
        # Real-time streaming tasks for Kafka connectors
        for name, connector in self.connectors.items():
            if hasattr(connector, 'consume_real_time_data'):
                stream_task = asyncio.create_task(self._start_real_time_streaming(name, connector))
                self.background_tasks.add(stream_task)
                stream_task.add_done_callback(self.background_tasks.discard)
    
    async def _batch_processing_loop(self):
        """Periodic batch processing of all systems"""
        while self.is_running:
            try:
                logger.info("Starting batch processing cycle")
                
                # Get data from all systems
                all_employee_data = {}
                all_performance_data = {}
                
                for system_name, connector in self.connectors.items():
                    try:
                        # Get activities from last batch interval
                        end_time = datetime.now()
                        start_time = end_time - timedelta(seconds=self.config.batch_interval)
                        
                        activities = await connector.get_task_activities((start_time, end_time))
                        performance_metrics = await connector.get_performance_metrics()
                        
                        # Group by employee
                        for activity in activities:
                            if activity.employee_id not in all_employee_data:
                                all_employee_data[activity.employee_id] = []
                            all_employee_data[activity.employee_id].append(activity)
                        
                        for metric in performance_metrics:
                            all_performance_data[metric.employee_id] = metric
                        
                        logger.info(f"Processed {len(activities)} activities and {len(performance_metrics)} performance records from {system_name}")
                        
                    except Exception as e:
                        logger.error(f"Error processing data from {system_name}: {e}")
                
                # Analyze all employees
                if all_employee_data and self.analysis_engine:
                    results = await self.analysis_engine.batch_analyze_organization(
                        all_employee_data, all_performance_data
                    )
                    
                    # Trigger callbacks
                    await self._trigger_callbacks('batch_analysis', results)
                    
                    logger.info(f"Completed batch analysis for {len(results)} employees")
                
            except Exception as e:
                logger.error(f"Error in batch processing: {e}")
            
            # Wait for next cycle
            await asyncio.sleep(self.config.batch_interval)
    
    async def _health_monitoring_loop(self):
        """Monitor health of all connected systems"""
        while self.is_running:
            try:
                health_results = {}
                
                for system_name, connector in self.connectors.items():
                    health_results[system_name] = await connector.health_check()
                
                # Log unhealthy systems
                for system_name, health in health_results.items():
                    if health['status'] != 'healthy':
                        logger.warning(f"System {system_name} is unhealthy: {health.get('error', 'Unknown error')}")
                
                # Trigger health callbacks
                await self._trigger_callbacks('health_check', health_results)
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
            
            # Check every 5 minutes
            await asyncio.sleep(300)
    
    async def _start_real_time_streaming(self, system_name: str, connector):
        """Start real-time streaming for Kafka-like connectors"""
        try:
            topics = self.config.systems[system_name].get('topics', ['activities', 'performance'])
            
            async def process_message(data: Dict[str, Any], topic: str):
                try:
                    if topic == 'activities':
                        # Process activity data
                        activity = TaskActivity(**data)
                        await self._process_real_time_activity(activity)
                    elif topic == 'performance':
                        # Process performance data
                        performance = PerformanceMetrics(**data)
                        await self._process_real_time_performance(performance)
                    
                except Exception as e:
                    logger.error(f"Error processing real-time message from {system_name}: {e}")
            
            await connector.consume_real_time_data(topics, process_message)
            
        except Exception as e:
            logger.error(f"Error in real-time streaming for {system_name}: {e}")
    
    async def _process_real_time_activity(self, activity: TaskActivity):
        """Process a real-time activity"""
        try:
            # Get recent activities for the employee
            activities = await self._get_employee_recent_activities(activity.employee_id)
            activities.append(activity)
            
            # Get performance data
            performance = await self._get_employee_performance(activity.employee_id)
            
            if performance and self.analysis_engine:
                # Analyze in real-time
                suggestions = await self.analysis_engine.analyze_employee_real_time(
                    activity.employee_id, activities, performance, activity.role
                )
                
                # Trigger real-time callbacks
                await self._trigger_callbacks('real_time_analysis', {
                    'employee_id': activity.employee_id,
                    'suggestions': suggestions,
                    'trigger_activity': activity
                })
        
        except Exception as e:
            logger.error(f"Error processing real-time activity: {e}")
    
    async def _process_real_time_performance(self, performance: PerformanceMetrics):
        """Process real-time performance data"""
        try:
            # Get recent activities for the employee
            activities = await self._get_employee_recent_activities(performance.employee_id)
            
            if activities and self.analysis_engine:
                # Analyze in real-time
                suggestions = await self.analysis_engine.analyze_employee_real_time(
                    performance.employee_id, activities, performance, performance.role
                )
                
                # Trigger real-time callbacks
                await self._trigger_callbacks('real_time_analysis', {
                    'employee_id': performance.employee_id,
                    'suggestions': suggestions,
                    'trigger_performance': performance
                })
        
        except Exception as e:
            logger.error(f"Error processing real-time performance: {e}")
    
    async def _get_employee_recent_activities(self, employee_id: str, days: int = 30) -> List[TaskActivity]:
        """Get recent activities for an employee from all systems"""
        all_activities = []
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        for connector in self.connectors.values():
            try:
                activities = await connector.get_task_activities((start_time, end_time))
                employee_activities = [a for a in activities if a.employee_id == employee_id]
                all_activities.extend(employee_activities)
            except Exception as e:
                logger.error(f"Error getting activities for {employee_id}: {e}")
        
        return sorted(all_activities, key=lambda x: x.timestamp, reverse=True)
    
    async def _get_employee_performance(self, employee_id: str) -> Optional[PerformanceMetrics]:
        """Get performance data for an employee from all systems"""
        for connector in self.connectors.values():
            try:
                performance_data = await connector.get_performance_metrics([employee_id])
                if performance_data:
                    return performance_data[0]  # Return the first/most recent
            except Exception as e:
                logger.error(f"Error getting performance for {employee_id}: {e}")
        
        return None
    
    async def _trigger_callbacks(self, event_type: str, data: Any):
        """Trigger registered callbacks"""
        for callback in self.data_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, data)
                else:
                    callback(event_type, data)
            except Exception as e:
                logger.error(f"Error in callback: {e}")
    
    def register_callback(self, callback: Callable):
        """Register a callback for data events"""
        self.data_callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable):
        """Unregister a callback"""
        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)
    
    async def analyze_employee(self, employee_id: str) -> List[SFIALevelSuggestion]:
        """Analyze a specific employee on-demand"""
        try:
            activities = await self._get_employee_recent_activities(employee_id)
            performance = await self._get_employee_performance(employee_id)
            
            if not activities:
                logger.warning(f"No activities found for employee {employee_id}")
                return []
            
            if not performance:
                logger.warning(f"No performance data found for employee {employee_id}")
                return []
            
            if not self.analysis_engine:
                logger.error("Analysis engine not initialized")
                return []
            
            return await self.analysis_engine.analyze_employee_real_time(
                employee_id, activities, performance, performance.role
            )
            
        except Exception as e:
            logger.error(f"Error analyzing employee {employee_id}: {e}")
            return []
    
    async def analyze_department(self, department: str) -> Dict[str, List[SFIALevelSuggestion]]:
        """Analyze all employees in a department"""
        try:
            department_results = {}
            
            # Get all employees from all systems
            all_employees = set()
            for connector in self.connectors.values():
                try:
                    employee_data = await connector.get_employee_data()
                    department_employees = [emp for emp in employee_data 
                                          if emp.get('department', '').lower() == department.lower()]
                    all_employees.update(emp['employee_id'] for emp in department_employees if 'employee_id' in emp)
                except Exception as e:
                    logger.error(f"Error getting employees for department {department}: {e}")
            
            # Analyze each employee
            for employee_id in all_employees:
                suggestions = await self.analyze_employee(employee_id)
                if suggestions:
                    department_results[employee_id] = suggestions
            
            return department_results
            
        except Exception as e:
            logger.error(f"Error analyzing department {department}: {e}")
            return {}
    
    async def get_organization_insights(self) -> Dict[str, Any]:
        """Get organization-wide insights"""
        try:
            insights = {
                'total_employees': 0,
                'departments': {},
                'skill_distribution': {},
                'level_distribution': {},
                'improvement_opportunities': [],
                'high_performers': [],
                'skill_gaps': []
            }
            
            # Get all employee data
            all_employees = {}
            for system_name, connector in self.connectors.items():
                try:
                    employees = await connector.get_employee_data()
                    for emp in employees:
                        if 'employee_id' in emp:
                            all_employees[emp['employee_id']] = emp
                except Exception as e:
                    logger.error(f"Error getting employees from {system_name}: {e}")
            
            insights['total_employees'] = len(all_employees)
            
            # Analyze each employee and aggregate insights
            for employee_id, emp_data in all_employees.items():
                suggestions = await self.analyze_employee(employee_id)
                
                department = emp_data.get('department', 'Unknown')
                if department not in insights['departments']:
                    insights['departments'][department] = {
                        'employee_count': 0,
                        'avg_level': 0,
                        'skills': set()
                    }
                
                insights['departments'][department]['employee_count'] += 1
                
                for suggestion in suggestions:
                    # Update skill distribution
                    skill = suggestion.skill_name
                    if skill not in insights['skill_distribution']:
                        insights['skill_distribution'][skill] = {
                            'employees': 0,
                            'avg_level': 0,
                            'total_level': 0
                        }
                    
                    insights['skill_distribution'][skill]['employees'] += 1
                    insights['skill_distribution'][skill]['total_level'] += suggestion.suggested_level
                    insights['skill_distribution'][skill]['avg_level'] = (
                        insights['skill_distribution'][skill]['total_level'] / 
                        insights['skill_distribution'][skill]['employees']
                    )
                    
                    # Update level distribution
                    level = suggestion.suggested_level
                    if level not in insights['level_distribution']:
                        insights['level_distribution'][level] = 0
                    insights['level_distribution'][level] += 1
                    
                    # Track department skills
                    insights['departments'][department]['skills'].add(skill)
                    
                    # Identify improvement opportunities
                    if suggestion.improvement_areas:
                        insights['improvement_opportunities'].extend([
                            {
                                'employee_id': employee_id,
                                'skill': skill,
                                'current_level': suggestion.suggested_level,
                                'improvements': suggestion.improvement_areas
                            }
                        ])
                    
                    # Identify high performers
                    if suggestion.confidence_score > 0.9 and suggestion.suggested_level >= 5:
                        insights['high_performers'].append({
                            'employee_id': employee_id,
                            'skill': skill,
                            'level': suggestion.suggested_level,
                            'confidence': suggestion.confidence_score
                        })
            
            # Convert sets to lists for JSON serialization
            for dept in insights['departments'].values():
                dept['skills'] = list(dept['skills'])
            
            # Calculate department averages
            for dept_data in insights['departments'].values():
                if dept_data['employee_count'] > 0:
                    total_levels = sum(insights['level_distribution'].keys()) * len(insights['level_distribution'])
                    dept_data['avg_level'] = total_levels / dept_data['employee_count'] if dept_data['employee_count'] > 0 else 0
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting organization insights: {e}")
            return {}
    
    async def shutdown(self):
        """Shutdown the integration manager"""
        try:
            self.is_running = False
            
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Close all connectors
            for connector in self.connectors.values():
                await connector.disconnect()
            
            # Close analysis engine
            if self.analysis_engine:
                await self.analysis_engine.close()
            
            logger.info("Enterprise integration manager shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    @asynccontextmanager
    async def managed_lifecycle(self, redis_url: str = "redis://localhost:6379"):
        """Context manager for managing the lifecycle"""
        try:
            await self.initialize(redis_url)
            yield self
        finally:
            await self.shutdown()