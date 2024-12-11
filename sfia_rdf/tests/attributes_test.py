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


def test_attribute(attributes_graph):
    ress = attributes_graph.query("""
    select ?attribute
    where {
        ?attribute a owl:AnnotationProperty
    }
    order by ?attribute
    """)
    assert [str(res.attribute) for res in ress] == ["https://rdf.sfia-online.org/9/attributes/AUTO"]


def test_levels_assertion(attributes_graph):
    ress = attributes_graph.query("""
    select ?level ?autonomy
    where {
        ?level attributes:AUTO ?autonomy
    }
    order by ?level
    """)
    lor_namespace = "https://rdf.sfia-online.org/9/lor/"
    assert [str(res.level) for res in ress] == [
        f"{lor_namespace}1",
        f"{lor_namespace}2",
        f"{lor_namespace}3",
        f"{lor_namespace}4",
        f"{lor_namespace}5",
        f"{lor_namespace}6",
        f"{lor_namespace}7",
    ]
    assert [str(res.autonomy) for res in ress][0].startswith("Follows instructions")
