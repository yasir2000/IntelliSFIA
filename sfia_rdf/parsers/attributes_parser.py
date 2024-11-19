from rdflib import URIRef, RDF, OWL, RDFS, Literal, SKOS

from sfia_rdf import namespaces
from sfia_rdf.namespaces import SFIA_ONTOLOGY


def parse_row(row: list):
    """
    Returns a set of triples.

    """
    to_return = set()
    # skip headers
    if row[0].strip() == 'Levels':
        return {}
    levels = [level for level in row[0:6 + 1] if level != '']
    code = row[7].strip()
    attribute_iri = namespaces.ATTRIBUTES + code
    attribute_url = URIRef(row[8])
    name = row[9].strip()
    type = row[10].strip()
    overall_desc = row[11].strip()
    guidance_notes = row[12].strip()
    levels_notes = [d.strip() for d in row[13:19 + 1] if d != '']
    levels_notes_dict = {level: note for (level, note) in zip(levels, levels_notes)}

    # property definition
    to_return.add((attribute_iri, RDF.type, OWL.AnnotationProperty))
    to_return.add((attribute_iri, RDFS.label, Literal(name, 'en')))
    to_return.add((attribute_iri, SKOS.notation, Literal(code)))
    to_return.add((attribute_iri, SFIA_ONTOLOGY + "attributeType", Literal(type, 'en')))
    to_return.add((attribute_iri, RDFS.comment, Literal(overall_desc, 'en')))
    to_return.add((attribute_iri, SFIA_ONTOLOGY + "attributeGuidanceNotes", Literal(guidance_notes, 'en')))
    to_return.add((attribute_iri, SFIA_ONTOLOGY + "url", Literal(attribute_url)))

    # association to Level
    for level in levels:
        level_iri = namespaces.LEVELS + level
        to_return.add((level_iri, attribute_iri, Literal(levels_notes_dict[level], 'en')))
    return to_return
