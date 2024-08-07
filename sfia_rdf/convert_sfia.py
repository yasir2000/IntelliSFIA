import csv
import os

from rdflib import Graph

from sfia_rdf import namespaces, sfia_parser

SFIA_SPREADSHEET = os.path.expanduser('~') + "/Desktop/SFIA/sfia-8_en_220221.csv"
OUTPUT = os.path.expanduser('~') + "/Desktop/SFIA/SFIA.ttl"

sfia_graph = Graph()
namespaces.bind_namespaces(sfia_graph)
sfia_graph.parse(f"{os.path.dirname(__file__)}/levels_of_responsibility.ttl")

sfia_graph.update(""" 
INSERT DATA {

    categories:CategoryScheme a skos:ConceptScheme;
                rdfs:label "Categories Scheme"@en.
    categories:Category rdfs:subClassOf skos:Concept;
                skos:prefLabel "Category"@en.

    skills:Skill a owl:Class;
                rdfs:label "Skill"@en.

    skills:definedAtLevel a owl:ObjectProperty;
                        rdfs:domain skills:Skill;
                        rdfs:range skills_levels:SkillLevel;
                        rdfs:label "defined at level"@en.
    
    skills:description a owl:AnnotationProperty;
                    rdfs:domain skills:Skill;
                    rdfs:label "has overall description"@en.
    
    skills:notes a owl:AnnotationProperty;
                    rdfs:domain skills:Skill;
                    rdfs:label "notes"@en.
    
    skills:category a owl:ObjectProperty;
                    rdfs:domain skills:Skill;
                    rdfs:range categories:Category;
                    rdfs:label "has category"@en.
    
    skills_levels:SkillLevel a owl:Class;
                rdfs:label "Skill Level"@en.
    
    skills_levels:level a owl:ObjectProperty;
                rdfs:domain skills_levels:SkillLevel;
                rdfs:range levels:LevelOfResponsibility;
                rdfs:label "has level"@en.
                
    skills_levels:notes a owl:AnnotationProperty;
                rdfs:domain skills_levels:SkillLevel;
                rdfs:label "has guidance notes"@en.
}
""")

with open(SFIA_SPREADSHEET) as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        row_triples = sfia_parser.parse_row(row)
        [sfia_graph.add(triple) for triple in row_triples]

query = """
    INSERT {
         categories:CategoryScheme skos:hasTopConcept ?concept.
    }
    WHERE {
        ?concept a skos:Concept.
        filter not exists { ?concept skos:broader ?broaderConcept. }
    }
"""
sfia_graph.update(query)

sfia_graph.serialize(OUTPUT)
