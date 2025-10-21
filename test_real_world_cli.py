#!/usr/bin/env python3
"""
Direct CLI Command Examples - Real World Testing
==============================================

Test CLI commands with actual real-world scenarios.
"""

import subprocess
import sys
import json
import time

def run_command(command, description, timeout=30):
    """Run a command and display results."""
    print(f"\n🔥 {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            command.split(), 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            print(result.stdout)
        else:
            print("❌ ERROR")
            print(f"Return code: {result.returncode}")
            print(f"STDERR: {result.stderr}")
            print(f"STDOUT: {result.stdout}")
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ TIMEOUT after {timeout} seconds")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

def test_real_world_examples():
    """Test real-world CLI examples."""
    
    print("🚀 IntelliSFIA CLI - Real World Examples")
    print("=" * 60)
    
    # Test 1: Simple API health check via HTTP
    run_command(
        "curl -s http://localhost:8000/health",
        "API Health Check (Direct HTTP)"
    )
    
    # Test 2: Check LLM providers
    run_command(
        "curl -s http://localhost:8000/api/llm/providers",
        "List Available LLM Providers"
    )
    
    # Test 3: Create a simple assessment request
    assessment_json = {
        "skill_code": "PROG",
        "evidence": "I have 5 years of Python development experience, built REST APIs with FastAPI, worked with databases using SQLAlchemy, and deployed applications using Docker.",
        "llm_provider": {"provider": "ollama", "fallback": True}
    }
    
    # Write assessment data to temp file
    with open("temp_assessment.json", "w") as f:
        json.dump(assessment_json, f)
    
    run_command(
        'curl -s -X POST http://localhost:8000/api/ai/assess -H "Content-Type: application/json" -d @temp_assessment.json',
        "SFIA Programming Skill Assessment"
    )
    
    # Test 4: Evidence validation example
    evidence_json = {
        "evidence": "Led development of microservices architecture serving 1M+ users daily, implemented CI/CD pipelines, mentored team of 5 developers, reduced deployment time by 60%.",
        "skill_code": "ARCH",
        "llm_provider": {"provider": "ollama", "fallback": True}
    }
    
    with open("temp_evidence.json", "w") as f:
        json.dump(evidence_json, f)
        
    run_command(
        'curl -s -X POST http://localhost:8000/api/ai/validate-evidence -H "Content-Type: application/json" -d @temp_evidence.json',
        "Evidence Validation for Architecture Skills"
    )
    
    # Test 5: Career guidance
    career_json = {
        "current_skills": {"PROG": 4, "TEST": 3, "ARCH": 2},
        "career_goals": "Become a Senior Software Architect in 2 years",
        "experience_years": 4,
        "industry": "FinTech",
        "llm_provider": {"provider": "ollama", "fallback": True}
    }
    
    with open("temp_career.json", "w") as f:
        json.dump(career_json, f)
        
    run_command(
        'curl -s -X POST http://localhost:8000/api/ai/career-guidance -H "Content-Type: application/json" -d @temp_career.json',
        "Career Guidance for Software Development Path"
    )
    
    # Test 6: Chat/Conversation
    chat_json = {
        "message": "What SFIA skills should a Python developer focus on to advance their career?",
        "llm_provider": {"provider": "ollama", "fallback": True}
    }
    
    with open("temp_chat.json", "w") as f:
        json.dump(chat_json, f)
        
    run_command(
        'curl -s -X POST http://localhost:8000/api/ai/chat -H "Content-Type: application/json" -d @temp_chat.json',
        "AI Chat for Career Advice"
    )
    
    # Clean up temp files
    import os
    for temp_file in ["temp_assessment.json", "temp_evidence.json", "temp_career.json", "temp_chat.json"]:
        try:
            os.remove(temp_file)
        except:
            pass
    
    print("\n🎉 Real-world CLI testing complete!")
    print("\n📝 Summary of tested scenarios:")
    print("✅ Health check and system status")  
    print("✅ LLM provider management")
    print("✅ SFIA skill assessment with real evidence")
    print("✅ Evidence quality validation")
    print("✅ Career guidance and development planning")
    print("✅ AI-powered career conversation")
    
    print("\n💡 Next steps:")
    print("- Fix any failing endpoints")
    print("- Test CLI wrapper scripts")
    print("- Verify all LLM providers work correctly")
    print("- Test batch processing capabilities")

if __name__ == "__main__":
    test_real_world_examples()