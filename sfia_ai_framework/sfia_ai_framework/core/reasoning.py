"""
SFIA Reasoning Engine - Advanced semantic reasoning for SFIA ontology

This module provides intelligent reasoning capabilities for SFIA skills, roles,
and career pathways using rule-based inference and machine learning.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple, Set
import json
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import networkx as nx

from ..models.sfia_models import (
    Skill, SkillLevel, ProfessionalRole, CareerPathway, 
    SkillGap, CompetencyProfile, LearningResource, AssessmentResult
)


class ReasoningRuleType(Enum):
    """Types of reasoning rules"""
    SKILL_PREREQUISITE = "skill_prerequisite"
    CAREER_PROGRESSION = "career_progression"
    TEAM_COMPOSITION = "team_composition"
    LEARNING_PATH = "learning_path"
    ROLE_COMPATIBILITY = "role_compatibility"


@dataclass
class ReasoningRule:
    """Represents a reasoning rule in the SFIA domain"""
    rule_type: ReasoningRuleType
    conditions: Dict[str, Any]
    conclusions: Dict[str, Any]
    confidence: float
    description: str


class SFIAReasoningEngine:
    """
    Advanced reasoning engine for SFIA ontology with machine learning capabilities
    """
    
    def __init__(self, knowledge_graph=None):
        self.kg = knowledge_graph
        self.logger = logging.getLogger(__name__)
        
        # Rule base for inference
        self.rules: List[ReasoningRule] = []
        
        # ML models for different reasoning tasks
        self.skill_similarity_model = None
        self.role_clustering_model = None
        self.career_progression_model = None
        
        # Cached computations
        self._skill_embeddings = {}
        self._role_skill_matrix = None
        self._career_network = None
        
        # Initialize default rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default reasoning rules for SFIA"""
        
        # Skill prerequisite rules
        self.add_rule(ReasoningRule(
            rule_type=ReasoningRuleType.SKILL_PREREQUISITE,
            conditions={"skill_level_diff": "> 1", "same_skill": True},
            conclusions={"prerequisite_required": True},
            confidence=0.9,
            description="Same skill at lower level is prerequisite for higher level"
        ))
        
        # Career progression rules
        self.add_rule(ReasoningRule(
            rule_type=ReasoningRuleType.CAREER_PROGRESSION,
            conditions={"skill_overlap": "> 0.6", "level_progression": "> 0"},
            conclusions={"progression_feasible": True},
            confidence=0.8,
            description="High skill overlap enables career progression"
        ))
        
        # Team composition rules
        self.add_rule(ReasoningRule(
            rule_type=ReasoningRuleType.TEAM_COMPOSITION,
            conditions={"skill_coverage": "> 0.8", "skill_redundancy": "< 0.3"},
            conclusions={"team_optimal": True},
            confidence=0.85,
            description="Optimal team has high coverage with low redundancy"
        ))
    
    def add_rule(self, rule: ReasoningRule):
        """Add a new reasoning rule"""
        self.rules.append(rule)
        self.logger.info(f"Added reasoning rule: {rule.description}")
    
    async def initialize_ml_models(self):
        """Initialize machine learning models for reasoning"""
        if self.kg:
            # Build skill similarity model
            await self._build_skill_similarity_model()
            # Build role clustering model
            await self._build_role_clustering_model()
            # Build career progression model
            await self._build_career_progression_model()
    
    async def _build_skill_similarity_model(self):
        """Build skill similarity model using TF-IDF and descriptions"""
        try:
            skills_data = await self.kg.query_skills()
            if not skills_data:
                return
            
            # Extract skill descriptions
            skills_text = []
            skill_codes = []
            
            for skill in skills_data:
                text = f"{skill.get('name', '')} {skill.get('description', '')}"
                skills_text.append(text)
                skill_codes.append(skill.get('code', ''))
            
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(
                max_features=1000, 
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            skill_vectors = vectorizer.fit_transform(skills_text)
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(skill_vectors)
            
            # Store embeddings
            self._skill_embeddings = {
                'vectorizer': vectorizer,
                'vectors': skill_vectors,
                'similarity_matrix': similarity_matrix,
                'skill_codes': skill_codes
            }
            
            self.logger.info("Built skill similarity model successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to build skill similarity model: {e}")
    
    async def _build_role_clustering_model(self):
        """Build role clustering model for role similarity analysis"""
        try:
            # Get role-skill matrix
            role_skill_matrix = await self.kg.get_role_skill_matrix()
            if role_skill_matrix.empty:
                return
            
            # Convert to numerical representation
            matrix_numeric = pd.get_dummies(role_skill_matrix, prefix_sep='_')
            
            # Apply K-means clustering
            n_clusters = min(5, len(matrix_numeric) // 2)  # Adaptive cluster count
            if n_clusters > 1:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                clusters = kmeans.fit_predict(matrix_numeric)
                
                self.role_clustering_model = {
                    'model': kmeans,
                    'clusters': clusters,
                    'role_names': matrix_numeric.index.tolist(),
                    'feature_matrix': matrix_numeric
                }
                
                self.logger.info(f"Built role clustering model with {n_clusters} clusters")
            
        except Exception as e:
            self.logger.error(f"Failed to build role clustering model: {e}")
    
    async def _build_career_progression_model(self):
        """Build career progression prediction model"""
        try:
            # This would build a more sophisticated ML model for career progression
            # For now, we'll use network analysis
            
            career_paths = await self.kg.find_career_paths("", "", max_steps=5)  # Get all paths
            
            # Build career network
            G = nx.DiGraph()
            for path in career_paths:
                for i in range(len(path) - 1):
                    G.add_edge(path[i], path[i + 1])
            
            self._career_network = G
            
            self.logger.info("Built career progression network model")
            
        except Exception as e:
            self.logger.error(f"Failed to build career progression model: {e}")
    
    def get_skill_similarity(self, skill1_code: str, skill2_code: str) -> float:
        """Get similarity score between two skills"""
        if not self._skill_embeddings:
            return 0.0
        
        try:
            skill_codes = self._skill_embeddings['skill_codes']
            similarity_matrix = self._skill_embeddings['similarity_matrix']
            
            if skill1_code in skill_codes and skill2_code in skill_codes:
                idx1 = skill_codes.index(skill1_code)
                idx2 = skill_codes.index(skill2_code)
                return float(similarity_matrix[idx1][idx2])
            
        except Exception as e:
            self.logger.error(f"Error calculating skill similarity: {e}")
        
        return 0.0
    
    def find_similar_skills(self, skill_code: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find most similar skills to a given skill"""
        if not self._skill_embeddings:
            return []
        
        try:
            skill_codes = self._skill_embeddings['skill_codes']
            similarity_matrix = self._skill_embeddings['similarity_matrix']
            
            if skill_code in skill_codes:
                skill_idx = skill_codes.index(skill_code)
                similarities = similarity_matrix[skill_idx]
                
                # Get top-k similar skills (excluding self)
                similar_indices = np.argsort(similarities)[::-1][1:top_k+1]
                
                similar_skills = [
                    (skill_codes[idx], float(similarities[idx]))
                    for idx in similar_indices
                ]
                
                return similar_skills
            
        except Exception as e:
            self.logger.error(f"Error finding similar skills: {e}")
        
        return []
    
    async def analyze_skill_gaps(self, current_role: str, target_role: str) -> List[SkillGap]:
        """Analyze skill gaps between current and target roles"""
        skill_gaps = []
        
        try:
            # Get skill gaps from knowledge graph
            gap_data = await self.kg.analyze_skill_gaps(current_role, target_role)
            
            for gap in gap_data:
                skill_gap = SkillGap(
                    skill_code=gap['skill_code'],
                    skill_name=gap['skill_name'],
                    current_level=0,  # Assume not present
                    required_level=self._infer_required_level(gap['skill_code'], target_role),
                    gap_size=self._infer_required_level(gap['skill_code'], target_role),
                    priority=self._calculate_skill_priority(gap['skill_code'], target_role),
                    estimated_time_to_develop=self._estimate_development_time(
                        gap['skill_code'], 
                        self._infer_required_level(gap['skill_code'], target_role)
                    )
                )
                skill_gaps.append(skill_gap)
            
            # Sort by priority and gap size
            skill_gaps.sort(key=lambda x: (x.priority, -x.gap_size), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error analyzing skill gaps: {e}")
        
        return skill_gaps
    
    def _infer_required_level(self, skill_code: str, role: str) -> int:
        """Infer required skill level for a role (simplified logic)"""
        # This would use more sophisticated inference in practice
        return 4  # Default to level 4
    
    def _calculate_skill_priority(self, skill_code: str, role: str) -> int:
        """Calculate priority of skill for a role (1-5 scale)"""
        # This would analyze role requirements and skill criticality
        return 3  # Default to medium priority
    
    def _estimate_development_time(self, skill_code: str, target_level: int) -> int:
        """Estimate time in months to develop skill to target level"""
        # Simplified estimation logic
        base_time = 3  # Base 3 months per level
        return base_time * target_level
    
    async def recommend_career_paths(self, current_skills: List[str], career_goals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend career progression paths based on current skills and goals"""
        recommendations = []
        
        try:
            # Get target roles based on career goals
            target_roles = career_goals.get('target_roles', [])
            
            for target_role in target_roles:
                # Find paths from current position to target
                paths = await self._find_progression_paths(current_skills, target_role)
                
                for path in paths:
                    recommendation = {
                        'target_role': target_role,
                        'progression_path': path,
                        'feasibility_score': self._calculate_feasibility_score(current_skills, path),
                        'estimated_timeline': self._estimate_progression_timeline(path),
                        'key_milestones': self._identify_key_milestones(path),
                        'recommended_next_steps': self._suggest_next_steps(current_skills, path)
                    }
                    recommendations.append(recommendation)
            
            # Sort by feasibility score
            recommendations.sort(key=lambda x: x['feasibility_score'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error recommending career paths: {e}")
        
        return recommendations
    
    async def _find_progression_paths(self, current_skills: List[str], target_role: str) -> List[List[str]]:
        """Find possible progression paths to target role"""
        # This would use the career network to find optimal paths
        if self._career_network and target_role in self._career_network:
            # Find roles that match current skills well
            matching_roles = self._find_roles_matching_skills(current_skills)
            
            paths = []
            for start_role in matching_roles:
                try:
                    if nx.has_path(self._career_network, start_role, target_role):
                        path = nx.shortest_path(self._career_network, start_role, target_role)
                        paths.append(path)
                except:
                    continue
            
            return paths[:5]  # Return top 5 paths
        
        return []
    
    def _find_roles_matching_skills(self, skills: List[str]) -> List[str]:
        """Find roles that match current skills"""
        # Simplified implementation
        return ["Developer", "Analyst", "Consultant"]  # Would be more sophisticated
    
    def _calculate_feasibility_score(self, current_skills: List[str], path: List[str]) -> float:
        """Calculate feasibility score for a career path"""
        # Simplified scoring logic
        base_score = 0.7
        path_length_penalty = len(path) * 0.05
        return max(0.0, min(1.0, base_score - path_length_penalty))
    
    def _estimate_progression_timeline(self, path: List[str]) -> Dict[str, Any]:
        """Estimate timeline for career progression"""
        return {
            'total_months': len(path) * 18,  # 18 months per step
            'milestones': [f"Month {i*18}: {role}" for i, role in enumerate(path)]
        }
    
    def _identify_key_milestones(self, path: List[str]) -> List[str]:
        """Identify key milestones in career path"""
        return [f"Achieve competency in {role}" for role in path[1:]]
    
    def _suggest_next_steps(self, current_skills: List[str], path: List[str]) -> List[str]:
        """Suggest immediate next steps"""
        if len(path) > 1:
            next_role = path[1]
            return [
                f"Develop skills required for {next_role}",
                "Seek mentorship or coaching",
                "Gain relevant project experience",
                "Consider additional certifications"
            ]
        return []
    
    async def optimize_team_composition(self, project_requirements: Dict[str, Any], 
                                     available_resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize team composition for project requirements"""
        optimization_result = {
            'recommended_team': [],
            'skill_coverage': {},
            'identified_gaps': [],
            'alternative_options': [],
            'optimization_score': 0.0
        }
        
        try:
            required_skills = project_requirements.get('required_skills', [])
            project_complexity = project_requirements.get('complexity', 'medium')
            
            # Analyze available resources
            resource_skills = {}
            for resource in available_resources:
                resource_id = resource.get('id', '')
                skills = resource.get('skills', [])
                resource_skills[resource_id] = skills
            
            # Find optimal team combination
            optimal_team = self._find_optimal_team_combination(
                required_skills, resource_skills, project_complexity
            )
            
            optimization_result['recommended_team'] = optimal_team
            optimization_result['skill_coverage'] = self._calculate_skill_coverage(
                required_skills, optimal_team, resource_skills
            )
            optimization_result['identified_gaps'] = self._identify_team_skill_gaps(
                required_skills, optimal_team, resource_skills
            )
            optimization_result['optimization_score'] = self._calculate_team_score(
                required_skills, optimal_team, resource_skills
            )
            
        except Exception as e:
            self.logger.error(f"Error optimizing team composition: {e}")
        
        return optimization_result
    
    def _find_optimal_team_combination(self, required_skills: List[str], 
                                     resource_skills: Dict[str, List[str]], 
                                     complexity: str) -> List[str]:
        """Find optimal combination of team members"""
        # Simplified greedy algorithm
        selected_team = []
        covered_skills = set()
        
        # Sort resources by skill count (descending)
        sorted_resources = sorted(
            resource_skills.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )
        
        for resource_id, skills in sorted_resources:
            # Check if this resource adds new skills
            new_skills = set(skills) - covered_skills
            if new_skills and len(new_skills & set(required_skills)) > 0:
                selected_team.append(resource_id)
                covered_skills.update(skills)
                
                # Check if we have good coverage
                coverage = len(covered_skills & set(required_skills)) / len(required_skills)
                if coverage >= 0.8:  # 80% coverage threshold
                    break
        
        return selected_team
    
    def _calculate_skill_coverage(self, required_skills: List[str], 
                                team: List[str], 
                                resource_skills: Dict[str, List[str]]) -> Dict[str, float]:
        """Calculate skill coverage for the team"""
        coverage = {}
        team_skills = set()
        
        for member in team:
            team_skills.update(resource_skills.get(member, []))
        
        for skill in required_skills:
            coverage[skill] = 1.0 if skill in team_skills else 0.0
        
        return coverage
    
    def _identify_team_skill_gaps(self, required_skills: List[str], 
                                team: List[str], 
                                resource_skills: Dict[str, List[str]]) -> List[str]:
        """Identify missing skills in the team"""
        team_skills = set()
        for member in team:
            team_skills.update(resource_skills.get(member, []))
        
        return [skill for skill in required_skills if skill not in team_skills]
    
    def _calculate_team_score(self, required_skills: List[str], 
                            team: List[str], 
                            resource_skills: Dict[str, List[str]]) -> float:
        """Calculate overall team optimization score"""
        if not required_skills:
            return 0.0
        
        team_skills = set()
        for member in team:
            team_skills.update(resource_skills.get(member, []))
        
        coverage = len(team_skills & set(required_skills)) / len(required_skills)
        team_size_penalty = max(0, len(team) - 5) * 0.1  # Penalty for large teams
        
        return max(0.0, coverage - team_size_penalty)
    
    async def assess_role_fit(self, person_skills: List[str], 
                            role_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how well a person fits a role"""
        assessment = {
            'overall_fit_score': 0.0,
            'skill_match_details': {},
            'strengths': [],
            'gaps': [],
            'development_recommendations': []
        }
        
        try:
            required_skills = role_requirements.get('required_skills', [])
            preferred_skills = role_requirements.get('preferred_skills', [])
            
            # Calculate skill matches
            required_matches = len(set(person_skills) & set(required_skills))
            preferred_matches = len(set(person_skills) & set(preferred_skills))
            
            # Calculate fit score
            required_score = required_matches / len(required_skills) if required_skills else 1.0
            preferred_score = preferred_matches / len(preferred_skills) if preferred_skills else 0.0
            
            overall_score = (required_score * 0.8) + (preferred_score * 0.2)
            
            assessment['overall_fit_score'] = overall_score
            assessment['skill_match_details'] = {
                'required_skills_match': f"{required_matches}/{len(required_skills)}",
                'preferred_skills_match': f"{preferred_matches}/{len(preferred_skills)}",
                'match_percentage': f"{overall_score:.1%}"
            }
            
            # Identify strengths and gaps
            assessment['strengths'] = list(set(person_skills) & set(required_skills + preferred_skills))
            assessment['gaps'] = list(set(required_skills) - set(person_skills))
            
            # Generate development recommendations
            assessment['development_recommendations'] = self._generate_development_recommendations(
                assessment['gaps']
            )
            
        except Exception as e:
            self.logger.error(f"Error assessing role fit: {e}")
        
        return assessment
    
    def _generate_development_recommendations(self, skill_gaps: List[str]) -> List[str]:
        """Generate development recommendations for skill gaps"""
        recommendations = []
        
        for skill in skill_gaps[:5]:  # Top 5 gaps
            recommendations.extend([
                f"Develop {skill} through structured learning program",
                f"Seek project opportunities involving {skill}",
                f"Find mentorship for {skill} development"
            ])
        
        return recommendations
    
    async def get_learning_recommendations(self, target_skills: List[str], 
                                        current_level: int = 1) -> List[Dict[str, Any]]:
        """Get personalized learning recommendations"""
        recommendations = []
        
        try:
            for skill in target_skills:
                learning_path = {
                    'skill': skill,
                    'current_level': current_level,
                    'target_level': min(current_level + 2, 7),  # Progress 2 levels
                    'learning_resources': self._suggest_learning_resources(skill),
                    'estimated_duration': self._estimate_learning_duration(skill, current_level),
                    'prerequisites': self._identify_prerequisites(skill),
                    'assessment_milestones': self._define_assessment_milestones(skill)
                }
                recommendations.append(learning_path)
            
        except Exception as e:
            self.logger.error(f"Error getting learning recommendations: {e}")
        
        return recommendations
    
    def _suggest_learning_resources(self, skill: str) -> List[Dict[str, str]]:
        """Suggest learning resources for a skill"""
        # This would connect to a learning resource database
        return [
            {'type': 'online_course', 'title': f'{skill} Fundamentals', 'provider': 'Learning Platform'},
            {'type': 'book', 'title': f'Complete Guide to {skill}', 'author': 'Expert Author'},
            {'type': 'certification', 'title': f'{skill} Professional Certification', 'provider': 'Cert Body'}
        ]
    
    def _estimate_learning_duration(self, skill: str, current_level: int) -> str:
        """Estimate learning duration for skill development"""
        base_months = max(1, 4 - current_level)  # Higher current level = less time needed
        return f"{base_months}-{base_months + 2} months"
    
    def _identify_prerequisites(self, skill: str) -> List[str]:
        """Identify prerequisites for a skill"""
        # This would use the knowledge graph to find prerequisites
        return []  # Simplified
    
    def _define_assessment_milestones(self, skill: str) -> List[str]:
        """Define assessment milestones for skill development"""
        return [
            f"Complete foundational {skill} training",
            f"Apply {skill} in practice project",
            f"Demonstrate {skill} competency through assessment",
            f"Achieve advanced {skill} proficiency"
        ]
    
    async def predict_career_success(self, person_profile: Dict[str, Any], 
                                   target_role: str) -> Dict[str, Any]:
        """Predict career success probability for a person in a target role"""
        prediction = {
            'success_probability': 0.0,
            'key_success_factors': [],
            'risk_factors': [],
            'recommendations': []
        }
        
        try:
            current_skills = person_profile.get('skills', [])
            experience_years = person_profile.get('experience_years', 0)
            education_level = person_profile.get('education_level', '')
            
            # Simple predictive model (would be more sophisticated in practice)
            role_fit = await self.assess_role_fit(current_skills, {'required_skills': []})
            
            # Calculate success probability
            skill_factor = role_fit['overall_fit_score']
            experience_factor = min(1.0, experience_years / 10.0)  # Experience up to 10 years
            education_factor = 0.8 if education_level in ['Bachelor', 'Master', 'PhD'] else 0.6
            
            success_probability = (skill_factor * 0.5) + (experience_factor * 0.3) + (education_factor * 0.2)
            
            prediction['success_probability'] = success_probability
            prediction['key_success_factors'] = self._identify_success_factors(person_profile, target_role)
            prediction['risk_factors'] = self._identify_risk_factors(person_profile, target_role)
            prediction['recommendations'] = self._generate_success_recommendations(person_profile, target_role)
            
        except Exception as e:
            self.logger.error(f"Error predicting career success: {e}")
        
        return prediction
    
    def _identify_success_factors(self, profile: Dict[str, Any], target_role: str) -> List[str]:
        """Identify factors that contribute to success"""
        factors = []
        
        if profile.get('experience_years', 0) > 5:
            factors.append("Strong professional experience")
        
        if len(profile.get('skills', [])) > 10:
            factors.append("Diverse skill portfolio")
        
        factors.append("Relevant educational background")
        
        return factors
    
    def _identify_risk_factors(self, profile: Dict[str, Any], target_role: str) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        if profile.get('experience_years', 0) < 2:
            risks.append("Limited professional experience")
        
        if len(profile.get('skills', [])) < 5:
            risks.append("Narrow skill set")
        
        return risks
    
    def _generate_success_recommendations(self, profile: Dict[str, Any], target_role: str) -> List[str]:
        """Generate recommendations for career success"""
        return [
            "Continue developing technical skills",
            "Build leadership and communication capabilities",
            "Seek mentorship and networking opportunities",
            "Gain diverse project experience",
            "Consider relevant certifications"
        ]


# Factory function
def create_sfia_reasoning_engine(knowledge_graph=None) -> SFIAReasoningEngine:
    """Factory function to create SFIA reasoning engine"""
    return SFIAReasoningEngine(knowledge_graph)