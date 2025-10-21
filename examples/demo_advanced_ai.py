"""
Enhanced Demo: IntelliSFIA CrewAI Multi-Agent + Semantic Ontology System
=======================================================================

This demo showcases the advanced capabilities of IntelliSFIA enhanced with:
1. CrewAI Multi-Agent System (5 specialized agents)
2. SFIA Semantic Ontology and Knowledge Base
3. RDF/SPARQL reasoning and inference
4. Collaborative AI assessment workflow

Agents:
- SFIA Expert Agent: Deep SFIA framework knowledge
- Career Advisor Agent: Strategic career guidance  
- Evidence Analyst Agent: Validates evidence quality
- Semantic Reasoner Agent: Ontology-based inference
- Report Generator Agent: Synthesizes comprehensive reports

Technologies:
- CrewAI: Multi-agent orchestration
- RDFLib: Semantic web and ontologies
- SPARQL: Knowledge base queries
- OWL: Ontological reasoning
- Ollama: Local LLM integration
"""

import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def check_advanced_prerequisites():
    """Check if advanced libraries are available."""
    missing_libs = []
    
    try:
        import crewai
        print("✅ CrewAI available")
    except ImportError:
        missing_libs.append("CrewAI")
        print("❌ CrewAI not available")
    
    try:
        import rdflib
        print("✅ RDFLib (semantic web) available")
    except ImportError:
        missing_libs.append("RDFLib")
        print("❌ RDFLib not available")
    
    try:
        import owlrl
        print("✅ OWL-RL (reasoning) available")
    except ImportError:
        missing_libs.append("OWL-RL")
        print("❌ OWL-RL not available")
    
    if missing_libs:
        print(f"\n🔧 Install missing libraries:")
        print(f"   pip install -r requirements-crewai.txt")
        return False
    
    return True

def demo_basic_vs_advanced():
    """Compare basic single-agent vs advanced multi-agent assessment."""
    
    print("\n" + "="*70)
    print("🔬 COMPARISON: Basic vs Advanced AI Assessment")
    print("="*70)
    
    # Evidence for comparison
    evidence = """
    Senior Software Engineer with 5 years experience:
    - Led architecture redesign of core platform (microservices)
    - Managed team of 6 developers across 3 projects
    - Implemented DevOps practices reducing deployment time by 70%
    - Designed and delivered RESTful APIs serving 1M+ requests/day
    - Mentored junior developers and conducted technical interviews
    - Collaborated with product and business stakeholders on requirements
    - Presented technical solutions to C-level executives
    """
    
    context = "Assessment for Principal Engineer promotion"
    skill_code = "PROG"
    
    print(f"\n📋 Assessment Scenario:")
    print(f"   Skill: {skill_code} (Programming/Software Development)")
    print(f"   Context: {context}")
    print(f"   Evidence: Senior engineer with 5 years experience...")
    
    # Basic Assessment (Single Agent)
    print(f"\n🤖 BASIC ASSESSMENT (Single Agent)")
    print(f"   Method: Single LLM + SFIA data")
    print(f"   Processing: Simple prompt-response")
    
    try:
        from ollama_service import OllamaService, OllamaConfig, IntelliSFIAAgent
        
        config = OllamaConfig(model="deepseek-coder:latest", temperature=0.3)
        ollama = OllamaService(config)
        basic_agent = IntelliSFIAAgent(ollama)
        
        if ollama.is_available():
            basic_result = basic_agent.assess_skill_level(skill_code, evidence, context)
            print(f"   ✅ Basic assessment completed")
            print(f"   📊 Result: Level {basic_result.get('recommended_level', 'N/A')}")
            print(f"   🎯 Confidence: {basic_result.get('confidence', 'N/A')}%")
        else:
            print(f"   ❌ Ollama not available for basic assessment")
            
    except Exception as e:
        print(f"   ❌ Basic assessment error: {e}")
    
    # Advanced Assessment (Multi-Agent + Semantic)
    print(f"\n🧠 ADVANCED ASSESSMENT (Multi-Agent + Semantic)")
    print(f"   Method: 5 specialized agents + SFIA ontology")
    print(f"   Processing: Collaborative workflow + semantic reasoning")
    
    try:
        from crewai_multi_agent import create_crewai_system
        
        crewai_system = create_crewai_system()
        if crewai_system:
            print(f"   ✅ Multi-agent system initialized")
            print(f"   🤝 Agents: {list(crewai_system.agents.keys())}")
            print(f"   🧬 Ontology: {len(crewai_system.ontology.graph)} triples")
            print(f"   🔍 Semantic reasoning: {'Enabled' if crewai_system.semantic_config.enable_inference else 'Disabled'}")
            
            # Perform multi-agent assessment
            print(f"\n   🚀 Starting collaborative assessment...")
            advanced_result = crewai_system.assess_skill_with_crew(skill_code, evidence, context)
            
            if 'error' not in advanced_result:
                print(f"   ✅ Multi-agent assessment completed")
                print(f"   👥 Agents involved: {len(advanced_result.get('agents_involved', []))}")
                print(f"   🧬 Semantic analysis: {advanced_result.get('semantic_analysis', 'N/A')}")
                print(f"   📋 Evidence validation: {advanced_result.get('evidence_validation', 'N/A')}")
                print(f"   🎓 Expert assessment: {advanced_result.get('expert_assessment', 'N/A')}")
                print(f"   🚀 Career guidance: {advanced_result.get('career_guidance', 'N/A')}")
            else:
                print(f"   ❌ Multi-agent assessment failed: {advanced_result.get('error')}")
        else:
            print(f"   ❌ Could not create multi-agent system")
            
    except ImportError as e:
        print(f"   ❌ Advanced libraries not available: {e}")
        print(f"   💡 Install with: pip install -r requirements-crewai.txt")
    except Exception as e:
        print(f"   ❌ Advanced assessment error: {e}")

