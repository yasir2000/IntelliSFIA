"""
Quick Test for IntelliSFIA + Ollama Integration
==============================================

This script performs a quick test of the Ollama integration
to ensure everything is working correctly.
"""

import sys
import json
from pathlib import Path

# Add framework to path
sys.path.append(str(Path(__file__).parent))

def test_ollama_connection():
    """Test basic Ollama connection"""
    print("🔌 Testing Ollama Connection...")
    
    try:
        from ollama_service import OllamaService, OllamaConfig
        
        config = OllamaConfig()
        ollama = OllamaService(config)
        
        if ollama.is_available():
            print(f"✅ Ollama service available at {ollama.base_url}")
            
            models = ollama.list_models()
            print(f"📚 Available models: {models}")
            
            if models:
                print("🧪 Testing text generation...")
                response = ollama.generate(
                    "What is SFIA? Please provide a brief explanation.",
                    temperature=0.3
                )
                
                if response:
                    print(f"✅ Text generation successful!")
                    print(f"📝 Response: {response[:200]}...")
                    return True
                else:
                    print("❌ Text generation failed")
                    return False
            else:
                print("⚠️ No models available. Please download a model:")
                print("   ollama pull llama3.1:8b")
                return False
        else:
            print("❌ Ollama service not available")
            print("💡 Please start Ollama: ollama serve")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_sfia_data():
    """Test SFIA data availability"""
    print("\n📊 Testing SFIA Data...")
    
    data_path = Path(__file__).parent / "sfia_ai_framework" / "sfia_ai_framework" / "data" / "sfia9"
    
    required_files = [
        "sfia9_skills.json",
        "sfia9_attributes.json", 
        "sfia9_levels.json"
    ]
    
    all_present = True
    for file_name in required_files:
        file_path = data_path / file_name
        if file_path.exists():
            print(f"✅ {file_name} found")
            
            # Check file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"   📈 Contains {len(data)} items")
            except Exception as e:
                print(f"   ⚠️ Error reading file: {e}")
                
        else:
            print(f"❌ {file_name} missing")
            all_present = False
    
    if not all_present:
        print("\n💡 To generate SFIA data, run:")
        print("   python sfia_ai_framework/sfia_ai_framework/data/sfia9_data_processor.py")
    
    return all_present

def test_intelligent_agent():
    """Test the intelligent SFIA agent"""
    print("\n🧠 Testing Intelligent Agent...")
    
    try:
        from ollama_service import IntelliSFIAAgent, OllamaService, OllamaConfig
        
        config = OllamaConfig(temperature=0.3, max_tokens=500)
        ollama = OllamaService(config)
        
        if not ollama.is_available():
            print("❌ Ollama not available for agent test")
            return False
        
        agent = IntelliSFIAAgent(ollama)
        skills_count = len(agent.sfia_data.get('skills', []))
        
        if skills_count == 0:
            print("❌ No SFIA skills data available")
            return False
        
        print(f"✅ Agent initialized with {skills_count} skills")
        
        # Test simple assessment
        print("🧪 Testing skill assessment...")
        
        simple_evidence = "I can write basic Python scripts and have completed online tutorials."
        assessment = agent.assess_skill_level("PROG", simple_evidence, "Entry level developer")
        
        if assessment and "error" not in assessment:
            print("✅ Skill assessment successful!")
            print(f"📊 Assessment type: {assessment.get('status', 'structured')}")
            return True
        else:
            print(f"❌ Assessment failed: {assessment.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Agent test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 IntelliSFIA + Ollama Integration Test")
    print("=" * 45)
    
    results = {
        "ollama_connection": test_ollama_connection(),
        "sfia_data": test_sfia_data(),
        "intelligent_agent": False
    }
    
    # Only test agent if previous tests pass
    if results["ollama_connection"] and results["sfia_data"]:
        results["intelligent_agent"] = test_intelligent_agent()
    
    print("\n📋 Test Results Summary:")
    print("=" * 25)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Ready to run the demo:")
        print("   python demo_ollama_integration.py")
    else:
        print("\n⚠️ Some tests failed. Please check the setup:")
        print("   1. Start Ollama: ollama serve")
        print("   2. Download model: ollama pull llama3.1:8b")
        print("   3. Process SFIA data: python sfia_ai_framework/sfia_ai_framework/data/sfia9_data_processor.py")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)