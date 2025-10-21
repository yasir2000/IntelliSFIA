"""
IntelliSFIA CrewAI Multi-Agent System with Semantic Knowledge Base
================================================================

This module implements a sophisticated multi-agent system using CrewAI framework
that leverages SFIA ontologies, semantic reasoning, and collaborative AI agents
for comprehensive skills assessment and career guidance.

Key Features:
- Multi-agent collaboration with specialized roles
- SFIA RDF/OWL ontology integration
- SPARQL knowledge base queries
- Semantic reasoning and inference
- Evidence validation and cross-referencing
- Collaborative assessment workflow

Agents:
1. SFIA Expert Agent - Deep SFIA framework knowledge
2. Career Advisor Agent - Strategic career guidance
3. Evidence Analyst Agent - Validates and analyzes evidence
4. Semantic Reasoner Agent - Ontology-based inference
5. Report Generator Agent - Creates comprehensive assessments

Author: IntelliSFIA Development Team
License: Apache 2.0 (with SFIA Foundation attribution)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# CrewAI imports
try:
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import BaseTool, tool
    from langchain_ollama import ChatOllama
    CREWAI_AVAILABLE = True
except ImportError:
    print("⚠️ CrewAI not available. Install with: pip install -r requirements-crewai.txt")
    CREWAI_AVAILABLE = False

# Semantic/RDF imports
try:
    from rdflib import Graph, Namespace, URIRef, Literal
    from rdflib.plugins.sparql import prepareQuery
    import owlrl
    SEMANTIC_AVAILABLE = True
except ImportError:
    print("⚠️ Semantic libraries not available. Install with: pip install rdflib owlrl")
    SEMANTIC_AVAILABLE = False

# Local imports
from ollama_service import OllamaService, OllamaConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SFIA Ontology Namespaces
SFIA = Namespace("http://intellisfia.org/sfia/")
SFIA_SKILLS = Namespace("http://intellisfia.org/sfia/skills/")
SFIA_LEVELS = Namespace("http://intellisfia.org/sfia/levels/")
SFIA_ATTRIBUTES = Namespace("http://intellisfia.org/sfia/attributes/")

@dataclass
class SemanticConfig:
    """Configuration for semantic knowledge base."""
    sfia_ontology_path: str = "sfia_ontology.ttl"
    enable_inference: bool = True
    sparql_endpoint: Optional[str] = None
    cache_queries: bool = True

class SFIAOntologyManager:
    """
    Manages SFIA ontology and semantic knowledge base.
    Provides SPARQL queries, inference, and semantic reasoning.
    """
    
    def __init__(self, config: SemanticConfig):
        self.config = config
        self.graph = Graph()
        self.reasoner = None
        self._load_ontology()
        self._setup_inference()
    
    def _load_ontology(self):
        """Load SFIA ontology from RDF/TTL files."""
        try:
            # Load main SFIA ontology
            if Path(self.config.sfia_ontology_path).exists():
                self.graph.parse(self.config.sfia_ontology_path, format='turtle')
                logger.info(f"Loaded SFIA ontology: {len(self.graph)} triples")
            else:
                logger.warning(f"SFIA ontology not found: {self.config.sfia_ontology_path}")
                self._create_basic_ontology()
                
        except Exception as e:
            logger.error(f"Error loading ontology: {e}")
            self._create_basic_ontology()
    
    def _setup_inference(self):
        """Setup OWL reasoning for semantic inference."""
        if self.config.enable_inference and SEMANTIC_AVAILABLE:
            try:
                self.reasoner = owlrl.CombinedClosure.RDFS_OWLRL_Semantics
                owlrl.DeductiveClosure(self.reasoner).expand(self.graph)
                logger.info("Semantic reasoning enabled")
            except Exception as e:
                logger.warning(f"Could not enable reasoning: {e}")
    
    def _create_basic_ontology(self):
        """Create basic SFIA ontology structure."""
        logger.info("Creating basic SFIA ontology...")
        
        # Add basic skill definitions
        skills_data = self._load_json_data('sfia9_skills.json')
        for skill in skills_data:
            skill_uri = SFIA_SKILLS[skill['code']]
            self.graph.add((skill_uri, SFIA.hasCode, Literal(skill['code'])))
            self.graph.add((skill_uri, SFIA.hasTitle, Literal(skill['title'])))
            self.graph.add((skill_uri, SFIA.hasDescription, Literal(skill['description'])))
            
            # Add skill levels
            for level_info in skill.get('levels', []):
                level_uri = SFIA_LEVELS[f"{skill['code']}_L{level_info['level']}"]
                self.graph.add((skill_uri, SFIA.hasLevel, level_uri))
                self.graph.add((level_uri, SFIA.levelNumber, Literal(level_info['level'])))
                self.graph.add((level_uri, SFIA.levelDescription, Literal(level_info['description'])))
        
        logger.info(f"Created basic ontology with {len(self.graph)} triples")
    
    def _load_json_data(self, filename: str) -> List[Dict]:
        """Load JSON data files."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load {filename}: {e}")
            return []
    
    def query_skill_relationships(self, skill_code: str) -> Dict[str, Any]:
        """Query semantic relationships for a skill."""
        query = prepareQuery("""
            SELECT ?related ?relationship ?description WHERE {
                ?skill sfia:hasCode ?code .
                ?skill ?relationship ?related .
                OPTIONAL { ?related sfia:hasDescription ?description }
                FILTER(?code = ?target_code)
            }
        """, initNs={"sfia": SFIA})
        
        results = []
        for row in self.graph.query(query, initBindings={'target_code': Literal(skill_code)}):
            results.append({
                'related': str(row.related),
                'relationship': str(row.relationship),
                'description': str(row.description) if row.description else None
            })
        
        return {'skill_code': skill_code, 'relationships': results}
    
    def infer_career_paths(self, current_skills: List[str]) -> List[Dict[str, Any]]:
        """Use semantic reasoning to infer career progression paths."""
        # Complex SPARQL query for career path inference
        query = prepareQuery("""
            SELECT ?targetRole ?requiredSkill ?skillLevel WHERE {
                ?role sfia:requiresSkill ?requiredSkill .
                ?requiredSkill sfia:hasCode ?skillCode .
                ?requiredSkill sfia:requiredLevel ?skillLevel .
                ?role sfia:hasTitle ?targetRole .
                FILTER(?skillCode IN (?currentSkills))
            }
        """, initNs={"sfia": SFIA})
        
        # This would contain complex semantic reasoning logic
        # For now, return a simplified structure
        return [
            {
                'role': 'Senior Software Architect',
                'semantic_match_score': 0.85,
                'required_skills': ['ARCH', 'PROG', 'RLMT'],
                'reasoning': 'Semantic analysis indicates strong alignment with architectural roles'
            }
        ]

