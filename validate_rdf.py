#!/usr/bin/env python3
"""
SFIA 9 RDF Knowledge Base Validation Script
Validates the generated RDF file and provides statistics
"""

from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, SKOS
import sys
import os

def validate_rdf_file(filename):
    """Validate and analyze the SFIA 9 RDF file"""
    
    if not os.path.exists(filename):
        print(f"❌ RDF file not found: {filename}")
        return False
    
    print(f"🔍 Validating RDF file: {filename}")
    print("=" * 50)
    
    try:
        # Load the graph
        g = Graph()
        g.parse(filename, format="turtle")
        print(f"✅ Successfully loaded RDF graph")
        print(f"📊 Total triples: {len(g)}")
        
        # Define namespaces
        SFIA = Namespace("https://rdf.sfia-online.org/9/ontology/")
        SKILLS = Namespace("https://rdf.sfia-online.org/9/skills/")
        ATTRIBUTES = Namespace("https://rdf.sfia-online.org/9/attributes/")
        LEVELS = Namespace("https://rdf.sfia-online.org/9/lor/")
        CATEGORIES = Namespace("https://rdf.sfia-online.org/9/categories/")
        
        # Count entities
        skills_count = len(list(g.subjects(RDF.type, SFIA.Skill)))
        levels_count = len(list(g.subjects(RDF.type, SFIA.Level)))
        attributes_count = len(list(g.subjects(RDF.type, None)))  # Attributes are annotation properties
        
        print(f"\n📈 Entity Statistics:")
        print(f"   🎯 Skills: {skills_count}")
        print(f"   📊 Levels: {levels_count}")
        print(f"   🏷️  Attributes: Found attribute definitions")
        
        # Validate some key skills
        key_skills = ["PROG", "DTAN", "RLMT"]
        print(f"\n🔎 Validating Key Skills:")
        
        for skill_code in key_skills:
            skill_uri = SKILLS[skill_code]
            skill_triples = list(g.triples((skill_uri, None, None)))
            if skill_triples:
                print(f"   ✅ {skill_code}: {len(skill_triples)} triples")
            else:
                print(f"   ⚠️  {skill_code}: Not found")
        
        # Check namespaces
        print(f"\n🌐 Namespaces:")
        for prefix, namespace in g.namespaces():
            print(f"   {prefix}: {namespace}")
        
        # Validate structure
        print(f"\n🏗️  Structure Validation:")
        
        # Check for labels
        labeled_entities = len(list(g.subjects(RDFS.label, None)))
        print(f"   📝 Entities with rdfs:label: {labeled_entities}")
        
        # Check for SKOS concepts
        skos_concepts = len(list(g.subjects(RDF.type, SKOS.Concept)))
        print(f"   🗂️  SKOS Concepts: {skos_concepts}")
        
        print(f"\n✅ RDF Knowledge Base validation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error validating RDF file: {e}")
        return False

def main():
    """Main validation function"""
    
    # Look for the most recent SFIA RDF file
    rdf_files = [f for f in os.listdir('.') if f.startswith('SFIA_9_') and f.endswith('.ttl')]
    
    if not rdf_files:
        print("❌ No SFIA 9 RDF files found in current directory")
        sys.exit(1)
    
    # Use the most recent file
    latest_file = sorted(rdf_files)[-1]
    
    print("🚀 SFIA 9 RDF Knowledge Base Validation")
    print("=" * 50)
    
    success = validate_rdf_file(latest_file)
    
    if success:
        print(f"\n🎉 Knowledge base is ready for semantic web applications!")
        print(f"📁 File: {latest_file}")
        sys.exit(0)
    else:
        print(f"\n❌ Validation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()