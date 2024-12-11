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


def test_levels(attributes_graph):
    ress = attributes_graph.query("""
    select ?level
    where {
        ?level a sfia:Level
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


def test_levels_url(attributes_graph):
    ress = attributes_graph.query("""
    select ?url
    where {
        ?level a sfia:Level;
            sfia:url ?url
    }
    order by ?url
    """)
    lor_url = "https://sfia-online.org/en/lor/9/"
    assert [str(res.url) for res in ress] == [
        f"{lor_url}1",
        f"{lor_url}2",
        f"{lor_url}3",
        f"{lor_url}4",
        f"{lor_url}5",
        f"{lor_url}6",
        f"{lor_url}7",
    ]


def test_levels_essences(attributes_graph):
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
    assert all([res.essence.language == 'en' for res in ress])
