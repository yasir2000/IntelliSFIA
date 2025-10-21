"""
SFIA Data Models - Pydantic models for SFIA ontology entities

This module defines comprehensive data models for all SFIA entities including
skills, roles, career pathways, assessments, and learning resources.

Updated to include SFIA 9 support with enhanced attributes, skills, and levels.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, validator

# Import SFIA 9 models for enhanced capabilities
try:
    from ..data.sfia9.sfia9_models import (
        SFIA9Attribute, SFIA9Skill, SFIA9Level, SFIA9Category,
        SFIA9AttributeType, SFIA9SkillCategory, SFIA9ResponsibilityLevel,
        SFIA9Data
    )
    SFIA9_AVAILABLE = True
except ImportError:
    SFIA9_AVAILABLE = False


class SkillCategory(str, Enum):
    """SFIA skill categories"""
    STRATEGY_AND_ARCHITECTURE = "strategy_and_architecture"
    BUSINESS_CHANGE = "business_change"
    SOLUTION_DEVELOPMENT = "solution_development"
    SERVICE_MANAGEMENT = "service_management"
    PROCUREMENT_AND_MANAGEMENT = "procurement_and_management"
    PEOPLE_AND_SKILLS = "people_and_skills"


class ResponsibilityLevel(int, Enum):
    """SFIA responsibility levels (1-7) - Enhanced with SFIA 9 descriptions"""
    LEVEL_1 = 1  # Follow
    LEVEL_2 = 2  # Assist
    LEVEL_3 = 3  # Apply
    LEVEL_4 = 4  # Enable
    LEVEL_5 = 5  # Ensure/Advise
    LEVEL_6 = 6  # Initiate/Influence
    LEVEL_7 = 7  # Set Strategy/Inspire/Mobilise

# SFIA 9 Enhanced Enums
class SFIA9AttributeCode(str, Enum):
    """SFIA 9 attribute codes"""
    AUTONOMY = "AUTO"
    INFLUENCE = "INFL"
    COMPLEXITY = "COMP"
    KNOWLEDGE = "KNGE"
    COLLABORATION = "COLL"
    COMMUNICATION = "COMM"
    IMPROVEMENT_MINDSET = "IMPM"
    CREATIVITY = "CRTY"
    DECISION_MAKING = "DECM"
    DIGITAL_MINDSET = "DIGI"
    LEADERSHIP = "LEAD"
    LEARNING_DEVELOPMENT = "LADV"
    PLANNING = "PLAN"
    PROBLEM_SOLVING = "PROB"
    ADAPTABILITY = "ADAP"
    SECURITY_PRIVACY_ETHICS = "SCPE"


class PriorityLevel(str, Enum):
    """Priority levels for skills and requirements"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AssessmentStatus(str, Enum):
    """Assessment status values"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"


class Skill(BaseModel):
    """SFIA Skill model"""
    code: str = Field(..., description="SFIA skill code (e.g., ITSP, PROG)")
    name: str = Field(..., description="Skill name")
    description: str = Field(..., description="Detailed skill description")
    guidance_notes: Optional[str] = Field(None, description="Additional guidance notes")
    category: SkillCategory = Field(..., description="Skill category")
    subcategory: Optional[str] = Field(None, description="Skill subcategory")
    url: Optional[str] = Field(None, description="Reference URL")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class SkillLevel(BaseModel):
    """SFIA Skill Level model - represents a skill at a specific responsibility level"""
    skill_code: str = Field(..., description="Associated skill code")
    level: ResponsibilityLevel = Field(..., description="Responsibility level (1-7)")
    description: str = Field(..., description="Level-specific skill description")
    activities: Optional[List[str]] = Field(None, description="Typical activities at this level")
    knowledge_areas: Optional[List[str]] = Field(None, description="Required knowledge areas")
    created_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def skill_level_id(self) -> str:
        """Generate unique skill-level identifier"""
        return f"{self.skill_code}_{self.level.value}"
    
    class Config:
        use_enum_values = True


class ProfessionalRole(BaseModel):
    """Professional Role model"""
    code: str = Field(..., description="Unique role code")
    name: str = Field(..., description="Role name")
    description: str = Field(..., description="Role description")
    typical_level: ResponsibilityLevel = Field(..., description="Typical SFIA level for this role")
    essential_skills: List[str] = Field(default_factory=list, description="Essential skill codes")
    desirable_skills: List[str] = Field(default_factory=list, description="Desirable skill codes")
    industry_sector: Optional[str] = Field(None, description="Industry sector")
    organization_size: Optional[str] = Field(None, description="Typical organization size")
    salary_range: Optional[Dict[str, int]] = Field(None, description="Salary range information")
    job_outlook: Optional[str] = Field(None, description="Job market outlook")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class SkillRequirement(BaseModel):
    """Skill requirement for roles or projects"""
    skill_code: str = Field(..., description="Required skill code")
    level: ResponsibilityLevel = Field(..., description="Required level")
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, description="Requirement priority")
    justification: Optional[str] = Field(None, description="Why this skill is required")
    alternatives: Optional[List[str]] = Field(None, description="Alternative skill codes")
    
    class Config:
        use_enum_values = True


class CompetencyProfile(BaseModel):
    """Competency Profile model - collection of skill requirements"""
    id: str = Field(..., description="Unique profile identifier")
    name: str = Field(..., description="Profile name")
    description: str = Field(..., description="Profile description")
    role_code: Optional[str] = Field(None, description="Associated role code")
    skill_requirements: List[SkillRequirement] = Field(default_factory=list)
    complexity_score: Optional[float] = Field(None, description="Profile complexity (0-1)")
    version: str = Field(default="1.0", description="Profile version")
    created_by: Optional[str] = Field(None, description="Creator information")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('complexity_score')
    def validate_complexity_score(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Complexity score must be between 0 and 1')
        return v


class CareerPathway(BaseModel):
    """Career Pathway model"""
    id: str = Field(..., description="Unique pathway identifier")
    from_role_code: str = Field(..., description="Starting role code")
    to_role_code: str = Field(..., description="Target role code")
    pathway_type: str = Field(default="progression", description="Type of pathway")
    difficulty: str = Field(default="medium", description="Difficulty level")
    typical_duration_months: int = Field(default=24, description="Typical duration in months")
    additional_skills_needed: List[str] = Field(default_factory=list, description="Additional skills needed")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites for transition")
    success_factors: List[str] = Field(default_factory=list, description="Key success factors")
    common_challenges: List[str] = Field(default_factory=list, description="Common challenges")
    created_at: datetime = Field(default_factory=datetime.now)


class SkillGap(BaseModel):
    """Skill Gap model"""
    skill_code: str = Field(..., description="Skill with gap")
    skill_name: str = Field(..., description="Skill name")
    current_level: int = Field(default=0, description="Current proficiency level")
    required_level: int = Field(..., description="Required proficiency level")
    gap_size: int = Field(..., description="Size of the gap (levels)")
    priority: int = Field(default=3, description="Priority for addressing gap (1-5)")
    estimated_time_to_develop: int = Field(..., description="Estimated months to develop")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    
    @validator('gap_size')
    def calculate_gap_size(cls, v, values):
        if 'required_level' in values and 'current_level' in values:
            return max(0, values['required_level'] - values['current_level'])
        return v


class LearningResource(BaseModel):
    """Learning Resource model"""
    id: str = Field(..., description="Unique resource identifier")
    title: str = Field(..., description="Resource title")
    description: str = Field(..., description="Resource description")
    resource_type: str = Field(..., description="Type of resource (course, book, certification, etc.)")
    provider: str = Field(..., description="Resource provider")
    target_skills: List[str] = Field(default_factory=list, description="Skills this resource develops")
    target_level: Optional[ResponsibilityLevel] = Field(None, description="Target SFIA level")
    duration_hours: Optional[int] = Field(None, description="Duration in hours")
    cost: Optional[Dict[str, Union[float, str]]] = Field(None, description="Cost information")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites")
    difficulty_level: str = Field(default="intermediate", description="Difficulty level")
    format: str = Field(..., description="Format (online, in-person, hybrid)")
    url: Optional[str] = Field(None, description="Resource URL")
    rating: Optional[float] = Field(None, description="User rating (1-5)")
    reviews_count: Optional[int] = Field(None, description="Number of reviews")
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v
    
    class Config:
        use_enum_values = True


class LearningPath(BaseModel):
    """Learning Path model - structured sequence of learning resources"""
    id: str = Field(..., description="Unique path identifier")
    name: str = Field(..., description="Learning path name")
    description: str = Field(..., description="Path description")
    target_role: Optional[str] = Field(None, description="Target role code")
    target_skills: List[str] = Field(default_factory=list, description="Skills developed in this path")
    resources: List[str] = Field(default_factory=list, description="Ordered list of resource IDs")
    estimated_duration_months: int = Field(default=6, description="Estimated completion time")
    difficulty_progression: List[str] = Field(default_factory=list, description="Difficulty progression")
    milestones: List[str] = Field(default_factory=list, description="Key milestones")
    created_by: Optional[str] = Field(None, description="Creator information")
    created_at: datetime = Field(default_factory=datetime.now)


class Assessment(BaseModel):
    """Assessment model"""
    id: str = Field(..., description="Unique assessment identifier")
    person_id: str = Field(..., description="Person being assessed")
    skill_code: str = Field(..., description="Skill being assessed")
    assessed_level: ResponsibilityLevel = Field(..., description="Assessed level")
    assessor_id: Optional[str] = Field(None, description="Assessor identifier")
    assessment_method: str = Field(..., description="Assessment method")
    confidence_score: float = Field(default=0.8, description="Confidence in assessment")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    assessment_date: date = Field(default_factory=date.today)
    expiry_date: Optional[date] = Field(None, description="Assessment expiry date")
    status: AssessmentStatus = Field(default=AssessmentStatus.COMPLETED)
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Confidence score must be between 0 and 1')
        return v
    
    class Config:
        use_enum_values = True


class AssessmentResult(BaseModel):
    """Assessment Result model - aggregated assessment information"""
    person_id: str = Field(..., description="Person identifier")
    skill_profile: Dict[str, int] = Field(default_factory=dict, description="Skill code to level mapping")
    assessment_date: date = Field(default_factory=date.today)
    overall_level: Optional[float] = Field(None, description="Overall competency level")
    strengths: List[str] = Field(default_factory=list, description="Key strengths")
    development_areas: List[str] = Field(default_factory=list, description="Development areas")
    next_steps: List[str] = Field(default_factory=list, description="Recommended next steps")


class Person(BaseModel):
    """Person model"""
    id: str = Field(..., description="Unique person identifier")
    name: str = Field(..., description="Person name")
    email: Optional[str] = Field(None, description="Email address")
    current_role: Optional[str] = Field(None, description="Current role code")
    department: Optional[str] = Field(None, description="Department")
    organization: Optional[str] = Field(None, description="Organization")
    experience_years: int = Field(default=0, description="Years of professional experience")
    education_level: Optional[str] = Field(None, description="Highest education level")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    skills: List[str] = Field(default_factory=list, description="Known skill codes")
    career_aspirations: List[str] = Field(default_factory=list, description="Career goals")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Organization(BaseModel):
    """Organization model"""
    id: str = Field(..., description="Unique organization identifier")
    name: str = Field(..., description="Organization name")
    industry: str = Field(..., description="Industry sector")
    size: str = Field(..., description="Organization size")
    location: Optional[str] = Field(None, description="Primary location")
    sfia_adoption_level: str = Field(default="basic", description="SFIA adoption maturity")
    strategic_skills: List[str] = Field(default_factory=list, description="Strategic skill priorities")
    skill_gaps: List[str] = Field(default_factory=list, description="Identified organizational skill gaps")
    created_at: datetime = Field(default_factory=datetime.now)


class Project(BaseModel):
    """Project model"""
    id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    required_skills: List[SkillRequirement] = Field(default_factory=list)
    team_size: int = Field(default=5, description="Required team size")
    duration_months: int = Field(default=12, description="Project duration")
    complexity: str = Field(default="medium", description="Project complexity")
    start_date: Optional[date] = Field(None, description="Project start date")
    end_date: Optional[date] = Field(None, description="Project end date")
    budget: Optional[Dict[str, float]] = Field(None, description="Budget information")
    success_criteria: List[str] = Field(default_factory=list, description="Success criteria")
    risk_factors: List[str] = Field(default_factory=list, description="Risk factors")


class TeamComposition(BaseModel):
    """Team Composition model"""
    id: str = Field(..., description="Unique composition identifier")
    project_id: str = Field(..., description="Associated project ID")
    team_members: List[str] = Field(default_factory=list, description="Team member IDs")
    skill_coverage: Dict[str, float] = Field(default_factory=dict, description="Skill coverage metrics")
    optimization_score: float = Field(default=0.0, description="Team optimization score")
    identified_gaps: List[str] = Field(default_factory=list, description="Identified skill gaps")
    recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")
    created_at: datetime = Field(default_factory=datetime.now)


class CareerRecommendation(BaseModel):
    """Career Recommendation model"""
    id: str = Field(..., description="Unique recommendation identifier")
    person_id: str = Field(..., description="Person receiving recommendation")
    recommendation_type: str = Field(..., description="Type of recommendation")
    current_role: str = Field(..., description="Current role")
    target_role: str = Field(..., description="Recommended target role")
    progression_path: List[str] = Field(default_factory=list, description="Suggested progression path")
    feasibility_score: float = Field(default=0.0, description="Feasibility score (0-1)")
    estimated_timeline: Dict[str, Any] = Field(default_factory=dict, description="Timeline information")
    key_milestones: List[str] = Field(default_factory=list, description="Key milestones")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    skill_development_plan: List[str] = Field(default_factory=list, description="Skill development recommendations")
    confidence_level: float = Field(default=0.7, description="Confidence in recommendation")
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('feasibility_score', 'confidence_level')
    def validate_scores(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Score must be between 0 and 1')
        return v


# SFIA 9 Enhanced Models
class EnhancedSFIAAttribute(BaseModel):
    """Enhanced SFIA attribute model with SFIA 9 capabilities"""
    code: str = Field(..., description="Attribute code")
    name: str = Field(..., description="Attribute name")
    type: str = Field(..., description="Attribute type")
    description: str = Field(..., description="Description")
    guidance_notes: str = Field(..., description="Guidance notes")
    url: Optional[str] = Field(None, description="SFIA online URL")
    levels: List[str] = Field(default_factory=list, description="Available levels")
    level_descriptions: Dict[str, str] = Field(default_factory=dict, description="Level descriptions")
    sfia_version: str = Field(default="9.0", description="SFIA version")

class EnhancedSFIASkill(BaseModel):
    """Enhanced SFIA skill model with SFIA 9 capabilities"""
    code: str = Field(..., description="Skill code")
    name: str = Field(..., description="Skill name")
    category: str = Field(..., description="Category")
    subcategory: str = Field(..., description="Subcategory")
    description: str = Field(..., description="Description")
    guidance_notes: str = Field(..., description="Guidance notes")
    url: Optional[str] = Field(None, description="SFIA online URL")
    available_levels: List[int] = Field(default_factory=list, description="Available levels")
    level_descriptions: Dict[str, str] = Field(default_factory=dict, description="Level descriptions")
    sfia_version: str = Field(default="9.0", description="SFIA version")
    
    # Legacy compatibility
    @property
    def skill_code(self) -> str:
        return self.code
    
    @property
    def skill_name(self) -> str:
        return self.name

class SFIA9LevelDefinition(BaseModel):
    """SFIA 9 level definition with enhanced descriptions"""
    level: int = Field(..., ge=1, le=7, description="Level number")
    guiding_phrase: str = Field(..., description="Guiding phrase")
    essence: str = Field(..., description="Essence of the level")
    url: Optional[str] = Field(None, description="Reference URL")

class SFIA9EnhancedFramework(BaseModel):
    """Complete SFIA 9 enhanced framework"""
    version: str = Field(default="9.0", description="SFIA version")
    last_updated: datetime = Field(default_factory=datetime.now)
    attributes: List[EnhancedSFIAAttribute] = Field(default_factory=list)
    skills: List[EnhancedSFIASkill] = Field(default_factory=list)
    level_definitions: List[SFIA9LevelDefinition] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    subcategories: List[str] = Field(default_factory=list)


# Response models for API
class APIResponse(BaseModel):
    """Base API response model"""
    success: bool = Field(default=True)
    message: str = Field(default="Success")
    timestamp: datetime = Field(default_factory=datetime.now)


class SkillAnalysisResponse(APIResponse):
    """Skill analysis API response"""
    skills: List[Skill] = Field(default_factory=list)
    total_count: int = Field(default=0)
    filters_applied: Dict[str, Any] = Field(default_factory=dict)


class CareerAnalysisResponse(APIResponse):
    """Career analysis API response"""
    current_role: str
    target_role: str
    skill_gaps: List[SkillGap] = Field(default_factory=list)
    career_recommendations: List[CareerRecommendation] = Field(default_factory=list)
    learning_path: Optional[LearningPath] = None


class TeamOptimizationResponse(APIResponse):
    """Team optimization API response"""
    project_id: str
    optimal_composition: TeamComposition
    alternative_compositions: List[TeamComposition] = Field(default_factory=list)
    optimization_metrics: Dict[str, float] = Field(default_factory=dict)