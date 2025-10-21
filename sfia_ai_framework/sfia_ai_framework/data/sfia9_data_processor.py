"""
SFIA 9 Data Ingestion Script
============================

This script processes the SFIA 9 CSV files and integrates them into IntelliSFIA's
knowledge base and data models. It handles:

1. Attributes data from sfia-9_current-standard_en_US_2501291.csv
2. Skills data from sfia-9_current-standard_en_US_250129.csv  
3. Level descriptions from sfia-9_current-standard_en_US_2501292.csv
"""

import csv
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SFIA9DataProcessor:
    """Process SFIA 9 CSV data files and generate structured data for IntelliSFIA"""
    
    def __init__(self, data_path: str = None):
        """Initialize with path to CSV files"""
        self.data_path = data_path or str(Path(__file__).parent)
        self.output_path = Path(__file__).parent / "sfia9"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # SFIA 9 file mappings
        self.files = {
            'attributes': 'sfia-9_current-standard_en_US_2501291.csv',
            'skills': 'sfia-9_current-standard_en_US_250129.csv',
            'levels': 'sfia-9_current-standard_en_US_2501292.csv'
        }
        
        self.processed_data = {
            'attributes': [],
            'skills': [],
            'levels': [],
            'categories': set(),
            'subcategories': set()
        }
    
    def process_attributes_file(self) -> List[Dict[str, Any]]:
        """Process the SFIA 9 attributes CSV file"""
        logger.info("Processing SFIA 9 attributes data...")
        
        attributes_file = os.path.join(self.data_path, self.files['attributes'])
        attributes_data = []
        
        # Use iso-8859-1 encoding for SFIA CSV files
        with open(attributes_file, 'r', encoding='iso-8859-1') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header
            
            for row in reader:
                if len(row) < 20:  # Skip incomplete rows
                    continue
                    
                # Parse levels (columns 0-6)
                levels = [level.strip() for level in row[0:7] if level.strip()]
                
                # Core attribute data
                code = row[7].strip() if len(row) > 7 else ""
                url = row[8].strip() if len(row) > 8 else ""
                name = row[9].strip() if len(row) > 9 else ""
                attribute_type = row[10].strip() if len(row) > 10 else ""
                description = row[11].strip() if len(row) > 11 else ""
                guidance = row[12].strip() if len(row) > 12 else ""
                
                # Level descriptions (columns 13-19)
                level_descriptions = {}
                for i, level in enumerate(levels):
                    if i + 13 < len(row) and row[i + 13].strip():
                        level_descriptions[level] = row[i + 13].strip()
                
                attribute_data = {
                    'code': code,
                    'url': url,
                    'name': name,
                    'type': attribute_type,
                    'description': description,
                    'guidance_notes': guidance,
                    'levels': levels,
                    'level_descriptions': level_descriptions,
                    'sfia_version': '9.0'
                }
                
                attributes_data.append(attribute_data)
                logger.info(f"Processed attribute: {code} - {name}")
        
        return attributes_data
    
    def process_skills_file(self) -> List[Dict[str, Any]]:
        """Process the SFIA 9 skills CSV file"""
        logger.info("Processing SFIA 9 skills data...")
        
        skills_file = os.path.join(self.data_path, self.files['skills'])
        skills_data = []
        
        # Use iso-8859-1 encoding for SFIA CSV files
        with open(skills_file, 'r', encoding='iso-8859-1') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header
            
            for row in reader:
                if len(row) < 15:  # Skip incomplete rows
                    continue
                
                # Parse skill levels (columns 1-7 for levels 1-7)
                skill_levels = []
                for i in range(1, 8):  # Levels 1-7
                    if i < len(row) and row[i].strip():
                        skill_levels.append(i)
                
                # Core skill data  
                code = row[8].strip() if len(row) > 8 else ""
                url = row[9].strip() if len(row) > 9 else ""
                name = row[10].strip() if len(row) > 10 else ""
                category = row[11].strip() if len(row) > 11 else ""
                subcategory = row[12].strip() if len(row) > 12 else ""
                description = row[13].strip() if len(row) > 13 else ""
                guidance = row[14].strip() if len(row) > 14 else ""
                
                # Level-specific descriptions (columns 15-21)
                level_descriptions = {}
                for i, level in enumerate(skill_levels):
                    desc_index = 14 + level  # Adjust for 0-based indexing
                    if desc_index < len(row) and row[desc_index].strip():
                        level_descriptions[str(level)] = row[desc_index].strip()
                
                skill_data = {
                    'code': code,
                    'url': url,
                    'name': name,
                    'category': category,
                    'subcategory': subcategory,
                    'description': description,
                    'guidance_notes': guidance,
                    'available_levels': skill_levels,
                    'level_descriptions': level_descriptions,
                    'sfia_version': '9.0'
                }
                
                skills_data.append(skill_data)
                self.processed_data['categories'].add(category)
                self.processed_data['subcategories'].add(subcategory)
                logger.info(f"Processed skill: {code} - {name}")
        
        return skills_data
    
    def process_levels_file(self) -> List[Dict[str, Any]]:
        """Process the SFIA 9 levels CSV file"""
        logger.info("Processing SFIA 9 levels data...")
        
        levels_file = os.path.join(self.data_path, self.files['levels'])
        levels_data = []
        
        # Use iso-8859-1 encoding for SFIA CSV files
        with open(levels_file, 'r', encoding='iso-8859-1') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header
            
            for row in reader:
                if len(row) < 3:  # Skip incomplete rows
                    continue
                
                field_name = row[0].strip()
                
                # Process each level (columns 1-7)
                for level_num in range(1, 8):
                    if level_num < len(row) and row[level_num].strip():
                        level_data = {
                            'level': level_num,
                            'field': field_name,
                            'content': row[level_num].strip(),
                            'sfia_version': '9.0'
                        }
                        levels_data.append(level_data)
        
        return levels_data
    
    def generate_enhanced_models(self):
        """Generate enhanced Pydantic models with SFIA 9 data"""
        logger.info("Generating enhanced SFIA models...")
        
        model_content = '''"""
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
'''
        
        # Write enhanced models
        enhanced_models_path = self.output_path / "sfia9_models.py"
        with open(enhanced_models_path, 'w', encoding='utf-8') as f:
            f.write(model_content)
        
        logger.info(f"Enhanced models written to: {enhanced_models_path}")
    
    def generate_knowledge_base_integration(self):
        """Generate knowledge base integration code"""
        logger.info("Generating knowledge base integration...")
        
        integration_content = '''"""
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
'''
        
        # Write integration code
        integration_path = self.output_path / "sfia9_knowledge_base.py"
        with open(integration_path, 'w', encoding='utf-8') as f:
            f.write(integration_content)
        
        logger.info(f"Knowledge base integration written to: {integration_path}")
    
    def process_all_files(self):
        """Process all SFIA 9 CSV files"""
        logger.info("Starting SFIA 9 data processing...")
        
        try:
            # Process each file type
            self.processed_data['attributes'] = self.process_attributes_file()
            self.processed_data['skills'] = self.process_skills_file()
            self.processed_data['levels'] = self.process_levels_file()
            
            # Generate categories data
            categories_data = []
            for category in self.processed_data['categories']:
                category_skills = [skill['code'] for skill in self.processed_data['skills'] 
                                 if skill['category'] == category]
                category_subcats = list(set(skill['subcategory'] for skill in self.processed_data['skills'] 
                                           if skill['category'] == category))
                
                categories_data.append({
                    'name': category,
                    'subcategories': category_subcats,
                    'skills': category_skills,
                    'sfia_version': '9.0'
                })
            
            self.processed_data['categories'] = categories_data
            
            # Save processed data to JSON files
            self.save_processed_data()
            
            # Generate enhanced models and integration
            self.generate_enhanced_models()
            self.generate_knowledge_base_integration()
            
            logger.info("SFIA 9 data processing completed successfully!")
            self.print_summary()
            
        except Exception as e:
            logger.error(f"Error processing SFIA 9 data: {e}")
            raise
    
    def save_processed_data(self):
        """Save processed data to JSON files"""
        logger.info("Saving processed data to JSON files...")
        
        # Save each data type to separate JSON files
        for data_type, data in self.processed_data.items():
            if isinstance(data, set):
                data = list(data)  # Convert sets to lists for JSON serialization
            
            output_file = self.output_path / f"sfia9_{data_type}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(data)} {data_type} records to {output_file}")
    
    def print_summary(self):
        """Print processing summary"""
        print("\n" + "="*60)
        print("SFIA 9 DATA PROCESSING SUMMARY")
        print("="*60)
        print(f"✅ Attributes processed: {len(self.processed_data['attributes'])}")
        print(f"✅ Skills processed: {len(self.processed_data['skills'])}")
        print(f"✅ Level definitions processed: {len(self.processed_data['levels'])}")
        print(f"✅ Categories identified: {len(self.processed_data['categories'])}")
        print(f"✅ Data saved to: {self.output_path}")
        print("\nFiles generated:")
        print("- sfia9_models.py (Enhanced Pydantic models)")
        print("- sfia9_knowledge_base.py (Knowledge base integration)")
        print("- sfia9_*.json (Processed data files)")
        print("="*60)

def main():
    """Main processing function"""
    # Note: CSV files should be copied to the downloads path or adjust path as needed
    processor = SFIA9DataProcessor()
    processor.process_all_files()

if __name__ == "__main__":
    main()