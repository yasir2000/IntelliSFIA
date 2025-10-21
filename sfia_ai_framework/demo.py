#!/usr/bin/env python3
"""
SFIA AI Framework - Quick Start Demo

This script demonstrates the key capabilities of the SFIA AI Framework
with a comprehensive example showing all major features.
"""

import asyncio
import json
import os
from datetime import datetime

# Add the framework to Python path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig, SFIASDKContext
from sfia_ai_framework.examples.scenarios import SFIAScenarios


async def demo_basic_functionality():
    """Demonstrate basic SFIA AI Framework functionality"""
    
    print("🧠 SFIA AI Framework - Quick Start Demo")
    print("=" * 50)
    
    # Configuration (adjust these values for your environment)
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",  # Change this to your Neo4j password
        openai_api_key=None,  # Add your OpenAI key here for agent features
        enable_agents=True,   # Set to False if no OpenAI key
        enable_reasoning=True,
        log_level="INFO"
    )
    
    print(f"📋 Configuration:")
    print(f"   Neo4j URI: {config.neo4j_uri}")
    print(f"   Agents Enabled: {config.enable_agents}")
    print(f"   Reasoning Enabled: {config.enable_reasoning}")
    print()
    
    try:
        # Use SDK with context manager for proper cleanup
        async with SFIASDKContext(config) as sdk:
            print("✅ SDK initialized successfully!")
            print()
            
            # 1. Load SFIA Ontology (optional - comment out if no RDF file available)
            print("📊 Loading SFIA Ontology...")
            try:
                # Try to load the RDF file if it exists
                rdf_file = "../SFIA_9_2025-10-21.ttl"
                if os.path.exists(rdf_file):
                    await sdk.load_sfia_ontology(rdf_file)
                    print("✅ SFIA ontology loaded successfully!")
                else:
                    print("ℹ️  SFIA RDF file not found, using default knowledge graph")
            except Exception as e:
                print(f"⚠️  Could not load RDF file: {e}")
            print()
            
            # 2. Query Skills
            print("🔍 Querying Skills...")
            skills_result = await sdk.query_skills(keyword="programming")
            print(f"✅ Found {skills_result.get('count', 0)} programming-related skills")
            
            if skills_result.get('skills'):
                for skill in skills_result['skills'][:3]:  # Show first 3
                    print(f"   • {skill.get('skill_name', 'Unknown skill')}")
            print()
            
            # 3. Analyze Skill Gaps
            print("📈 Analyzing Skill Gaps...")
            gap_analysis = await sdk.analyze_skill_gaps(
                current_role="Junior Developer",
                target_role="Senior Developer"
            )
            
            if gap_analysis.get('success'):
                gaps = gap_analysis.get('skill_gaps', [])
                print(f"✅ Identified {len(gaps)} skill gaps")
                for gap in gaps[:3]:  # Show first 3
                    if isinstance(gap, dict):
                        print(f"   • {gap.get('skill_code', 'Unknown')}: {gap.get('description', 'No description')}")
            else:
                print(f"⚠️  Gap analysis unavailable: {gap_analysis.get('error', 'Unknown error')}")
            print()
            
            # 4. Generate Development Plan
            print("🎯 Generating Development Plan...")
            person_profile = {
                "name": "Demo User",
                "current_role": "Junior Developer",
                "current_skills": ["PROG", "TEST"],
                "experience_years": 2,
                "career_aspirations": ["Senior Developer"],
                "learning_preferences": ["online_courses", "hands_on_projects"],
                "time_availability": "10 hours per week"
            }
            
            dev_plan = await sdk.generate_development_plan(
                person_profile, 
                "Senior Developer"
            )
            
            if dev_plan.get('success'):
                print("✅ Development plan generated!")
                timeline = dev_plan.get('timeline', {})
                for phase, description in timeline.items():
                    print(f"   • {phase.replace('_', ' ').title()}: {description}")
            else:
                print(f"⚠️  Development plan unavailable: {dev_plan.get('error', 'Unknown error')}")
            print()
            
            # 5. Knowledge Graph Statistics
            print("📊 Knowledge Graph Statistics...")
            stats = await sdk.get_knowledge_graph_statistics()
            
            if stats.get('success'):
                basic_stats = stats.get('basic_stats', {})
                print("✅ Knowledge graph statistics:")
                print(f"   • Skills: {basic_stats.get('skills_count', 0)}")
                print(f"   • Levels: {basic_stats.get('levels_count', 0)}")
                print(f"   • Categories: {basic_stats.get('categories_count', 0)}")
                print(f"   • Relationships: {basic_stats.get('relationships_count', 0)}")
            else:
                print(f"⚠️  Statistics unavailable: {stats.get('error', 'Unknown error')}")
            print()
            
            # 6. Run a Complete Scenario (if time permits)
            print("🎭 Running Complete Scenario Demo...")
            try:
                scenarios = SFIAScenarios(sdk)
                
                # Run hiring optimization scenario
                print("   Running hiring optimization scenario...")
                hiring_result = await scenarios.hiring_optimization_scenario()
                
                if hiring_result:
                    recommendations = hiring_result.get('recommendations', [])
                    print(f"   ✅ Generated {len(recommendations)} hiring recommendations")
                    
                    for rec in recommendations[:2]:  # Show first 2
                        print(f"      • {rec.get('position', 'Unknown')}: {rec.get('recommended_candidate', 'None')}")
                
            except Exception as e:
                print(f"   ⚠️  Scenario demo unavailable: {e}")
            print()
            
            # 7. Generate Visualization (optional)
            print("🎨 Generating Visualization...")
            try:
                viz_result = await sdk.visualize_knowledge_graph("demo_knowledge_graph.html")
                if viz_result.get('success'):
                    print(f"✅ Visualization saved: {viz_result.get('visualization_file')}")
                    print("   Open the HTML file in your browser to explore the knowledge graph!")
                else:
                    print(f"⚠️  Visualization unavailable: {viz_result.get('error')}")
            except Exception as e:
                print(f"⚠️  Visualization error: {e}")
            print()
            
            print("🎉 Demo completed successfully!")
            print()
            print("🚀 Next Steps:")
            print("   1. Install Neo4j and configure connection details")
            print("   2. Add your OpenAI API key for full agent capabilities")
            print("   3. Load your SFIA RDF data for complete functionality")
            print("   4. Run the web applications:")
            print("      • Streamlit: streamlit run sfia_ai_framework/web/app.py")
            print("      • FastAPI: uvicorn sfia_ai_framework.web.api:app --reload")
            print("   5. Explore the comprehensive scenarios in examples/scenarios.py")
            print()
            print("📚 Documentation: Check README.md for detailed instructions")
            print("🔧 API Docs: http://localhost:8000/docs (when FastAPI is running)")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print()
        print("🔧 Troubleshooting:")
        print("   • Ensure Neo4j is running and accessible")
        print("   • Check your Neo4j credentials")
        print("   • Install all required dependencies: pip install -r requirements.txt")
        print("   • For agent features, provide a valid OpenAI API key")


