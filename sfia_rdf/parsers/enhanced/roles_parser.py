"""
Professional roles parser for enhanced SFIA ontology
Converts role definitions to RDF triples
"""

from rdflib import RDF, RDFS, Literal, URIRef
from sfia_rdf import namespaces
from sfia_rdf.namespaces import SFIA_ONTOLOGY

# Enhanced namespaces
ROLES = namespaces.BASE + 'roles/'


def parse_role_row(row_dict):
    """
    Parse a professional role definition from CSV row
    
    Args:
        row_dict: Dictionary with keys: role_code, role_name, role_level, 
                 essential_skills, desirable_skills
    
    Returns:
        Set of RDF triples defining the professional role
    """
    triples = set()
    
    role_code = row_dict['role_code'].strip()
    role_name = row_dict['role_name'].strip()
    role_level = int(row_dict['role_level'])
    essential_skills = [s.strip() for s in row_dict['essential_skills'].split(';') if s.strip()]
    desirable_skills = [s.strip() for s in row_dict['desirable_skills'].split(';') if s.strip()]
    
    # Create role IRI
    role_iri = ROLES + role_code
    
    # Basic role properties
    triples.update({
        (role_iri, RDF.type, SFIA_ONTOLOGY + "ProfessionalRole"),
        (role_iri, RDFS.label, Literal(role_name, 'en')),
        (role_iri, SFIA_ONTOLOGY + "roleLevel", Literal(role_level)),
        (role_iri, SFIA_ONTOLOGY + "roleCode", Literal(role_code))
    })
    
    # Essential skills
    for skill_ref in essential_skills:
        if '_' in skill_ref:  # e.g., "ITSP_6"
            skill_level_iri = namespaces.SKILL_LEVELS + skill_ref
            triples.add((role_iri, SFIA_ONTOLOGY + "requiresEssentialSkill", skill_level_iri))
        else:  # Just skill code without level
            skill_iri = namespaces.SKILLS + skill_ref
            triples.add((role_iri, SFIA_ONTOLOGY + "requiresSkill", skill_iri))
    
    # Desirable skills
    for skill_ref in desirable_skills:
        if '_' in skill_ref:
            skill_level_iri = namespaces.SKILL_LEVELS + skill_ref
            triples.add((role_iri, SFIA_ONTOLOGY + "requiresDesirableSkill", skill_level_iri))
        else:
            skill_iri = namespaces.SKILLS + skill_ref
            triples.add((role_iri, SFIA_ONTOLOGY + "prefersSkill", skill_iri))
    
    return triples


def parse_role_hierarchy(parent_role, child_role):
    """
    Create hierarchical relationship between roles
    
    Args:
        parent_role: Senior role code
        child_role: Junior role code
    
    Returns:
        Set of triples defining the relationship
    """
    parent_iri = ROLES + parent_role
    child_iri = ROLES + child_role
    
    triples = {
        (child_iri, SFIA_ONTOLOGY + "progressesTo", parent_iri),
        (parent_iri, SFIA_ONTOLOGY + "hasJuniorRole", child_iri)
    }
    
    return triples


def create_role_competency_matrix(roles_data):
    """
    Create a competency matrix showing skill requirements across roles
    
    Args:
        roles_data: List of role dictionaries
    
    Returns:
        Set of triples defining competency relationships
    """
    triples = set()
    
    # Group roles by similar competencies
    for i, role1 in enumerate(roles_data):
        for role2 in roles_data[i+1:]:
            role1_skills = set(role1.get('essential_skills', '').split(';'))
            role2_skills = set(role2.get('essential_skills', '').split(';'))
            
            # Calculate overlap
            overlap = role1_skills.intersection(role2_skills)
            if len(overlap) >= 2:  # Significant overlap
                role1_iri = ROLES + role1['role_code']
                role2_iri = ROLES + role2['role_code']
                triples.add((role1_iri, SFIA_ONTOLOGY + "similarTo", role2_iri))
                triples.add((role2_iri, SFIA_ONTOLOGY + "similarTo", role1_iri))
    
    return triples