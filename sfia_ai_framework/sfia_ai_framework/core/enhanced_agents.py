"""
IntelliSFIA Enhanced Multi-Agent System with Multi-LLM Support

This module extends the original agent system to support multiple LLM providers
including Ollama local models, allowing agents to work autonomously with
different language models.
"""

import asyncio
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
import json

try:
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import BaseTool
    from langchain.llms.base import LLM
    from langchain.callbacks.manager import CallbackManagerForLLMRun
    from langchain.schema import LLMResult, Generation
except ImportError:
    # Mock classes if CrewAI is not available
    class Agent: pass
    class Task: pass  
    class Crew: pass
    class Process: pass
    class BaseTool: pass
    class LLM: pass
    class CallbackManagerForLLMRun: pass
    class LLMResult: pass
    class Generation: pass

from ..llm.providers import LLMManager, LLMConfig, LLMProvider

logger = logging.getLogger(__name__)


class MultiLLMLangChainWrapper(LLM):
    """LangChain wrapper for multi-LLM provider support"""
    
    def __init__(self, llm_manager: LLMManager, provider: Optional[str] = None):
        super().__init__()
        self.llm_manager = llm_manager
        self.provider = provider
    
    @property
    def _llm_type(self) -> str:
        return "multi_llm_wrapper"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Synchronous call wrapper"""
        # Run async method in event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new task
                import asyncio
                future = asyncio.ensure_future(self._acall(prompt, stop, run_manager, **kwargs))
                return asyncio.run_coroutine_threadsafe(future, loop).result()
            else:
                return loop.run_until_complete(self._acall(prompt, stop, run_manager, **kwargs))
        except RuntimeError:
            # No event loop, create a new one
            return asyncio.run(self._acall(prompt, stop, run_manager, **kwargs))
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Asynchronous call to LLM provider"""
        try:
            response = await self.llm_manager.generate(prompt, provider=self.provider, **kwargs)
            
            # Handle stop sequences
            if stop:
                for stop_seq in stop:
                    if stop_seq in response:
                        response = response.split(stop_seq)[0]
            
            return response
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return f"Error: {e}"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get identifying parameters"""
        return {
            "provider": self.provider or "default",
            "llm_manager": id(self.llm_manager)
        }


class EnhancedSFIAToolkit(BaseTool):
    """Enhanced IntelliSFIA toolkit with multi-LLM support"""
    
    name = "intellisfia_toolkit"
    description = "Comprehensive SFIA skills analysis toolkit with multi-LLM capabilities"
    
    def __init__(self, knowledge_graph, reasoning_engine, llm_manager: LLMManager):
        super().__init__()
        self.knowledge_graph = knowledge_graph
        self.reasoning_engine = reasoning_engine
        self.llm_manager = llm_manager
    
    def _run(self, query: str) -> str:
        """Synchronous tool execution"""
        return asyncio.run(self._arun(query))
    
    async def _arun(self, query: str) -> str:
        """Asynchronous tool execution"""
        try:
            # Parse query to determine operation
            if "skills" in query.lower():
                return await self._handle_skills_query(query)
            elif "gap" in query.lower():
                return await self._handle_gap_analysis(query)
            elif "career" in query.lower():
                return await self._handle_career_query(query)
            elif "team" in query.lower():
                return await self._handle_team_query(query)
            else:
                return await self._handle_general_query(query)
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return f"Error executing query: {e}"
    
    async def _handle_skills_query(self, query: str) -> str:
        """Handle skills-related queries"""
        try:
            # Extract potential filters from query using LLM
            filter_prompt = f"""
            Extract filters from this skills query: "{query}"
            Return JSON with category, level, and keyword if mentioned.
            Example: {{"category": "Technical", "level": 3, "keyword": "programming"}}
            """
            
            filters_json = await self.llm_manager.generate(filter_prompt)
            
            try:
                filters = json.loads(filters_json)
            except:
                filters = {}
            
            # Query knowledge graph
            skills = await self.knowledge_graph.query_skills(
                category=filters.get("category"),
                level=filters.get("level"),
                keyword=filters.get("keyword")
            )
            
            return f"Found {len(skills)} skills matching your criteria: {skills[:5]}"
        
        except Exception as e:
            return f"Error handling skills query: {e}"
    
    async def _handle_gap_analysis(self, query: str) -> str:
        """Handle skill gap analysis queries"""
        try:
            # Extract roles from query using LLM
            roles_prompt = f"""
            Extract current role and target role from: "{query}"
            Return JSON: {{"current_role": "...", "target_role": "..."}}
            """
            
            roles_json = await self.llm_manager.generate(roles_prompt)
            
            try:
                roles = json.loads(roles_json)
                current_role = roles.get("current_role", "Unknown")
                target_role = roles.get("target_role", "Unknown")
            except:
                current_role = "Unknown"
                target_role = "Unknown"
            
            # Perform gap analysis
            if self.reasoning_engine:
                gaps = await self.reasoning_engine.analyze_skill_gaps(current_role, target_role)
                return f"Skill gaps from {current_role} to {target_role}: {gaps[:3]}"
            else:
                return "Reasoning engine not available for gap analysis"
        
        except Exception as e:
            return f"Error handling gap analysis: {e}"
    
    async def _handle_career_query(self, query: str) -> str:
        """Handle career-related queries"""
        try:
            # Use LLM to understand career query
            career_prompt = f"""
            Analyze this career query: "{query}"
            Provide career guidance based on SFIA framework.
            Keep response concise and actionable.
            """
            
            response = await self.llm_manager.generate(career_prompt)
            return response
        
        except Exception as e:
            return f"Error handling career query: {e}"
    
    async def _handle_team_query(self, query: str) -> str:
        """Handle team-related queries"""
        try:
            # Use LLM for team analysis
            team_prompt = f"""
            Analyze this team query: "{query}"
            Provide team optimization advice based on SFIA skills framework.
            Keep response practical and specific.
            """
            
            response = await self.llm_manager.generate(team_prompt)
            return response
        
        except Exception as e:
            return f"Error handling team query: {e}"
    
    async def _handle_general_query(self, query: str) -> str:
        """Handle general SFIA queries"""
        try:
            # Use LLM for general SFIA analysis
            general_prompt = f"""
            Answer this SFIA-related query: "{query}"
            Use your knowledge of the Skills Framework for the Information Age.
            Provide accurate, helpful information.
            """
            
            response = await self.llm_manager.generate(general_prompt)
            return response
        
        except Exception as e:
            return f"Error handling general query: {e}"


class MultiLLMAgent:
    """Enhanced agent with multi-LLM support"""
    
    def __init__(self, 
                 name: str,
                 role: str, 
                 goal: str,
                 backstory: str,
                 llm_manager: LLMManager,
                 tools: List[BaseTool] = None,
                 preferred_provider: Optional[str] = None):
        
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.llm_manager = llm_manager
        self.tools = tools or []
        self.preferred_provider = preferred_provider
        
        # Create LangChain wrapper
        self.llm_wrapper = MultiLLMLangChainWrapper(llm_manager, preferred_provider)
        
        # Create CrewAI agent
        try:
            self.agent = Agent(
                role=role,
                goal=goal,
                backstory=backstory,
                tools=self.tools,
                llm=self.llm_wrapper,
                verbose=True,
                allow_delegation=False
            )
        except Exception as e:
            logger.warning(f"CrewAI not available, using mock agent: {e}")
            self.agent = None
    
    async def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> str:
        """Execute a task using the agent"""
        try:
            if self.agent:
                # Use CrewAI agent
                task = Task(
                    description=task_description,
                    agent=self.agent,
                    context=context
                )
                
                crew = Crew(
                    agents=[self.agent],
                    tasks=[task],
                    verbose=True,
                    process=Process.sequential
                )
                
                result = crew.kickoff()
                return str(result)
            else:
                # Fallback to direct LLM call
                prompt = f"""
                As a {self.role}, {self.backstory}
                
                Your goal: {self.goal}
                
                Task: {task_description}
                
                Context: {json.dumps(context or {}, indent=2)}
                
                Please complete this task thoroughly and professionally.
                """
                
                return await self.llm_manager.generate(prompt, provider=self.preferred_provider)
        
        except Exception as e:
            logger.error(f"Task execution error for {self.name}: {e}")
            return f"Error executing task: {e}"
    
    async def analyze_with_provider(self, query: str, provider: str) -> str:
        """Analyze query using specific LLM provider"""
        try:
            prompt = f"""
            As a {self.role}, analyze this query: "{query}"
            
            Background: {self.backstory}
            Goal: {self.goal}
            
            Provide detailed analysis based on your expertise.
            """
            
            return await self.llm_manager.generate(prompt, provider=provider)
        except Exception as e:
            logger.error(f"Provider-specific analysis error: {e}")
            return f"Error with provider {provider}: {e}"


class EnhancedSFIAAgentCrew:
    """Enhanced IntelliSFIA multi-agent crew with multi-LLM support"""
    
    def __init__(self, knowledge_graph, reasoning_engine, llm_manager: LLMManager):
        self.knowledge_graph = knowledge_graph
        self.reasoning_engine = reasoning_engine
        self.llm_manager = llm_manager
        
        # Create enhanced toolkit
        self.toolkit = EnhancedSFIAToolkit(knowledge_graph, reasoning_engine, llm_manager)
        
        # Create specialized agents with different LLM preferences
        self.agents = self._create_agents()
    
    def _create_agents(self) -> Dict[str, MultiLLMAgent]:
        """Create specialized agents with different LLM providers"""
        
        # Get available providers
        providers = list(self.llm_manager.clients.keys())
        
        agents = {}
        
        # Skills Analyst - preferably using the most capable model
        agents["skills_analyst"] = MultiLLMAgent(
            name="Skills Analyst",
            role="SFIA Skills Analysis Expert",
            goal="Provide comprehensive analysis of skills, competencies, and their relationships within the SFIA framework",
            backstory="You are an expert in the Skills Framework for the Information Age with deep knowledge of skill categories, levels, and professional development pathways. You excel at analyzing skill requirements and identifying competency gaps.",
            llm_manager=self.llm_manager,
            tools=[self.toolkit],
            preferred_provider=providers[0] if providers else None
        )
        
        # Career Advisor - using a different provider for diversity
        agents["career_advisor"] = MultiLLMAgent(
            name="Career Advisor",
            role="Career Development Specialist",
            goal="Provide personalized career guidance and development recommendations based on SFIA skills framework",
            backstory="You are a professional career counselor specializing in IT and digital careers. You understand career progression paths and can provide actionable advice for professional development.",
            llm_manager=self.llm_manager,
            tools=[self.toolkit],
            preferred_provider=providers[1] if len(providers) > 1 else providers[0] if providers else None
        )
        
        # Team Specialist - potentially using local model for privacy
        agents["team_specialist"] = MultiLLMAgent(
            name="Team Specialist",
            role="Team Composition and Dynamics Expert",
            goal="Optimize team composition and analyze team dynamics for maximum effectiveness",
            backstory="You are an expert in team psychology and organizational behavior with deep understanding of how different skills complement each other in team settings.",
            llm_manager=self.llm_manager,
            tools=[self.toolkit],
            preferred_provider="ollama" if "ollama" in self.llm_manager.clients else providers[0] if providers else None
        )
        
        # Learning Specialist
        agents["learning_specialist"] = MultiLLMAgent(
            name="Learning Specialist",
            role="Learning and Development Expert",
            goal="Design effective learning paths and recommend appropriate resources for skill development",
            backstory="You are a learning and development professional with expertise in adult learning principles and technology training methodologies.",
            llm_manager=self.llm_manager,
            tools=[self.toolkit],
            preferred_provider=providers[-1] if providers else None
        )
        
        # Workforce Planner
        agents["workforce_planner"] = MultiLLMAgent(
            name="Workforce Planner",
            role="Strategic Workforce Planning Analyst",
            goal="Provide strategic workforce planning insights and organizational capability analysis",
            backstory="You are a strategic HR analyst with expertise in workforce planning, skills forecasting, and organizational development.",
            llm_manager=self.llm_manager,
            tools=[self.toolkit],
            preferred_provider=providers[0] if providers else None
        )
        
        return agents
    
    async def analyze_skill(self, skill_code: str) -> Dict[str, Any]:
        """Comprehensive skill analysis using multiple agents"""
        results = {}
        
        # Skills Analyst provides detailed analysis
        task = f"Analyze the SFIA skill '{skill_code}' in detail, including its definition, levels, relationships, and applications."
        results["detailed_analysis"] = await self.agents["skills_analyst"].execute_task(task)
        
        # Career Advisor provides career context
        task = f"Explain how the skill '{skill_code}' fits into career development and what roles typically require this skill."
        results["career_context"] = await self.agents["career_advisor"].execute_task(task)
        
        # Learning Specialist provides learning recommendations
        task = f"Recommend learning resources and development strategies for improving the skill '{skill_code}'."
        results["learning_recommendations"] = await self.agents["learning_specialist"].execute_task(task)
        
        return {
            "skill_code": skill_code,
            "analysis_timestamp": datetime.now().isoformat(),
            "multi_agent_analysis": results
        }
    
    async def analyze_career_progression(self, current_role: str, target_role: str, timeline: str = "2 years") -> Dict[str, Any]:
        """Multi-agent career progression analysis"""
        context = {
            "current_role": current_role,
            "target_role": target_role,
            "timeline": timeline
        }
        
        results = {}
        
        # Skills Analyst identifies skill gaps
        task = f"Analyze the skill differences between '{current_role}' and '{target_role}' roles. Identify key skills that need development."
        results["skill_gap_analysis"] = await self.agents["skills_analyst"].execute_task(task, context)
        
        # Career Advisor provides progression strategy
        task = f"Create a career progression strategy from '{current_role}' to '{target_role}' within {timeline}. Include milestones and intermediate steps."
        results["progression_strategy"] = await self.agents["career_advisor"].execute_task(task, context)
        
        # Learning Specialist creates development plan
        task = f"Design a comprehensive learning and development plan to progress from '{current_role}' to '{target_role}' within {timeline}."
        results["development_plan"] = await self.agents["learning_specialist"].execute_task(task, context)
        
        # Workforce Planner provides market insights
        task = f"Provide market insights and industry trends relevant to the career progression from '{current_role}' to '{target_role}'."
        results["market_insights"] = await self.agents["workforce_planner"].execute_task(task, context)
        
        return {
            "career_progression": f"{current_role} → {target_role}",
            "timeline": timeline,
            "analysis_timestamp": datetime.now().isoformat(),
            "multi_agent_analysis": results
        }
    
    async def optimize_team_for_project(self, project_requirements: Dict[str, Any], available_team: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Multi-agent team optimization"""
        context = {
            "project_requirements": project_requirements,
            "available_team": available_team
        }
        
        results = {}
        
        # Skills Analyst analyzes skill requirements
        task = "Analyze the skill requirements for this project and identify critical competencies needed for success."
        results["skill_analysis"] = await self.agents["skills_analyst"].execute_task(task, context)
        
        # Team Specialist optimizes composition
        task = "Optimize the team composition based on project requirements and available team members. Consider skill complementarity and team dynamics."
        results["team_optimization"] = await self.agents["team_specialist"].execute_task(task, context)
        
        # Learning Specialist identifies development opportunities
        task = "Identify skill development opportunities for team members during this project."
        results["development_opportunities"] = await self.agents["learning_specialist"].execute_task(task, context)
        
        # Workforce Planner provides strategic perspective
        task = "Provide strategic workforce insights for this project team composition and its impact on organizational capabilities."
        results["strategic_insights"] = await self.agents["workforce_planner"].execute_task(task, context)
        
        return {
            "project_name": project_requirements.get("project_name", "Unnamed Project"),
            "optimization_timestamp": datetime.now().isoformat(),
            "multi_agent_analysis": results
        }
    
    async def assess_organizational_skills(self, organization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive organizational skills assessment"""
        results = {}
        
        # Skills Analyst performs capability analysis
        task = "Analyze the current skills and capabilities within this organization. Identify strengths and gaps."
        results["capability_analysis"] = await self.agents["skills_analyst"].execute_task(task, organization_data)
        
        # Workforce Planner provides strategic assessment
        task = "Provide strategic workforce planning recommendations based on this organizational skills profile."
        results["strategic_assessment"] = await self.agents["workforce_planner"].execute_task(task, organization_data)
        
        # Learning Specialist recommends development programs
        task = "Design organizational learning and development programs to address identified skills gaps."
        results["development_programs"] = await self.agents["learning_specialist"].execute_task(task, organization_data)
        
        # Career Advisor provides career pathway insights
        task = "Analyze career development opportunities and progression paths within this organization."
        results["career_pathways"] = await self.agents["career_advisor"].execute_task(task, organization_data)
        
        return {
            "organization": organization_data.get("company", "Unknown Organization"),
            "assessment_timestamp": datetime.now().isoformat(),
            "multi_agent_analysis": results
        }
    
    async def compare_llm_responses(self, query: str) -> Dict[str, str]:
        """Compare responses from different LLM providers"""
        providers = list(self.llm_manager.clients.keys())
        results = {}
        
        for provider in providers:
            try:
                agent = self.agents["skills_analyst"]  # Use skills analyst for comparison
                response = await agent.analyze_with_provider(query, provider)
                results[provider] = response
            except Exception as e:
                results[provider] = f"Error: {e}"
        
        return results
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all agents and LLM providers"""
        llm_health = await self.llm_manager.health_check_all()
        
        agent_health = {}
        for name, agent in self.agents.items():
            try:
                # Simple test task
                test_response = await agent.execute_task("Say hello and confirm you're working correctly.")
                agent_health[name] = "healthy" if "hello" in test_response.lower() else "unhealthy"
            except Exception as e:
                agent_health[name] = f"error: {e}"
        
        return {
            "llm_providers": llm_health,
            "agents": agent_health,
            "timestamp": datetime.now().isoformat()
        }


# Factory function for creating enhanced agent crew
async def create_enhanced_sfia_agent_crew(knowledge_graph, reasoning_engine, llm_config: Dict[str, Any]) -> EnhancedSFIAAgentCrew:
    """Create enhanced IntelliSFIA agent crew with multi-LLM support"""
    from ..llm.providers import create_llm_manager_from_config
    
    # Create LLM manager
    llm_manager = await create_llm_manager_from_config(llm_config)
    
    # Create and return enhanced agent crew
    return EnhancedSFIAAgentCrew(knowledge_graph, reasoning_engine, llm_manager)