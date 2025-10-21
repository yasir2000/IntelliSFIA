# SFIA 9 Ontology Enhancement Implementation Plan

## Phase 1: Core Ontology Extensions

### 1.1 Enhanced Namespace Structure
```python
# Enhanced namespaces.py
BASE = URIRef("https://rdf.sfia-online.org/9/")
SKILLS = BASE + 'skills/'
SKILL_LEVELS = BASE + 'skilllevels/'
ATTRIBUTES = BASE + 'attributes/'
LEVELS = BASE + 'lor/'
CATEGORIES = BASE + 'categories/'
SFIA_ONTOLOGY = BASE + 'ontology/'

# New namespaces for extensions
ROLES = BASE + 'roles/'
PROFILES = BASE + 'profiles/'
ASSESSMENTS = BASE + 'assessments/'
LEARNING = BASE + 'learning/'
ORGANIZATIONS = BASE + 'organizations/'
PATHWAYS = BASE + 'pathways/'
CLUSTERS = BASE + 'clusters/'
```

### 1.2 New Parser Modules

#### A. roles_parser.py
```python
def parse_role_definition(row: list):
    """Parse professional role definitions from CSV"""
    role_code = row[0]
    role_name = row[1]
    role_level = row[2]
    required_skills = row[3].split(';')  # e.g., "ITSP_5;ISCO_6"
    
    role_iri = namespaces.ROLES + role_code
    triples = {
        (role_iri, RDF.type, SFIA_ONTOLOGY + "ProfessionalRole"),
        (role_iri, RDFS.label, Literal(role_name, 'en')),
        (role_iri, SFIA_ONTOLOGY + "roleLevel", Literal(role_level))
    }
    
    # Link to required skills
    for skill_ref in required_skills:
        skill_level_iri = namespaces.SKILL_LEVELS + skill_ref
        triples.add((role_iri, SFIA_ONTOLOGY + "requiresSkill", skill_level_iri))
    
    return triples
```

#### B. competency_parser.py
```python
def parse_competency_profile(row: list):
    """Parse competency profiles for roles"""
    profile_id = row[0]
    role_code = row[1]
    essential_skills = row[2].split(';')
    desirable_skills = row[3].split(';')
    
    profile_iri = namespaces.PROFILES + profile_id
    role_iri = namespaces.ROLES + role_code
    
    triples = {
        (profile_iri, RDF.type, SFIA_ONTOLOGY + "CompetencyProfile"),
        (role_iri, SFIA_ONTOLOGY + "hasCompetencyProfile", profile_iri)
    }
    
    # Essential vs desirable skills
    for skill in essential_skills:
        skill_iri = namespaces.SKILL_LEVELS + skill
        triples.add((profile_iri, SFIA_ONTOLOGY + "requiresEssentialSkill", skill_iri))
    
    for skill in desirable_skills:
        skill_iri = namespaces.SKILL_LEVELS + skill
        triples.add((profile_iri, SFIA_ONTOLOGY + "requiresDesirableSkill", skill_iri))
    
    return triples
```

### 1.3 Enhanced Data Model Classes

#### Enhanced convert_sfia.py additions
```python
# Add to the main SPARQL insert in convert_sfia.py
enhanced_ontology = """
INSERT DATA {
    ##
    ## Extended Classes for Complete SFIA Ontology
    ##
    
    # Professional Context
    sfia:ProfessionalRole a owl:Class ;
        rdfs:label "Professional Role"@en ;
        rdfs:comment "A role requiring specific SFIA competencies"@en .
    
    sfia:CompetencyProfile a owl:Class ;
        rdfs:label "Competency Profile"@en ;
        rdfs:comment "Set of skills and levels for a role"@en .
    
    sfia:CareerPathway a owl:Class ;
        rdfs:label "Career Pathway"@en ;
        rdfs:comment "Progression route between roles"@en .
    
    # Assessment Framework
    sfia:Assessment a owl:Class ;
        rdfs:label "Skill Assessment"@en ;
        rdfs:comment "Evaluation of competency"@en .
    
    sfia:SkillGap a owl:Class ;
        rdfs:label "Skill Gap"@en ;
        rdfs:comment "Difference between required and actual level"@en .
    
    # Learning and Development
    sfia:LearningResource a owl:Class ;
        rdfs:label "Learning Resource"@en ;
        rdfs:comment "Resource for skill development"@en .
    
    sfia:LearningPath a owl:Class ;
        rdfs:label "Learning Path"@en ;
        rdfs:comment "Structured sequence of learning resources"@en .
    
    # Organizational Context
    sfia:Organization a owl:Class ;
        rdfs:label "Organization"@en ;
        rdfs:comment "Entity adopting SFIA framework"@en .
    
    sfia:Department a owl:Class ;
        rdfs:label "Department"@en ;
        rdfs:comment "Organizational unit"@en .
    
    # Enhanced Properties
    sfia:requiresSkill a owl:ObjectProperty ;
        rdfs:domain sfia:ProfessionalRole ;
        rdfs:range sfia:SkillLevel ;
        rdfs:label "requires skill at level"@en .
    
    sfia:prerequisiteFor a owl:ObjectProperty ;
        rdfs:domain sfia:SkillLevel ;
        rdfs:range sfia:SkillLevel ;
        rdfs:label "prerequisite for"@en .
    
    sfia:complementaryTo a owl:ObjectProperty ;
        rdfs:domain sfia:Skill ;
        rdfs:range sfia:Skill ;
        rdfs:label "complementary to"@en .
    
    sfia:assessedAt a owl:ObjectProperty ;
        rdfs:domain [a owl:Restriction ; 
                     owl:onProperty sfia:hasSkill ; 
                     owl:someValuesFrom sfia:Skill] ;
        rdfs:range sfia:Level ;
        rdfs:label "assessed at level"@en .
}
"""
```

