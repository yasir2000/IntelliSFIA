"""
IntelliSFIA + Ollama LLM Integration Demo
=======================================

This demo showcases intelligent SFIA assessment using local Ollama LLM.
It demonstrates real-world scenarios of AI-powered skills evaluation,
career guidance, and professional development recommendations.

Requirements:
1. Ollama installed and running (ollama serve)
2. A model downloaded (e.g., ollama pull llama3.1:8b)
3. SFIA 9 data processed and available

Usage:
    python demo_ollama_integration.py
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add the framework to path
sys.path.append(str(Path(__file__).parent))

try:
    from ollama_service import OllamaService, OllamaConfig, IntelliSFIAAgent
except ImportError:
    print("❌ Could not import Ollama service. Please ensure ollama_service.py is in the current directory.")
    sys.exit(1)

class IntelliSFIADemo:
    """Demonstration of intelligent SFIA assessment with Ollama LLM"""
    
    def __init__(self):
        # Configure Ollama
        self.config = OllamaConfig(
            model="deepseek-coder:latest",  # Using available model
            temperature=0.3,      # Lower temperature for more consistent assessments
            max_tokens=2048
        )
        
        self.ollama = OllamaService(self.config)
        self.agent = None
        
    def setup(self) -> bool:
        """Initialize the demo environment"""
        print("🚀 IntelliSFIA + Ollama LLM Integration Demo")
        print("=" * 50)
        
        # Check Ollama availability
        if not self.ollama.is_available():
            print("❌ Ollama service not available!")
            print("\nPlease start Ollama:")
            print("   1. Install Ollama: https://ollama.ai")
            print("   2. Start service: ollama serve")
            print("   3. Download model: ollama pull llama3.1:8b")
            return False
        
        print(f"✅ Ollama service running at {self.ollama.base_url}")
        
        # List available models
        models = self.ollama.list_models()
        print(f"📚 Available models: {', '.join(models)}")
        
        if self.config.model not in models:
            print(f"⚠️  Model {self.config.model} not found!")
            print(f"   Please run: ollama pull {self.config.model}")
            return False
        
        # Initialize intelligent agent
        try:
            self.agent = IntelliSFIAAgent(self.ollama)
            skills_count = len(self.agent.sfia_data.get('skills', []))
            print(f"🧠 IntelliSFIA Agent initialized with {skills_count} SFIA skills")
            
            if skills_count == 0:
                print("⚠️  No SFIA data found. Please run the data processor first:")
                print("   python sfia_ai_framework/data/sfia9_data_processor.py")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing agent: {e}")
            return False
        
        return True
    
    def demo_skill_assessment(self):
        """Demonstrate intelligent skill level assessment"""
        print("\n🎯 DEMO 1: Intelligent Skill Assessment")
        print("-" * 40)
        
        # Real-world example: Software Development skill assessment
        skill_code = "PROG"  # Programming/Software Development
        evidence = """
        I have been working as a software developer for 3 years. My experience includes:
        
        - Led development of a microservices architecture for an e-commerce platform
        - Mentored 2 junior developers on coding best practices and design patterns
        - Implemented automated testing strategies including unit tests and integration tests
        - Designed and developed RESTful APIs used by multiple frontend applications
        - Collaborated with DevOps team to implement CI/CD pipelines
        - Conducted code reviews and established coding standards for the team
        - Troubleshot and resolved complex production issues independently
        - Participated in technical architecture discussions and decision-making
        - Used technologies: Python, JavaScript, Docker, Kubernetes, PostgreSQL
        - Delivered 3 major features ahead of schedule with zero critical bugs
        """
        
        context = "Mid-level developer seeking promotion to senior role in fintech company"
        
        print(f"🔍 Assessing SFIA skill: {skill_code}")
        print(f"📝 Evidence: {evidence[:100]}...")
        print(f"🎯 Context: {context}")
        print("\n🤖 AI Assessment in progress...")
        
        try:
            assessment = self.agent.assess_skill_level(skill_code, evidence, context)
            
            if "error" in assessment:
                print(f"❌ Assessment error: {assessment['error']}")
                return
            
            print("\n📊 ASSESSMENT RESULTS:")
            print("=" * 30)
            
            if assessment.get("status") == "text_response":
                print(assessment.get("assessment", "No assessment available"))
            else:
                print(f"🎯 Skill: {assessment.get('skill_name', 'Unknown')} ({assessment.get('skill_code', 'Unknown')})")
                print(f"📈 Recommended Level: {assessment.get('recommended_level', 'Unknown')}")
                print(f"🎪 Confidence: {assessment.get('confidence', 'Unknown')}%")
                
                if assessment.get('evidence_points'):
                    print(f"\n✅ Key Evidence Points:")
                    for point in assessment.get('evidence_points', []):
                        print(f"   • {point}")
                
                if assessment.get('improvement_areas'):
                    print(f"\n🎯 Areas for Improvement:")
                    for area in assessment.get('improvement_areas', []):
                        print(f"   • {area}")
                
                if assessment.get('reasoning'):
                    print(f"\n💭 Reasoning: {assessment.get('reasoning')}")
                
                if assessment.get('next_level_requirements'):
                    print(f"\n⬆️  Next Level Requirements: {assessment.get('next_level_requirements')}")
                
        except Exception as e:
            print(f"❌ Error during assessment: {e}")
    
    def demo_skills_gap_analysis(self):
        """Demonstrate intelligent skills gap analysis"""
        print("\n🔍 DEMO 2: Skills Gap Analysis")
        print("-" * 40)
        
        # Example current skills profile
        current_skills = {
            "PROG": 4,    # Programming - Level 4 (Enable)
            "DTAN": 3,    # Data Analysis - Level 3 (Apply)
            "ARCH": 2,    # Solution Architecture - Level 2 (Assist)
            "RLMT": 3,    # Relationship Management - Level 3 (Apply)
            "PROF": 4     # IT Professionalism - Level 4 (Enable)
        }
        
        target_role = "Senior Software Architect"
        
        print(f"🎯 Target Role: {target_role}")
        print(f"📊 Current Skills Profile:")
        for skill, level in current_skills.items():
            print(f"   • {skill}: Level {level}")
        
        print("\n🤖 AI Gap Analysis in progress...")
        
        try:
            gap_analysis = self.agent.analyze_skills_gap(current_skills, target_role)
            
            if "error" in gap_analysis:
                print(f"❌ Analysis error: {gap_analysis['error']}")
                return
            
            print("\n📊 SKILLS GAP ANALYSIS:")
            print("=" * 30)
            
            if gap_analysis.get("status") == "text_response":
                print(gap_analysis.get("analysis", "No analysis available"))
            else:
                # Display structured analysis
                if "skills_gap_analysis" in gap_analysis:
                    sga = gap_analysis["skills_gap_analysis"]
                    
                    if sga.get("strengths"):
                        print("💪 Strengths:")
                        for strength in sga["strengths"]:
                            print(f"   • {strength}")
                    
                    if sga.get("gaps"):
                        print("\n🎯 Skill Gaps:")
                        for gap in sga["gaps"]:
                            print(f"   • {gap}")
                    
                    if sga.get("priority_skills"):
                        print("\n🚨 Priority Skills to Develop:")
                        for skill in sga["priority_skills"]:
                            print(f"   • {skill}")
                
                if "recommendations" in gap_analysis:
                    rec = gap_analysis["recommendations"]
                    
                    if rec.get("immediate_actions"):
                        print("\n⚡ Immediate Actions:")
                        for action in rec["immediate_actions"]:
                            print(f"   • {action}")
                    
                    if rec.get("learning_path"):
                        print("\n📚 Learning Path:")
                        for i, step in enumerate(rec["learning_path"], 1):
                            print(f"   {i}. {step}")
                    
                    if rec.get("timeline"):
                        print(f"\n⏰ Timeline: {rec['timeline']}")
                
                if "role_readiness" in gap_analysis:
                    rr = gap_analysis["role_readiness"]
                    
                    if rr.get("current_readiness"):
                        print(f"\n📈 Current Readiness: {rr['current_readiness']}")
                    
                    if rr.get("key_blockers"):
                        print("\n🚧 Key Blockers:")
                        for blocker in rr["key_blockers"]:
                            print(f"   • {blocker}")
                
        except Exception as e:
            print(f"❌ Error during gap analysis: {e}")
    
    def demo_career_path_recommendation(self):
        """Demonstrate intelligent career path recommendations"""
        print("\n🚀 DEMO 3: Career Path Recommendations")
        print("-" * 40)
        
        # Example professional profile
        profile = {
            "name": "Alex Johnson",
            "current_role": "Software Developer",
            "years_experience": 5,
            "current_skills": {
                "Programming": 4,
                "System Design": 3,
                "Data Analysis": 3,
                "Team Leadership": 2,
                "Project Management": 2
            },
            "interests": [
                "Machine Learning",
                "Cloud Architecture",
                "Team Leadership",
                "Technical Strategy"
            ],
            "education": "Computer Science Degree",
            "industry": "Financial Technology",
            "career_goals": "Become a technical leader who can bridge technology and business strategy"
        }
        
        print(f"👤 Profile: {profile['name']}")
        print(f"💼 Current Role: {profile['current_role']}")
        print(f"⏰ Experience: {profile['years_experience']} years")
        print(f"🎯 Goals: {profile['career_goals']}")
        
        print("\n🤖 AI Career Guidance in progress...")
        
        try:
            recommendations = self.agent.recommend_career_path(profile)
            
            if "error" in recommendations:
                print(f"❌ Recommendation error: {recommendations['error']}")
                return
            
            print("\n🗺️  CAREER PATH RECOMMENDATIONS:")
            print("=" * 40)
            
            if recommendations.get("status") == "text_response":
                print(recommendations.get("recommendations", "No recommendations available"))
            else:
                # Display structured recommendations
                if "career_paths" in recommendations:
                    print("🎯 Recommended Career Paths:")
                    for i, path in enumerate(recommendations["career_paths"], 1):
                        print(f"\n   {i}. {path.get('role_title', 'Unknown Role')}")
                        print(f"      Timeline: {path.get('timeline', 'Unknown')}")
                        print(f"      Description: {path.get('description', 'No description')}")
                        if path.get('key_skills_needed'):
                            print(f"      Key Skills: {', '.join(path['key_skills_needed'])}")
                
                if "immediate_development" in recommendations:
                    dev = recommendations["immediate_development"]
                    print(f"\n⚡ Immediate Development Focus:")
                    if dev.get("priority_skills"):
                        print(f"   Priority Skills: {', '.join(dev['priority_skills'])}")
                    if dev.get("timeframe"):
                        print(f"   Timeframe: {dev['timeframe']}")
                    if dev.get("learning_activities"):
                        print("   Learning Activities:")
                        for activity in dev["learning_activities"]:
                            print(f"     • {activity}")
                
                if "long_term_vision" in recommendations:
                    vision = recommendations["long_term_vision"]
                    print(f"\n🌟 Long-term Vision:")
                    if vision.get("senior_roles"):
                        print(f"   Senior Roles: {', '.join(vision['senior_roles'])}")
                    if vision.get("leadership_path"):
                        print(f"   Leadership Path: {vision['leadership_path']}")
                    if vision.get("specialist_path"):
                        print(f"   Specialist Path: {vision['specialist_path']}")
                
        except Exception as e:
            print(f"❌ Error during career recommendation: {e}")
    
    def run_demo(self):
        """Run the complete demonstration"""
        if not self.setup():
            return
        
        try:
            # Run all demonstrations
            self.demo_skill_assessment()
            input("\n⏸️  Press Enter to continue to Skills Gap Analysis...")
            
            self.demo_skills_gap_analysis()
            input("\n⏸️  Press Enter to continue to Career Recommendations...")
            
            self.demo_career_path_recommendation()
            
            print("\n🎉 Demo Complete!")
            print("\n📋 Summary:")
            print("   ✅ Intelligent skill level assessment using local LLM")
            print("   ✅ AI-powered skills gap analysis")
            print("   ✅ Personalized career path recommendations")
            print("   ✅ Privacy-focused local processing")
            print("   ✅ SFIA framework integration")
            
            print("\n🚀 Next Steps:")
            print("   • Integrate with IntelliSFIA web interface")
            print("   • Add more sophisticated prompting")
            print("   • Implement conversation memory")
            print("   • Create specialized assessment agents")
            print("   • Add evidence validation workflows")
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    demo = IntelliSFIADemo()
    demo.run_demo()