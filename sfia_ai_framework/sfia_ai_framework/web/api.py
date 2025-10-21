"""
SFIA AI Framework - API Server

FastAPI-based REST API for the SFIA AI Framework providing programmatic access
to all framework capabilities including knowledge graph operations, AI agents,
and reasoning services.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import asyncio
import logging
import os
from datetime import datetime
import json

# Add parent directory to Python path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig, SFIASDKContext
from sfia_ai_framework.examples.scenarios import SFIAScenarios
from sfia_ai_framework.models.sfia_models import APIResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="SFIA AI Framework API",
    description="REST API for SFIA AI Framework - Intelligent Skills Analysis with Multi-Agent AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global SDK instance
sdk_instance: Optional[SFIASDK] = None
scenarios_instance: Optional[SFIAScenarios] = None

# Request/Response Models
class SDKConfigRequest(BaseModel):
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="Neo4j database URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: str = Field(description="Neo4j password")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    enable_agents: bool = Field(default=True, description="Enable AI agents")
    enable_reasoning: bool = Field(default=True, description="Enable reasoning engine")
    log_level: str = Field(default="INFO", description="Logging level")

class SkillQueryRequest(BaseModel):
    category: Optional[str] = Field(default=None, description="Skill category filter")
    level: Optional[int] = Field(default=None, description="Skill level filter")
    keyword: Optional[str] = Field(default=None, description="Keyword filter")

class SkillGapRequest(BaseModel):
    current_role: str = Field(description="Current role")
    target_role: str = Field(description="Target role")

class CareerRecommendationRequest(BaseModel):
    current_skills: List[str] = Field(description="List of current skills")
    career_goals: Dict[str, Any] = Field(description="Career goals and preferences")

class TeamOptimizationRequest(BaseModel):
    project_requirements: Dict[str, Any] = Field(description="Project requirements")
    available_team: List[Dict[str, Any]] = Field(description="Available team members")

class RoleAssessmentRequest(BaseModel):
    person_skills: List[str] = Field(description="Person's current skills")
    role_requirements: Dict[str, Any] = Field(description="Role requirements")

class LearningRecommendationRequest(BaseModel):
    target_skills: List[str] = Field(description="Skills to learn")
    current_level: int = Field(default=1, description="Current skill level")

class CareerProgressionRequest(BaseModel):
    current_role: str = Field(description="Current role")
    target_role: str = Field(description="Target role")
    timeline: str = Field(default="2 years", description="Timeline for progression")

class OrganizationAssessmentRequest(BaseModel):
    organization_data: Dict[str, Any] = Field(description="Organization data")

class DevelopmentPlanRequest(BaseModel):
    person_profile: Dict[str, Any] = Field(description="Person's profile")
    career_goal: str = Field(description="Career goal")

class PortfolioAssessmentRequest(BaseModel):
    portfolio_entries: List[Dict[str, Any]] = Field(description="Portfolio entries")
    supervisor_comments: List[Dict[str, Any]] = Field(description="Supervisor comments")
    student_info: Dict[str, Any] = Field(description="Student information")
    assessor_info: Dict[str, Any] = Field(description="Assessor information")
    suggested_skill: Optional[str] = Field(None, description="Suggested SFIA skill code")
    suggested_level: Optional[int] = Field(None, description="Suggested SFIA level")

class PortfolioGuidanceRequest(BaseModel):
    activities_description: str = Field(description="Description of student activities")
    student_level: str = Field(default="placement", description="Student level")

class PortfolioValidationRequest(BaseModel):
    portfolio_entries: List[Dict[str, Any]] = Field(description="Portfolio entries")
    skill_code: str = Field(description="SFIA skill code")
    skill_level: int = Field(description="SFIA level")

class PortfolioTemplateRequest(BaseModel):
    skill_code: str = Field(description="SFIA skill code")
    skill_level: int = Field(description="SFIA level")
    placement_context: Optional[str] = Field(None, description="Placement context")

class HiringScenarioRequest(BaseModel):
    company: str = Field(description="Company name")
    open_positions: List[Dict[str, Any]] = Field(description="Open positions")
    candidates: List[Dict[str, Any]] = Field(description="Candidates")

class TeamFormationScenarioRequest(BaseModel):
    organization: str = Field(description="Organization name")
    projects: List[Dict[str, Any]] = Field(description="Projects")
    available_staff: List[Dict[str, Any]] = Field(description="Available staff")

# Dependency to ensure SDK is initialized
async def get_sdk() -> SFIASDK:
    if sdk_instance is None:
        raise HTTPException(status_code=503, detail="SDK not initialized. Please initialize SDK first.")
    return sdk_instance

async def get_scenarios() -> SFIAScenarios:
    if scenarios_instance is None:
        raise HTTPException(status_code=503, detail="Scenarios not available. Please initialize SDK first.")
    return scenarios_instance

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "sdk_initialized": sdk_instance is not None
    }

# SDK Management Endpoints
@app.post("/sdk/initialize")
async def initialize_sdk(config: SDKConfigRequest):
    """Initialize the SFIA AI SDK"""
    global sdk_instance, scenarios_instance
    
    try:
        # Create SDK config
        sdk_config = SFIASDKConfig(
            neo4j_uri=config.neo4j_uri,
            neo4j_user=config.neo4j_user,
            neo4j_password=config.neo4j_password,
            openai_api_key=config.openai_api_key,
            enable_agents=config.enable_agents,
            enable_reasoning=config.enable_reasoning,
            log_level=config.log_level
        )
        
        # Initialize SDK
        sdk_instance = SFIASDK(sdk_config)
        await sdk_instance.initialize()
        
        # Initialize scenarios
        scenarios_instance = SFIAScenarios(sdk_instance)
        
        logger.info("SFIA AI SDK initialized successfully")
        
        return {
            "success": True,
            "message": "SDK initialized successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize SDK: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize SDK: {str(e)}")

@app.post("/sdk/shutdown")
async def shutdown_sdk():
    """Shutdown the SFIA AI SDK"""
    global sdk_instance, scenarios_instance
    
    try:
        if sdk_instance:
            await sdk_instance.close()
            sdk_instance = None
            scenarios_instance = None
        
        return {
            "success": True,
            "message": "SDK shutdown successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to shutdown SDK: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to shutdown SDK: {str(e)}")

@app.get("/sdk/status")
async def get_sdk_status():
    """Get SDK initialization status"""
    return {
        "initialized": sdk_instance is not None,
        "timestamp": datetime.now().isoformat(),
        "capabilities": {
            "knowledge_graph": sdk_instance.knowledge_graph is not None if sdk_instance else False,
            "reasoning_engine": sdk_instance.reasoning_engine is not None if sdk_instance else False,
            "agent_crew": sdk_instance.agent_crew is not None if sdk_instance else False
        } if sdk_instance else {}
    }

# Knowledge Graph Endpoints
@app.post("/knowledge-graph/load-ontology")
async def load_ontology(rdf_file_path: str, sdk: SFIASDK = Depends(get_sdk)):
    """Load SFIA ontology from RDF file"""
    result = await sdk.load_sfia_ontology(rdf_file_path)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result

@app.get("/knowledge-graph/statistics")
async def get_knowledge_graph_statistics(sdk: SFIASDK = Depends(get_sdk)):
    """Get knowledge graph statistics"""
    return await sdk.get_knowledge_graph_statistics()

@app.post("/knowledge-graph/query-skills")
async def query_skills(request: SkillQueryRequest, sdk: SFIASDK = Depends(get_sdk)):
    """Query skills from the knowledge graph"""
    return await sdk.query_skills(request.category, request.level, request.keyword)

@app.get("/knowledge-graph/visualize")
async def visualize_knowledge_graph(output_file: str = "knowledge_graph.html", 
                                  sdk: SFIASDK = Depends(get_sdk)):
    """Generate knowledge graph visualization"""
    result = await sdk.visualize_knowledge_graph(output_file)
    if result.get("success"):
        return FileResponse(result.get("visualization_file"), media_type="text/html")
    else:
        raise HTTPException(status_code=500, detail=result.get("error"))

@app.get("/knowledge-graph/export")
async def export_knowledge_graph(format: str = "rdf", output_file: str = "export", 
                               sdk: SFIASDK = Depends(get_sdk)):
    """Export knowledge graph"""
    result = await sdk.export_knowledge_graph(format, output_file)
    if result.get("success"):
        return FileResponse(result.get("export_file"))
    else:
        raise HTTPException(status_code=500, detail=result.get("error"))

# Reasoning Endpoints
@app.post("/reasoning/skill-gaps")
async def analyze_skill_gaps(request: SkillGapRequest, sdk: SFIASDK = Depends(get_sdk)):
    """Analyze skill gaps between current and target roles"""
    return await sdk.analyze_skill_gaps(request.current_role, request.target_role)

@app.post("/reasoning/career-recommendations")
async def recommend_career_paths(request: CareerRecommendationRequest, sdk: SFIASDK = Depends(get_sdk)):
    """Get career path recommendations"""
    return await sdk.recommend_career_paths(request.current_skills, request.career_goals)

@app.post("/reasoning/team-optimization")
async def optimize_team_composition(request: TeamOptimizationRequest, sdk: SFIASDK = Depends(get_sdk)):
    """Optimize team composition for project requirements"""
    return await sdk.optimize_team_composition(request.project_requirements, request.available_team)

@app.post("/reasoning/role-assessment")
async def assess_role_fit(request: RoleAssessmentRequest, sdk: SFIASDK = Depends(get_sdk)):
    """Assess how well a person fits a role"""
    return await sdk.assess_role_fit(request.person_skills, request.role_requirements)

@app.post("/reasoning/learning-recommendations")
async def get_learning_recommendations(request: LearningRecommendationRequest, 
                                     sdk: SFIASDK = Depends(get_sdk)):
    """Get learning recommendations for skill development"""
    return await sdk.get_learning_recommendations(request.target_skills, request.current_level)

# Agent Endpoints
@app.post("/agents/career-progression")
async def analyze_career_progression(request: CareerProgressionRequest, sdk: SFIASDK = Depends(get_sdk)):
    """Multi-agent career progression analysis"""
    return await sdk.analyze_career_progression(request.current_role, request.target_role, request.timeline)

@app.post("/agents/project-team")
async def optimize_project_team(request: TeamOptimizationRequest, sdk: SFIASDK = Depends(get_sdk)):
    """Multi-agent team optimization for projects"""
    return await sdk.optimize_project_team(request.project_requirements, request.available_team)

@app.post("/agents/organizational-assessment")
async def assess_organizational_skills(request: OrganizationAssessmentRequest, 
                                     sdk: SFIASDK = Depends(get_sdk)):
    """Comprehensive organizational skills assessment"""
    return await sdk.assess_organizational_skills(request.organization_data)

# Insights Endpoints
@app.get("/insights/skill/{skill_code}")
async def get_skill_insights(skill_code: str, sdk: SFIASDK = Depends(get_sdk)):
    """Get comprehensive insights about a specific skill"""
    return await sdk.get_skill_insights(skill_code)

@app.get("/insights/role/{role_code}")
async def get_role_analysis(role_code: str, sdk: SFIASDK = Depends(get_sdk)):
    """Get comprehensive analysis of a professional role"""
    return await sdk.get_role_analysis(role_code)

@app.post("/insights/development-plan")
async def generate_development_plan(request: DevelopmentPlanRequest, sdk: SFIASDK = Depends(get_sdk)):
    """Generate a comprehensive development plan for a person"""
    return await sdk.generate_development_plan(request.person_profile, request.career_goal)

# Scenario Endpoints
@app.post("/scenarios/hiring-optimization")
async def run_hiring_optimization(background_tasks: BackgroundTasks, 
                                scenarios: SFIAScenarios = Depends(get_scenarios)):
    """Run hiring optimization scenario"""
    try:
        result = await scenarios.hiring_optimization_scenario()
        return {
            "success": True,
            "scenario": "hiring_optimization",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario execution failed: {str(e)}")

@app.post("/scenarios/career-development")
async def run_career_development(background_tasks: BackgroundTasks,
                               scenarios: SFIAScenarios = Depends(get_scenarios)):
    """Run career development scenario"""
    try:
        result = await scenarios.career_development_scenario()
        return {
            "success": True,
            "scenario": "career_development",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario execution failed: {str(e)}")

@app.post("/scenarios/team-formation")
async def run_team_formation(background_tasks: BackgroundTasks,
                           scenarios: SFIAScenarios = Depends(get_scenarios)):
    """Run team formation scenario"""
    try:
        result = await scenarios.team_formation_scenario()
        return {
            "success": True,
            "scenario": "team_formation",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario execution failed: {str(e)}")

@app.post("/scenarios/organizational-assessment")
async def run_organizational_assessment(background_tasks: BackgroundTasks,
                                      scenarios: SFIAScenarios = Depends(get_scenarios)):
    """Run organizational assessment scenario"""
    try:
        result = await scenarios.organizational_assessment_scenario()
        return {
            "success": True,
            "scenario": "organizational_assessment",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario execution failed: {str(e)}")

@app.post("/scenarios/skills-gap-analysis")
async def run_skills_gap_analysis(background_tasks: BackgroundTasks,
                                scenarios: SFIAScenarios = Depends(get_scenarios)):
    """Run skills gap analysis scenario"""
    try:
        result = await scenarios.skills_gap_analysis_scenario()
        return {
            "success": True,
            "scenario": "skills_gap_analysis",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario execution failed: {str(e)}")

@app.get("/scenarios/all")
async def run_all_scenarios(background_tasks: BackgroundTasks,
                          scenarios: SFIAScenarios = Depends(get_scenarios)):
    """Run all available scenarios"""
    try:
        results = {}
        
        # Run all scenarios
        results["hiring"] = await scenarios.hiring_optimization_scenario()
        results["career"] = await scenarios.career_development_scenario()
        results["team"] = await scenarios.team_formation_scenario()
        results["organization"] = await scenarios.organizational_assessment_scenario()
        results["skills_gap"] = await scenarios.skills_gap_analysis_scenario()
        
        return {
            "success": True,
            "scenarios_executed": 5,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenarios execution failed: {str(e)}")

# Utility Endpoints
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "SFIA AI Framework API",
        "version": "1.0.0",
        "documentation": "/docs",
        "redoc": "/redoc",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/info")
async def api_info():
    """Get API information"""
    return {
        "title": "SFIA AI Framework API",
        "description": "REST API for SFIA AI Framework - Intelligent Skills Analysis with Multi-Agent AI",
        "version": "1.0.0",
        "capabilities": [
            "Knowledge Graph Operations",
            "Multi-Agent Intelligence",
            "Semantic Reasoning",
            "Skills Analysis",
            "Career Planning",
            "Team Optimization",
            "Organizational Assessment"
        ],
        "endpoints": {
            "sdk": ["/sdk/initialize", "/sdk/shutdown", "/sdk/status"],
            "knowledge_graph": ["/knowledge-graph/load-ontology", "/knowledge-graph/statistics", 
                              "/knowledge-graph/query-skills", "/knowledge-graph/visualize"],
            "reasoning": ["/reasoning/skill-gaps", "/reasoning/career-recommendations", 
                        "/reasoning/team-optimization", "/reasoning/role-assessment"],
            "agents": ["/agents/career-progression", "/agents/project-team", 
                     "/agents/organizational-assessment"],
            "insights": ["/insights/skill/{skill_code}", "/insights/role/{role_code}", 
                       "/insights/development-plan"],
            "scenarios": ["/scenarios/hiring-optimization", "/scenarios/career-development",
                        "/scenarios/team-formation", "/scenarios/organizational-assessment"]
        },
        "timestamp": datetime.now().isoformat()
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("SFIA AI Framework API starting up...")

# Enterprise Integration Endpoints
@app.post("/api/enterprise/initialize")
async def initialize_enterprise_integration(request: Dict[str, Any]):
    """Initialize enterprise integration"""
    try:
        config_path = request.get("config_path")
        redis_url = request.get("redis_url", "redis://localhost:6379")
        
        sdk = await get_sdk()
        result = await sdk.initialize_enterprise_integration(config_path, redis_url)
        
        return {"success": result.success, "message": result.message}
    except Exception as e:
        logger.error(f"Enterprise integration initialization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/enterprise/systems/add")
async def add_enterprise_system(request: Dict[str, Any]):
    """Add a new enterprise system connection"""
    try:
        system_name = request.get("system_name")
        system_type = request.get("system_type")
        credentials = request.get("credentials", {})
        config = request.get("config", {})
        
        if not system_name or not system_type:
            raise HTTPException(status_code=400, detail="system_name and system_type are required")
        
        sdk = await get_sdk()
        result = await sdk.add_enterprise_system(system_name, system_type, credentials, config)
        
        return {"success": result.success, "message": result.message}
    except Exception as e:
        logger.error(f"Add enterprise system error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/enterprise/systems/health")
async def get_systems_health():
    """Get health status of all connected enterprise systems"""
    try:
        sdk = await get_sdk()
        result = await sdk.get_system_health_status()
        
        return result
    except Exception as e:
        logger.error(f"Systems health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/enterprise/analyze/employee")
async def analyze_employee_sfia_levels(request: Dict[str, Any]):
    """Analyze SFIA levels for a specific employee using enterprise data"""
    try:
        employee_id = request.get("employee_id")
        
        if not employee_id:
            raise HTTPException(status_code=400, detail="employee_id is required")
        
        sdk = await get_sdk()
        result = await sdk.analyze_employee_sfia_levels(employee_id)
        
        return result
    except Exception as e:
        logger.error(f"Employee analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/enterprise/analyze/department")
async def analyze_department_sfia_levels(request: Dict[str, Any]):
    """Analyze SFIA levels for all employees in a department"""
    try:
        department = request.get("department")
        
        if not department:
            raise HTTPException(status_code=400, detail="department is required")
        
        sdk = await get_sdk()
        result = await sdk.analyze_department_sfia_levels(department)
        
        return result
    except Exception as e:
        logger.error(f"Department analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/enterprise/insights/organization")
async def get_organization_sfia_insights():
    """Get organization-wide SFIA insights and analytics"""
    try:
        sdk = await get_sdk()
        result = await sdk.get_organization_sfia_insights()
        
        return result
    except Exception as e:
        logger.error(f"Organization insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/enterprise/reports/compliance")
async def generate_sfia_compliance_report(request: Dict[str, Any]):
    """Generate SFIA compliance report for audit and governance"""
    try:
        department = request.get("department")  # Optional
        
        sdk = await get_sdk()
        result = await sdk.generate_sfia_compliance_report(department)
        
        return result
    except Exception as e:
        logger.error(f"Compliance report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/enterprise/callbacks/register")
async def register_real_time_callback(request: Dict[str, Any]):
    """Register a webhook URL for real-time SFIA analysis events"""
    try:
        webhook_url = request.get("webhook_url")
        event_types = request.get("event_types", ["real_time_analysis", "batch_analysis", "health_check"])
        
        if not webhook_url:
            raise HTTPException(status_code=400, detail="webhook_url is required")
        
        # Create callback function that sends HTTP requests to webhook
        import httpx
        
        async def webhook_callback(event_type: str, data):
            if event_type in event_types:
                try:
                    async with httpx.AsyncClient() as client:
                        await client.post(webhook_url, json={
                            "event_type": event_type,
                            "data": data,
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e:
                    logger.error(f"Webhook callback error: {e}")
        
        sdk = await get_sdk()
        result = await sdk.register_real_time_callback(webhook_callback)
        
        return {"success": result.success, "message": result.message}
    except Exception as e:
        logger.error(f"Callback registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/enterprise/metrics/dashboard")
async def get_enterprise_dashboard_metrics():
    """Get comprehensive dashboard metrics for enterprise integration"""
    try:
        sdk = await get_sdk()
        
        # Get organization insights
        insights = await sdk.get_organization_sfia_insights()
        
        # Get system health
        health = await sdk.get_system_health_status()
        
        # Combine into dashboard metrics
        dashboard_data = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "overview": {
                "total_employees": insights.get("total_employees", 0),
                "departments": len(insights.get("departments", {})),
                "skills_tracked": len(insights.get("skill_distribution", {})),
                "connected_systems": len(health.get("systems", {})),
                "healthy_systems": len([s for s in health.get("systems", {}).values() 
                                      if s.get("status") == "healthy"])
            },
            "level_distribution": insights.get("level_distribution", {}),
            "top_departments": dict(list(sorted(
                insights.get("departments", {}).items(),
                key=lambda x: x[1].get("employee_count", 0),
                reverse=True
            ))[:5]) if insights.get("departments") else {},
            "high_performers": insights.get("high_performers", [])[:10],
            "improvement_opportunities": insights.get("improvement_opportunities", [])[:10],
            "system_health": health.get("systems", {}),
            "skill_gaps": insights.get("skill_gaps", [])[:10]
        }
        
        return dashboard_data
    except Exception as e:
        logger.error(f"Dashboard metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Portfolio Assessment Endpoints (IoC Methodology)
@app.post("/api/portfolio/assess")
async def assess_portfolio(request: PortfolioAssessmentRequest, sdk: SFIASDK = Depends(get_sdk)):
    """Assess student portfolio using IoC (Institute of Coding) methodology"""
    try:
        result = await sdk.assess_portfolio(
            portfolio_entries=request.portfolio_entries,
            supervisor_comments=request.supervisor_comments,
            student_info=request.student_info,
            assessor_info=request.assessor_info,
            suggested_skill=request.suggested_skill,
            suggested_level=request.suggested_level
        )
        return result.dict()
    except Exception as e:
        logger.error(f"Portfolio assessment error: {e}")
        raise HTTPException(status_code=500, detail=f"Portfolio assessment failed: {str(e)}")

@app.post("/api/portfolio/guidance")
async def get_portfolio_guidance(request: PortfolioGuidanceRequest, sdk: SFIASDK = Depends(get_sdk)):
    """Get guidance for mapping portfolio activities to SFIA skills"""
    try:
        guidance = await sdk.get_portfolio_mapping_guidance(
            activities_description=request.activities_description,
            student_level=request.student_level
        )
        return {
            "status": "success",
            "guidance": guidance.dict(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Portfolio guidance error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio guidance: {str(e)}")

@app.post("/api/portfolio/validate")
async def validate_portfolio_evidence(request: PortfolioValidationRequest, sdk: SFIASDK = Depends(get_sdk)):
    """Validate portfolio evidence against SFIA skill requirements"""
    try:
        validation = await sdk.validate_portfolio_evidence(
            portfolio_entries=request.portfolio_entries,
            skill_code=request.skill_code,
            skill_level=request.skill_level
        )
        return validation
    except Exception as e:
        logger.error(f"Portfolio validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Portfolio validation failed: {str(e)}")

@app.post("/api/portfolio/template")
async def generate_portfolio_template(request: PortfolioTemplateRequest, sdk: SFIASDK = Depends(get_sdk)):
    """Generate a portfolio template for a specific SFIA skill and level"""
    try:
        template = await sdk.generate_portfolio_template(
            skill_code=request.skill_code,
            skill_level=request.skill_level,
            placement_context=request.placement_context
        )
        return template
    except Exception as e:
        logger.error(f"Template generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Template generation failed: {str(e)}")

@app.get("/api/portfolio/ioc-methodology")
async def get_ioc_methodology_info():
    """Get information about the IoC (Institute of Coding) portfolio mapping methodology"""
    return {
        "methodology": "Institute of Coding (IoC) Portfolio Mapping",
        "description": "Criterion-based assessment approach for evaluating student portfolios against SFIA skills and levels",
        "assessment_components": {
            "technical_achievement": {
                "weight": 16,
                "description": "Portfolio entries showing completion of SFIA skill components",
                "criteria": [
                    "Multiple entries for at least 85% of skill components",
                    "Supervisor verification of accuracy",
                    "Evidence-based content rather than assertions", 
                    "Contextual evaluation by supervisor"
                ]
            },
            "reflection": {
                "weight": 9,  
                "description": "Reflective entries on learning and professional development",
                "criteria": [
                    "Professional writing style",
                    "Personal development identification",
                    "Professional accountability demonstration",
                    "Evidence-based reflection with comparisons"
                ]
            },
            "generic_responsibility_characteristics": {
                "description": "SFIA generic responsibility characteristics for the assessed level",
                "thresholds": {
                    "core_characteristics": "13+ of 17 core characteristics demonstrated",
                    "core_instances": "26+ instances of core characteristics",
                    "total_instances": "44+ total instances of all characteristics"
                }
            }
        },
        "scoring_thresholds": {
            "competency": 85,
            "proficiency": 65,
            "developing": "Below 65"
        },
        "evidence_quality_levels": [
            "evidence_based: Specific details, numbers, concrete examples",
            "assertion_based: General statements without specific evidence", 
            "insufficient: Lacking adequate detail or support"
        ],
        "best_practices": [
            "Document separate achievements rather than incremental progress",
            "Include specific details like numbers, quantities, examples",
            "Demonstrate challenges encountered and solutions applied",
            "Show progression and development over time",
            "Include supervisor verification and contextual comments",
            "Reflect on business impact and professional accountability"
        ],
        "academic_integration": {
            "supported_contexts": ["BCS RITTech", "IoC Accreditation", "University Assessment"],
            "assessment_types": ["Work Placement", "Industrial Training", "Professional Experience"],
            "quality_assurance": ["Internal Moderation", "External Examiner Review", "Peer Assessment"]
        }
    }


# ============================================================================
# SFIA 9 Enhanced Framework API Endpoints  
# ============================================================================

@app.get("/api/sfia9/attributes/{code}")
async def get_sfia9_attribute(code: str):
    """Get SFIA 9 attribute by code"""
    try:
        sdk = await get_sdk()
        attribute = sdk.get_sfia9_attribute(code)
        
        if not attribute:
            raise HTTPException(status_code=404, detail=f"Attribute {code} not found")
        
        return {
            "success": True,
            "attribute": attribute.dict()
        }
    except Exception as e:
        logger.error(f"Error getting SFIA 9 attribute: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sfia9/skills/{code}")
async def get_sfia9_skill(code: str):
    """Get SFIA 9 skill by code"""
    try:
        sdk = await get_sdk()
        skill = sdk.get_sfia9_skill(code)
        
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill {code} not found")
        
        return {
            "success": True,
            "skill": skill.dict()
        }
    except Exception as e:
        logger.error(f"Error getting SFIA 9 skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sfia9/skills")
async def search_sfia9_skills(query: str, limit: int = 10):
    """Search SFIA 9 skills"""
    try:
        sdk = await get_sdk()
        skills = sdk.search_sfia9_skills(query, limit)
        
        return {
            "success": True,
            "query": query,
            "total_results": len(skills),
            "skills": [skill.dict() for skill in skills]
        }
    except Exception as e:
        logger.error(f"Error searching SFIA 9 skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sfia9/statistics")
async def get_sfia9_statistics():
    """Get SFIA 9 framework statistics"""
    try:
        sdk = await get_sdk()
        stats = sdk.get_sfia9_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting SFIA 9 statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    global sdk_instance
    if sdk_instance:
        await sdk_instance.close()
        logger.info("SDK shutdown completed")
    logger.info("SFIA AI Framework API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )