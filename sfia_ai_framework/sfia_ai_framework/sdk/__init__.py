"""
SFIA AI SDK - Complete Software Development Kit for SFIA AI Framework

This SDK provides a high-level interface for integrating SFIA AI capabilities
into applications and systems.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
import json
import logging
from datetime import datetime, date
from pathlib import Path

from ..core.agents import SFIAAgentCrew, create_sfia_agent_crew
from ..core.knowledge_graph import SFIAKnowledgeGraph, create_sfia_knowledge_graph
from ..core.reasoning import SFIAReasoningEngine, create_sfia_reasoning_engine
from ..services.portfolio_assessment_service import PortfolioAssessmentService
from ..services.sfia9_service import SFIA9Service, sfia9_service
from ..models.sfia_models import (
    Skill, SkillLevel, ProfessionalRole, CareerPathway,
    SkillGap, CompetencyProfile, LearningResource, Person,
    Assessment, AssessmentResult, Project, TeamComposition,
    CareerRecommendation, APIResponse, EnhancedSFIAAttribute,
    EnhancedSFIASkill, SFIA9LevelDefinition, SFIA9EnhancedFramework
)
from ..models.portfolio_models import (
    PortfolioAssessment, PortfolioAnalysisResponse, 
    PortfolioMappingGuidance, ProficiencyThreshold
)


class SFIASDKConfig:
    """Configuration for SFIA SDK"""
    def __init__(self, 
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j", 
                 neo4j_password: str = "password",
                 openai_api_key: Optional[str] = None,
                 enable_agents: bool = True,
                 enable_reasoning: bool = True,
                 log_level: str = "INFO"):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.openai_api_key = openai_api_key
        self.enable_agents = enable_agents
        self.enable_reasoning = enable_reasoning
        self.log_level = log_level


class SFIASDK:
    """
    Main SDK class for SFIA AI Framework
    
    Provides a unified interface for all SFIA AI capabilities including
    knowledge graph operations, intelligent reasoning, and multi-agent analysis.
    """
    
    def __init__(self, config: SFIASDKConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, config.log_level))
        
        # Core components
        self.knowledge_graph: Optional[SFIAKnowledgeGraph] = None
        self.reasoning_engine: Optional[SFIAReasoningEngine] = None
        self.agent_crew: Optional[SFIAAgentCrew] = None
        self.portfolio_service: Optional[PortfolioAssessmentService] = None
        self.sfia9_service: SFIA9Service = sfia9_service
        
        # State
        self._initialized = False
    
    async def initialize(self):
        """Initialize all SDK components"""
        try:
            self.logger.info("Initializing SFIA AI SDK...")
            
            # Initialize knowledge graph
            self.knowledge_graph = await create_sfia_knowledge_graph(
                self.config.neo4j_uri,
                self.config.neo4j_user,
                self.config.neo4j_password
            )
            
            # Initialize reasoning engine
            if self.config.enable_reasoning:
                self.reasoning_engine = create_sfia_reasoning_engine(self.knowledge_graph)
                await self.reasoning_engine.initialize_ml_models()
            
            # Initialize agent crew
            if self.config.enable_agents and self.config.openai_api_key:
                import os
                os.environ["OPENAI_API_KEY"] = self.config.openai_api_key
                self.agent_crew = create_sfia_agent_crew(
                    self.knowledge_graph, 
                    self.reasoning_engine
                )
            
            # Initialize portfolio assessment service
            self.portfolio_service = PortfolioAssessmentService(self.knowledge_graph)
            
            self._initialized = True
            self.logger.info("SFIA AI SDK initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize SFIA AI SDK: {e}")
            raise
    
    async def close(self):
        """Clean up resources"""
        if self.knowledge_graph:
            await self.knowledge_graph.close()
        self._initialized = False
        self.logger.info("SFIA AI SDK closed")
    
    def _ensure_initialized(self):
        """Ensure SDK is initialized before operations"""
        if not self._initialized:
            raise RuntimeError("SDK not initialized. Call initialize() first.")
    
    # Knowledge Graph Operations
    async def load_sfia_ontology(self, rdf_file_path: str) -> APIResponse:
        """Load SFIA ontology from RDF file"""
        self._ensure_initialized()
        
        try:
            await self.knowledge_graph.load_sfia_ontology_from_rdf(rdf_file_path)
            return APIResponse(message="SFIA ontology loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load SFIA ontology: {e}")
            return APIResponse(success=False, message=str(e))
    
    async def add_professional_roles(self, roles: List[Dict[str, Any]]) -> APIResponse:
        """Add professional roles to the knowledge graph"""
        self._ensure_initialized()
        
        try:
            await self.knowledge_graph.add_professional_roles(roles)
            return APIResponse(message=f"Added {len(roles)} professional roles")
        except Exception as e:
            self.logger.error(f"Failed to add professional roles: {e}")
            return APIResponse(success=False, message=str(e))
    
    async def add_career_pathways(self, pathways: List[Dict[str, Any]]) -> APIResponse:
        """Add career pathways to the knowledge graph"""
        self._ensure_initialized()
        
        try:
            await self.knowledge_graph.add_career_pathways(pathways)
            return APIResponse(message=f"Added {len(pathways)} career pathways")
        except Exception as e:
            self.logger.error(f"Failed to add career pathways: {e}")
            return APIResponse(success=False, message=str(e))
    
    async def query_skills(self, category: str = None, level: int = None, 
                         keyword: str = None) -> Dict[str, Any]:
        """Query skills from the knowledge graph"""
        self._ensure_initialized()
        
        try:
            skills = await self.knowledge_graph.query_skills(category, level, keyword)
            return {
                "success": True,
                "skills": skills,
                "count": len(skills),
                "filters": {"category": category, "level": level, "keyword": keyword}
            }
        except Exception as e:
            self.logger.error(f"Failed to query skills: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_knowledge_graph_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the knowledge graph"""
        self._ensure_initialized()
        
        try:
            stats = await self.knowledge_graph.get_statistics()
            network_analysis = await self.knowledge_graph.get_network_analysis()
            
            return {
                "success": True,
                "basic_stats": stats,
                "network_analysis": network_analysis,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {"success": False, "error": str(e)}
    
    # Reasoning Operations
    async def analyze_skill_gaps(self, current_role: str, target_role: str) -> Dict[str, Any]:
        """Analyze skill gaps between current and target roles"""
        self._ensure_initialized()
        
        try:
            if self.reasoning_engine:
                skill_gaps = await self.reasoning_engine.analyze_skill_gaps(current_role, target_role)
                return {
                    "success": True,
                    "current_role": current_role,
                    "target_role": target_role,
                    "skill_gaps": [gap.dict() for gap in skill_gaps],
                    "total_gaps": len(skill_gaps)
                }
            else:
                # Fallback to knowledge graph only
                gaps = await self.knowledge_graph.analyze_skill_gaps(current_role, target_role)
                return {
                    "success": True,
                    "current_role": current_role,
                    "target_role": target_role,
                    "skill_gaps": gaps,
                    "total_gaps": len(gaps)
                }
        except Exception as e:
            self.logger.error(f"Failed to analyze skill gaps: {e}")
            return {"success": False, "error": str(e)}
    
    async def recommend_career_paths(self, current_skills: List[str], 
                                   career_goals: Dict[str, Any]) -> Dict[str, Any]:
        """Get career path recommendations"""
        self._ensure_initialized()
        
        try:
            if self.reasoning_engine:
                recommendations = await self.reasoning_engine.recommend_career_paths(
                    current_skills, career_goals
                )
                return {
                    "success": True,
                    "current_skills": current_skills,
                    "career_goals": career_goals,
                    "recommendations": recommendations,
                    "count": len(recommendations)
                }
            else:
                return {"success": False, "error": "Reasoning engine not available"}
        except Exception as e:
            self.logger.error(f"Failed to recommend career paths: {e}")
            return {"success": False, "error": str(e)}
    
    async def optimize_team_composition(self, project_requirements: Dict[str, Any], 
                                      available_team: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize team composition for project requirements"""
        self._ensure_initialized()
        
        try:
            if self.reasoning_engine:
                optimization = await self.reasoning_engine.optimize_team_composition(
                    project_requirements, available_team
                )
                return {
                    "success": True,
                    "project_requirements": project_requirements,
                    "optimization_result": optimization
                }
            else:
                return {"success": False, "error": "Reasoning engine not available"}
        except Exception as e:
            self.logger.error(f"Failed to optimize team composition: {e}")
            return {"success": False, "error": str(e)}
    
    async def assess_role_fit(self, person_skills: List[str], 
                            role_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how well a person fits a role"""
        self._ensure_initialized()
        
        try:
            if self.reasoning_engine:
                assessment = await self.reasoning_engine.assess_role_fit(
                    person_skills, role_requirements
                )
                return {
                    "success": True,
                    "person_skills": person_skills,
                    "role_requirements": role_requirements,
                    "assessment": assessment
                }
            else:
                return {"success": False, "error": "Reasoning engine not available"}
        except Exception as e:
            self.logger.error(f"Failed to assess role fit: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_learning_recommendations(self, target_skills: List[str], 
                                         current_level: int = 1) -> Dict[str, Any]:
        """Get learning recommendations for skill development"""
        self._ensure_initialized()
        
        try:
            if self.reasoning_engine:
                recommendations = await self.reasoning_engine.get_learning_recommendations(
                    target_skills, current_level
                )
                return {
                    "success": True,
                    "target_skills": target_skills,
                    "current_level": current_level,
                    "learning_recommendations": recommendations
                }
            else:
                return {"success": False, "error": "Reasoning engine not available"}
        except Exception as e:
            self.logger.error(f"Failed to get learning recommendations: {e}")
            return {"success": False, "error": str(e)}
    
    # Agent Operations
    async def analyze_career_progression(self, current_role: str, target_role: str, 
                                       timeline: str = "2 years") -> Dict[str, Any]:
        """Comprehensive career progression analysis using multi-agent crew"""
        self._ensure_initialized()
        
        try:
            if self.agent_crew:
                analysis = await self.agent_crew.analyze_career_progression(
                    current_role, target_role, timeline
                )
                return {
                    "success": True,
                    "analysis_type": "multi_agent_career_progression",
                    "result": analysis
                }
            else:
                return {"success": False, "error": "Agent crew not available"}
        except Exception as e:
            self.logger.error(f"Failed to analyze career progression: {e}")
            return {"success": False, "error": str(e)}
    
    async def optimize_project_team(self, project_requirements: Dict[str, Any], 
                                  available_team: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Multi-agent team optimization for projects"""
        self._ensure_initialized()
        
        try:
            if self.agent_crew:
                optimization = await self.agent_crew.optimize_team_for_project(
                    project_requirements, available_team
                )
                return {
                    "success": True,
                    "analysis_type": "multi_agent_team_optimization",
                    "result": optimization
                }
            else:
                return {"success": False, "error": "Agent crew not available"}
        except Exception as e:
            self.logger.error(f"Failed to optimize project team: {e}")
            return {"success": False, "error": str(e)}
    
    async def assess_organizational_skills(self, organization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive organizational skills assessment"""
        self._ensure_initialized()
        
        try:
            if self.agent_crew:
                assessment = await self.agent_crew.assess_organizational_skills(organization_data)
                return {
                    "success": True,
                    "analysis_type": "multi_agent_organizational_assessment",
                    "result": assessment
                }
            else:
                return {"success": False, "error": "Agent crew not available"}
        except Exception as e:
            self.logger.error(f"Failed to assess organizational skills: {e}")
            return {"success": False, "error": str(e)}
    
    # Utility Operations
    async def visualize_knowledge_graph(self, output_file: str = "sfia_knowledge_graph.html") -> Dict[str, Any]:
        """Create interactive visualization of the knowledge graph"""
        self._ensure_initialized()
        
        try:
            viz_file = await self.knowledge_graph.visualize_knowledge_graph(output_file)
            return {
                "success": True,
                "visualization_file": viz_file,
                "message": f"Knowledge graph visualization saved to {viz_file}"
            }
        except Exception as e:
            self.logger.error(f"Failed to visualize knowledge graph: {e}")
            return {"success": False, "error": str(e)}
    
    async def export_knowledge_graph(self, format: str = "rdf", 
                                   output_file: str = "sfia_export") -> Dict[str, Any]:
        """Export knowledge graph in various formats"""
        self._ensure_initialized()
        
        try:
            if format.lower() == "rdf":
                await self.knowledge_graph.export_to_rdf(f"{output_file}.ttl")
                return {
                    "success": True,
                    "export_file": f"{output_file}.ttl",
                    "format": "RDF/Turtle"
                }
            else:
                return {"success": False, "error": f"Unsupported format: {format}"}
        except Exception as e:
            self.logger.error(f"Failed to export knowledge graph: {e}")
            return {"success": False, "error": str(e)}
    
    # High-level convenience methods
    async def get_skill_insights(self, skill_code: str) -> Dict[str, Any]:
        """Get comprehensive insights about a specific skill"""
        self._ensure_initialized()
        
        try:
            # Get basic skill information
            skills = await self.query_skills(keyword=skill_code)
            
            insights = {
                "success": True,
                "skill_code": skill_code,
                "basic_info": skills.get("skills", []),
                "insights": {}
            }
            
            # Add similarity analysis if reasoning engine is available
            if self.reasoning_engine and skills.get("skills"):
                similar_skills = self.reasoning_engine.find_similar_skills(skill_code)
                insights["insights"]["similar_skills"] = similar_skills
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to get skill insights: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_role_analysis(self, role_code: str) -> Dict[str, Any]:
        """Get comprehensive analysis of a professional role"""
        self._ensure_initialized()
        
        try:
            # This would gather comprehensive role information
            analysis = {
                "success": True,
                "role_code": role_code,
                "skill_requirements": [],
                "career_paths": {
                    "from_roles": [],
                    "to_roles": []
                },
                "market_insights": {}
            }
            
            # Get career paths
            from_paths = await self.knowledge_graph.find_career_paths("", role_code)
            to_paths = await self.knowledge_graph.find_career_paths(role_code, "")
            
            analysis["career_paths"]["from_roles"] = from_paths
            analysis["career_paths"]["to_roles"] = to_paths
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get role analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_development_plan(self, person_profile: Dict[str, Any], 
                                      career_goal: str) -> Dict[str, Any]:
        """Generate a comprehensive development plan for a person"""
        self._ensure_initialized()
        
        try:
            current_skills = person_profile.get("skills", [])
            current_role = person_profile.get("current_role", "")
            
            # Get skill gaps
            gap_analysis = await self.analyze_skill_gaps(current_role, career_goal)
            
            # Get learning recommendations
            if gap_analysis.get("success") and gap_analysis.get("skill_gaps"):
                target_skills = [gap["skill_code"] for gap in gap_analysis["skill_gaps"][:5]]
                learning_recs = await self.get_learning_recommendations(target_skills)
            else:
                learning_recs = {"learning_recommendations": []}
            
            # Generate comprehensive plan
            development_plan = {
                "success": True,
                "person_profile": person_profile,
                "career_goal": career_goal,
                "skill_gap_analysis": gap_analysis,
                "learning_recommendations": learning_recs.get("learning_recommendations", []),
                "timeline": {
                    "short_term": "0-6 months: Focus on critical skill gaps",
                    "medium_term": "6-18 months: Build intermediate competencies",
                    "long_term": "18+ months: Achieve target role readiness"
                },
                "success_factors": [
                    "Regular skill assessment and progress tracking",
                    "Practical application through projects",
                    "Mentorship and professional networking",
                    "Continuous learning and adaptation"
                ]
            }
            
            return development_plan
            
        except Exception as e:
            self.logger.error(f"Failed to generate development plan: {e}")
            return {"success": False, "error": str(e)}
    
    # Enterprise Integration Methods
    async def initialize_enterprise_integration(self, integration_config_path: str = None, 
                                              redis_url: str = "redis://localhost:6379") -> APIResponse:
        """Initialize enterprise integration capabilities"""
        self._ensure_initialized()
        
        try:
            from ..enterprise.integration_manager import EnterpriseIntegrationManager
            
            self.integration_manager = EnterpriseIntegrationManager(integration_config_path)
            await self.integration_manager.initialize(redis_url)
            
            return APIResponse(message="Enterprise integration initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize enterprise integration: {e}")
            return APIResponse(success=False, message=str(e))
    
    async def add_enterprise_system(self, system_name: str, system_type: str, 
                                  credentials: Dict[str, Any], config: Dict[str, Any] = None) -> APIResponse:
        """Add a new enterprise system connection"""
        self._ensure_initialized()
        
        if not hasattr(self, 'integration_manager'):
            return APIResponse(success=False, message="Enterprise integration not initialized")
        
        try:
            from ..enterprise.connectors import SystemCredentials, create_connector
            
            system_credentials = SystemCredentials(
                system_type=system_type,
                **credentials
            )
            
            connector = create_connector(system_type, system_credentials, config)
            if await connector.connect():
                self.integration_manager.connectors[system_name] = connector
                return APIResponse(message=f"Successfully connected to {system_name}")
            else:
                return APIResponse(success=False, message=f"Failed to connect to {system_name}")
                
        except Exception as e:
            self.logger.error(f"Failed to add enterprise system {system_name}: {e}")
            return APIResponse(success=False, message=str(e))
    
    async def analyze_employee_sfia_levels(self, employee_id: str) -> Dict[str, Any]:
        """Analyze SFIA levels for a specific employee using enterprise data"""
        self._ensure_initialized()
        
        if not hasattr(self, 'integration_manager'):
            return {"success": False, "error": "Enterprise integration not initialized"}
        
        try:
            suggestions = await self.integration_manager.analyze_employee(employee_id)
            
            result = {
                "success": True,
                "employee_id": employee_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "suggestions": []
            }
            
            for suggestion in suggestions:
                result["suggestions"].append({
                    "skill_code": suggestion.skill_code,
                    "skill_name": suggestion.skill_name,
                    "current_level": suggestion.current_level,
                    "suggested_level": suggestion.suggested_level,
                    "confidence_score": suggestion.confidence_score,
                    "reasoning": suggestion.reasoning,
                    "supporting_evidence": suggestion.supporting_evidence,
                    "improvement_areas": suggestion.improvement_areas,
                    "timeline_estimate": suggestion.timeline_estimate,
                    "business_justification": suggestion.business_justification
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze employee SFIA levels: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_department_sfia_levels(self, department: str) -> Dict[str, Any]:
        """Analyze SFIA levels for all employees in a department"""
        self._ensure_initialized()
        
        if not hasattr(self, 'integration_manager'):
            return {"success": False, "error": "Enterprise integration not initialized"}
        
        try:
            department_results = await self.integration_manager.analyze_department(department)
            
            result = {
                "success": True,
                "department": department,
                "analysis_timestamp": datetime.now().isoformat(),
                "employees": {}
            }
            
            for employee_id, suggestions in department_results.items():
                result["employees"][employee_id] = []
                for suggestion in suggestions:
                    result["employees"][employee_id].append({
                        "skill_code": suggestion.skill_code,
                        "skill_name": suggestion.skill_name,
                        "suggested_level": suggestion.suggested_level,
                        "confidence_score": suggestion.confidence_score,
                        "reasoning": suggestion.reasoning,
                        "improvement_areas": suggestion.improvement_areas
                    })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze department SFIA levels: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_organization_sfia_insights(self) -> Dict[str, Any]:
        """Get organization-wide SFIA insights and analytics"""
        self._ensure_initialized()
        
        if not hasattr(self, 'integration_manager'):
            return {"success": False, "error": "Enterprise integration not initialized"}
        
        try:
            insights = await self.integration_manager.get_organization_insights()
            insights["success"] = True
            insights["analysis_timestamp"] = datetime.now().isoformat()
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to get organization insights: {e}")
            return {"success": False, "error": str(e)}
    
    async def register_real_time_callback(self, callback_function) -> APIResponse:
        """Register a callback for real-time SFIA analysis events"""
        self._ensure_initialized()
        
        if not hasattr(self, 'integration_manager'):
            return APIResponse(success=False, message="Enterprise integration not initialized")
        
        try:
            self.integration_manager.register_callback(callback_function)
            return APIResponse(message="Real-time callback registered successfully")
        except Exception as e:
            self.logger.error(f"Failed to register callback: {e}")
            return APIResponse(success=False, message=str(e))
    
    async def get_system_health_status(self) -> Dict[str, Any]:
        """Get health status of all connected enterprise systems"""
        self._ensure_initialized()
        
        if not hasattr(self, 'integration_manager'):
            return {"success": False, "error": "Enterprise integration not initialized"}
        
        try:
            health_results = {}
            
            for system_name, connector in self.integration_manager.connectors.items():
                health_results[system_name] = await connector.health_check()
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "systems": health_results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system health status: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_sfia_compliance_report(self, department: str = None) -> Dict[str, Any]:
        """Generate SFIA compliance report for organization or department"""
        self._ensure_initialized()
        
        if not hasattr(self, 'integration_manager'):
            return {"success": False, "error": "Enterprise integration not initialized"}
        
        try:
            if department:
                data = await self.analyze_department_sfia_levels(department)
                scope = f"Department: {department}"
            else:
                data = await self.get_organization_sfia_insights()
                scope = "Organization-wide"
            
            # Generate compliance metrics
            compliance_report = {
                "success": True,
                "scope": scope,
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_employees_analyzed": 0,
                    "skills_assessed": 0,
                    "average_confidence_score": 0.0,
                    "compliance_percentage": 0.0
                },
                "level_distribution": {},
                "skill_gaps": [],
                "recommendations": []
            }
            
            # Calculate metrics from data
            if department and "employees" in data:
                total_suggestions = 0
                total_confidence = 0.0
                
                for employee_id, suggestions in data["employees"].items():
                    compliance_report["summary"]["total_employees_analyzed"] += 1
                    for suggestion in suggestions:
                        total_suggestions += 1
                        total_confidence += suggestion["confidence_score"]
                        
                        level = suggestion["suggested_level"]
                        if level not in compliance_report["level_distribution"]:
                            compliance_report["level_distribution"][level] = 0
                        compliance_report["level_distribution"][level] += 1
                
                compliance_report["summary"]["skills_assessed"] = total_suggestions
                if total_suggestions > 0:
                    compliance_report["summary"]["average_confidence_score"] = total_confidence / total_suggestions
                    compliance_report["summary"]["compliance_percentage"] = (
                        sum(1 for s in [s for suggs in data["employees"].values() for s in suggs] 
                            if s["confidence_score"] >= 0.8) / total_suggestions * 100
                    )
            
            elif "total_employees" in data:
                compliance_report["summary"]["total_employees_analyzed"] = data["total_employees"]
                compliance_report["level_distribution"] = data.get("level_distribution", {})
                
                # Generate recommendations based on insights
                if "improvement_opportunities" in data:
                    compliance_report["recommendations"].extend([
                        f"Focus on {opp['skill']} development for employees at level {opp['current_level']}"
                        for opp in data["improvement_opportunities"][:5]
                    ])
                
                if "skill_gaps" in data:
                    compliance_report["skill_gaps"] = data["skill_gaps"]
            
            return compliance_report
            
        except Exception as e:
            self.logger.error(f"Failed to compare LLM responses: {e}")
            return {"success": False, "error": str(e)}
    
    # Portfolio Assessment Operations (IoC Methodology)
    async def assess_portfolio(
        self,
        portfolio_entries: List[Dict[str, Any]],
        supervisor_comments: List[Dict[str, Any]],
        student_info: Dict[str, Any],
        assessor_info: Dict[str, Any],
        suggested_skill: Optional[str] = None,
        suggested_level: Optional[int] = None
    ) -> PortfolioAnalysisResponse:
        """
        Assess student portfolio using IoC (Institute of Coding) methodology
        
        Args:
            portfolio_entries: List of portfolio entry dictionaries
            supervisor_comments: List of supervisor comment dictionaries  
            student_info: Student information dictionary
            assessor_info: Assessor information dictionary
            suggested_skill: Optional suggested SFIA skill code
            suggested_level: Optional suggested SFIA level
            
        Returns:
            PortfolioAnalysisResponse with complete assessment results
        """
        self._ensure_initialized()
        
        try:
            return await self.portfolio_service.analyze_portfolio(
                portfolio_entries=portfolio_entries,
                supervisor_comments=supervisor_comments,
                student_info=student_info,
                assessor_info=assessor_info,
                suggested_skill=suggested_skill,
                suggested_level=suggested_level
            )
        except Exception as e:
            self.logger.error(f"Portfolio assessment failed: {e}")
            return PortfolioAnalysisResponse(
                success=False,
                message=f"Portfolio assessment failed: {str(e)}"
            )
    
    async def get_portfolio_mapping_guidance(
        self,
        activities_description: str,
        student_level: str = "placement"
    ) -> PortfolioMappingGuidance:
        """
        Get guidance for mapping portfolio activities to SFIA skills
        
        Args:
            activities_description: Description of student activities
            student_level: Student level (placement, graduate, etc.)
            
        Returns:
            PortfolioMappingGuidance with recommendations and best practices
        """
        self._ensure_initialized()
        
        try:
            return await self.portfolio_service.get_portfolio_mapping_guidance(
                activities_description=activities_description,
                student_level=student_level
            )
        except Exception as e:
            self.logger.error(f"Failed to get portfolio guidance: {e}")
            return PortfolioMappingGuidance()
    
    async def validate_portfolio_evidence(
        self,
        portfolio_entries: List[Dict[str, Any]],
        skill_code: str,
        skill_level: int
    ) -> Dict[str, Any]:
        """
        Validate portfolio evidence against SFIA skill requirements
        
        Args:
            portfolio_entries: List of portfolio entries
            skill_code: SFIA skill code to validate against
            skill_level: SFIA level to validate against
            
        Returns:
            Validation results with coverage analysis and recommendations
        """
        self._ensure_initialized()
        
        try:
            # Parse entries using the portfolio service
            entries = await self.portfolio_service._parse_portfolio_entries(portfolio_entries)
            
            # Map to skill components
            component_mappings = await self.portfolio_service._map_entries_to_skill_components(
                entries, skill_code, skill_level
            )
            
            # Calculate coverage metrics
            total_components = len(component_mappings)
            covered_components = sum(1 for mapping in component_mappings if len(mapping.portfolio_entries) > 0)
            multiple_entry_components = sum(1 for mapping in component_mappings if len(mapping.portfolio_entries) >= 2)
            
            coverage_percentage = (covered_components / total_components * 100) if total_components > 0 else 0
            multiple_entry_percentage = (multiple_entry_components / total_components * 100) if total_components > 0 else 0
            
            # Generate recommendations
            recommendations = []
            if coverage_percentage < 85:
                recommendations.append("Increase coverage: Add portfolio entries to address more skill components")
            if multiple_entry_percentage < 85:
                recommendations.append("Add multiple entries: Ensure 85%+ of components have multiple supporting entries")
            
            evidence_quality_distribution = {}
            for mapping in component_mappings:
                quality = mapping.evidence_quality.value
                evidence_quality_distribution[quality] = evidence_quality_distribution.get(quality, 0) + 1
            
            return {
                "success": True,
                "skill_code": skill_code,
                "skill_level": skill_level,
                "coverage_metrics": {
                    "total_components": total_components,
                    "covered_components": covered_components,
                    "coverage_percentage": coverage_percentage,
                    "multiple_entry_components": multiple_entry_components,
                    "multiple_entry_percentage": multiple_entry_percentage
                },
                "evidence_quality_distribution": evidence_quality_distribution,
                "component_mappings": [
                    {
                        "component": mapping.component_description[:100] + "..." if len(mapping.component_description) > 100 else mapping.component_description,
                        "entries_count": len(mapping.portfolio_entries),
                        "coverage_percentage": mapping.coverage_percentage,
                        "evidence_quality": mapping.evidence_quality.value
                    }
                    for mapping in component_mappings
                ],
                "recommendations": recommendations,
                "meets_ioc_criteria": coverage_percentage >= 85 and multiple_entry_percentage >= 85
            }
            
        except Exception as e:
            self.logger.error(f"Portfolio validation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_portfolio_template(
        self,
        skill_code: str,
        skill_level: int,
        placement_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a portfolio template for a specific SFIA skill and level
        
        Args:
            skill_code: SFIA skill code
            skill_level: SFIA level
            placement_context: Optional context about the placement/internship
            
        Returns:
            Portfolio template with guidance and structure
        """
        self._ensure_initialized()
        
        try:
            # Get skill details
            skill_data = await self.knowledge_graph.get_skill_details(skill_code, skill_level)
            
            if not skill_data:
                return {"success": False, "error": f"Skill {skill_code} level {skill_level} not found"}
            
            # Generate template structure
            template = {
                "success": True,
                "skill_code": skill_code,
                "skill_name": skill_data.get('name', skill_code),
                "skill_level": skill_level,
                "skill_description": skill_data.get('description', ''),
                "activities": skill_data.get('activities', []),
                "portfolio_structure": {
                    "technical_achievement_entries": {
                        "description": "Portfolio entries demonstrating completion of skill components",
                        "requirements": [
                            "Multiple entries for at least 85% of skill components",
                            "Evidence-based content with specific details",
                            "Workplace context and real-world application",
                            "Supervisor verification"
                        ],
                        "suggested_entries": []
                    },
                    "reflection_entries": {
                        "description": "Reflective entries on learning and development",
                        "requirements": [
                            "Professional writing style",
                            "Personal development identification",
                            "Professional accountability demonstration",
                            "Evidence-based reflection"
                        ],
                        "suggested_topics": [
                            "Key learning outcomes from the experience",
                            "Challenges encountered and how they were overcome",
                            "Skills development and progression",
                            "Business impact and professional accountability",
                            "Future development needs and plans"
                        ]
                    },
                    "supervisor_comments": {
                        "description": "Comments from workplace supervisor",
                        "requirements": [
                            "Confirmation of portfolio entry accuracy",
                            "Contextual evaluation of achievements",
                            "Assessment of task difficulty and importance",
                            "Professional recommendation"
                        ]
                    }
                },
                "assessment_criteria": {
                    "technical_achievement": {
                        "weight": 16,
                        "criteria": [
                            "Portfolio entries showing completion of skill components",
                            "Multiple entries for 85%+ of components",
                            "Supervisor verification of accuracy",
                            "Evidence-based rather than assertion-based content",
                            "Contextual evaluation by supervisor"
                        ]
                    },
                    "reflection": {
                        "weight": 9,
                        "criteria": [
                            "Reflective portfolio entries across skill area",
                            "Professional writing style",
                            "Personal development identification",
                            "Professional accountability demonstration",
                            "Evidence-based reflection with comparisons"
                        ]
                    },
                    "generic_responsibility_characteristics": {
                        "description": "SFIA Level 3 generic responsibility characteristics",
                        "requirements": [
                            "Demonstrate 13+ core characteristics",
                            "26+ instances of core characteristics",
                            "44+ total instances of all characteristics"
                        ]
                    }
                },
                "scoring_thresholds": {
                    "competency": 85,
                    "proficiency": 65,
                    "developing": "<65"
                }
            }
            
            # Generate suggested entries for each skill component/activity
            if skill_data.get('activities'):
                for i, activity in enumerate(skill_data['activities']):
                    template["portfolio_structure"]["technical_achievement_entries"]["suggested_entries"].append({
                        "component": f"Component {i+1}",
                        "activity_description": activity,
                        "suggested_entries": [
                            f"Entry 1: Describe a specific instance of {activity.lower()}",
                            f"Entry 2: Detail another example demonstrating {activity.lower()}",
                            f"Entry 3: Optional third example showing progression or complexity"
                        ],
                        "evidence_suggestions": [
                            "Include specific numbers, quantities, or metrics",
                            "Describe challenges encountered and solutions applied",
                            "Mention tools, techniques, or methodologies used",
                            "Reference business context and stakeholder impact"
                        ]
                    })
            
            return template
            
        except Exception as e:
            self.logger.error(f"Failed to generate portfolio template: {e}")
            return {"success": False, "error": str(e)}

    # ============================================================================
    # SFIA 9 Enhanced Framework Methods
    # ============================================================================
    
    def get_sfia9_attribute(self, code: str) -> Optional[EnhancedSFIAAttribute]:
        """Get SFIA 9 attribute by code"""
        return self.sfia9_service.get_attribute_by_code(code)
    
    def get_sfia9_skill(self, code: str) -> Optional[EnhancedSFIASkill]:
        """Get SFIA 9 skill by code"""
        return self.sfia9_service.get_skill_by_code(code)
    
    def search_sfia9_skills(self, query: str, limit: int = 10) -> List[EnhancedSFIASkill]:
        """Search SFIA 9 skills"""
        return self.sfia9_service.search_skills(query, limit)
    
    def get_sfia9_skills_by_category(self, category: str) -> List[EnhancedSFIASkill]:
        """Get SFIA 9 skills by category"""
        return self.sfia9_service.get_skills_by_category(category)
    
    def get_sfia9_level_description(self, level: int) -> Optional[SFIA9LevelDefinition]:
        """Get SFIA 9 level description"""
        return self.sfia9_service.get_level_description(level)
    
    def assess_sfia9_skill_evidence(self, skill_code: str, level: int, evidence: str) -> Dict[str, Any]:
        """Assess evidence against SFIA 9 skill and level"""
        return self.sfia9_service.assess_skill_level_match(skill_code, level, evidence)
    
    def get_sfia9_comprehensive_skill_analysis(self, skill_code: str) -> Dict[str, Any]:
        """Get comprehensive SFIA 9 skill analysis"""
        return self.sfia9_service.get_comprehensive_skill_analysis(skill_code)
    
    def get_sfia9_category_overview(self, category: str) -> Dict[str, Any]:
        """Get SFIA 9 category overview"""
        return self.sfia9_service.get_category_overview(category)
    
    def get_sfia9_statistics(self) -> Dict[str, Any]:
        """Get SFIA 9 framework statistics"""
        return self.sfia9_service.get_statistics()


# Context manager support
class SFIASDKContext:
    """Context manager for SFIA SDK"""
    
    def __init__(self, config: SFIASDKConfig):
        self.config = config
        self.sdk = None
    
    async def __aenter__(self) -> SFIASDK:
        self.sdk = SFIASDK(self.config)
        await self.sdk.initialize()
        return self.sdk
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.sdk:
            await self.sdk.close()


# Factory functions
def create_sfia_sdk(config: SFIASDKConfig) -> SFIASDK:
    """Factory function to create SFIA SDK instance"""
    return SFIASDK(config)


def create_sfia_sdk_context(config: SFIASDKConfig) -> SFIASDKContext:
    """Factory function to create SFIA SDK context manager"""
    return SFIASDKContext(config)