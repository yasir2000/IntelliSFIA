from rdflib import URIRef, Graph, SKOS

SFIA_VERSION = '8'

BASE = URIRef("https://sfia-online.org/en/")
LEVELS = BASE + "lor/" + SFIA_VERSION + '/'
SKILLS = BASE + "skillcode/" + SFIA_VERSION + '/'
CATEGORIES = BASE + "categories/" + SFIA_VERSION + '/'
SKILLS_LEVELS = BASE + "skill-levels/" + SFIA_VERSION + '/'


def bind_namespaces(g: Graph):
    g.bind('categories', CATEGORIES)
    g.bind('skills', SKILLS)
    g.bind('levels', LEVELS)
    g.bind('skills_levels', SKILLS_LEVELS)
    g.bind('skos', SKOS)
    return g
