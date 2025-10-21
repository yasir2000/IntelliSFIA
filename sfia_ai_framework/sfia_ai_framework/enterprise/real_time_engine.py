"""
Real-time SFIA Analysis Engine

This module provides real-time analysis capabilities for automatically weighing,
reasoning about tasks and activities, and suggesting SFIA levels for roles and employees.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import redis.asyncio as redis
from pydantic import BaseModel
import json

from .connectors import TaskActivity, PerformanceMetrics, SFIALevelSuggestion

logger = logging.getLogger(__name__)


@dataclass
class ActivityWeights:
    """Weights for different activity characteristics"""
    complexity_weight: float = 0.25
    impact_weight: float = 0.20
    quality_weight: float = 0.15
    time_efficiency_weight: float = 0.15
    skills_breadth_weight: float = 0.10
    innovation_weight: float = 0.10
    leadership_weight: float = 0.05


@dataclass
class SFIALevelCriteria:
    """Criteria for SFIA level assessment"""
    level: int
    autonomy_score: float  # 0-1
    influence_score: float  # 0-1
    complexity_score: float  # 0-1
    business_skills_score: float  # 0-1
    required_experience: int  # years
    min_performance_threshold: float  # 0-1


class RealTimeAnalysisEngine:
    """Real-time analysis engine for SFIA level suggestions"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.activity_weights = ActivityWeights()
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)
        
        # SFIA level criteria mapping
        self.sfia_criteria = {
            1: SFIALevelCriteria(1, 0.1, 0.0, 0.2, 0.1, 0, 0.6),
            2: SFIALevelCriteria(2, 0.2, 0.1, 0.3, 0.2, 1, 0.65),
            3: SFIALevelCriteria(3, 0.4, 0.2, 0.5, 0.3, 2, 0.7),
            4: SFIALevelCriteria(4, 0.6, 0.4, 0.6, 0.5, 4, 0.75),
            5: SFIALevelCriteria(5, 0.7, 0.6, 0.7, 0.6, 6, 0.8),
            6: SFIALevelCriteria(6, 0.8, 0.7, 0.8, 0.7, 8, 0.85),
            7: SFIALevelCriteria(7, 0.9, 0.8, 0.9, 0.8, 10, 0.9)
        }
        
        # Initialize models
        self._initialize_models()
    
    async def initialize(self):
        """Initialize Redis connection and load models"""
        self.redis_client = redis.from_url(self.redis_url)
        await self._load_models()
    
    def _initialize_models(self):
        """Initialize ML models"""
        # SFIA level prediction model
        self.models['sfia_level'] = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        )
        
        # Performance prediction model
        self.models['performance'] = GradientBoostingRegressor(
            n_estimators=100,
            random_state=42
        )
        
        # Skill proficiency model
        self.models['skill_proficiency'] = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        
        # Activity complexity model
        self.models['complexity'] = RandomForestClassifier(
            n_estimators=50,
            random_state=42
        )
        
        # Initialize scalers and encoders
        self.scalers['activity_features'] = StandardScaler()
        self.scalers['performance_features'] = StandardScaler()
        self.encoders['department'] = LabelEncoder()
        self.encoders['role'] = LabelEncoder()
        self.encoders['task_type'] = LabelEncoder()
    
    async def _load_models(self):
        """Load pre-trained models from cache or train new ones"""
        try:
            # Try to load from Redis cache
            for model_name in self.models.keys():
                cached_model = await self.redis_client.get(f"model:{model_name}")
                if cached_model:
                    self.models[model_name] = joblib.loads(cached_model)
                    logger.info(f"Loaded model {model_name} from cache")
            
            # Load scalers and encoders
            for scaler_name in self.scalers.keys():
                cached_scaler = await self.redis_client.get(f"scaler:{scaler_name}")
                if cached_scaler:
                    self.scalers[scaler_name] = joblib.loads(cached_scaler)
            
            for encoder_name in self.encoders.keys():
                cached_encoder = await self.redis_client.get(f"encoder:{encoder_name}")
                if cached_encoder:
                    self.encoders[encoder_name] = joblib.loads(cached_encoder)
                    
        except Exception as e:
            logger.warning(f"Could not load models from cache: {e}")
    
    async def save_models(self):
        """Save models to cache"""
        try:
            for model_name, model in self.models.items():
                serialized_model = joblib.dumps(model)
                await self.redis_client.set(f"model:{model_name}", serialized_model, ex=86400)  # 24 hours
            
            for scaler_name, scaler in self.scalers.items():
                serialized_scaler = joblib.dumps(scaler)
                await self.redis_client.set(f"scaler:{scaler_name}", serialized_scaler, ex=86400)
            
            for encoder_name, encoder in self.encoders.items():
                serialized_encoder = joblib.dumps(encoder)
                await self.redis_client.set(f"encoder:{encoder_name}", serialized_encoder, ex=86400)
                
            logger.info("Models saved to cache")
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
    
    def extract_activity_features(self, activities: List[TaskActivity]) -> np.ndarray:
        """Extract features from task activities"""
        features = []
        
        for activity in activities:
            feature_vector = [
                activity.complexity_level / 10.0,  # Normalized complexity
                activity.time_spent,
                activity.completion_quality,
                len(activity.skills_required),
                1.0 if activity.business_impact == 'critical' else 
                0.75 if activity.business_impact == 'high' else
                0.5 if activity.business_impact == 'medium' else 0.25,
                # Add more features as needed
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def extract_performance_features(self, metrics: PerformanceMetrics) -> np.ndarray:
        """Extract features from performance metrics"""
        kpi_avg = np.mean(list(metrics.kpi_scores.values())) if metrics.kpi_scores else 0.5
        productivity_avg = np.mean(list(metrics.productivity_metrics.values())) if metrics.productivity_metrics else 0.5
        quality_avg = np.mean(list(metrics.quality_metrics.values())) if metrics.quality_metrics else 0.5
        technical_avg = np.mean(list(metrics.technical_proficiency.values())) if metrics.technical_proficiency else 0.5
        leadership_avg = np.mean(list(metrics.leadership_indicators.values())) if metrics.leadership_indicators else 0.5
        
        features = [
            kpi_avg,
            productivity_avg,
            quality_avg,
            metrics.collaboration_score,
            metrics.innovation_score,
            technical_avg,
            leadership_avg
        ]
        
        return np.array(features).reshape(1, -1)
    
    def calculate_autonomy_score(self, activities: List[TaskActivity], performance: PerformanceMetrics) -> float:
        """Calculate autonomy score based on activities and performance"""
        if not activities:
            return 0.0
        
        # Factors contributing to autonomy
        avg_complexity = np.mean([a.complexity_level for a in activities]) / 10.0
        quality_consistency = 1.0 - np.std([a.completion_quality for a in activities])
        self_directed_tasks = sum(1 for a in activities if 'independent' in a.task_type.lower()) / len(activities)
        
        # Performance indicators
        performance_score = np.mean(list(performance.kpi_scores.values())) if performance.kpi_scores else 0.5
        
        autonomy_score = (
            avg_complexity * 0.3 +
            quality_consistency * 0.3 +
            self_directed_tasks * 0.2 +
            performance_score * 0.2
        )
        
        return min(1.0, max(0.0, autonomy_score))
    
    def calculate_influence_score(self, activities: List[TaskActivity], performance: PerformanceMetrics) -> float:
        """Calculate influence score based on activities and performance"""
        if not activities:
            return 0.0
        
        # Leadership and collaboration indicators
        leadership_tasks = sum(1 for a in activities if any(skill in ['leadership', 'management', 'coaching'] 
                                                           for skill in a.skills_required)) / len(activities)
        
        high_impact_tasks = sum(1 for a in activities if a.business_impact in ['high', 'critical']) / len(activities)
        
        collaboration_score = performance.collaboration_score
        leadership_avg = np.mean(list(performance.leadership_indicators.values())) if performance.leadership_indicators else 0.0
        
        influence_score = (
            leadership_tasks * 0.3 +
            high_impact_tasks * 0.3 +
            collaboration_score * 0.2 +
            leadership_avg * 0.2
        )
        
        return min(1.0, max(0.0, influence_score))
    
    def calculate_complexity_score(self, activities: List[TaskActivity]) -> float:
        """Calculate complexity score based on activities"""
        if not activities:
            return 0.0
        
        avg_complexity = np.mean([a.complexity_level for a in activities]) / 10.0
        skills_diversity = len(set(skill for a in activities for skill in a.skills_required)) / 20.0  # Normalize
        problem_solving_tasks = sum(1 for a in activities if 'problem' in a.task_type.lower() or 
                                   'analysis' in a.task_type.lower()) / len(activities)
        
        complexity_score = (
            avg_complexity * 0.5 +
            skills_diversity * 0.3 +
            problem_solving_tasks * 0.2
        )
        
        return min(1.0, max(0.0, complexity_score))
    
    def calculate_business_skills_score(self, activities: List[TaskActivity], performance: PerformanceMetrics) -> float:
        """Calculate business skills score"""
        if not activities:
            return 0.0
        
        business_activities = sum(1 for a in activities if any(skill in ['strategy', 'planning', 'budgeting', 
                                                                        'stakeholder', 'communication'] 
                                                              for skill in a.skills_required)) / len(activities)
        
        innovation_score = performance.innovation_score
        
        # Look for business impact
        strategic_impact = sum(1 for a in activities if a.business_impact in ['high', 'critical']) / len(activities)
        
        business_score = (
            business_activities * 0.4 +
            innovation_score * 0.3 +
            strategic_impact * 0.3
        )
        
        return min(1.0, max(0.0, business_score))
    
    async def analyze_employee_real_time(self, 
                                       employee_id: str,
                                       activities: List[TaskActivity],
                                       performance: PerformanceMetrics,
                                       current_role: str) -> List[SFIALevelSuggestion]:
        """Analyze employee data in real-time and suggest SFIA levels"""
        try:
            suggestions = []
            
            if not activities:
                logger.warning(f"No activities found for employee {employee_id}")
                return suggestions
            
            # Calculate key scores
            autonomy_score = self.calculate_autonomy_score(activities, performance)
            influence_score = self.calculate_influence_score(activities, performance)
            complexity_score = self.calculate_complexity_score(activities)
            business_skills_score = self.calculate_business_skills_score(activities, performance)
            
            # Get unique skills from activities
            all_skills = set()
            for activity in activities:
                all_skills.update(activity.skills_required)
            
            # Analyze each skill
            for skill in all_skills:
                if not skill.strip():
                    continue
                    
                skill_activities = [a for a in activities if skill in a.skills_required]
                if not skill_activities:
                    continue
                
                # Calculate skill-specific metrics
                skill_performance = self._calculate_skill_performance(skill_activities)
                experience_estimate = self._estimate_experience(skill_activities, performance)
                
                # Determine suggested SFIA level
                suggested_level = self._determine_sfia_level(
                    autonomy_score,
                    influence_score,
                    complexity_score,
                    business_skills_score,
                    skill_performance,
                    experience_estimate
                )
                
                # Generate reasoning and evidence
                reasoning, evidence = self._generate_reasoning(
                    skill, skill_activities, suggested_level,
                    autonomy_score, influence_score, complexity_score, business_skills_score
                )
                
                # Calculate confidence score
                confidence = self._calculate_confidence(skill_activities, performance, suggested_level)
                
                # Generate improvement areas
                improvement_areas = self._generate_improvement_areas(suggested_level, 
                                                                   autonomy_score, influence_score,
                                                                   complexity_score, business_skills_score)
                
                suggestion = SFIALevelSuggestion(
                    employee_id=employee_id,
                    current_role=current_role,
                    skill_code=self._get_skill_code(skill),
                    skill_name=skill,
                    current_level=None,  # Would need to be provided or looked up
                    suggested_level=suggested_level,
                    confidence_score=confidence,
                    reasoning=reasoning,
                    supporting_evidence=evidence,
                    improvement_areas=improvement_areas,
                    timeline_estimate=self._estimate_timeline(suggested_level, experience_estimate),
                    business_justification=self._generate_business_justification(skill, suggested_level, activities),
                    timestamp=datetime.now()
                )
                
                suggestions.append(suggestion)
            
            # Cache the results
            await self._cache_suggestions(employee_id, suggestions)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error analyzing employee {employee_id}: {e}")
            return []
    
    def _calculate_skill_performance(self, skill_activities: List[TaskActivity]) -> float:
        """Calculate performance for a specific skill"""
        if not skill_activities:
            return 0.0
        
        avg_quality = np.mean([a.completion_quality for a in skill_activities])
        avg_efficiency = np.mean([8.0 / max(a.time_spent, 1) for a in skill_activities])  # Assuming 8h standard
        avg_complexity = np.mean([a.complexity_level for a in skill_activities]) / 10.0
        
        performance = (avg_quality * 0.4 + 
                      min(avg_efficiency, 1.0) * 0.3 + 
                      avg_complexity * 0.3)
        
        return min(1.0, max(0.0, performance))
    
    def _estimate_experience(self, skill_activities: List[TaskActivity], performance: PerformanceMetrics) -> int:
        """Estimate years of experience for a skill"""
        # This is a simplified estimation - in real implementation, 
        # you'd have more sophisticated logic
        activity_count = len(skill_activities)
        avg_complexity = np.mean([a.complexity_level for a in skill_activities])
        
        if activity_count < 5:
            return 0
        elif activity_count < 20 and avg_complexity < 5:
            return 1
        elif activity_count < 50 and avg_complexity < 7:
            return 3
        elif avg_complexity < 8:
            return 5
        else:
            return 8
    
    def _determine_sfia_level(self, autonomy: float, influence: float, complexity: float, 
                            business_skills: float, skill_performance: float, experience: int) -> int:
        """Determine SFIA level based on calculated scores"""
        scores = []
        
        for level, criteria in self.sfia_criteria.items():
            # Calculate how well the person meets this level's criteria
            score = 0.0
            
            if autonomy >= criteria.autonomy_score:
                score += 0.25
            if influence >= criteria.influence_score:
                score += 0.25
            if complexity >= criteria.complexity_score:
                score += 0.25
            if business_skills >= criteria.business_skills_score:
                score += 0.15
            if experience >= criteria.required_experience:
                score += 0.1
            
            scores.append((level, score))
        
        # Find the highest level where the person meets most criteria
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Must meet at least 70% of criteria for a level
        for level, score in scores:
            if score >= 0.7:
                return level
        
        # Fallback to level 1 if no criteria are strongly met
        return 1
    
    def _generate_reasoning(self, skill: str, activities: List[TaskActivity], 
                          suggested_level: int, autonomy: float, influence: float,
                          complexity: float, business_skills: float) -> Tuple[str, List[str]]:
        """Generate reasoning and evidence for the suggestion"""
        criteria = self.sfia_criteria[suggested_level]
        
        reasoning_parts = [
            f"Based on analysis of {len(activities)} activities involving {skill}",
            f"Autonomy score: {autonomy:.2f} (required: {criteria.autonomy_score:.2f})",
            f"Influence score: {influence:.2f} (required: {criteria.influence_score:.2f})",
            f"Complexity score: {complexity:.2f} (required: {criteria.complexity_score:.2f})",
            f"Business skills score: {business_skills:.2f} (required: {criteria.business_skills_score:.2f})"
        ]
        
        reasoning = ". ".join(reasoning_parts) + "."
        
        evidence = [
            f"Completed {len(activities)} tasks involving {skill}",
            f"Average task complexity: {np.mean([a.complexity_level for a in activities]):.1f}/10",
            f"Average completion quality: {np.mean([a.completion_quality for a in activities]):.1%}",
            f"Business impact distribution: {Counter(a.business_impact for a in activities)}"
        ]
        
        return reasoning, evidence
    
    def _calculate_confidence(self, activities: List[TaskActivity], 
                            performance: PerformanceMetrics, suggested_level: int) -> float:
        """Calculate confidence score for the suggestion"""
        # Factors affecting confidence
        data_volume = min(len(activities) / 20.0, 1.0)  # More activities = higher confidence
        consistency = 1.0 - np.std([a.completion_quality for a in activities])
        recency = sum(1 for a in activities 
                     if (datetime.now() - a.timestamp).days < 90) / len(activities)
        
        confidence = (data_volume * 0.4 + consistency * 0.3 + recency * 0.3)
        
        return min(1.0, max(0.1, confidence))
    
    def _generate_improvement_areas(self, suggested_level: int, autonomy: float,
                                  influence: float, complexity: float, business_skills: float) -> List[str]:
        """Generate improvement areas for reaching higher SFIA levels"""
        improvements = []
        
        next_level = min(suggested_level + 1, 7)
        if next_level > suggested_level:
            criteria = self.sfia_criteria[next_level]
            
            if autonomy < criteria.autonomy_score:
                improvements.append("Increase autonomy by taking on more self-directed tasks")
            
            if influence < criteria.influence_score:
                improvements.append("Develop leadership and mentoring capabilities")
            
            if complexity < criteria.complexity_score:
                improvements.append("Take on more complex, challenging assignments")
            
            if business_skills < criteria.business_skills_score:
                improvements.append("Develop strategic thinking and business acumen")
        
        return improvements[:3]  # Top 3 improvements
    
    def _estimate_timeline(self, suggested_level: int, experience: int) -> str:
        """Estimate timeline for achieving the suggested level"""
        if suggested_level <= 2:
            return "0-6 months"
        elif suggested_level <= 4:
            return "6-18 months"
        elif suggested_level <= 6:
            return "1-3 years"
        else:
            return "3+ years"
    
    def _generate_business_justification(self, skill: str, level: int, activities: List[TaskActivity]) -> str:
        """Generate business justification for the SFIA level"""
        high_impact_count = sum(1 for a in activities if a.business_impact in ['high', 'critical'])
        avg_quality = np.mean([a.completion_quality for a in activities])
        
        justification = f"Employee demonstrates Level {level} proficiency in {skill} "
        justification += f"with {high_impact_count} high-impact deliverables "
        justification += f"and {avg_quality:.1%} average quality score."
        
        return justification
    
    def _get_skill_code(self, skill_name: str) -> str:
        """Map skill name to SFIA skill code"""
        # This would typically be a lookup table or mapping
        # For now, return a simplified code
        return skill_name.upper().replace(' ', '_')[:10]
    
    async def _cache_suggestions(self, employee_id: str, suggestions: List[SFIALevelSuggestion]):
        """Cache suggestions in Redis"""
        try:
            cache_key = f"suggestions:{employee_id}"
            suggestions_data = [s.model_dump() for s in suggestions]
            
            await self.redis_client.set(
                cache_key, 
                json.dumps(suggestions_data, default=str),
                ex=3600  # 1 hour cache
            )
        except Exception as e:
            logger.error(f"Failed to cache suggestions: {e}")
    
    async def get_cached_suggestions(self, employee_id: str) -> List[SFIALevelSuggestion]:
        """Get cached suggestions from Redis"""
        try:
            cache_key = f"suggestions:{employee_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                suggestions_data = json.loads(cached_data)
                return [SFIALevelSuggestion(**s) for s in suggestions_data]
            
            return []
        except Exception as e:
            logger.error(f"Failed to get cached suggestions: {e}")
            return []
    
    async def batch_analyze_organization(self, 
                                       employee_data: Dict[str, List[TaskActivity]],
                                       performance_data: Dict[str, PerformanceMetrics]) -> Dict[str, List[SFIALevelSuggestion]]:
        """Batch analyze entire organization"""
        results = {}
        
        tasks = []
        for employee_id, activities in employee_data.items():
            performance = performance_data.get(employee_id)
            if performance:
                # Determine role from performance data or activities
                role = performance.role or (activities[0].role if activities else "Unknown")
                
                task = self.analyze_employee_real_time(employee_id, activities, performance, role)
                tasks.append((employee_id, task))
        
        # Execute all analyses concurrently
        for employee_id, task in tasks:
            try:
                suggestions = await task
                results[employee_id] = suggestions
            except Exception as e:
                logger.error(f"Failed to analyze employee {employee_id}: {e}")
                results[employee_id] = []
        
        return results
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()