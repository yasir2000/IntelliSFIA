"""
Multi-Agent System for SFIA Ontology Intelligence

This module defines specialized AI agents that collaborate to understand and reason
about SFIA skills, roles, and career pathways.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from pydantic import BaseModel, Field

from .knowledge_graph import SFIAKnowledgeGraph
from .reasoning import SFIAReasoningEngine
from ..models.sfia_models import Skill, ProfessionalRole, CareerPathway, SkillGap


class SFIAToolkit:
    """Tools for SFIA agents to interact with the knowledge graph and reasoning engine"""
    
    def __init__(self, knowledge_graph: SFIAKnowledgeGraph, reasoning_engine: SFIAReasoningEngine):
        self.kg = knowledge_graph
        self.reasoning = reasoning_engine
        self._setup_tools()
    
    def _setup_tools(self):
        """Initialize all SFIA-specific tools"""
        self.tools = [
            Tool(
                name="query_skills",
                description="Query SFIA skills by category, level, or keyword. Input: JSON with 'category', 'level', or 'keyword'",
                func=self._query_skills
            ),
            Tool(
                name="analyze_skill_gaps",
                description="Analyze skill gaps between current and target roles. Input: JSON with 'current_role' and 'target_role'",
                func=self._analyze_skill_gaps
            ),
            Tool(
                name="recommend_career_path",
                description="Recommend career progression paths. Input: JSON with 'current_skills' and 'career_goals'",
                func=self._recommend_career_path
            ),
            Tool(
                name="build_team_composition",
                description="Suggest optimal team composition for a project. Input: JSON with 'project_requirements' and 'available_resources'",
                func=self._build_team_composition
            ),
            Tool(
                name="assess_role_fit",
                description="Assess how well a person fits a role. Input: JSON with 'person_skills' and 'role_requirements'",
                func=self._assess_role_fit
            ),
            Tool(
                name="get_learning_recommendations",
                description="Get learning recommendations for skill development. Input: JSON with 'target_skills' and 'current_level'",
                func=self._get_learning_recommendations
            )
        ]
    
    def _query_skills(self, query_input: str) -> str:
        """Query skills from the knowledge graph"""
        try:
            query_data = json.loads(query_input)
            results = self.kg.query_skills(**query_data)
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error querying skills: {str(e)}"
    
    def _analyze_skill_gaps(self, gap_input: str) -> str:
        """Analyze skill gaps between roles"""
        try:
            gap_data = json.loads(gap_input)
            gaps = self.reasoning.analyze_skill_gaps(
                gap_data['current_role'], 
                gap_data['target_role']
            )
            return json.dumps([gap.dict() for gap in gaps], indent=2)
        except Exception as e:
            return f"Error analyzing skill gaps: {str(e)}"
    
    def _recommend_career_path(self, path_input: str) -> str:
        """Recommend career progression paths"""
        try:
            path_data = json.loads(path_input)
            recommendations = self.reasoning.recommend_career_paths(
                path_data['current_skills'],
                path_data['career_goals']
            )
            return json.dumps(recommendations, indent=2)
        except Exception as e:
            return f"Error recommending career path: {str(e)}"
    
    def _build_team_composition(self, team_input: str) -> str:
        """Build optimal team composition"""
        try:
            team_data = json.loads(team_input)
            composition = self.reasoning.optimize_team_composition(
                team_data['project_requirements'],
                team_data.get('available_resources', [])
            )
            return json.dumps(composition, indent=2)
        except Exception as e:
            return f"Error building team composition: {str(e)}"
    
    def _assess_role_fit(self, fit_input: str) -> str:
        """Assess role fit for a person"""
        try:
            fit_data = json.loads(fit_input)
            assessment = self.reasoning.assess_role_fit(
                fit_data['person_skills'],
                fit_data['role_requirements']
            )
            return json.dumps(assessment, indent=2)
        except Exception as e:
            return f"Error assessing role fit: {str(e)}"
    
    def _get_learning_recommendations(self, learning_input: str) -> str:
        """Get learning recommendations"""
        try:
            learning_data = json.loads(learning_input)
            recommendations = self.reasoning.get_learning_recommendations(
                learning_data['target_skills'],
                learning_data.get('current_level', 1)
            )
            return json.dumps(recommendations, indent=2)
        except Exception as e:
            return f"Error getting learning recommendations: {str(e)}"


class SFIAAgentCrew:
    """Collaborative multi-agent crew for SFIA intelligence"""
    
    def __init__(self, knowledge_graph: SFIAKnowledgeGraph, reasoning_engine: SFIAReasoningEngine):
        self.kg = knowledge_graph
        self.reasoning = reasoning_engine
        self.toolkit = SFIAToolkit(knowledge_graph, reasoning_engine)
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.1)
        self._setup_agents()
        self._setup_crew()
    
    def _setup_agents(self):
        """Initialize specialized SFIA agents"""
        
        # Skills Analyst Agent
        self.skills_analyst = Agent(
            role="SFIA Skills Analyst",
            goal="Analyze and understand SFIA skills, their relationships, and applications",
            backstory="""You are an expert in the SFIA (Skills Framework for the Information Age) 
            with deep knowledge of all skill categories, levels, and their practical applications. 
            You can analyze skill requirements, identify gaps, and provide recommendations for 
            skill development and career progression.""",
            tools=self.toolkit.tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )
        
        # Career Advisor Agent
        self.career_advisor = Agent(
            role="AI Career Advisor",
            goal="Provide intelligent career guidance and progression recommendations",
            backstory="""You are a senior career advisor specializing in IT and digital careers. 
            You understand how SFIA skills translate to real-world roles and can provide 
            personalized career guidance, identify progression opportunities, and suggest 
            learning paths for professional development.""",
            tools=self.toolkit.tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )
        
        # Team Composition Specialist
        self.team_specialist = Agent(
            role="Team Composition Specialist",
            goal="Optimize team formations and resource allocation based on skills",
            backstory="""You are an expert in team dynamics and project management with 
            specialized knowledge in skill-based resource allocation. You can analyze 
            project requirements and build optimal teams by matching skills to needs, 
            identifying potential gaps, and suggesting alternatives.""",
            tools=self.toolkit.tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )
        
        # Learning and Development Specialist
        self.learning_specialist = Agent(
            role="Learning & Development Specialist",
            goal="Design personalized learning paths and skill development programs",
            backstory="""You are a learning and development expert who specializes in 
            skill-based training programs. You can create personalized learning paths, 
            recommend training resources, and design development programs that align 
            with SFIA competency frameworks.""",
            tools=self.toolkit.tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )
        
        # Strategic Workforce Planner
        self.workforce_planner = Agent(
            role="Strategic Workforce Planner",
            goal="Provide strategic insights for workforce planning and organizational development",
            backstory="""You are a strategic workforce planning expert who understands 
            how skills and competencies align with business objectives. You can analyze 
            organizational skill portfolios, identify future skill needs, and provide 
            recommendations for strategic workforce development.""",
            tools=self.toolkit.tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )
    
    def _setup_crew(self):
        """Initialize the crew with agents"""
        self.crew = Crew(
            agents=[
                self.skills_analyst,
                self.career_advisor,
                self.team_specialist,
                self.learning_specialist,
                self.workforce_planner
            ],
            process=Process.hierarchical,
            manager_llm=self.llm,
            verbose=True
        )
    
    async def analyze_career_progression(self, current_role: str, target_role: str, timeline: str = "2 years") -> Dict[str, Any]:
        """Comprehensive career progression analysis"""
        
        tasks = [
            Task(
                description=f"""Analyze the skill requirements and gaps between the current role 
                '{current_role}' and target role '{target_role}'. Provide a detailed breakdown of:
                1. Required skills for the target role
                2. Current skill gaps that need to be addressed
                3. Skill overlap and transferable competencies
                4. Priority levels for skill development""",
                agent=self.skills_analyst,
                expected_output="Detailed skill gap analysis with prioritized recommendations"
            ),
            
            Task(
                description=f"""Based on the skill analysis, create a comprehensive career 
                progression plan from '{current_role}' to '{target_role}' within {timeline}. Include:
                1. Step-by-step progression pathway
                2. Intermediate roles or positions
                3. Timeline and milestones
                4. Alternative pathways if direct progression isn't possible""",
                agent=self.career_advisor,
                expected_output="Complete career progression roadmap with timelines"
            ),
            
            Task(
                description=f"""Design a personalized learning and development program to bridge 
                the skill gaps identified for progressing from '{current_role}' to '{target_role}'. 
                Provide:
                1. Structured learning path with specific resources
                2. Skill development priorities and sequence
                3. Practical projects and experience recommendations
                4. Certification and assessment milestones""",
                agent=self.learning_specialist,
                expected_output="Comprehensive learning and development plan"
            )
        ]
        
        result = self.crew.kickoff(tasks=tasks)
        return {
            "career_analysis": result,
            "timestamp": datetime.now().isoformat(),
            "current_role": current_role,
            "target_role": target_role,
            "timeline": timeline
        }
    
    async def optimize_team_for_project(self, project_requirements: Dict[str, Any], available_team: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize team composition for a specific project"""
        
        tasks = [
            Task(
                description=f"""Analyze the project requirements: {json.dumps(project_requirements, indent=2)}
                Extract and categorize:
                1. Required SFIA skills and competency levels
                2. Project complexity and scale indicators
                3. Critical success factors and risk areas
                4. Timeline and resource constraints""",
                agent=self.skills_analyst,
                expected_output="Detailed project skill requirements analysis"
            ),
            
            Task(
                description=f"""Based on the project requirements and available team members: 
                {json.dumps(available_team, indent=2)}
                Create an optimal team composition by:
                1. Matching team member skills to project needs
                2. Identifying skill gaps and overlaps
                3. Recommending team structure and roles
                4. Suggesting mitigation strategies for gaps""",
                agent=self.team_specialist,
                expected_output="Optimized team composition with role assignments"
            ),
            
            Task(
                description="""Provide strategic recommendations for the team composition including:
                1. Risk assessment and mitigation strategies
                2. Team performance optimization suggestions
                3. Resource allocation recommendations
                4. Success metrics and monitoring approach""",
                agent=self.workforce_planner,
                expected_output="Strategic team optimization recommendations"
            )
        ]
        
        result = self.crew.kickoff(tasks=tasks)
        return {
            "team_optimization": result,
            "timestamp": datetime.now().isoformat(),
            "project_requirements": project_requirements,
            "team_analysis": available_team
        }
    
    async def assess_organizational_skills(self, organization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive organizational skills assessment"""
        
        tasks = [
            Task(
                description=f"""Analyze the organizational skill portfolio: 
                {json.dumps(organization_data, indent=2)}
                Provide insights on:
                1. Current skill distribution and strengths
                2. Skill gaps and vulnerabilities
                3. Skill redundancies and optimization opportunities
                4. Competency maturity assessment""",
                agent=self.skills_analyst,
                expected_output="Comprehensive organizational skill assessment"
            ),
            
            Task(
                description="""Based on the skill analysis, provide strategic workforce 
                planning recommendations including:
                1. Future skill needs and market trends
                2. Strategic hiring and development priorities
                3. Succession planning recommendations
                4. Organizational capability development roadmap""",
                agent=self.workforce_planner,
                expected_output="Strategic workforce planning recommendations"
            ),
            
            Task(
                description="""Design an organizational learning and development strategy 
                that addresses identified skill gaps and supports strategic objectives:
                1. Enterprise learning programs and initiatives
                2. Skill development pathways for different career tracks
                3. Knowledge management and transfer strategies
                4. Performance measurement and ROI framework""",
                agent=self.learning_specialist,
                expected_output="Organizational L&D strategic plan"
            )
        ]
        
        result = self.crew.kickoff(tasks=tasks)
        return {
            "organizational_assessment": result,
            "timestamp": datetime.now().isoformat(),
            "organization_data": organization_data
        }


# Factory function for easy initialization
def create_sfia_agent_crew(knowledge_graph: SFIAKnowledgeGraph, reasoning_engine: SFIAReasoningEngine) -> SFIAAgentCrew:
    """Factory function to create and initialize SFIA agent crew"""
    return SFIAAgentCrew(knowledge_graph, reasoning_engine)