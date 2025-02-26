import csv
import os

from rdflib import Graph

from sfia_rdf import namespaces
from sfia_rdf.parsers import skills_parser, levels_parser, attributes_parser

SFIA_SKILLS_SHEET = os.path.expanduser('~') + "/Desktop/SFIA/sfia-9_current-standard_en_241029_SKILLS.csv"
SFIA_ATTRIBUTES_SHEET = os.path.expanduser('~') + "/Desktop/SFIA/sfia-9_current-standard_en_241029_ATTRIBUTES.csv"
SFIA_LEVELS_SHEET = os.path.expanduser('~') + "/Desktop/SFIA/sfia-9_current-standard_en_241029_LEVELS.csv"

OUTPUT = os.path.expanduser('~') + "/Desktop/SFIA/SFIA.ttl"

DELIMITER = ","
QUOTE_CHAR = '"'

sfia_graph = Graph()
namespaces.bind_namespaces(sfia_graph)

sfia_graph.update(""" 
INSERT DATA {
    
    ##
    ## Classes
    ##

    sfia:CategoryScheme a skos:ConceptScheme;
                rdfs:label "Scheme for the Skills' Categories"@en.
                
    sfia:Category rdfs:subClassOf skos:Concept;
                skos:prefLabel "Category"@en.

    sfia:LorScheme a skos:ConceptScheme;
                rdfs:label "Scheme for the Levels of Responsibility"@en.
                
    sfia:Level a owl:Class;
                rdfs:subClassOf skos:Concept;
                rdfs:label "Level of Responsibility"@en.

    sfia:Skill a owl:Class;
                rdfs:label "Skill"@en.

    sfia:SkillLevel a owl:Class;
                rdfs:label "Skill Level"@en.
    

    
    ##
    ## Object Properties
    ##

    sfia:skillCategory a owl:ObjectProperty;
                    rdfs:domain sfia:Skill;
                    rdfs:range sfia:Category;
                    rdfs:label "has category"@en.
    
    sfia:definedAtLevel a owl:ObjectProperty;
                        rdfs:domain sfia:Skill;
                        rdfs:range sfia:SkillLevel;
                        rdfs:label "defined at level"@en.
    
    sfia:level a owl:ObjectProperty;
                rdfs:domain sfia:SkillLevel;
                rdfs:range sfia:Level;
                rdfs:label "has level"@en.
                
    
    ##
    ## Annotation Properties
    ##
    
    sfia:skillDescription a owl:AnnotationProperty;
                    rdfs:domain sfia:Skill;
                    rdfs:label "has overall description"@en.
    
    sfia:skillNotes a owl:AnnotationProperty;
                    rdfs:domain sfia:Skill;
                    rdfs:label "notes"@en.
                     
    sfia:skillLevelDescription a owl:AnnotationProperty;
                rdfs:domain sfia:SkillLevel;
                rdfs:label "has skill-level description"@en.
    
    sfia:attributeType a owl:AnnotationProperty;
                rdfs:domain owl:AnnotationProperty;
                rdfs:label "has attribute type"@en.
                
    sfia:attributeGuidanceNotes a owl:AnnotationProperty;
                rdfs:domain owl:AnnotationProperty;
                rdfs:label "has guidance notes"@en.
    
    sfia:levelGuidingPhrase a owl:AnnotationProperty;
            rdfs:domain owl:Level;
            rdfs:label "has guiding phrase"@en.
    
    sfia:levelEssence a owl:AnnotationProperty;
            rdfs:domain owl:Level;
            rdfs:label "essence of the level"@en.
    
    ###
    ### Plus, every SFIA attribute becomes a property (AUTO, ADAP, COLL, COMM, etc.)
    
}
""")

with open(SFIA_ATTRIBUTES_SHEET) as csvfile:
    reader = csv.reader(csvfile, delimiter=DELIMITER, quotechar=QUOTE_CHAR)
    for row in reader:
        row_triples = attributes_parser.parse_row(row)
        [sfia_graph.add(triple) for triple in row_triples]

with open(SFIA_LEVELS_SHEET) as csvfile:
    reader = csv.reader(csvfile, delimiter=DELIMITER, quotechar=QUOTE_CHAR)
    row_triples = levels_parser.parse_levels_table([row for row in reader])
    [sfia_graph.add(triple) for triple in row_triples]

with open(SFIA_SKILLS_SHEET) as csvfile:
    reader = csv.reader(csvfile, delimiter=DELIMITER, quotechar=QUOTE_CHAR)
    for row in reader:
        row_triples = skills_parser.parse_row(row)
        [sfia_graph.add(triple) for triple in row_triples]
    query = """
        INSERT {
             sfia:CategoryScheme skos:hasTopConcept ?concept.
        }
        WHERE {
            ?concept a sfia:Category.
            filter not exists { ?concept skos:broader ?broaderConcept. }
        }
    """
    sfia_graph.update(query)

sfia_graph.serialize(OUTPUT)