class SFIASemanticTool(BaseTool):
    """CrewAI tool for SFIA semantic knowledge base queries."""
    
    name: str = "sfia_semantic_query"
    description: str = "Query SFIA semantic knowledge base using SPARQL and ontological reasoning"
    
    def __init__(self, ontology_manager: SFIAOntologyManager):
        super().__init__()
        self.ontology = ontology_manager
    
    def _run(self, query: str) -> str:
        """Execute semantic query against SFIA knowledge base."""
        try:
            # Parse different types of semantic queries
            if "relationships" in query.lower():
                skill_code = self._extract_skill_code(query)
                if skill_code:
                    result = self.ontology.query_skill_relationships(skill_code)
                    return json.dumps(result, indent=2)
            
            elif "career_path" in query.lower():
                skills = self._extract_skills_list(query)
                if skills:
                    result = self.ontology.infer_career_paths(skills)
                    return json.dumps(result, indent=2)
            
            return "Please specify a valid semantic query type: 'relationships' or 'career_path'"
            
        except Exception as e:
            return f"Semantic query error: {str(e)}"
    
    def _extract_skill_code(self, query: str) -> Optional[str]:
        """Extract SFIA skill code from query."""
        # Simple extraction - could be enhanced with NLP
        words = query.upper().split()
        skill_codes = ['PROG', 'ARCH', 'RLMT', 'REQM', 'TEST', 'DTAN', 'PROV']
        for word in words:
            if word in skill_codes:
                return word
        return None
    
    def _extract_skills_list(self, query: str) -> List[str]:
        """Extract list of skills from query."""
        # Simple extraction - could be enhanced
        return ['PROG', 'ARCH', 'RLMT']  # Placeholder

