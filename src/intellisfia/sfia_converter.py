#!/usr/bin/env python3
"""
Enhanced SFIA RDF Converter with Professional Context
Extends the existing converter to include roles, competency profiles, and career pathways
"""

import csv
import os
from datetime import datetime
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, SKOS

# Enhanced namespaces
from sfia_rdf import namespaces
from sfia_rdf.parsers import skills_parser, levels_parser, attributes_parser

# New parsers for enhanced functionality
from sfia_rdf.parsers.enhanced import roles_parser, competency_parser, pathway_parser

# Enhanced namespace definitions
ROLES = namespaces.BASE + 'roles/'
PROFILES = namespaces.BASE + 'profiles/'
PATHWAYS = namespaces.BASE + 'pathways/'
ASSESSMENTS = namespaces.BASE + 'assessments/'

def create_enhanced_sfia_graph():
    """Create enhanced SFIA graph with professional context"""
    
    sfia_graph = Graph()
    namespaces.bind_namespaces(sfia_graph)
    
    # Bind new namespaces
    sfia_graph.bind('roles', ROLES)
    sfia_graph.bind('profiles', PROFILES)
    sfia_graph.bind('pathways', PATHWAYS)
    sfia_graph.bind('assessments', ASSESSMENTS)
    
    # Enhanced ontology definition
    enhanced_ontology = """
    INSERT DATA {
        ##
        ## Enhanced SFIA 9 Ontology
        ##
        
        # Professional Context Classes
        sfia:ProfessionalRole a owl:Class ;
            rdfs:label "Professional Role"@en ;
            rdfs:comment "A professional role requiring specific SFIA competencies"@en ;
            rdfs:subClassOf [
                a owl:Restriction ;
                owl:onProperty sfia:requiresSkill ;
                owl:minCardinality 1
            ] .
        
        sfia:CompetencyProfile a owl:Class ;
            rdfs:label "Competency Profile"@en ;
            rdfs:comment "A structured set of skills and levels required for effective performance"@en .
        
        sfia:CareerPathway a owl:Class ;
            rdfs:label "Career Pathway"@en ;
            rdfs:comment "A progression route between professional roles"@en .
        
        sfia:SkillCluster a owl:Class ;
            rdfs:label "Skill Cluster"@en ;
            rdfs:comment "A group of related skills that are commonly used together"@en .
        
        # Assessment and Development Classes
        sfia:Assessment a owl:Class ;
            rdfs:label "Skill Assessment"@en ;
            rdfs:comment "An evaluation of current competency against SFIA standards"@en .
        
        sfia:SkillGap a owl:Class ;
            rdfs:label "Skill Gap"@en ;
            rdfs:comment "The difference between required and current skill levels"@en .
        
        sfia:LearningResource a owl:Class ;
            rdfs:label "Learning Resource"@en ;
            rdfs:comment "Educational material for developing SFIA skills"@en .
        
        sfia:LearningPath a owl:Class ;
            rdfs:label "Learning Path"@en ;
            rdfs:comment "Structured sequence of learning resources"@en .
        
        # Enhanced Object Properties
        sfia:requiresSkill a owl:ObjectProperty ;
            rdfs:domain sfia:ProfessionalRole ;
            rdfs:range sfia:SkillLevel ;
            rdfs:label "requires skill at level"@en ;
            rdfs:comment "Indicates that a role requires a specific skill at a particular level"@en .
        
        sfia:hasCompetencyProfile a owl:ObjectProperty ;
            rdfs:domain sfia:ProfessionalRole ;
            rdfs:range sfia:CompetencyProfile ;
            rdfs:label "has competency profile"@en .
        
        sfia:progressesTo a owl:ObjectProperty ;
            rdfs:domain sfia:ProfessionalRole ;
            rdfs:range sfia:ProfessionalRole ;
            rdfs:label "progresses to"@en ;
            rdfs:comment "Indicates natural career progression between roles"@en .
        
        sfia:prerequisiteFor a owl:ObjectProperty ;
            rdfs:domain sfia:SkillLevel ;
            rdfs:range sfia:SkillLevel ;
            rdfs:label "prerequisite for"@en ;
            rdfs:comment "Indicates that one skill level is a prerequisite for another"@en .
        
        sfia:complementaryTo a owl:ObjectProperty ;
            rdfs:domain sfia:Skill ;
            rdfs:range sfia:Skill ;
            rdfs:label "complementary to"@en ;
            rdfs:comment "Indicates skills that work well together"@en .
        
        sfia:belongsToCluster a owl:ObjectProperty ;
            rdfs:domain sfia:Skill ;
            rdfs:range sfia:SkillCluster ;
            rdfs:label "belongs to cluster"@en .
        
        sfia:assessedAt a owl:ObjectProperty ;
            rdfs:domain sfia:Assessment ;
            rdfs:range sfia:Level ;
            rdfs:label "assessed at level"@en .
        
        sfia:targetsSkill a owl:ObjectProperty ;
            rdfs:domain sfia:LearningResource ;
            rdfs:range sfia:SkillLevel ;
            rdfs:label "targets skill development"@en .
        
        # Enhanced Datatype Properties
        sfia:roleLevel a owl:DatatypeProperty ;
            rdfs:domain sfia:ProfessionalRole ;
            rdfs:range xsd:integer ;
            rdfs:label "role level"@en ;
            rdfs:comment "The typical SFIA level for this role"@en .
        
        sfia:priority a owl:DatatypeProperty ;
            rdfs:domain sfia:SkillLevel ;
            rdfs:range xsd:string ;
            rdfs:label "skill priority"@en ;
            rdfs:comment "Priority level: essential, important, or desirable"@en .
        
        sfia:assessmentDate a owl:DatatypeProperty ;
            rdfs:domain sfia:Assessment ;
            rdfs:range xsd:dateTime ;
            rdfs:label "assessment date"@en .
        
        sfia:validFrom a owl:DatatypeProperty ;
            rdfs:range xsd:date ;
            rdfs:label "valid from"@en .
        
        sfia:validTo a owl:DatatypeProperty ;
            rdfs:range xsd:date ;
            rdfs:label "valid to"@en .
    }
    """
    
    sfia_graph.update(enhanced_ontology)
    return sfia_graph


