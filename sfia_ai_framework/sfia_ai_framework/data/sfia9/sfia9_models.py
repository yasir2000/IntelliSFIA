"""
Enhanced SFIA 9 Data Models
===========================

Updated Pydantic models incorporating SFIA 9 attributes, skills, and levels.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class SFIA9Attribute(BaseModel):
    """SFIA 9 Attribute model"""
    code: str = Field(..., description="Attribute code (e.g., AUTO, INFL)")
    name: str = Field(..., description="Attribute name")
    type: str = Field(..., description="Attribute type (Attributes or Business skills/Behavioural factors)")
    description: str = Field(..., description="Overall description")
    guidance_notes: str = Field(..., description="Detailed guidance notes")
    url: Optional[str] = Field(None, description="SFIA online URL")
    levels: List[str] = Field(default_factory=list, description="Available levels")
    level_descriptions: Dict[str, str] = Field(default_factory=dict, description="Level-specific descriptions")
    sfia_version: str = Field(default="9.0", description="SFIA version")

class SFIA9Skill(BaseModel):
    """SFIA 9 Skill model"""
    code: str = Field(..., description="Skill code (e.g., PROG, DBDS)")
    name: str = Field(..., description="Skill name")
    category: str = Field(..., description="Primary category")
    subcategory: str = Field(..., description="Subcategory")
    description: str = Field(..., description="Overall description")
    guidance_notes: str = Field(..., description="Detailed guidance notes")
    url: Optional[str] = Field(None, description="SFIA online URL")
    available_levels: List[int] = Field(default_factory=list, description="Available levels (1-7)")
    level_descriptions: Dict[str, str] = Field(default_factory=dict, description="Level-specific descriptions")
    sfia_version: str = Field(default="9.0", description="SFIA version")

class SFIA9Level(BaseModel):
    """SFIA 9 Level model"""
    level: int = Field(..., ge=1, le=7, description="Level number (1-7)")
    field: str = Field(..., description="Level field (Level, Guiding phrase, Essence, URL)")
    content: str = Field(..., description="Level content/description")
    sfia_version: str = Field(default="9.0", description="SFIA version")

class SFIA9Category(BaseModel):
    """SFIA 9 Category model"""
    name: str = Field(..., description="Category name")
    subcategories: List[str] = Field(default_factory=list, description="Subcategories")
    skills: List[str] = Field(default_factory=list, description="Skills in this category")
    sfia_version: str = Field(default="9.0", description="SFIA version")

# Enhanced enums for SFIA 9
class SFIA9AttributeType(str, Enum):
    """SFIA 9 attribute types"""
    ATTRIBUTES = "Attributes"
    BUSINESS_SKILLS = "Business skills/Behavioural factors"

class SFIA9SkillCategory(str, Enum):
    """SFIA 9 skill categories"""
    STRATEGY_AND_ARCHITECTURE = "Strategy and architecture"
    # Additional categories will be added based on processed data

class SFIA9ResponsibilityLevel(int, Enum):
    """SFIA 9 responsibility levels with descriptions"""
    FOLLOW = 1  # Follow
    ASSIST = 2  # Assist  
    APPLY = 3   # Apply
    ENABLE = 4  # Enable
    ENSURE_ADVISE = 5  # Ensure, advise
    INITIATE_INFLUENCE = 6  # Initiate, influence
    SET_STRATEGY = 7  # Set strategy, inspire, mobilise

# Comprehensive SFIA 9 data structure
class SFIA9Data(BaseModel):
    """Complete SFIA 9 data structure"""
    version: str = Field(default="9.0", description="SFIA version")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    attributes: List[SFIA9Attribute] = Field(default_factory=list, description="All SFIA 9 attributes")
    skills: List[SFIA9Skill] = Field(default_factory=list, description="All SFIA 9 skills")
    levels: List[SFIA9Level] = Field(default_factory=list, description="All SFIA 9 level definitions")
    categories: List[SFIA9Category] = Field(default_factory=list, description="All SFIA 9 categories")
