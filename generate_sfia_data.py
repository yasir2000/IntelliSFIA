"""
Simple SFIA 9 Data Generator for Ollama Integration Demo
=======================================================

This script creates minimal SFIA 9 data files in JSON format
for use with the IntelliSFIA + Ollama integration.

This is a simplified version that includes core SFIA skills
most relevant for software development roles.
"""

import json
from pathlib import Path

def create_sfia_skills_data():
    """Create basic SFIA skills data for demo"""
    skills_data = [
        {
            "code": "PROG",
            "title": "Programming/software development",
            "description": "The planning, design, creation, amendment, verification, testing and documentation of new and amended software components from supplied specifications in accordance with agreed standards.",
            "levels": [
                {
                    "level": 1,
                    "description": "Uses development tools and programming languages to develop simple programs and software components. Performs standard tests on software components."
                },
                {
                    "level": 2, 
                    "description": "Designs, codes, verifies, tests, documents, amends and refactors simple programs and scripts. Applies agreed standards and tools to achieve a well-engineered result."
                },
                {
                    "level": 3,
                    "description": "Designs, codes, verifies, tests, documents, amends and refactors moderately complex programs and scripts. Applies agreed standards and tools to achieve a well-engineered result."
                },
                {
                    "level": 4,
                    "description": "Designs, codes, verifies, tests, documents, amends and refactors programs and scripts of significant complexity. Collaborates in reviews of specifications and uses these to design, code and test software."
                },
                {
                    "level": 5,
                    "description": "Takes technical responsibility for programming and software development activities. Plans and leads programming tasks. Influences the design of software components."
                },
                {
                    "level": 6,
                    "description": "Takes overall responsibility for software development and programming activities within a significant development programme."
                }
            ]
        },
        {
            "code": "ARCH",
            "title": "Solution architecture",
            "description": "The design and communication of high-level structures to enable and guide the design and development of integrated information and technology solutions.",
            "levels": [
                {
                    "level": 3,
                    "description": "Assists with the design of components of solution architectures consistent with agreed enterprise and solution architecture standards, policies and approaches."
                },
                {
                    "level": 4,
                    "description": "Designs components of larger solutions and ensures design consistency across projects."
                },
                {
                    "level": 5,
                    "description": "Designs solutions comprising multiple architectural components, ensures design consistency and coordinates design activities across multiple teams."
                },
                {
                    "level": 6,
                    "description": "Takes responsibility for the development and integrity of a solution architecture and contributes to enterprise architecture."
                },
                {
                    "level": 7,
                    "description": "Takes overall responsibility for the integrity and evolution of solution architectures within a significant programme or organisation."
                }
            ]
        },
        {
            "code": "RLMT",
            "title": "Relationship management",  
            "description": "The identification, analysis, management and monitoring of relationships with and between stakeholders.",
            "levels": [
                {
                    "level": 3,
                    "description": "Contributes to relationship building activities. Collects feedback from stakeholders."
                },
                {
                    "level": 4,
                    "description": "Builds and maintains effective working relationships with stakeholders. Facilitates collaboration between different groups."
                },
                {
                    "level": 5,
                    "description": "Builds, manages and maintains strategic relationships with stakeholders. Influences stakeholder decisions."
                },
                {
                    "level": 6,
                    "description": "Develops long-term strategic relationships. Creates frameworks for stakeholder engagement."
                }
            ]
        },
        {
            "code": "REQM",
            "title": "Requirements definition and management",
            "description": "The elicitation, analysis, specification, validation and management of requirements.",
            "levels": [
                {
                    "level": 2,
                    "description": "Assists with requirements elicitation and documentation under guidance."
                },
                {
                    "level": 3,
                    "description": "Investigates, defines and documents requirements for moderately complex systems."
                },
                {
                    "level": 4,
                    "description": "Facilitates requirements workshops and manages complex requirements."
                },
                {
                    "level": 5,
                    "description": "Takes responsibility for requirements management across multiple projects."
                }
            ]
        },
        {
            "code": "TEST",
            "title": "Testing",
            "description": "The planning, design, management, execution and reporting of tests using appropriate testing tools and techniques.",
            "levels": [
                {
                    "level": 1,
                    "description": "Executes test scripts under supervision."
                },
                {
                    "level": 2,
                    "description": "Designs test conditions and creates test scripts and test data."
                },
                {
                    "level": 3,
                    "description": "Reviews requirements and specifies test conditions. Creates test scripts and test data."
                },
                {
                    "level": 4,
                    "description": "Plans and manages testing activities. Creates test strategy and manages test teams."
                },
                {
                    "level": 5,
                    "description": "Takes responsibility for testing strategy and test management across multiple projects."
                }
            ]
        },
        {
            "code": "DTAN",
            "title": "Data analysis",
            "description": "The investigation, evaluation, interpretation and classification of data.",
            "levels": [
                {
                    "level": 2,
                    "description": "Uses standard techniques to analyse data. Presents findings clearly."
                },
                {
                    "level": 3,
                    "description": "Investigates data requirements and sources. Applies analytical techniques."
                },
                {
                    "level": 4,
                    "description": "Plans and manages data analysis activities. Designs analytical approaches."
                },
                {
                    "level": 5,
                    "description": "Takes responsibility for data analysis strategy across the organisation."
                }
            ]
        },
        {
            "code": "PROV",
            "title": "Service provisioning",
            "description": "The provision of services to enable operation of products and systems.",
            "levels": [
                {
                    "level": 1,
                    "description": "Assists with basic service provisioning tasks under supervision."
                },
                {
                    "level": 2,
                    "description": "Provisions standard services using established procedures."
                },
                {
                    "level": 3,
                    "description": "Provisions complex services and resolves provisioning issues."
                },
                {
                    "level": 4,
                    "description": "Plans and manages service provisioning activities."
                }
            ]
        }
    ]
    
    return skills_data

