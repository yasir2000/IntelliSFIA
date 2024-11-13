import csv
import os

import pytest
from rdflib import Graph

from sfia_rdf import namespaces
from sfia_rdf.parsers import levels_parser


@pytest.fixture
def attributes_graph():
    g = Graph()
    namespaces.bind_namespaces(g)
    with open(os.path.dirname(__file__) + "/test_files/levels_test.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        triples = levels_parser.parse_levels_table([row for row in reader])
        [g.add(triple) for triple in triples]
    return g


def test_properties(attributes_graph):
    ress = attributes_graph.query("""
    select ?level
    where {
        ?level a sfia:Level
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


def test_levels_assertion(attributes_graph):
    ress = attributes_graph.query("""
    select ?level ?essence
    where {
        ?level sfia:levelEssence ?essence
    }
    order by ?level
    """)
    assert [str(res.essence) for res in ress] == [
        "Performs routine tasks",
        "Provides assistance",
        "Performs varied tasks",
        "Performs diverse activities",
        "Provides guidance.",
        "Has organisational influence.",
        "Operates at the highest organisational level.",
    ]