def demo_semantic_knowledge_base():
    """Demonstrate semantic knowledge base and ontology features."""
    
    print("\n" + "="*70)
    print("🧬 SEMANTIC KNOWLEDGE BASE DEMO")
    print("="*70)
    
    print(f"\n📚 SFIA Ontology Features:")
    print(f"   • RDF triples for skills, levels, attributes")
    print(f"   • SPARQL queries for complex relationships")
    print(f"   • OWL reasoning for semantic inference")
    print(f"   • Knowledge graph navigation")
    
    try:
        from crewai_multi_agent import SFIAOntologyManager, SemanticConfig
        
        config = SemanticConfig(enable_inference=True)
        ontology = SFIAOntologyManager(config)
        
        print(f"\n🏗️ Ontology Structure:")
        print(f"   📊 Total triples: {len(ontology.graph)}")
        print(f"   🔍 Reasoning: {'Enabled' if config.enable_inference else 'Disabled'}")
        
        # Demo semantic queries
        print(f"\n🔍 Semantic Query Examples:")
        
        # Query skill relationships
        print(f"\n   1. Skill Relationships (PROG):")
        prog_relations = ontology.query_skill_relationships("PROG")
        print(f"      Relationships found: {len(prog_relations.get('relationships', []))}")
        
        # Infer career paths
        print(f"\n   2. Career Path Inference:")
        current_skills = ['PROG', 'ARCH', 'RLMT']
        career_paths = ontology.infer_career_paths(current_skills)
        print(f"      Career paths identified: {len(career_paths)}")
        for path in career_paths[:2]:  # Show first 2
            print(f"      • {path.get('role', 'Unknown')} (Match: {path.get('semantic_match_score', 0):.2f})")
        
        print(f"\n✅ Semantic knowledge base operational!")
        
    except ImportError as e:
        print(f"❌ Semantic libraries not available: {e}")
        print(f"💡 Install with: pip install rdflib owlrl")
    except Exception as e:
        print(f"❌ Semantic demo error: {e}")

