from rdflib import URIRef, Graph, SKOS

BASE = URIRef("https://rdf.sfia-online.org/9/")
SKILLS = BASE + 'skills/'
SKILL_LEVELS = BASE + 'skilllevels/'
ATTRIBUTES = BASE + 'attributes/'
LEVELS = BASE + 'lor/'
CATEGORIES = BASE + 'categories/'
SFIA_ONTOLOGY = BASE + 'ontology/'


def bind_namespaces(g: Graph):
    g.bind('skills', SKILLS)
    g.bind('skilllevels', SKILL_LEVELS)
    g.bind('attributes', ATTRIBUTES)
    g.bind('levels', LEVELS)
    g.bind('categories', CATEGORIES)
    g.bind('sfia', SFIA_ONTOLOGY)
    g.bind('skos', SKOS)
    return g