def create_sfia_attributes_data():
    """Create basic SFIA attributes data for demo"""
    attributes_data = [
        {
            "code": "AUTC",
            "title": "Autonomy",
            "description": "The ability to work independently and take responsibility for decisions."
        },
        {
            "code": "INFC", 
            "title": "Influence",
            "description": "The ability to persuade others and gain commitment to proposals."
        },
        {
            "code": "CMPLX",
            "title": "Complexity",
            "description": "The ability to work with complex, ambiguous or contradictory situations."
        },
        {
            "code": "KNOW",
            "title": "Knowledge",
            "description": "The knowledge and experience needed to perform effectively."
        },
        {
            "code": "BUS_KNOW",
            "title": "Business knowledge",
            "description": "Understanding of the business context and commercial aspects."
        }
    ]
    
    return attributes_data

def create_sfia_levels_data():
    """Create basic SFIA levels data for demo"""
    levels_data = [
        {
            "level": 1,
            "title": "Follow",
            "description": "Works under close direction. Uses little discretion."
        },
        {
            "level": 2,
            "title": "Assist", 
            "description": "Works under general direction. Uses limited discretion."
        },
        {
            "level": 3,
            "title": "Apply",
            "description": "Works under broad direction. Uses discretion in identifying and responding to complex issues."
        },
        {
            "level": 4,
            "title": "Enable",
            "description": "Works under general direction within a clear framework. Influences others."
        },
        {
            "level": 5,
            "title": "Ensure/Advise",
            "description": "Works under broad direction. Has significant influence over the allocation of resources."
        },
        {
            "level": 6,
            "title": "Initiate/Influence",
            "description": "Determines policy and strategy. Has very significant influence."
        },
        {
            "level": 7,
            "title": "Set strategy/Inspire",
            "description": "Has ultimate responsibility for strategy. Influences industry leaders."
        }
    ]
    
    return levels_data

def main():
    """Generate SFIA data files for Ollama integration demo"""
    
    print("🔧 Generating SFIA 9 Data for Ollama Integration...")
    
    # Create data
    skills_data = create_sfia_skills_data()
    attributes_data = create_sfia_attributes_data()
    levels_data = create_sfia_levels_data()
    
    # Write JSON files
    with open('sfia9_skills.json', 'w', encoding='utf-8') as f:
        json.dump(skills_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created sfia9_skills.json ({len(skills_data)} skills)")
    
    with open('sfia9_attributes.json', 'w', encoding='utf-8') as f:
        json.dump(attributes_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created sfia9_attributes.json ({len(attributes_data)} attributes)")
    
    with open('sfia9_levels.json', 'w', encoding='utf-8') as f:
        json.dump(levels_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created sfia9_levels.json ({len(levels_data)} levels)")
    
    print("\n🚀 SFIA data generation complete!")
    print("   Files ready for Ollama integration demo")
    print("   Run: python demo_ollama_integration.py")

if __name__ == "__main__":
    main()