def add_professional_roles(graph, roles_file):
    """Add professional role definitions to the graph"""
    with open(roles_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            role_triples = roles_parser.parse_role_row(row)
            for triple in role_triples:
                graph.add(triple)


def add_competency_profiles(graph, profiles_file):
    """Add competency profiles to the graph"""
    with open(profiles_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            profile_triples = competency_parser.parse_profile_row(row)
            for triple in profile_triples:
                graph.add(triple)


def add_career_pathways(graph, pathways_file):
    """Add career pathway information to the graph"""
    with open(pathways_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pathway_triples = pathway_parser.parse_pathway_row(row)
            for triple in pathway_triples:
                graph.add(triple)


def add_skill_relationships(graph):
    """Add inferred skill relationships based on common patterns"""
    
    # Add prerequisite relationships based on skill levels
    prerequisite_query = """
    INSERT {
        ?lower_level sfia:prerequisiteFor ?higher_level .
    }
    WHERE {
        ?skill sfia:definedAtLevel ?lower_level, ?higher_level .
        ?lower_level sfia:level ?l1 .
        ?higher_level sfia:level ?l2 .
        FILTER(?l1 < ?l2)
    }
    """
    graph.update(prerequisite_query)
    
    # Add complementary relationships for skills in same category
    complementary_query = """
    INSERT {
        ?skill1 sfia:complementaryTo ?skill2 .
    }
    WHERE {
        ?skill1 sfia:skillCategory ?category .
        ?skill2 sfia:skillCategory ?category .
        FILTER(?skill1 != ?skill2)
    }
    """
    graph.update(complementary_query)


def generate_sample_data():
    """Generate sample professional roles and competency data"""
    
    # Sample roles data
    roles_data = [
        {
            'role_code': 'SWARCH',
            'role_name': 'Software Architect',
            'role_level': 6,
            'essential_skills': 'ITSP_6;ARCH_6;TECR_5',
            'desirable_skills': 'TEAM_5;BUAN_4'
        },
        {
            'role_code': 'DEVLEAD',
            'role_name': 'Development Team Lead',
            'role_level': 5,
            'essential_skills': 'PROG_5;TEAM_5;ARCH_4',
            'desirable_skills': 'ITSP_4;TECR_4'
        }
    ]
    
    # Create sample CSV files
    with open('enhanced_data/roles.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['role_code', 'role_name', 'role_level', 'essential_skills', 'desirable_skills'])
        writer.writeheader()
        writer.writerows(roles_data)
    
    # Sample pathways data
    pathways_data = [
        {
            'from_role': 'DEVLEAD',
            'to_role': 'SWARCH',
            'pathway_type': 'progression',
            'additional_skills_needed': 'ITSP_6;ARCH_6'
        }
    ]
    
    with open('enhanced_data/pathways.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['from_role', 'to_role', 'pathway_type', 'additional_skills_needed'])
        writer.writeheader()
        writer.writerows(pathways_data)


def main():
    """Main conversion function with enhancements"""
    
    # Create base SFIA graph (existing functionality)
    sfia_graph = create_enhanced_sfia_graph()
    
    # Load existing SFIA data
    print("Loading base SFIA data...")
    
    # Attributes
    with open("sfia_rdf/tests/test_files/attributes_test.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in reader:
            row_triples = attributes_parser.parse_row(row)
            [sfia_graph.add(triple) for triple in row_triples]
    
    # Levels
    with open("sfia_rdf/tests/test_files/levels_test.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        row_triples = levels_parser.parse_levels_table([row for row in reader])
        [sfia_graph.add(triple) for triple in row_triples]
    
    # Skills
    with open("sfia_rdf/tests/test_files/skills_test.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in reader:
            row_triples = skills_parser.parse_row(row)
            [sfia_graph.add(triple) for triple in row_triples]
    
    # Add enhanced data if available
    print("Adding enhanced professional context...")
    
    # Generate sample data
    os.makedirs('enhanced_data', exist_ok=True)
    generate_sample_data()
    
    # Add professional roles
    if os.path.exists('enhanced_data/roles.csv'):
        add_professional_roles(sfia_graph, 'enhanced_data/roles.csv')
    
    # Add career pathways
    if os.path.exists('enhanced_data/pathways.csv'):
        add_career_pathways(sfia_graph, 'enhanced_data/pathways.csv')
    
    # Add inferred relationships
    print("Adding skill relationships...")
    add_skill_relationships(sfia_graph)
    
    # Update category scheme
    category_query = """
    INSERT {
        sfia:CategoryScheme skos:hasTopConcept ?concept.
    }
    WHERE {
        ?concept a sfia:Category.
        FILTER NOT EXISTS { ?concept skos:broader ?broaderConcept. }
    }
    """
    sfia_graph.update(category_query)
    
    # Generate output
    TODAY = datetime.today().strftime('%Y-%m-%d')
    OUTPUT = f"Enhanced_SFIA_9_{TODAY}.ttl"
    
    print(f"Serializing enhanced ontology to {OUTPUT}...")
    sfia_graph.serialize(OUTPUT, format='turtle')
    
    print(f"Enhanced SFIA ontology created with {len(sfia_graph)} triples")
    
    # Generate statistics
    stats_query = """
    SELECT 
        (COUNT(DISTINCT ?skill) AS ?skills)
        (COUNT(DISTINCT ?role) AS ?roles)
        (COUNT(DISTINCT ?level) AS ?levels)
        (COUNT(DISTINCT ?category) AS ?categories)
    WHERE {
        OPTIONAL { ?skill a sfia:Skill }
        OPTIONAL { ?role a sfia:ProfessionalRole }
        OPTIONAL { ?level a sfia:Level }
        OPTIONAL { ?category a sfia:Category }
    }
    """
    
    result = list(sfia_graph.query(stats_query))[0]
    print(f"Statistics:")
    print(f"  - Skills: {result.skills}")
    print(f"  - Professional Roles: {result.roles}")
    print(f"  - Levels: {result.levels}")
    print(f"  - Categories: {result.categories}")


if __name__ == "__main__":
    main()