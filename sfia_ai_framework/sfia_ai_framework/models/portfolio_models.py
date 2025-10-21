"""
Portfolio Assessment Models - IoC Portfolio Mapping Methodology

This module implements the complete Institute of Coding (IoC) portfolio mapping
methodology for assessing student competencies against SFIA skills and levels.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, validator


class EvidenceQuality(str, Enum):
    """Evidence quality levels"""
    EVIDENCE_BASED = "evidence_based"
    ASSERTION_BASED = "assertion_based"
    INSUFFICIENT = "insufficient"


class ProficiencyThreshold(str, Enum):
    """IoC proficiency thresholds"""
    COMPETENCY = "competency"  # 85+ score
    PROFICIENCY = "proficiency"  # 65+ score
    DEVELOPING = "developing"  # Below 65


class PortfolioEntryType(str, Enum):
    """Types of portfolio entries"""
    TECHNICAL_ACTIVITY = "technical_activity"
    REFLECTION = "reflection"
    SUPERVISOR_COMMENT = "supervisor_comment"
    EVIDENCE_ARTIFACT = "evidence_artifact"


class GenericResponsibilityCharacteristic(str, Enum):
    """SFIA Generic Responsibility Characteristics"""
    # Autonomy
    WORKS_UNDER_GENERAL_DIRECTION = "works_under_general_direction"
    RECEIVES_SPECIFIC_DIRECTION = "receives_specific_direction"
    USES_DISCRETION_COMPLEX_ISSUES = "uses_discretion_complex_issues"
    DETERMINES_ESCALATION = "determines_escalation"
    PLANS_MONITORS_WORK = "plans_monitors_work"
    
    # Influence
    INTERACTS_INFLUENCES_COLLEAGUES = "interacts_influences_colleagues"
    OVERSEES_OTHERS = "oversees_others"
    WORKING_CONTACT_CUSTOMERS = "working_contact_customers"
    COLLABORATES_USER_NEEDS = "collaborates_user_needs"
    CONTRIBUTES_TEAMS = "contributes_teams"
    
    # Complexity
    PERFORMS_RANGE_WORK = "performs_range_work"
    APPLIES_METHODICAL_APPROACH = "applies_methodical_approach"
    APPLIES_CREATIVE_THINKING = "applies_creative_thinking"
    
    # Knowledge
    SOUND_GENERIC_KNOWLEDGE = "sound_generic_knowledge"
    APPRECIATION_BUSINESS_CONTEXT = "appreciation_business_context"
    DEMONSTRATES_EFFECTIVE_APPLICATION = "demonstrates_effective_application"
    ABSORBS_NEW_INFORMATION = "absorbs_new_information"
    TAKES_INITIATIVE_DEVELOPMENT = "takes_initiative_development"
    
    # Business Skills
    EFFECTIVE_COMMUNICATION = "effective_communication"
    UNDERSTANDS_APPLIES_METHODS = "understands_applies_methods"
    IMPACTS_SECURITY_ETHICS = "impacts_security_ethics"
    DEMONSTRATES_JUDGEMENT = "demonstrates_judgement"
    APPLIES_DIGITAL_SKILLS = "applies_digital_skills"


class PortfolioEntry(BaseModel):
    """Individual portfolio entry"""
    id: str = Field(..., description="Unique entry identifier")
    date: date = Field(..., description="Entry date")
    title: str = Field(..., description="Entry title")
    content: str = Field(..., description="Entry content/description")
    entry_type: PortfolioEntryType = Field(..., description="Type of entry")
    skill_components: List[str] = Field(default_factory=list, description="SFIA skill components addressed")
    evidence_quality: EvidenceQuality = Field(default=EvidenceQuality.ASSERTION_BASED)
    supervisor_verified: bool = Field(default=False, description="Verified by workplace supervisor")
    reflective_elements: List[str] = Field(default_factory=list, description="Reflective elements identified")
    professional_accountability: Optional[str] = Field(None, description="Evidence of professional accountability")
    page_reference: Optional[str] = Field(None, description="Page or paragraph reference")
    url_reference: Optional[str] = Field(None, description="URL reference if applicable")
    attachments: List[str] = Field(default_factory=list, description="Attached artifacts")
    created_at: datetime = Field(default_factory=datetime.now)


class SupervisorComment(BaseModel):
    """Supervisor comments on portfolio entries"""
    id: str = Field(..., description="Unique comment identifier")
    supervisor_name: str = Field(..., description="Supervisor name")
    supervisor_role: str = Field(..., description="Supervisor role/title")
    organization: str = Field(..., description="Organization name")
    entry_ids: List[str] = Field(default_factory=list, description="Related portfolio entry IDs")
    comment: str = Field(..., description="Supervisor comment content")
    accuracy_confirmation: bool = Field(default=False, description="Confirms accuracy of portfolio entries")
    contextual_evaluation: bool = Field(default=False, description="Evaluates achievements against context")
    achievement_assessment: str = Field(..., description="Assessment of student achievements")
    difficulty_context: Optional[str] = Field(None, description="Context about task difficulty")
    recommendation: Optional[str] = Field(None, description="Supervisor recommendation")
    date: date = Field(default_factory=date.today)
    created_at: datetime = Field(default_factory=datetime.now)


class SkillComponentMapping(BaseModel):
    """Mapping of portfolio entries to SFIA skill components"""
    skill_code: str = Field(..., description="SFIA skill code")
    skill_level: int = Field(..., description="SFIA level (1-7)")
    component_description: str = Field(..., description="Skill component description")
    portfolio_entries: List[str] = Field(default_factory=list, description="Portfolio entry IDs")
    coverage_percentage: float = Field(default=0.0, description="Coverage percentage")
    evidence_quality: EvidenceQuality = Field(default=EvidenceQuality.ASSERTION_BASED)
    supervisor_verified: bool = Field(default=False)
    
    @validator('coverage_percentage')
    def validate_coverage(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Coverage percentage must be between 0 and 100')
        return v


class TechnicalAchievementAssessment(BaseModel):
    """Technical achievement assessment according to IoC criteria"""
    skill_code: str = Field(..., description="Assessed SFIA skill code")
    skill_level: int = Field(..., description="Assessed SFIA level")
    
    # Items of Evidence
    portfolio_entries_present: bool = Field(default=False, description="Portfolio entries showing completion")
    supervisor_comments_present: bool = Field(default=False, description="Supervisor comments confirming accuracy")
    
    # Quality Criteria
    multiple_entries_85_percent: bool = Field(default=False, description=">85% components have multiple entries")
    multiple_entries_50_percent: bool = Field(default=False, description=">50% components have multiple entries")
    supervisor_evaluates_context: bool = Field(default=False, description="Supervisor evaluates against context")
    evidence_based_entries: bool = Field(default=False, description="Entries based on evidence not assertion")
    
    # Scoring
    items_present_score: int = Field(default=0, description="Items present (0-2)")
    criteria_satisfied_percentage: float = Field(default=0.0, description="Criteria satisfied percentage")
    unweighted_score: int = Field(default=0, description="Unweighted score (0-4)")
    
    @validator('unweighted_score')
    def validate_score(cls, v):
        if v < 0 or v > 4:
            raise ValueError('Unweighted score must be between 0 and 4')
        return v


class ReflectionAssessment(BaseModel):
    """Reflection assessment according to IoC criteria"""
    
    # Items of Evidence
    reflective_entries_present: bool = Field(default=False, description="Reflective portfolio entries present")
    personal_development_identified: bool = Field(default=False, description="Personal development areas identified")
    accountability_demonstrated: bool = Field(default=False, description="Professional accountability demonstrated")
    
    # Quality Criteria  
    professional_style: bool = Field(default=False, description="Appropriately professional style")
    evidence_based_reflection: bool = Field(default=False, description="Reflection based on evidence")
    development_comparison: bool = Field(default=False, description="Development claims supported by comparison")
    customer_facing_accountability: bool = Field(default=False, description="Customer-facing accountability recognized")
    
    # Scoring
    items_present_score: int = Field(default=0, description="Items present (0-3)")
    criteria_satisfied_score: int = Field(default=0, description="Criteria satisfied (0-4)")
    unweighted_score: int = Field(default=0, description="Unweighted score (0-4)")
    
    @validator('unweighted_score')
    def validate_score(cls, v):
        if v < 0 or v > 4:
            raise ValueError('Unweighted score must be between 0 and 4')
        return v


class GenericResponsibilityAssessment(BaseModel):
    """Generic responsibility characteristics assessment"""
    characteristic: GenericResponsibilityCharacteristic = Field(..., description="Responsibility characteristic")
    is_core: bool = Field(default=False, description="Is this a core characteristic")
    evidence_entries: List[str] = Field(default_factory=list, description="Portfolio entry IDs providing evidence")
    demonstrated: bool = Field(default=False, description="Characteristic demonstrated")
    evidence_quality: EvidenceQuality = Field(default=EvidenceQuality.ASSERTION_BASED)
    notes: Optional[str] = Field(None, description="Assessment notes")


class PortfolioAssessment(BaseModel):
    """Complete IoC portfolio assessment"""
    id: str = Field(..., description="Unique assessment identifier")
    student_id: str = Field(..., description="Student identifier")
    student_name: str = Field(..., description="Student name")
    assessor_id: str = Field(..., description="Assessor identifier")
    assessor_name: str = Field(..., description="Assessor name")
    
    # Portfolio Information
    portfolio_entries: List[PortfolioEntry] = Field(default_factory=list)
    supervisor_comments: List[SupervisorComment] = Field(default_factory=list)
    
    # SFIA Skill Mapping
    selected_skill_code: str = Field(..., description="Selected SFIA skill for assessment")
    selected_skill_level: int = Field(..., description="Selected SFIA level for assessment")
    skill_component_mappings: List[SkillComponentMapping] = Field(default_factory=list)
    
    # Assessments
    technical_achievement: TechnicalAchievementAssessment
    reflection_assessment: ReflectionAssessment
    generic_responsibility_assessments: List[GenericResponsibilityAssessment] = Field(default_factory=list)
    
    # Scoring
    technical_weighted_score: float = Field(default=0.0, description="Technical achievement weighted score (max 64)")
    reflection_weighted_score: float = Field(default=0.0, description="Reflection weighted score (max 36)")
    total_weighted_score: float = Field(default=0.0, description="Total weighted score (max 100)")
    
    # Generic Responsibility Thresholds
    core_characteristics_demonstrated: int = Field(default=0, description="Core characteristics demonstrated")
    total_core_instances: int = Field(default=0, description="Total core characteristic instances")
    total_all_instances: int = Field(default=0, description="Total all characteristic instances")
    generic_responsibility_pass: bool = Field(default=False, description="Generic responsibility requirements met")
    
    # Final Assessment
    proficiency_threshold: ProficiencyThreshold = Field(default=ProficiencyThreshold.DEVELOPING)
    overall_pass: bool = Field(default=False, description="Overall assessment pass")
    
    # Metadata
    assessment_date: date = Field(default_factory=date.today)
    placement_organization: Optional[str] = Field(None, description="Placement organization")
    placement_duration_weeks: Optional[int] = Field(None, description="Placement duration")
    academic_institution: Optional[str] = Field(None, description="Academic institution")
    academic_program: Optional[str] = Field(None, description="Academic program")
    assessment_context: Optional[str] = Field(None, description="Assessment context (BCS, IoC, etc.)")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('total_weighted_score')
    def calculate_total_score(cls, v, values):
        if 'technical_weighted_score' in values and 'reflection_weighted_score' in values:
            return values['technical_weighted_score'] + values['reflection_weighted_score']
        return v
    
    @validator('proficiency_threshold')
    def determine_threshold(cls, v, values):
        if 'total_weighted_score' in values:
            score = values['total_weighted_score']
            if score >= 85:
                return ProficiencyThreshold.COMPETENCY
            elif score >= 65:
                return ProficiencyThreshold.PROFICIENCY
            else:
                return ProficiencyThreshold.DEVELOPING
        return v


class BCSRITTechAssessment(BaseModel):
    """BCS Registered IT Technician assessment integration"""
    assessment_id: str = Field(..., description="Assessment identifier")
    portfolio_assessment_id: str = Field(..., description="Related portfolio assessment ID")
    rittech_matrix_score: Optional[Dict[str, Any]] = Field(None, description="RITTech matrix scoring (confidential)")
    bcs_assessor_id: Optional[str] = Field(None, description="BCS assessor identifier")
    rittech_application_status: Optional[str] = Field(None, description="RITTech application status")
    assessment_date: date = Field(default_factory=date.today)


class AcademicIntegration(BaseModel):
    """Academic institution integration model"""
    institution_id: str = Field(..., description="Institution identifier")
    institution_name: str = Field(..., description="Institution name")
    program_code: str = Field(..., description="Academic program code")
    program_name: str = Field(..., description="Academic program name")
    module_code: Optional[str] = Field(None, description="Module/course code")
    academic_year: str = Field(..., description="Academic year")
    semester: Optional[str] = Field(None, description="Semester/term")
    credit_value: Optional[int] = Field(None, description="Credit value for assessment")
    assessment_weighting: Optional[float] = Field(None, description="Assessment weighting percentage")
    submission_deadline: Optional[date] = Field(None, description="Portfolio submission deadline")
    moderation_required: bool = Field(default=False, description="Requires moderation")
    external_examiner_review: bool = Field(default=False, description="External examiner review required")


class PortfolioAssessmentSummary(BaseModel):
    """Portfolio assessment summary for reporting"""
    assessment_id: str
    student_name: str
    skill_assessed: str
    level_assessed: int
    total_score: float
    proficiency_level: ProficiencyThreshold
    pass_status: bool
    technical_score: float
    reflection_score: float
    generic_responsibility_pass: bool
    assessor_name: str
    assessment_date: date
    placement_organization: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)


# Response models for API
class PortfolioAnalysisResponse(BaseModel):
    """Portfolio analysis API response"""
    success: bool = Field(default=True)
    message: str = Field(default="Success")
    assessment: Optional[PortfolioAssessment] = None
    summary: Optional[PortfolioAssessmentSummary] = None
    recommendations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class PortfolioMappingGuidance(BaseModel):
    """Guidance for portfolio mapping to SFIA skills"""
    recommended_skills: List[Dict[str, Any]] = Field(default_factory=list)
    mapping_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_requirements: Dict[str, Any] = Field(default_factory=dict)
    quality_criteria: List[str] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)