def demo_sdk_without_external_services():
    """Demonstrate SDK capabilities without external services"""
    
    print("🧠 SFIA AI Framework - Offline Demo")
    print("=" * 40)
    
    print("📋 This demo shows framework capabilities without external services:")
    print()
    
    # Test data models
    print("1. Data Models Demo:")
    from sfia_ai_framework.models.sfia_models import Skill, ProfessionalRole, APIResponse
    
    # Create sample skill
    skill = Skill(
        skill_code="PROG",
        skill_name="Programming/software development",
        category="Development and implementation",
        subcategory="Systems development",
        description="The planning, designing, creation, amendment, verification, testing and documentation of new and amended software components from supplied specifications in accordance with agreed standards."
    )
    
    print(f"   ✅ Created skill: {skill.skill_name}")
    print(f"      Code: {skill.skill_code}")
    print(f"      Category: {skill.category}")
    
    # Create sample role
    role = ProfessionalRole(
        role_code="DEV001",
        role_title="Software Developer",
        role_description="Develops and maintains software applications",
        required_skills=[
            {"skill_code": "PROG", "minimum_level": 3},
            {"skill_code": "SENG", "minimum_level": 2},
            {"skill_code": "TEST", "minimum_level": 2}
        ],
        experience_level="Intermediate",
        responsibility_level=3
    )
    
    print(f"   ✅ Created role: {role.role_title}")
    print(f"      Required skills: {len(role.required_skills)}")
    print(f"      Responsibility level: {role.responsibility_level}")
    print()
    
    # Test API response
    print("2. API Response Demo:")
    success_response = APIResponse(message="Operation completed successfully")
    error_response = APIResponse(success=False, message="Operation failed", error="Connection timeout")
    
    print(f"   ✅ Success response: {success_response.message}")
    print(f"   ❌ Error response: {error_response.error}")
    print()
    
    # Test configuration
    print("3. Configuration Demo:")
    from sfia_ai_framework.sdk import SFIASDKConfig
    
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687",
        enable_agents=False,  # Disabled for offline demo
        enable_reasoning=True,
        log_level="INFO"
    )
    
    print(f"   ✅ Configuration created")
    print(f"      Neo4j URI: {config.neo4j_uri}")
    print(f"      Agents enabled: {config.enable_agents}")
    print(f"      Reasoning enabled: {config.enable_reasoning}")
    print()
    
    print("4. Framework Structure:")
    print("   ✅ Core Components:")
    print("      • Multi-agent system (agents.py)")
    print("      • Knowledge graph (knowledge_graph.py)")
    print("      • Reasoning engine (reasoning.py)")
    print("   ✅ SDK Layer:")
    print("      • Unified interface (sdk/__init__.py)")
    print("      • Easy integration")
    print("   ✅ Web Applications:")
    print("      • Streamlit dashboard (web/app.py)")
    print("      • FastAPI REST API (web/api.py)")
    print("   ✅ Real-world Scenarios:")
    print("      • Hiring optimization")
    print("      • Career development")
    print("      • Team formation")
    print("      • Organizational assessment")
    print()
    
    print("🎉 Offline demo completed!")
    print()
    print("🚀 To run the full demo with external services:")
    print("   python demo.py")


async def main():
    """Main demo function"""
    
    print("Welcome to the SFIA AI Framework Demo!")
    print()
    print("Choose demo mode:")
    print("1. Full demo (requires Neo4j)")
    print("2. Offline demo (no external services)")
    print()
    
    try:
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            await demo_basic_functionality()
        elif choice == "2":
            demo_sdk_without_external_services()
        else:
            print("Invalid choice. Running offline demo...")
            demo_sdk_without_external_services()
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nDemo error: {e}")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())