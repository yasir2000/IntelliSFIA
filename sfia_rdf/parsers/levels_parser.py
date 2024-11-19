from rdflib import RDF, Literal, URIRef, SKOS, XSD

from sfia_rdf import namespaces
from sfia_rdf.namespaces import SFIA_ONTOLOGY


def is_row_for(s: str):
    return lambda row: row[0].strip() == s


def get_row_for(rows: list, s: str):
    return list(filter(is_row_for(s), rows))[0]


def get_items_for(rows, row_header: str):
    return [item for item in get_row_for(rows, row_header)][1:]


def parse_levels_table(rows: list):
    """
    Returns a set of triples.
    """
    to_return = set()
    levels = get_items_for(rows, 'Level')
    guiding_phrases = get_items_for(rows, 'Guiding phrase')
    essences = get_items_for(rows, 'Essence of the level')
    urls = get_items_for(rows, 'URL')
    zipped = list(zip(levels, guiding_phrases, essences, urls))
    for i in zipped:
        level = i[0]
        iri = namespaces.LEVELS + level
        url = URIRef(i[3].strip())
        guiding_phrase = Literal(i[1].strip(), 'en')
        essence = Literal(i[2].strip(), 'en')
        to_return.add((iri, RDF.type, SFIA_ONTOLOGY + 'Level'))
        to_return.add((iri, SKOS.notation, Literal(i[0], datatype=XSD.integer)))
        to_return.add((iri, SKOS.inScheme, SFIA_ONTOLOGY + 'LorScheme'))
        to_return.add((iri, SFIA_ONTOLOGY + 'levelGuidingPhrase', guiding_phrase))
        to_return.add((iri, SFIA_ONTOLOGY + 'levelEssence', essence))
        to_return.add((iri, SFIA_ONTOLOGY + 'url', Literal(url)))
    return to_return
