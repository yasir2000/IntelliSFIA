"""
SFIA 9 RDF Converter
===================

Converts SFIA 9 JSON data to RDF/Turtle format for integration with the main SFIA knowledge base.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, RDF, RDFS, SKOS, OWL, Literal, XSD

# SFIA Namespaces
SFIA = Namespace("https://sfia-online.org/sfia9/")
SFIA_SKILLS = Namespace("https://sfia-online.org/sfia9/skills/")
SFIA_ATTRIBUTES = Namespace("https://sfia-online.org/sfia9/attributes/")
SFIA_LEVELS = Namespace("https://sfia-online.org/sfia9/levels/")
SFIA_CATEGORIES = Namespace("https://sfia-online.org/sfia9/categories/")

class SFIA9RDFConverter:
    """Convert SFIA 9 JSON data to RDF format"""
    
    def __init__(self, data_path: Path = None):
        """Initialize converter with data path"""
        self.data_path = data_path or Path(__file__).parent / "sfia9"
        self.graph = Graph()
        self._bind_namespaces()
        
    def _bind_namespaces(self):
        """Bind RDF namespaces"""
        self.graph.bind("sfia", SFIA)
        self.graph.bind("sfia-skills", SFIA_SKILLS)
        self.graph.bind("sfia-attributes", SFIA_ATTRIBUTES)
        self.graph.bind("sfia-levels", SFIA_LEVELS)
        self.graph.bind("sfia-categories", SFIA_CATEGORIES)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("skos", SKOS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
    
    def convert_attributes(self):
        """Convert SFIA 9 attributes to RDF"""
        attrs_file = self.data_path / "sfia9_attributes.json"
        if not attrs_file.exists():
            print(f"Attributes file not found: {attrs_file}")
            return
            
        with open(attrs_file, 'r', encoding='utf-8') as f:
            attributes = json.load(f)
        
        print(f"Converting {len(attributes)} attributes to RDF...")
        
        for attr in attributes:
            attr_uri = SFIA_ATTRIBUTES[attr['code']]
            
            # Basic properties
            self.graph.add((attr_uri, RDF.type, SFIA.Attribute))
            self.graph.add((attr_uri, RDFS.label, Literal(attr['name'], lang='en')))
            self.graph.add((attr_uri, SKOS.notation, Literal(attr['code'])))
            self.graph.add((attr_uri, RDFS.comment, Literal(attr['description'], lang='en')))
            self.graph.add((attr_uri, SFIA.attributeType, Literal(attr['type'], lang='en')))
            self.graph.add((attr_uri, SFIA.guidanceNotes, Literal(attr['guidance_notes'], lang='en')))
            self.graph.add((attr_uri, SFIA.sfiaVersion, Literal(attr['sfia_version'])))
            
            if attr.get('url'):
                self.graph.add((attr_uri, SFIA.url, URIRef(attr['url'])))
            
            # Level descriptions
            for level, description in attr.get('level_descriptions', {}).items():
                level_uri = SFIA_LEVELS[f"level{level}"]
                self.graph.add((attr_uri, SFIA.hasLevelDescription, level_uri))
                self.graph.add((level_uri, SFIA.attributeDescription, Literal(description, lang='en')))
                self.graph.add((level_uri, SFIA.level, Literal(int(level), datatype=XSD.integer)))
    
    def convert_skills(self):
        """Convert SFIA 9 skills to RDF"""
        skills_file = self.data_path / "sfia9_skills.json"
        if not skills_file.exists():
            print(f"Skills file not found: {skills_file}")
            return
            
        with open(skills_file, 'r', encoding='utf-8') as f:
            skills = json.load(f)
        
        print(f"Converting {len(skills)} skills to RDF...")
        
        for skill in skills:
            skill_uri = SFIA_SKILLS[skill['code']]
            
            # Basic properties
            self.graph.add((skill_uri, RDF.type, SFIA.Skill))
            self.graph.add((skill_uri, RDFS.label, Literal(skill['name'], lang='en')))
            self.graph.add((skill_uri, SKOS.notation, Literal(skill['code'])))
            self.graph.add((skill_uri, RDFS.comment, Literal(skill['description'], lang='en')))
            self.graph.add((skill_uri, SFIA.guidanceNotes, Literal(skill['guidance_notes'], lang='en')))
            self.graph.add((skill_uri, SFIA.sfiaVersion, Literal(skill['sfia_version'])))
            
            # Category and subcategory
            category_uri = SFIA_CATEGORIES[skill['category'].replace(' ', '_').replace('/', '_')]
            self.graph.add((skill_uri, SFIA.category, category_uri))
            self.graph.add((category_uri, RDF.type, SFIA.Category))
            self.graph.add((category_uri, RDFS.label, Literal(skill['category'], lang='en')))
            
            self.graph.add((skill_uri, SFIA.subcategory, Literal(skill['subcategory'], lang='en')))
            
            if skill.get('url'):
                self.graph.add((skill_uri, SFIA.url, URIRef(skill['url'])))
            
            # Available levels
            for level in skill.get('available_levels', []):
                level_uri = SFIA_LEVELS[f"level{level}"]
                self.graph.add((skill_uri, SFIA.availableAtLevel, level_uri))
                self.graph.add((level_uri, RDF.type, SFIA.Level))
                self.graph.add((level_uri, SFIA.level, Literal(level, datatype=XSD.integer)))
            
            # Level descriptions
            for level, description in skill.get('level_descriptions', {}).items():
                level_uri = SFIA_LEVELS[f"level{level}"]
                skill_level_uri = SFIA_SKILLS[f"{skill['code']}_Level{level}"]
                
                self.graph.add((skill_level_uri, RDF.type, SFIA.SkillLevel))
                self.graph.add((skill_level_uri, SFIA.skill, skill_uri))
                self.graph.add((skill_level_uri, SFIA.level, level_uri))
                self.graph.add((skill_level_uri, RDFS.comment, Literal(description, lang='en')))
    
    def convert_levels(self):
        """Convert SFIA 9 levels to RDF"""
        levels_file = self.data_path / "sfia9_levels.json"
        if not levels_file.exists():
            print(f"Levels file not found: {levels_file}")
            return
            
        with open(levels_file, 'r', encoding='utf-8') as f:
            levels = json.load(f)
        
        print(f"Converting {len(levels)} level definitions to RDF...")
        
        # Group levels by level number
        level_data = {}
        for level_item in levels:
            level_num = level_item['level']
            if level_num not in level_data:
                level_data[level_num] = {}
            level_data[level_num][level_item['field']] = level_item['content']
        
        # Create RDF for each level
        for level_num, data in level_data.items():
            level_uri = SFIA_LEVELS[f"level{level_num}"]
            
            self.graph.add((level_uri, RDF.type, SFIA.Level))
            self.graph.add((level_uri, SFIA.level, Literal(level_num, datatype=XSD.integer)))
            
            # Add level properties
            if 'Guiding phrase' in data:
                self.graph.add((level_uri, SFIA.guidingPhrase, Literal(data['Guiding phrase'], lang='en')))
            
            if 'Essence of the level' in data:
                self.graph.add((level_uri, SFIA.essence, Literal(data['Essence of the level'], lang='en')))
            
            if 'URL' in data:
                self.graph.add((level_uri, SFIA.url, URIRef(data['URL'])))
    
    def convert_categories(self):
        """Convert SFIA 9 categories to RDF"""
        categories_file = self.data_path / "sfia9_categories.json"
        if not categories_file.exists():
            print(f"Categories file not found: {categories_file}")
            return
            
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories = json.load(f)
        
        print(f"Converting {len(categories)} categories to RDF...")
        
        for category in categories:
            # Handle both dict and string formats
            if isinstance(category, dict):
                cat_name = category['name']
                subcategories = category.get('subcategories', [])
                skills = category.get('skills', [])
            else:
                cat_name = category
                subcategories = []
                skills = []
            
            category_uri = SFIA_CATEGORIES[cat_name.replace(' ', '_').replace('/', '_')]
            
            self.graph.add((category_uri, RDF.type, SFIA.Category))
            self.graph.add((category_uri, RDFS.label, Literal(cat_name, lang='en')))
            
            # Add subcategories
            for subcat in subcategories:
                subcat_uri = SFIA_CATEGORIES[f"{cat_name.replace(' ', '_')}_{subcat.replace(' ', '_')}"]
                self.graph.add((subcat_uri, RDF.type, SFIA.Subcategory))
                self.graph.add((subcat_uri, RDFS.label, Literal(subcat, lang='en')))
                self.graph.add((subcat_uri, SFIA.parentCategory, category_uri))
            
            # Link skills to category
            for skill_code in skills:
                skill_uri = SFIA_SKILLS[skill_code]
                self.graph.add((skill_uri, SFIA.category, category_uri))
    
    def add_ontology_definitions(self):
        """Add SFIA 9 ontology class and property definitions"""
        print("Adding ontology definitions...")
        
        # Classes
        self.graph.add((SFIA.Skill, RDF.type, OWL.Class))
        self.graph.add((SFIA.Skill, RDFS.label, Literal("SFIA Skill", lang='en')))
        self.graph.add((SFIA.Skill, RDFS.comment, Literal("A skill in the SFIA framework", lang='en')))
        
        self.graph.add((SFIA.Attribute, RDF.type, OWL.Class))
        self.graph.add((SFIA.Attribute, RDFS.label, Literal("SFIA Attribute", lang='en')))
        self.graph.add((SFIA.Attribute, RDFS.comment, Literal("An attribute in the SFIA framework", lang='en')))
        
        self.graph.add((SFIA.Level, RDF.type, OWL.Class))
        self.graph.add((SFIA.Level, RDFS.label, Literal("SFIA Level", lang='en')))
        self.graph.add((SFIA.Level, RDFS.comment, Literal("A responsibility level in the SFIA framework", lang='en')))
        
        self.graph.add((SFIA.SkillLevel, RDF.type, OWL.Class))
        self.graph.add((SFIA.SkillLevel, RDFS.label, Literal("SFIA Skill Level", lang='en')))
        self.graph.add((SFIA.SkillLevel, RDFS.comment, Literal("A skill at a specific level", lang='en')))
        
        self.graph.add((SFIA.Category, RDF.type, OWL.Class))
        self.graph.add((SFIA.Category, RDFS.label, Literal("SFIA Category", lang='en')))
        self.graph.add((SFIA.Category, RDFS.comment, Literal("A skill category in the SFIA framework", lang='en')))
        
        # Properties
        self.graph.add((SFIA.level, RDF.type, OWL.DatatypeProperty))
        self.graph.add((SFIA.level, RDFS.label, Literal("level", lang='en')))
        self.graph.add((SFIA.level, RDFS.range, XSD.integer))
        
        self.graph.add((SFIA.guidanceNotes, RDF.type, OWL.DatatypeProperty))
        self.graph.add((SFIA.guidanceNotes, RDFS.label, Literal("guidance notes", lang='en')))
        
        self.graph.add((SFIA.availableAtLevel, RDF.type, OWL.ObjectProperty))
        self.graph.add((SFIA.availableAtLevel, RDFS.label, Literal("available at level", lang='en')))
        self.graph.add((SFIA.availableAtLevel, RDFS.domain, SFIA.Skill))
        self.graph.add((SFIA.availableAtLevel, RDFS.range, SFIA.Level))
        
        self.graph.add((SFIA.category, RDF.type, OWL.ObjectProperty))
        self.graph.add((SFIA.category, RDFS.label, Literal("category", lang='en')))
        self.graph.add((SFIA.category, RDFS.domain, SFIA.Skill))
        self.graph.add((SFIA.category, RDFS.range, SFIA.Category))
    
    def convert_all(self):
        """Convert all SFIA 9 data to RDF"""
        print("Starting SFIA 9 to RDF conversion...")
        
        # Add ontology definitions
        self.add_ontology_definitions()
        
        # Convert all data types
        self.convert_attributes()
        self.convert_skills()
        self.convert_levels()
        self.convert_categories()
        
        print(f"Conversion complete. Generated {len(self.graph)} RDF triples.")
        
        return self.graph
    
    def save_turtle(self, output_file: str = None):
        """Save the RDF graph as Turtle format"""
        if not output_file:
            today = datetime.today().strftime('%Y-%m-%d')
            output_file = f"SFIA_9_Enhanced_{today}.ttl"
        
        print(f"Saving RDF graph to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.graph.serialize(format='turtle'))
        
        print(f"Saved {len(self.graph)} triples to {output_file}")
        return output_file

def main():
    """Main conversion function"""
    # Initialize converter
    data_path = Path(__file__).parent / "sfia9"
    converter = SFIA9RDFConverter(data_path)
    
    # Convert all data
    graph = converter.convert_all()
    
    # Save to Turtle file
    output_file = converter.save_turtle()
    
    print(f"\n✅ SFIA 9 RDF conversion completed!")
    print(f"📁 Output file: {output_file}")
    print(f"📊 Total triples: {len(graph)}")
    
    return output_file

if __name__ == "__main__":
    main()