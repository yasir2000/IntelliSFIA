"""
SFIA 9 Integration Service
==========================

Service layer for integrating SFIA 9 data with IntelliSFIA's core functionality.
Provides enhanced skill analysis, assessment, and recommendations using SFIA 9 framework.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

try:
    from ..models.sfia_models import (
        EnhancedSFIAAttribute, EnhancedSFIASkill, SFIA9LevelDefinition,
        SFIA9EnhancedFramework, ResponsibilityLevel
    )
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from models.sfia_models import (
        EnhancedSFIAAttribute, EnhancedSFIASkill, SFIA9LevelDefinition,
        SFIA9EnhancedFramework, ResponsibilityLevel
    )

logger = logging.getLogger(__name__)

class SFIA9Service:
    """SFIA 9 enhanced service for skill analysis and assessment"""
    
    def __init__(self, data_path: Path = None):
        """Initialize SFIA 9 service with data"""
        self.data_path = data_path or Path(__file__).parent.parent / "data" / "sfia9"
        self.framework: Optional[SFIA9EnhancedFramework] = None
        self._attributes_cache: Dict[str, EnhancedSFIAAttribute] = {}
        self._skills_cache: Dict[str, EnhancedSFIASkill] = {}
        self._categories_cache: Dict[str, List[EnhancedSFIASkill]] = {}
        
        self._load_sfia9_data()
    
    def _load_sfia9_data(self):
        """Load SFIA 9 data from JSON files"""
        try:
            # Load attributes
            attributes_file = self.data_path / "sfia9_attributes.json"
            skills_file = self.data_path / "sfia9_skills.json"
            levels_file = self.data_path / "sfia9_levels.json"
            categories_file = self.data_path / "sfia9_categories.json"
            
            attributes = []
            skills = []
            level_definitions = []
            categories = []
            
            if attributes_file.exists():
                with open(attributes_file, 'r', encoding='utf-8') as f:
                    attrs_data = json.load(f)
                    attributes = [EnhancedSFIAAttribute(**attr) for attr in attrs_data]
                    # Cache attributes by code
                    self._attributes_cache = {attr.code: attr for attr in attributes}
            
            if skills_file.exists():
                with open(skills_file, 'r', encoding='utf-8') as f:
                    skills_data = json.load(f)
                    skills = [EnhancedSFIASkill(**skill) for skill in skills_data]
                    # Cache skills by code
                    self._skills_cache = {skill.code: skill for skill in skills}
                    # Cache by category
                    for skill in skills:
                        if skill.category not in self._categories_cache:
                            self._categories_cache[skill.category] = []
                        self._categories_cache[skill.category].append(skill)
            
            # Process level definitions
            if levels_file.exists():
                with open(levels_file, 'r', encoding='utf-8') as f:
                    levels_data = json.load(f)
                    # Group level data by level number
                    level_groups = {}
                    for level_item in levels_data:
                        level_num = level_item['level']
                        if level_num not in level_groups:
                            level_groups[level_num] = {}
                        level_groups[level_num][level_item['field']] = level_item['content']
                    
                    # Create level definitions
                    for level_num, level_data in level_groups.items():
                        level_def = SFIA9LevelDefinition(
                            level=level_num,
                            guiding_phrase=level_data.get('Guiding phrase', ''),
                            essence=level_data.get('Essence of the level', ''),
                            url=level_data.get('URL', '')
                        )
                        level_definitions.append(level_def)
            
            # Load categories
            if categories_file.exists():
                with open(categories_file, 'r', encoding='utf-8') as f:
                    categories = json.load(f)
            
            # Create framework
            self.framework = SFIA9EnhancedFramework(
                attributes=attributes,
                skills=skills,
                level_definitions=level_definitions,
                categories=[cat['name'] if isinstance(cat, dict) else cat for cat in categories],
                subcategories=list(set(skill.subcategory for skill in skills))
            )
            
            logger.info(f"Loaded SFIA 9 framework: {len(attributes)} attributes, {len(skills)} skills")
            
        except Exception as e:
            logger.error(f"Error loading SFIA 9 data: {e}")
            self.framework = SFIA9EnhancedFramework()
    
    def get_attribute_by_code(self, code: str) -> Optional[EnhancedSFIAAttribute]:
        """Get attribute by code"""
        return self._attributes_cache.get(code.upper())
    
    def get_skill_by_code(self, code: str) -> Optional[EnhancedSFIASkill]:
        """Get skill by code"""
        return self._skills_cache.get(code.upper())
    
    def get_skills_by_category(self, category: str) -> List[EnhancedSFIASkill]:
        """Get skills by category"""
        return self._categories_cache.get(category, [])
    
    def search_skills(self, query: str, limit: int = 10) -> List[EnhancedSFIASkill]:
        """Search skills by name, description, or code"""
        if not self.framework:
            return []
        
        query_lower = query.lower()
        results = []
        
        for skill in self.framework.skills:
            score = 0
            # Exact code match gets highest score
            if skill.code.lower() == query_lower:
                score += 100
            elif query_lower in skill.code.lower():
                score += 50
            
            # Name matching
            if query_lower in skill.name.lower():
                score += 30
            
            # Description matching
            if query_lower in skill.description.lower():
                score += 10
            
            if score > 0:
                results.append((score, skill))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[0], reverse=True)
        return [skill for _, skill in results[:limit]]
    
    def get_level_description(self, level: int) -> Optional[SFIA9LevelDefinition]:
        """Get level description"""
        if not self.framework:
            return None
        
        for level_def in self.framework.level_definitions:
            if level_def.level == level:
                return level_def
        return None
    
    def get_skill_level_description(self, skill_code: str, level: int) -> Optional[str]:
        """Get skill-specific level description"""
        skill = self.get_skill_by_code(skill_code)
        if skill and str(level) in skill.level_descriptions:
            return skill.level_descriptions[str(level)]
        return None
    
    def get_attribute_level_description(self, attr_code: str, level: int) -> Optional[str]:
        """Get attribute-specific level description"""
        attr = self.get_attribute_by_code(attr_code)
        if attr and str(level) in attr.level_descriptions:
            return attr.level_descriptions[str(level)]
        return None
    
    def assess_skill_level_match(self, skill_code: str, level: int, evidence: str) -> Dict[str, Any]:
        """Assess how well evidence matches a skill at a specific level"""
        skill = self.get_skill_by_code(skill_code)
        if not skill:
            return {"error": "Skill not found"}
        
        if level not in skill.available_levels:
            return {"error": "Level not available for this skill"}
        
        # Get level description
        level_desc = self.get_skill_level_description(skill_code, level)
        general_level = self.get_level_description(level)
        
        # Basic keyword matching (could enhance with LLM analysis)
        evidence_lower = evidence.lower()
        level_desc_lower = level_desc.lower() if level_desc else ""
        
        # Calculate match score based on keyword overlap
        level_keywords = set(level_desc_lower.split()) if level_desc else set()
        evidence_keywords = set(evidence_lower.split())
        
        if level_keywords:
            overlap = len(level_keywords.intersection(evidence_keywords))
            match_score = overlap / len(level_keywords)
        else:
            match_score = 0.0
        
        return {
            "skill": skill.dict(),
            "level": level,
            "level_description": level_desc,
            "general_level_description": general_level.dict() if general_level else None,
            "match_score": match_score,
            "assessment": self._get_match_assessment(match_score),
            "recommendations": self._get_level_recommendations(skill, level, match_score)
        }
    
    def _get_match_assessment(self, score: float) -> str:
        """Get assessment based on match score"""
        if score >= 0.7:
            return "Strong match - evidence clearly demonstrates competency at this level"
        elif score >= 0.5:
            return "Good match - evidence shows competency with some gaps"
        elif score >= 0.3:
            return "Partial match - evidence shows some relevant experience"
        else:
            return "Weak match - evidence does not clearly demonstrate competency"
    
    def _get_level_recommendations(self, skill: EnhancedSFIASkill, level: int, score: float) -> List[str]:
        """Generate recommendations based on assessment"""
        recommendations = []
        
        if score < 0.5:
            recommendations.append("Consider providing more specific examples that demonstrate the required competencies")
            recommendations.append(f"Review the SFIA level {level} description for {skill.name}")
        
        if level > 1 and score >= 0.7:
            recommendations.append(f"Evidence supports competency at level {level}")
            if level < max(skill.available_levels):
                recommendations.append(f"Consider exploring level {level + 1} opportunities")
        
        if score < 0.3:
            if level > 1:
                recommendations.append(f"Consider targeting level {level - 1} initially")
            recommendations.append("Focus on developing specific competencies outlined in the skill description")
        
        return recommendations
    
    def get_category_overview(self, category: str) -> Dict[str, Any]:
        """Get overview of a skill category"""
        skills = self.get_skills_by_category(category)
        if not skills:
            return {"error": "Category not found"}
        
        # Analyze category
        subcategories = list(set(skill.subcategory for skill in skills))
        level_distribution = {}
        
        for skill in skills:
            for level in skill.available_levels:
                if level not in level_distribution:
                    level_distribution[level] = 0
                level_distribution[level] += 1
        
        return {
            "category": category,
            "total_skills": len(skills),
            "subcategories": subcategories,
            "level_distribution": level_distribution,
            "skills": [{"code": s.code, "name": s.name, "levels": s.available_levels} for s in skills[:10]]
        }
    
    def get_comprehensive_skill_analysis(self, skill_code: str) -> Dict[str, Any]:
        """Get comprehensive analysis of a skill"""
        skill = self.get_skill_by_code(skill_code)
        if not skill:
            return {"error": "Skill not found"}
        
        # Get related attributes (basic implementation)
        related_attributes = []
        if hasattr(self, '_attributes_cache'):
            # Simple relatedness based on common keywords
            skill_keywords = set(skill.name.lower().split() + skill.description.lower().split())
            for attr in self._attributes_cache.values():
                attr_keywords = set(attr.name.lower().split() + attr.description.lower().split())
                overlap = len(skill_keywords.intersection(attr_keywords))
                if overlap > 0:
                    related_attributes.append({
                        "code": attr.code,
                        "name": attr.name,
                        "relevance_score": overlap / len(skill_keywords)
                    })
        
        related_attributes.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return {
            "skill": skill.dict(),
            "level_analysis": {
                str(level): self.get_skill_level_description(skill_code, level)
                for level in skill.available_levels
            },
            "related_attributes": related_attributes[:5],  # Top 5 related attributes
            "category_context": self.get_category_overview(skill.category),
            "career_progression": self._analyze_career_progression(skill)
        }
    
    def _analyze_career_progression(self, skill: EnhancedSFIASkill) -> Dict[str, Any]:
        """Analyze career progression for a skill"""
        progression = {
            "entry_level": min(skill.available_levels) if skill.available_levels else 1,
            "senior_level": max(skill.available_levels) if skill.available_levels else 7,
            "typical_progression": []
        }
        
        # Generate typical progression path
        for level in sorted(skill.available_levels):
            level_desc = self.get_skill_level_description(skill.code, level)
            general_level = self.get_level_description(level)
            
            progression["typical_progression"].append({
                "level": level,
                "guiding_phrase": general_level.guiding_phrase if general_level else "",
                "skill_specific": level_desc[:200] + "..." if level_desc and len(level_desc) > 200 else level_desc
            })
        
        return progression
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get SFIA 9 framework statistics"""
        if not self.framework:
            return {}
        
        return {
            "sfia_version": self.framework.version,
            "total_attributes": len(self.framework.attributes),
            "total_skills": len(self.framework.skills),
            "total_categories": len(self.framework.categories),
            "total_subcategories": len(self.framework.subcategories),
            "level_definitions": len(self.framework.level_definitions),
            "data_loaded": True
        }

# Global service instance
sfia9_service = SFIA9Service()