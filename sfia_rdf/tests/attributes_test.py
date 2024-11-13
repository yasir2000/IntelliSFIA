import csv
import os

import pytest
from rdflib import Graph

from sfia_rdf import namespaces
from sfia_rdf.parsers import attributes_parser


@pytest.fixture
def attributes_graph():
    g = Graph()
    namespaces.bind_namespaces(g)
    with open(os.path.dirname(__file__) + "/test_files/attributes_test.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        reader.__next__()  # skip header
        for row in reader:
            triples = attributes_parser.parse_row(row)
            [g.add(triple) for triple in triples]
    return g


def test_properties(attributes_graph):
    ress = attributes_graph.query("""
    select ?attribute
    where {
        ?attribute a owl:AnnotationProperty
    }
    order by ?attribute
    """)
    assert [str(res.attribute) for res in ress] == ["https://sfia-online.org/en/shortcode/9/AUTO"]


def test_levels_assertion(attributes_graph):
    ress = attributes_graph.query("""
    select ?level ?autonomy
    where {
        ?level attributes:AUTO ?autonomy
    }
    order by ?level
    """)
    assert [str(res.level) for res in ress] == [
        "https://sfia-online.org/en/lor/9/1",
        "https://sfia-online.org/en/lor/9/2",
        "https://sfia-online.org/en/lor/9/3",
        "https://sfia-online.org/en/lor/9/4",
        "https://sfia-online.org/en/lor/9/5",
        "https://sfia-online.org/en/lor/9/6",
        "https://sfia-online.org/en/lor/9/7",
    ]
    assert [str(res.autonomy) for res in ress][0].startswith("Follows instructions")