def demo_multi_agent_collaboration():
    """Demonstrate multi-agent collaborative workflow."""
    
    print("\n" + "="*70)
    print("🤝 MULTI-AGENT COLLABORATION DEMO")
    print("="*70)
    
    print(f"\n👥 Agent Specializations:")
    print(f"   🎓 SFIA Expert: Deep framework knowledge")
    print(f"   💼 Career Advisor: Strategic guidance")
    print(f"   🔍 Evidence Analyst: Validation specialist")
    print(f"   🧬 Semantic Reasoner: Ontology reasoning")
    print(f"   📋 Report Generator: Synthesis expert")
    
    print(f"\n🔄 Collaborative Workflow:")
    print(f"   1. Semantic Reasoner analyzes ontological relationships")
    print(f"   2. Evidence Analyst validates professional evidence")
    print(f"   3. SFIA Expert maps evidence to competency levels")
    print(f"   4. Career Advisor provides strategic recommendations")
    print(f"   5. Report Generator synthesizes comprehensive assessment")
    
    try:
        from crewai_multi_agent import create_crewai_system
        
        system = create_crewai_system()
        if system:
            print(f"\n🚀 Multi-Agent System Status:")
            print(f"   ✅ System initialized successfully")
            print(f"   👥 Agents created: {len(system.agents)}")
            print(f"   🛠️ Tools available: Semantic knowledge base")
            print(f"   🧬 Ontology loaded: {len(system.ontology.graph)} triples")
            
            # Demo portfolio analysis
            print(f"\n📊 Portfolio Analysis Demo:")
            portfolio = {
                'skills': {
                    'PROG': 4,
                    'ARCH': 3, 
                    'RLMT': 3,
                    'TEST': 4
                },
                'experience_years': 5,
                'current_role': 'Senior Developer'
            }
            
            print(f"   📋 Analyzing portfolio with {len(portfolio['skills'])} skills...")
            analysis = system.analyze_skills_portfolio(portfolio)
            
            if 'error' not in analysis:
                print(f"   ✅ Portfolio analysis completed")
                print(f"   🧬 Semantic insights: {len(analysis.get('semantic_insights', {}))}")
                print(f"   🛤️ Career paths: {len(analysis.get('inferred_career_paths', []))}")
                print(f"   📊 KB queries: {analysis.get('knowledge_base_queries', 0)}")
            else:
                print(f"   ❌ Portfolio analysis failed")
        else:
            print(f"❌ Could not initialize multi-agent system")
            
    except ImportError as e:
        print(f"❌ CrewAI not available: {e}")
    except Exception as e:
        print(f"❌ Multi-agent demo error: {e}")

def main():
    """Run the complete advanced IntelliSFIA demo."""
    
    print("🚀 IntelliSFIA ADVANCED AI DEMO")
    print("=" * 70)
    print("🤖 CrewAI Multi-Agent + Semantic Ontology System")
    print("🧬 RDF Knowledge Base + SPARQL Reasoning")
    print("🔒 Privacy-First Local Processing")
    print("=" * 70)
    
    # Check prerequisites
    print(f"\n🔍 Checking Advanced Prerequisites...")
    if not check_advanced_prerequisites():
        print(f"\n⚠️ Advanced features require additional libraries")
        print(f"   Install with: pip install -r requirements-crewai.txt")
        print(f"\n💡 You can still use basic Ollama integration:")
        print(f"   python demo_ollama_integration.py")
        return
    
    print(f"\n✅ All advanced libraries available!")
    
    # Check basic Ollama availability
    try:
        from ollama_service import test_ollama_connection
        if not test_ollama_connection():
            print(f"\n❌ Ollama service not available")
            print(f"   Please start: ollama serve")
            return
        print(f"✅ Ollama service available")
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        return
    
    # Run advanced demos
    print(f"\n🎬 Starting Advanced Demo Scenarios...")
    
    # Demo 1: Basic vs Advanced comparison
    demo_basic_vs_advanced()
    
    # Demo 2: Semantic knowledge base
    demo_semantic_knowledge_base()
    
    # Demo 3: Multi-agent collaboration
    demo_multi_agent_collaboration()
    
    # Summary
    print(f"\n" + "="*70)
    print(f"🎉 ADVANCED DEMO COMPLETE!")
    print(f"="*70)
    
    print(f"\n✨ What You've Experienced:")
    print(f"   🤖 Multi-agent AI collaboration (5 specialized agents)")
    print(f"   🧬 Semantic knowledge base with SFIA ontology")
    print(f"   🔍 SPARQL queries and semantic reasoning")
    print(f"   📊 Advanced evidence validation and analysis")
    print(f"   🚀 Intelligent career path inference")
    print(f"   🔒 Complete privacy with local processing")
    
    print(f"\n🌟 Key Advantages:")
    print(f"   • More accurate assessments through agent collaboration")
    print(f"   • Deeper insights via semantic reasoning")
    print(f"   • Evidence validation by specialized agents")
    print(f"   • Strategic career guidance from expert agents")
    print(f"   • Comprehensive reporting and synthesis")
    
    print(f"\n🚀 Next Steps:")
    print(f"   • Integrate with IntelliSFIA web interface")
    print(f"   • Expand SFIA ontology with more relationships")
    print(f"   • Add domain-specific knowledge bases")
    print(f"   • Implement conversation memory across agents")
    print(f"   • Create specialized assessment workflows")
    
    print(f"\n📖 Documentation:")
    print(f"   • README_OLLAMA.md - Basic integration guide")
    print(f"   • crewai_multi_agent.py - Advanced system code")
    print(f"   • requirements-crewai.txt - Advanced dependencies")

if __name__ == "__main__":
    main()