## Phase 2: Advanced Analytics and Reasoning

### 2.1 SPARQL Queries for Insights

#### Skill Gap Analysis
```sparql
# Find skill gaps for a specific role
PREFIX sfia: <https://rdf.sfia-online.org/9/ontology/>
PREFIX roles: <https://rdf.sfia-online.org/9/roles/>

SELECT ?skill ?requiredLevel ?currentLevel ?gap
WHERE {
    roles:SoftwareArchitect sfia:requiresSkill ?skillLevel .
    ?skillLevel sfia:skill ?skill ;
               sfia:level ?requiredLevel .
    
    # Current assessment (would come from assessment data)
    ?assessment sfia:assessesSkill ?skill ;
               sfia:assessedAt ?currentLevel .
    
    BIND(?requiredLevel - ?currentLevel AS ?gap)
    FILTER(?gap > 0)
}
```

#### Career Progression Analysis
```sparql
# Find possible career progressions
SELECT ?currentRole ?nextRole ?sharedSkills
WHERE {
    ?currentRole sfia:requiresSkill ?skill1 .
    ?nextRole sfia:requiresSkill ?skill2 .
    ?skill1 sfia:skill ?commonSkill .
    ?skill2 sfia:skill ?commonSkill .
    
    # Count shared skills
    {
        SELECT ?currentRole ?nextRole (COUNT(?commonSkill) AS ?sharedSkills)
        WHERE {
            ?currentRole sfia:requiresSkill/sfia:skill ?commonSkill .
            ?nextRole sfia:requiresSkill/sfia:skill ?commonSkill .
        }
        GROUP BY ?currentRole ?nextRole
        HAVING(?sharedSkills >= 3)
    }
}
```

### 2.2 Reasoning Rules (SWRL)

```swrl
# Skill progression rule
Skill(?s) ∧ definedAtLevel(?s, ?sl1) ∧ level(?sl1, ?l1) ∧ 
definedAtLevel(?s, ?sl2) ∧ level(?sl2, ?l2) ∧ 
swrlb:greaterThan(?l2, ?l1) → prerequisiteFor(?sl1, ?sl2)

# Role compatibility rule  
ProfessionalRole(?r1) ∧ ProfessionalRole(?r2) ∧
requiresSkill(?r1, ?sk1) ∧ requiresSkill(?r2, ?sk2) ∧
skill(?sk1, ?s) ∧ skill(?sk2, ?s) → compatibleWith(?r1, ?r2)
```

## Phase 3: Integration and Validation

### 3.1 Data Validation Framework

#### validation/ontology_validator.py
```python
def validate_ontology_completeness(graph):
    """Validate that all skills have proper level definitions"""
    query = """
    SELECT ?skill WHERE {
        ?skill a sfia:Skill .
        FILTER NOT EXISTS { ?skill sfia:definedAtLevel ?level }
    }
    """
    orphaned_skills = list(graph.query(query))
    return len(orphaned_skills) == 0, f"Found {len(orphaned_skills)} skills without levels"

def validate_role_coherence(graph):
    """Ensure roles have coherent skill requirements"""
    query = """
    SELECT ?role ?skill1 ?level1 ?skill2 ?level2 WHERE {
        ?role sfia:requiresSkill ?sl1, ?sl2 .
        ?sl1 sfia:skill ?skill1 ; sfia:level ?level1 .
        ?sl2 sfia:skill ?skill2 ; sfia:level ?level2 .
        ?skill1 sfia:prerequisiteFor ?skill2 .
        FILTER(?level1 >= ?level2)  # Prerequisite should be lower level
    }
    """
    inconsistencies = list(graph.query(query))
    return len(inconsistencies) == 0, f"Found {len(inconsistencies)} role inconsistencies"
```

### 3.2 Performance Optimization

#### Indexing Strategy
```python
# Add indexes for common query patterns
def add_performance_indexes(graph):
    """Add SPARQL query hints for better performance"""
    graph.update("""
    PREFIX sfia: <https://rdf.sfia-online.org/9/ontology/>
    
    # Create virtual triple patterns for common queries
    INSERT DATA {
        sfia:SkillLevelIndex a owl:Class ;
            rdfs:comment "Index for skill-level combinations"@en .
    }
    """)
```

## Phase 4: API and Integration Layer

### 4.1 REST API Endpoints

```python
# api/sfia_api.py
from flask import Flask, jsonify
from rdflib import Graph

app = Flask(__name__)
sfia_graph = Graph()

@app.route('/api/skills/<skill_code>/levels')
def get_skill_levels(skill_code):
    """Get all levels for a specific skill"""
    query = f"""
    SELECT ?level ?description WHERE {{
        skills:{skill_code} sfia:definedAtLevel ?sl .
        ?sl sfia:level ?level ; sfia:skillLevelDescription ?description .
    }}
    ORDER BY ?level
    """
    results = sfia_graph.query(query)
    return jsonify([{"level": r.level, "description": str(r.description)} for r in results])

@app.route('/api/roles/<role_code>/requirements')
def get_role_requirements(role_code):
    """Get skill requirements for a role"""
    query = f"""
    SELECT ?skill ?level ?skillName WHERE {{
        roles:{role_code} sfia:requiresSkill ?sl .
        ?sl sfia:skill ?skill ; sfia:level ?level .
        ?skill rdfs:label ?skillName .
    }}
    ORDER BY ?skillName
    """
    results = sfia_graph.query(query)
    return jsonify([{
        "skill": str(r.skill).split('/')[-1], 
        "level": int(r.level),
        "name": str(r.skillName)
    } for r in results])
```