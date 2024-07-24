from rdflib import RDF, SKOS, Literal, RDFS

from sfia_rdf.namespaces import CATEGORIES, SKILLS, SKILLS_LEVELS, LEVELS


def hash_name(name: str):
    return name.lower().replace(' ', '_').replace(',', '_')


def parse_row(row: list):
    """Returns a set of triples"""
    to_return = set()
    row_number = row[0]
    if row_number == "#":
        return {}
    # levels_header = row[1]
    levels = [level for level in row[2:7 + 1] if level != '']
    code = row[8]
    skill = row[9]
    category = row[10]
    subcategory = row[11]
    desc = row[12]
    notes = row[13]
    levels_notes = [d for d in row[14:20 + 1] if d != '']
    levels_notes_dict = {level: note for (level, note) in zip(levels, levels_notes)}

    # side effect: build the hierarchy of categories
    for concept in [category, subcategory]:
        to_return.add((CATEGORIES + hash_name(concept), RDF.type, CATEGORIES + 'Category'))
        to_return.add((CATEGORIES + hash_name(concept), SKOS.prefLabel, Literal(concept, 'en')))
        to_return.add((CATEGORIES + hash_name(concept), SKOS.inScheme, CATEGORIES + "CategoryScheme"))
    to_return.add((CATEGORIES + hash_name(subcategory), SKOS.broader, CATEGORIES + hash_name(category)))

    skill_iri = SKILLS + f"{code}"
    to_return.add((skill_iri, RDF.type, SKILLS + "Skill"))
    to_return.add((skill_iri, RDFS.label, Literal(skill, 'en')))
    to_return.add((skill_iri, SKOS.notation, Literal(f"{code}")))
    to_return.add((skill_iri, SKILLS + "description", Literal(desc, 'en')))
    to_return.add((skill_iri, SKILLS + "notes", Literal(notes, 'en')))
    to_return.add((skill_iri, SKILLS + "category", CATEGORIES + hash_name(subcategory)))

    # each row must become multiple skills, whose identity are the code and level
    for level in levels:
        skill_level = SKILLS_LEVELS + f"{code}_{level}"
        to_return.add((skill_iri, SKILLS + "definedAtLevel", skill_level))
        to_return.add((skill_level, RDF.type, SKILLS_LEVELS + "SkillLevel"))
        to_return.add((skill_level, SKOS.notation, Literal(f"{code}_{level}")))
        to_return.add((skill_level, SKILLS_LEVELS + "level", LEVELS + level))
        to_return.add((skill_level, SKILLS_LEVELS + "notes", Literal(levels_notes_dict[level], 'en')))

    return to_return
