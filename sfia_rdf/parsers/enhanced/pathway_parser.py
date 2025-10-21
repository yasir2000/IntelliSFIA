"""
Career pathways parser for enhanced SFIA ontology
Handles career progression and development paths
"""

from rdflib import RDF, RDFS, Literal, URIRef
from sfia_rdf import namespaces
from sfia_rdf.namespaces import SFIA_ONTOLOGY

# Enhanced namespaces
PATHWAYS = namespaces.BASE + 'pathways/'
ROLES = namespaces.BASE + 'roles/'


def parse_pathway_row(row_dict):
    """
    Parse career pathway from CSV row
    
    Args:
        row_dict: Dictionary with pathway data
    
    Returns:
        Set of RDF triples defining the career pathway
    """
    triples = set()
    
    from_role = row_dict.get('from_role', '').strip()
    to_role = row_dict.get('to_role', '').strip()
    pathway_type = row_dict.get('pathway_type', 'progression').strip()
    additional_skills = row_dict.get('additional_skills_needed', '').strip()
    
    # Create pathway IRI
    pathway_id = f"{from_role}_to_{to_role}"
    pathway_iri = PATHWAYS + pathway_id
    
    from_role_iri = ROLES + from_role
    to_role_iri = ROLES + to_role
    
    # Basic pathway properties
    triples.update({
        (pathway_iri, RDF.type, SFIA_ONTOLOGY + "CareerPathway"),
        (pathway_iri, SFIA_ONTOLOGY + "fromRole", from_role_iri),
        (pathway_iri, SFIA_ONTOLOGY + "toRole", to_role_iri),
        (pathway_iri, SFIA_ONTOLOGY + "pathwayType", Literal(pathway_type)),
        (from_role_iri, SFIA_ONTOLOGY + "progressesTo", to_role_iri)
    })
    
    # Additional skills needed for progression
    if additional_skills:
        skills_list = [s.strip() for s in additional_skills.split(';') if s.strip()]
        for skill_ref in skills_list:
            if '_' in skill_ref:  # e.g., "ITSP_6"
                skill_level_iri = namespaces.SKILL_LEVELS + skill_ref
                triples.add((pathway_iri, SFIA_ONTOLOGY + "requiresAdditionalSkill", skill_level_iri))
    
    return triples


def create_progression_matrix(pathways_data):
    """
    Create a progression matrix showing all possible career paths
    
    Args:
        pathways_data: List of pathway data
    
    Returns:
        Set of triples defining progression relationships
    """
    triples = set()
    
    # Create progression levels based on role levels
    role_levels = {}
    for pathway in pathways_data:
        from_role = pathway['from_role']
        to_role = pathway['to_role']
        
        # Assume progression typically goes to higher levels
        if from_role not in role_levels:
            role_levels[from_role] = 1
        if to_role not in role_levels:
            role_levels[to_role] = role_levels[from_role] + 1
    
    # Create progression difficulty metrics
    for pathway in pathways_data:
        pathway_id = f"{pathway['from_role']}_to_{pathway['to_role']}"
        pathway_iri = PATHWAYS + pathway_id
        
        additional_skills_count = len(pathway.get('additional_skills_needed', '').split(';'))
        difficulty = "high" if additional_skills_count > 3 else "medium" if additional_skills_count > 1 else "low"
        
        triples.add((pathway_iri, SFIA_ONTOLOGY + "progressionDifficulty", Literal(difficulty)))
    
    return triples


def analyze_career_networks(pathways_data):
    """
    Analyze the network of career progressions to identify key roles and bottlenecks
    
    Args:
        pathways_data: List of pathway data
    
    Returns:
        Set of analytical triples
    """
    triples = set()
    
    # Count incoming and outgoing pathways for each role
    role_stats = {}
    
    for pathway in pathways_data:
        from_role = pathway['from_role']
        to_role = pathway['to_role']
        
        if from_role not in role_stats:
            role_stats[from_role] = {'outgoing': 0, 'incoming': 0}
        if to_role not in role_stats:
            role_stats[to_role] = {'outgoing': 0, 'incoming': 0}
        
        role_stats[from_role]['outgoing'] += 1
        role_stats[to_role]['incoming'] += 1
    
    # Classify roles based on their position in the career network
    for role_code, stats in role_stats.items():
        role_iri = ROLES + role_code
        
        if stats['outgoing'] > 2 and stats['incoming'] == 0:
            triples.add((role_iri, SFIA_ONTOLOGY + "roleType", Literal("entry_level")))
        elif stats['incoming'] > 2 and stats['outgoing'] == 0:
            triples.add((role_iri, SFIA_ONTOLOGY + "roleType", Literal("senior_level")))
        elif stats['incoming'] > 1 and stats['outgoing'] > 1:
            triples.add((role_iri, SFIA_ONTOLOGY + "roleType", Literal("bridge_role")))
        else:
            triples.add((role_iri, SFIA_ONTOLOGY + "roleType", Literal("specialist_role")))
    
    return triples