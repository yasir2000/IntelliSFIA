"""
Enhanced validation framework for SFIA RDF ontology
Provides comprehensive validation of the enhanced ontology structure
"""

import csv
from rdflib import Graph, Namespace, RDF, RDFS, OWL, SKOS
from sfia_rdf import namespaces


class SFIAOntologyValidator:
    """Validator for enhanced SFIA ontology"""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate_all(self):
        """Run all validation checks"""
        print("Running SFIA ontology validation...")
        
        # Core validation
        self.validate_skills_structure()
        self.validate_levels_structure()
        self.validate_categories_structure()
        self.validate_attributes_structure()
        
        # Enhanced validation
        self.validate_roles_structure()
        self.validate_pathways_structure()
        self.validate_competency_profiles()
        
        # Relationship validation
        self.validate_skill_relationships()
        self.validate_role_relationships()
        
        # Data quality checks
        self.check_data_completeness()
        self.check_consistency()
        
        self.print_summary()
        return len(self.errors) == 0
    
    def validate_skills_structure(self):
        """Validate skills have proper structure"""
        query = """
        SELECT ?skill WHERE {
            ?skill a sfia:Skill .
            FILTER NOT EXISTS { ?skill rdfs:label ?label }
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.errors.append(f"Found {len(results)} skills without labels")
        
        # Check skills have level definitions
        query = """
        SELECT ?skill WHERE {
            ?skill a sfia:Skill .
            FILTER NOT EXISTS { ?skill sfia:definedAtLevel ?level }
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.errors.append(f"Found {len(results)} skills without level definitions")
    
    def validate_levels_structure(self):
        """Validate levels of responsibility structure"""
        # Check all levels 1-7 exist
        for level in range(1, 8):
            level_iri = namespaces.LEVELS + str(level)
            if (level_iri, RDF.type, namespaces.SFIA_ONTOLOGY + 'Level') not in self.graph:
                self.errors.append(f"Missing level {level}")
        
        # Check levels have proper attributes
        query = """
        SELECT ?level WHERE {
            ?level a sfia:Level .
            FILTER NOT EXISTS { ?level sfia:levelEssence ?essence }
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.warnings.append(f"Found {len(results)} levels without essence descriptions")
    
    def validate_categories_structure(self):
        """Validate category hierarchy"""
        # Check categories have proper SKOS structure
        query = """
        SELECT ?category WHERE {
            ?category a sfia:Category .
            FILTER NOT EXISTS { ?category skos:prefLabel ?label }
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.errors.append(f"Found {len(results)} categories without preferred labels")
        
        # Check for orphaned categories
        query = """
        SELECT ?category WHERE {
            ?category a sfia:Category .
            FILTER NOT EXISTS { 
                { ?category skos:broader ?parent } 
                UNION 
                { ?child skos:broader ?category } 
            }
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.warnings.append(f"Found {len(results)} orphaned categories")
    
    def validate_attributes_structure(self):
        """Validate attributes structure"""
        query = """
        SELECT ?attr WHERE {
            ?attr a owl:AnnotationProperty .
            ?attr sfia:attributeType "Attributes" .
            FILTER NOT EXISTS { ?attr rdfs:label ?label }
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.errors.append(f"Found {len(results)} attributes without labels")
    
    def validate_roles_structure(self):
        """Validate professional roles structure"""
        query = """
        SELECT ?role WHERE {
            ?role a sfia:ProfessionalRole .
            FILTER NOT EXISTS { ?role rdfs:label ?label }
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.errors.append(f"Found {len(results)} roles without labels")
        
        # Check roles have skill requirements
        query = """
        SELECT ?role WHERE {
            ?role a sfia:ProfessionalRole .
            FILTER NOT EXISTS { 
                ?role sfia:requiresEssentialSkill|sfia:requiresDesirableSkill ?skill 
            }
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.warnings.append(f"Found {len(results)} roles without skill requirements")
    
    def validate_pathways_structure(self):
        """Validate career pathways structure"""
        query = """
        SELECT ?pathway WHERE {
            ?pathway a sfia:CareerPathway .
            FILTER NOT EXISTS { 
                ?pathway sfia:fromRole ?from ; sfia:toRole ?to 
            }
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.errors.append(f"Found {len(results)} pathways without proper from/to roles")
    
    def validate_competency_profiles(self):
        """Validate competency profiles"""
        query = """
        SELECT ?profile WHERE {
            ?profile a sfia:CompetencyProfile .
            FILTER NOT EXISTS { ?role sfia:hasCompetencyProfile ?profile }
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.warnings.append(f"Found {len(results)} unused competency profiles")
    
    def validate_skill_relationships(self):
        """Validate skill relationships make sense"""
        # Check for circular prerequisites
        query = """
        SELECT ?skill1 ?skill2 WHERE {
            ?skill1 sfia:prerequisiteFor+ ?skill2 .
            ?skill2 sfia:prerequisiteFor+ ?skill1 .
            FILTER(?skill1 != ?skill2)
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.errors.append(f"Found {len(results)} circular prerequisite relationships")
        
        # Check prerequisite levels make sense
        query = """
        SELECT ?skill ?level1 ?level2 WHERE {
            ?sl1 sfia:prerequisiteFor ?sl2 .
            ?sl1 sfia:skill ?skill ; sfia:level ?level1 .
            ?sl2 sfia:skill ?skill ; sfia:level ?level2 .
            FILTER(?level1 >= ?level2)
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.errors.append(f"Found {len(results)} invalid prerequisite level relationships")
    
    def validate_role_relationships(self):
        """Validate role relationships"""
        # Check for circular progressions
        query = """
        SELECT ?role1 ?role2 WHERE {
            ?role1 sfia:progressesTo+ ?role2 .
            ?role2 sfia:progressesTo+ ?role1 .
            FILTER(?role1 != ?role2)
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.errors.append(f"Found {len(results)} circular career progressions")
    
    def check_data_completeness(self):
        """Check for data completeness"""
        # Count various entities
        counts = {}
        
        entities = [
            ('Skills', 'sfia:Skill'),
            ('Levels', 'sfia:Level'),  
            ('Categories', 'sfia:Category'),
            ('Professional Roles', 'sfia:ProfessionalRole'),
            ('Career Pathways', 'sfia:CareerPathway'),
            ('Competency Profiles', 'sfia:CompetencyProfile')
        ]
        
        for name, class_type in entities:
            query = f"SELECT (COUNT(?x) AS ?count) WHERE {{ ?x a {class_type} }}"
            result = list(self.graph.query(query))[0]
            counts[name] = int(result[0])  # Access first element of result tuple
            self.info.append(f"{name}: {counts[name]}")
        
        # Check expected minimums
        if counts.get('Skills', 0) < 2:
            self.warnings.append("Very few skills defined")
        if counts.get('Levels', 0) != 7:
            self.warnings.append(f"Expected 7 levels, found {counts.get('Levels', 0)}")
    
    def check_consistency(self):
        """Check for data consistency issues"""
        # Check skill levels reference valid levels
        query = """
        SELECT ?skillLevel WHERE {
            ?skillLevel sfia:level ?level .
            FILTER NOT EXISTS { ?level a sfia:Level }
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.errors.append(f"Found {len(results)} skill levels referencing invalid levels")
        
        # Check role skill requirements reference valid skills
        query = """
        SELECT ?role ?skillLevel WHERE {
            ?role sfia:requiresEssentialSkill|sfia:requiresDesirableSkill ?skillLevel .
            FILTER NOT EXISTS { ?skillLevel a sfia:SkillLevel }
        }
        """
        results = list(self.graph.query(query))
        if results:
            self.errors.append(f"Found {len(results)} role requirements referencing invalid skill levels")
    
    def print_summary(self):
        """Print validation summary"""
        print(f"\n=== SFIA Ontology Validation Summary ===")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Info: {len(self.info)}")
        
        if self.errors:
            print(f"\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.info:
            print(f"\nℹ️  INFO:")
            for info in self.info:
                print(f"  - {info}")
        
        if not self.errors:
            print(f"\n✅ Ontology validation passed!")
        else:
            print(f"\n❌ Ontology validation failed with {len(self.errors)} errors")


def validate_ontology_file(ttl_file_path):
    """Validate a Turtle ontology file"""
    graph = Graph()
    namespaces.bind_namespaces(graph)
    
    try:
        graph.parse(ttl_file_path, format='turtle')
        print(f"Successfully loaded {len(graph)} triples from {ttl_file_path}")
    except Exception as e:
        print(f"Error loading ontology file: {e}")
        return False
    
    validator = SFIAOntologyValidator(graph)
    return validator.validate_all()


if __name__ == "__main__":
    # Validate the current output file
    validate_ontology_file("SFIA_9_2025-10-21.ttl")