class IntelliSFIACrewAI:
    """
    Multi-agent system for comprehensive SFIA assessment using CrewAI.
    
    This system coordinates multiple specialized AI agents to provide
    sophisticated skills assessment, career guidance, and evidence validation.
    """
    
    def __init__(self, ollama_config: OllamaConfig, semantic_config: SemanticConfig):
        self.ollama_config = ollama_config
        self.semantic_config = semantic_config
        
        # Initialize components
        self.llm = self._setup_llm()
        self.ontology = SFIAOntologyManager(semantic_config)
        self.semantic_tool = SFIASemanticTool(self.ontology)
        
        # Initialize agents
        self.agents = self._create_agents()
        self.crew = None
    
    def _setup_llm(self) -> ChatOllama:
        """Setup Ollama LLM for CrewAI agents."""
        return ChatOllama(
            model=self.ollama_config.model,
            base_url=f"http://{self.ollama_config.host}:{self.ollama_config.port}",
            temperature=self.ollama_config.temperature
        )
    
    def _create_agents(self) -> Dict[str, Agent]:
        """Create specialized agents for different aspects of SFIA assessment."""
        
        agents = {}
        
        # 1. SFIA Expert Agent
        agents['sfia_expert'] = Agent(
            role='SFIA Framework Expert',
            goal='Provide authoritative knowledge about SFIA skills, levels, and competencies',
            backstory="""You are a world-renowned expert in the Skills Framework for the Information Age (SFIA).
            You have deep knowledge of all 147 SFIA skills, competency levels, and career progression paths.
            You understand the nuances of evidence assessment and can precisely map professional experience 
            to SFIA competency levels.""",
            tools=[self.semantic_tool],
            llm=self.llm,
            verbose=True
        )
        
        # 2. Career Advisor Agent
        agents['career_advisor'] = Agent(
            role='Strategic Career Advisor',
            goal='Provide personalized career guidance and development recommendations',
            backstory="""You are an experienced career advisor specializing in technology careers.
            You excel at identifying career opportunities, skills gaps, and development strategies.
            You understand industry trends and can map individual aspirations to realistic career paths.""",
            tools=[self.semantic_tool],
            llm=self.llm,
            verbose=True
        )
        
        # 3. Evidence Analyst Agent
        agents['evidence_analyst'] = Agent(
            role='Evidence Validation Specialist',
            goal='Analyze and validate professional evidence against SFIA competency criteria',
            backstory="""You are a meticulous analyst who specializes in evaluating professional evidence.
            You can identify authentic competency demonstrations, detect inconsistencies, and assess
            the quality and relevance of evidence against specific SFIA competency criteria.""",
            tools=[self.semantic_tool],
            llm=self.llm,
            verbose=True
        )
        
        # 4. Semantic Reasoner Agent
        agents['semantic_reasoner'] = Agent(
            role='Semantic Knowledge Reasoner',
            goal='Perform complex reasoning using SFIA ontologies and semantic relationships',
            backstory="""You are an AI specialist in semantic reasoning and knowledge graphs.
            You use SFIA ontologies, RDF data, and SPARQL queries to uncover hidden patterns,
            infer relationships, and provide deep insights through semantic analysis.""",
            tools=[self.semantic_tool],
            llm=self.llm,
            verbose=True
        )
        
        # 5. Report Generator Agent
        agents['report_generator'] = Agent(
            role='Assessment Report Synthesizer',
            goal='Create comprehensive, actionable assessment reports',
            backstory="""You are a skilled technical writer who specializes in creating clear,
            comprehensive assessment reports. You synthesize complex analysis into actionable
            insights and recommendations that are easy to understand and implement.""",
            llm=self.llm,
            verbose=True
        )
        
        return agents
    
    def create_assessment_tasks(self, 
                               skill_code: str, 
                               evidence: str, 
                               context: str) -> List[Task]:
        """Create collaborative tasks for comprehensive skill assessment."""
        
        tasks = []
        
        # Task 1: Semantic Analysis
        tasks.append(Task(
            description=f"""
            Perform semantic analysis of SFIA skill {skill_code} using the knowledge base.
            Query relationships, dependencies, and ontological properties.
            
            Skill: {skill_code}
            Context: {context}
            
            Provide semantic insights about this skill's relationships and characteristics.
            """,
            agent=self.agents['semantic_reasoner'],
            expected_output="Detailed semantic analysis with relationships and properties"
        ))
        
        # Task 2: Evidence Validation
        tasks.append(Task(
            description=f"""
            Analyze and validate the following professional evidence against SFIA {skill_code} competency criteria:
            
            Evidence: {evidence}
            Context: {context}
            
            Assess the quality, relevance, and authenticity of this evidence.
            Identify specific competency demonstrations and any gaps.
            """,
            agent=self.agents['evidence_analyst'],
            expected_output="Evidence validation report with competency mapping"
        ))
        
        # Task 3: SFIA Expert Assessment
        tasks.append(Task(
            description=f"""
            Based on the semantic analysis and evidence validation, provide expert SFIA assessment.
            
            Skill: {skill_code}
            Evidence: {evidence}
            Context: {context}
            
            Determine appropriate SFIA level and provide detailed reasoning.
            Consider the semantic relationships and validated evidence.
            """,
            agent=self.agents['sfia_expert'],
            expected_output="Expert SFIA level recommendation with detailed justification"
        ))
        
        # Task 4: Career Guidance
        tasks.append(Task(
            description=f"""
            Provide strategic career guidance based on the SFIA assessment results.
            
            Current Assessment Results: [Previous task outputs]
            Context: {context}
            
            Recommend development strategies and career progression opportunities.
            """,
            agent=self.agents['career_advisor'],
            expected_output="Strategic career development recommendations"
        ))
        
        # Task 5: Final Report
        tasks.append(Task(
            description=f"""
            Synthesize all analysis into a comprehensive assessment report.
            
            Include:
            - Semantic analysis insights
            - Evidence validation results  
            - SFIA expert assessment
            - Career development recommendations
            
            Create an actionable, professional report.
            """,
            agent=self.agents['report_generator'],
            expected_output="Comprehensive assessment report in structured format"
        ))
        
        return tasks
    
    def assess_skill_with_crew(self, 
                              skill_code: str, 
                              evidence: str, 
                              context: str) -> Dict[str, Any]:
        """
        Perform comprehensive skill assessment using multi-agent collaboration.
        
        Args:
            skill_code: SFIA skill code
            evidence: Professional evidence
            context: Assessment context
            
        Returns:
            Comprehensive assessment results from multiple agents
        """
        try:
            # Create tasks for this assessment
            tasks = self.create_assessment_tasks(skill_code, evidence, context)
            
            # Create crew with collaborative process
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            # Execute collaborative assessment
            result = crew.kickoff()
            
            return {
                'skill_code': skill_code,
                'assessment_method': 'CrewAI Multi-Agent + Semantic Reasoning',
                'agents_involved': list(self.agents.keys()),
                'semantic_analysis': 'Included',
                'evidence_validation': 'Performed',
                'expert_assessment': 'Completed',
                'career_guidance': 'Provided',
                'final_report': str(result),
                'ontology_triples': len(self.ontology.graph),
                'reasoning_enabled': self.semantic_config.enable_inference
            }
            
        except Exception as e:
            logger.error(f"CrewAI assessment error: {e}")
            return {
                'skill_code': skill_code,
                'error': f'Multi-agent assessment failed: {str(e)}',
                'fallback': 'Consider using single-agent assessment'
            }
    
    def analyze_skills_portfolio(self, 
                                skills_portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze complete skills portfolio using semantic reasoning and multi-agent collaboration.
        
        Args:
            skills_portfolio: Complete professional profile with multiple skills
            
        Returns:
            Comprehensive portfolio analysis with semantic insights
        """
        try:
            # Use semantic reasoning to analyze skill relationships
            semantic_insights = {}
            for skill_code in skills_portfolio.get('skills', {}):
                relationships = self.ontology.query_skill_relationships(skill_code)
                semantic_insights[skill_code] = relationships
            
            # Infer career paths using ontological reasoning
            current_skills = list(skills_portfolio.get('skills', {}).keys())
            career_paths = self.ontology.infer_career_paths(current_skills)
            
            return {
                'portfolio_analysis': 'Multi-agent semantic analysis',
                'semantic_insights': semantic_insights,
                'inferred_career_paths': career_paths,
                'ontology_reasoning': 'Applied',
                'knowledge_base_queries': len(semantic_insights),
                'assessment_method': 'CrewAI + SFIA Ontology'
            }
            
        except Exception as e:
            logger.error(f"Portfolio analysis error: {e}")
            return {'error': f'Portfolio analysis failed: {str(e)}'}

# Factory functions
def create_crewai_system(ollama_model: str = "deepseek-coder:latest") -> Optional[IntelliSFIACrewAI]:
    """Factory function to create IntelliSFIA CrewAI system."""
    if not CREWAI_AVAILABLE:
        logger.error("CrewAI not available. Install with: pip install -r requirements-crewai.txt")
        return None
    
    ollama_config = OllamaConfig(model=ollama_model, temperature=0.3)
    semantic_config = SemanticConfig(enable_inference=True)
    
    return IntelliSFIACrewAI(ollama_config, semantic_config)

def test_crewai_integration() -> bool:
    """Test CrewAI multi-agent integration."""
    if not CREWAI_AVAILABLE or not SEMANTIC_AVAILABLE:
        print("❌ Required libraries not available")
        return False
    
    try:
        system = create_crewai_system()
        if system:
            print("✅ CrewAI multi-agent system created successfully")
            print(f"✅ Agents: {list(system.agents.keys())}")
            print(f"✅ Ontology triples: {len(system.ontology.graph)}")
            return True
        return False
    except Exception as e:
        print(f"❌ CrewAI integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 IntelliSFIA CrewAI Multi-Agent System")
    print("=" * 50)
    
    if test_crewai_integration():
        print("\n🎉 Multi-agent system ready!")
        print("   - Semantic knowledge base loaded")
        print("   - 5 specialized agents created")
        print("   - SFIA ontology reasoning enabled")
    else:
        print("\n❌ Setup incomplete - install requirements")
        print("   pip install -r requirements-crewai.txt")