"""
SFIA 9 Knowledge Base Integration
=================================

Integration layer for SFIA 9 data with IntelliSFIA's knowledge base.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from .sfia9_models import SFIA9Data, SFIA9Attribute, SFIA9Skill, SFIA9Level, SFIA9Category

class SFIA9KnowledgeBase:
    """SFIA 9 knowledge base integration"""
    
    def __init__(self, data_path: Path = None):
        """Initialize with SFIA 9 data"""
        self.data_path = data_path or Path(__file__).parent / "data"
        self.sfia_data: Optional[SFIA9Data] = None
        self._load_data()
    
    def _load_data(self):
        """Load SFIA 9 data from JSON files"""
        try:
            # Load processed SFIA 9 data
            attributes_file = self.data_path / "sfia9_attributes.json"
            skills_file = self.data_path / "sfia9_skills.json"
            levels_file = self.data_path / "sfia9_levels.json"
            
            attributes = []
            skills = []
            levels = []
            
            if attributes_file.exists():
                with open(attributes_file, 'r', encoding='utf-8') as f:
                    attrs_data = json.load(f)
                    attributes = [SFIA9Attribute(**attr) for attr in attrs_data]
            
            if skills_file.exists():
                with open(skills_file, 'r', encoding='utf-8') as f:
                    skills_data = json.load(f)
                    skills = [SFIA9Skill(**skill) for skill in skills_data]
            
            if levels_file.exists():
                with open(levels_file, 'r', encoding='utf-8') as f:
                    levels_data = json.load(f)
                    levels = [SFIA9Level(**level) for level in levels_data]
            
            # Create comprehensive data structure
            self.sfia_data = SFIA9Data(
                attributes=attributes,
                skills=skills,
                levels=levels
            )
            
        except Exception as e:
            logger.error(f"Error loading SFIA 9 data: {e}")
            self.sfia_data = SFIA9Data()
    
    def get_attribute_by_code(self, code: str) -> Optional[SFIA9Attribute]:
        """Get attribute by code"""
        if not self.sfia_data:
            return None
        
        for attr in self.sfia_data.attributes:
            if attr.code == code:
                return attr
        return None
    
    def get_skill_by_code(self, code: str) -> Optional[SFIA9Skill]:
        """Get skill by code"""
        if not self.sfia_data:
            return None
        
        for skill in self.sfia_data.skills:
            if skill.code == code:
                return skill
        return None
    
    def get_skills_by_category(self, category: str) -> List[SFIA9Skill]:
        """Get all skills in a category"""
        if not self.sfia_data:
            return []
        
        return [skill for skill in self.sfia_data.skills if skill.category == category]
    
    def get_level_descriptions(self, level: int) -> Dict[str, str]:
        """Get all descriptions for a specific level"""
        if not self.sfia_data:
            return {}
        
        descriptions = {}
        for level_data in self.sfia_data.levels:
            if level_data.level == level:
                descriptions[level_data.field] = level_data.content
        
        return descriptions
    
    def search_skills(self, query: str) -> List[SFIA9Skill]:
        """Search skills by name or description"""
        if not self.sfia_data:
            return []
        
        query_lower = query.lower()
        results = []
        
        for skill in self.sfia_data.skills:
            if (query_lower in skill.name.lower() or 
                query_lower in skill.description.lower() or
                query_lower in skill.code.lower()):
                results.append(skill)
        
        return results
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories"""
        if not self.sfia_data:
            return []
        
        return list(set(skill.category for skill in self.sfia_data.skills))
    
    def get_statistics(self) -> Dict[str, int]:
        """Get SFIA 9 data statistics"""
        if not self.sfia_data:
            return {}
        
        return {
            'total_attributes': len(self.sfia_data.attributes),
            'total_skills': len(self.sfia_data.skills),
            'total_levels': 7,  # SFIA always has 7 levels
            'total_categories': len(self.get_all_categories())
        }

# Global instance
sfia9_kb = SFIA9KnowledgeBase()
