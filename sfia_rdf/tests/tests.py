import csv

from rdflib import Graph

from sfia_rdf import namespaces, sfia_parser
from sfia_rdf.sfia_parser import hash_name


def test_hash():
    assert hash_name("My, category") == "my__category"


def test_bind_namespaces():
    g = Graph()
    namespaces.bind_namespaces(g)
    assert g.qname("https://sfia-online.org/en/lor/8/2") == "levels:2"


def test_parse_row():
    g = Graph()
    namespaces.bind_namespaces(g)
    with open("test_sfia-8_en_220221.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            triples = sfia_parser.parse_row(row)
            [g.add(triple) for triple in triples]
    ress = g.query("select ?skill where {?skill a skills:Skill} order by ?skill")
    assert [str(res.skill) for res in ress] == ["https://sfia-online.org/en/skillcode/8/ISCO",
                                                "https://sfia-online.org/en/skillcode/8/ITSP"]
    ress = g.query("select ?skillLevel where {skills:ISCO skills:definedAtLevel ?skillLevel} order by ?skillLevel")
    assert [str(res.skillLevel) for res in ress] == ["https://sfia-online.org/en/skill-levels/8/ISCO_6",
                                                     "https://sfia-online.org/en/skill-levels/8/ISCO_7"]
