from rdflib import RDF, SKOS, Literal, RDFS, URIRef

from sfia_rdf import namespaces
from sfia_rdf.namespaces import SFIA_ONTOLOGY


def hash_name(name: str):
    return name.lower().replace(' ', '_').replace(',', '_')


def mint_category_iri(s: str):
    return namespaces.CATEGORIES + hash_name(s)


def parse_row(row: list):
    """
    Args:
        row: a list representing a python CSV row
    Returns:
        A set of RDF triples
    """
    to_return = set()
    row_number = row[0]
    if row_number == "#":
        return {}
    levels = [level for level in row[2:7 + 1] if level != '']
    code = row[8].strip()
    skill_iri = namespaces.SKILLS + code
    skill_url = URIRef(row[9])
    skill = row[10]
    category = row[11].strip()
    subcategory = row[12].strip()
    desc = row[13].strip()
    notes = row[14].strip()
    levels_notes = [d for d in row[15:21 + 1] if d != '']
    levels_notes_dict = {level: note for (level, note) in zip(levels, levels_notes)}

    # side effect: build the hierarchy of categories
    for concept in [category, subcategory]:
        category_iri = mint_category_iri(concept)
        to_return.update({
            (category_iri, RDF.type, SFIA_ONTOLOGY + 'Category'),
            (category_iri, SKOS.prefLabel, Literal(concept, 'en')),
            (category_iri, SKOS.inScheme, SFIA_ONTOLOGY + "CategoryScheme")
        })
    to_return.add((mint_category_iri(subcategory), SKOS.broader, mint_category_iri(category)))

    to_return.update({
        (skill_iri, RDF.type, SFIA_ONTOLOGY + "Skill"),
        (skill_iri, RDFS.label, Literal(skill, 'en')),
        (skill_iri, SKOS.notation, Literal(f"{code}")),
        (skill_iri, SFIA_ONTOLOGY + "skillDescription", Literal(desc, 'en')),
        (skill_iri, SFIA_ONTOLOGY + "skillNotes", Literal(notes, 'en')),
        (skill_iri, SFIA_ONTOLOGY + "skillCategory", mint_category_iri(subcategory)),
        (skill_iri, SFIA_ONTOLOGY + 'url', Literal(skill_url))
    })

    # each row must become multiple skills, whose identity are the code and level
    for level in levels:
        skill_level = namespaces.SKILL_LEVELS + f"{code}_{level}"
        to_return.update({
            (skill_iri, SFIA_ONTOLOGY + "definedAtLevel", skill_level),
            (skill_level, RDF.type, SFIA_ONTOLOGY + "SkillLevel"),
            (skill_level, SKOS.notation, Literal(f"{code}_{level}")),
            (skill_level, SFIA_ONTOLOGY + "level", namespaces.LEVELS + level),
            (skill_level, SFIA_ONTOLOGY + "skillLevelDescription", Literal(levels_notes_dict[level], 'en'))
        })

    return to_return
