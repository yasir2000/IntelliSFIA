from rdflib import URIRef, Graph, SKOS

SFIA_ONTOLOGY = URIRef("https://sfia-online.org/ontology/")


def bind_namespaces(g: Graph):
    g.bind('skills', URIRef("https://sfia-online.org/en/skillcode/9/"))
    g.bind('attributes', URIRef("https://sfia-online.org/en/shortcode/9/"))
    g.bind('levels', URIRef("https://sfia-online.org/en/lor/9/"))
    g.bind('skos', SKOS)
    g.bind('sfia', SFIA_ONTOLOGY)
    return g
