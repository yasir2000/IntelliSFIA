"""
Competency profiles parser for enhanced SFIA ontology
Handles detailed competency requirements and skill profiles
"""

from rdflib import RDF, RDFS, Literal, URIRef
from sfia_rdf import namespaces
from sfia_rdf.namespaces import SFIA_ONTOLOGY

# Enhanced namespaces
PROFILES = namespaces.BASE + 'profiles/'
ROLES = namespaces.BASE + 'roles/'


def parse_profile_row(row_dict):
    """
    Parse competency profile from CSV row
    
    Args:
        row_dict: Dictionary with profile data
    
    Returns:
        Set of RDF triples defining the competency profile
    """
    triples = set()
    
    profile_id = row_dict.get('profile_id', '').strip()
    role_code = row_dict.get('role_code', '').strip()
    profile_name = row_dict.get('profile_name', '').strip()
    description = row_dict.get('description', '').strip()
    
    # Create profile IRI
    profile_iri = PROFILES + profile_id
    role_iri = ROLES + role_code
    
    # Basic profile properties
    triples.update({
        (profile_iri, RDF.type, SFIA_ONTOLOGY + "CompetencyProfile"),
        (profile_iri, RDFS.label, Literal(profile_name, 'en')),
        (profile_iri, RDFS.comment, Literal(description, 'en')),
        (profile_iri, SFIA_ONTOLOGY + "profileId", Literal(profile_id)),
        (role_iri, SFIA_ONTOLOGY + "hasCompetencyProfile", profile_iri)
    })
    
    return triples


def parse_competency_requirements(profile_id, skills_data):
    """
    Parse detailed competency requirements for a profile
    
    Args:
        profile_id: Profile identifier
        skills_data: List of skill requirements with priorities
    
    Returns:
        Set of triples defining competency requirements
    """
    triples = set()
    profile_iri = PROFILES + profile_id
    
    for skill_req in skills_data:
        skill_code = skill_req.get('skill_code', '').strip()
        level = skill_req.get('level', 1)
        priority = skill_req.get('priority', 'important').lower()  # essential, important, desirable
        weight = skill_req.get('weight', 1.0)  # Importance weighting
        
        # Create skill level IRI
        skill_level_iri = namespaces.SKILL_LEVELS + f"{skill_code}_{level}"
        
        # Create competency requirement
        requirement_iri = profile_iri + f"_req_{skill_code}_{level}"
        
        triples.update({
            (requirement_iri, RDF.type, SFIA_ONTOLOGY + "CompetencyRequirement"),
            (requirement_iri, SFIA_ONTOLOGY + "requiresSkillLevel", skill_level_iri),
            (requirement_iri, SFIA_ONTOLOGY + "priority", Literal(priority)),
            (requirement_iri, SFIA_ONTOLOGY + "weight", Literal(weight)),
            (profile_iri, SFIA_ONTOLOGY + "hasRequirement", requirement_iri)
        })
    
    return triples


def create_profile_analytics(profiles_data):
    """
    Generate analytics about competency profiles
    
    Args:
        profiles_data: List of profile data
    
    Returns:
        Set of analytical triples
    """
    triples = set()
    
    # Calculate profile complexity
    for profile in profiles_data:
        profile_iri = PROFILES + profile['profile_id']
        
        # Count essential vs desirable skills
        essential_count = len([s for s in profile.get('skills', []) if s.get('priority') == 'essential'])
        total_count = len(profile.get('skills', []))
        
        complexity = "high" if total_count > 10 else "medium" if total_count > 5 else "low"
        
        triples.update({
            (profile_iri, SFIA_ONTOLOGY + "complexity", Literal(complexity)),
            (profile_iri, SFIA_ONTOLOGY + "essentialSkillsCount", Literal(essential_count)),
            (profile_iri, SFIA_ONTOLOGY + "totalSkillsCount", Literal(total_count))
        })
    
    return triples