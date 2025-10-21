#!/usr/bin/env python3
"""
IntelliSFIA CLI Testing Script
=============================

Test all CLI commands with real-world examples to demonstrate functionality.
"""

import requests
import json
import time
import sys
from pathlib import Path

def check_api_health():
    """Check if the API server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API returned status {response.status_code}"
    except Exception as e:
        return False, str(e)

def test_llm_providers():
    """Test LLM provider endpoints."""
    print("🔍 Testing LLM Providers...")
    
    try:
        # Test provider list
        response = requests.get("http://localhost:8000/api/llm/providers")
        if response.status_code == 200:
            providers = response.json()
            print(f"✅ Available providers: {len(providers)} found")
            for provider in providers[:3]:  # Show first 3
                print(f"   - {provider.get('provider', 'Unknown')}: {provider.get('available', False)}")
        else:
            print(f"❌ Provider list failed: {response.status_code}")
            
        # Test provider availability
        response = requests.get("http://localhost:8000/api/llm/available")
        if response.status_code == 200:
            available = response.json()
            print(f"✅ Available providers: {available}")
        else:
            print(f"❌ Available providers check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ LLM provider test failed: {e}")

def test_skill_assessment():
    """Test skill assessment with real-world examples."""
    print("\n🎯 Testing Skill Assessment...")
    
    # Real-world programming assessment example
    assessment_data = {
        "skill_code": "PROG",
        "evidence": """Over the past 5 years, I have been working as a Senior Software Developer at TechCorp, 
        where I led a team of 4 developers in building a microservices-based e-commerce platform using Python, 
        FastAPI, and React. I designed and implemented RESTful APIs that handle over 10,000 requests per day, 
        integrated with payment gateways (Stripe, PayPal), and implemented caching strategies using Redis that 
        improved response times by 40%. I also mentored junior developers, conducted code reviews, and established 
        CI/CD pipelines using GitHub Actions and Docker. Recently, I architected a machine learning recommendation 
        system using scikit-learn that increased conversion rates by 15%.""",
        "llm_provider": {
            "provider": "ollama",
            "fallback": True
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/ai/assess",
            json=assessment_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Assessment completed:")
            print(f"   Skill: {result.get('skill_code')} - {result.get('skill_title', 'N/A')}")
            print(f"   Recommended Level: {result.get('recommended_level', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 0)}%")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')[:100]}...")
        else:
            print(f"❌ Assessment failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Assessment test failed: {e}")

def test_evidence_validation():
    """Test evidence validation."""
    print("\n🔍 Testing Evidence Validation...")
    
    validation_data = {
        "evidence": """I developed a React Native mobile application for a startup that allows users to track 
        their fitness goals. The app includes user authentication, real-time data synchronization, push 
        notifications, and integration with wearable devices. I used TypeScript for type safety, implemented 
        state management with Redux, and created automated tests with Jest. The app was published to both 
        iOS and Android app stores and gained 10,000+ downloads in the first month.""",
        "skill_code": "PROG",
        "llm_provider": {
            "provider": "ollama",
            "fallback": True
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/ai/validate-evidence",
            json=validation_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Evidence validation completed:")
            print(f"   Quality Score: {result.get('evidence_quality_score', 0)}%")
            print(f"   Completeness: {result.get('completeness_score', 0)}%")
            print(f"   Relevance: {result.get('relevance_score', 0)}%")
            suggestions = result.get('suggestions', [])
            if suggestions:
                print(f"   Suggestions: {len(suggestions)} recommendations")
        else:
            print(f"❌ Evidence validation failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Evidence validation test failed: {e}")

def test_conversation_chat():
    """Test conversation/chat functionality."""
    print("\n💬 Testing Conversation Chat...")
    
    chat_data = {
        "message": "I'm a Python developer with 3 years of experience. What SFIA skills should I focus on to become a senior developer?",
        "llm_provider": {
            "provider": "ollama",
            "fallback": True
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/ai/chat",
            json=chat_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat response received:")
            print(f"   Session ID: {result.get('session_id', 'N/A')}")
            print(f"   Response: {result.get('response', 'N/A')[:150]}...")
        else:
            print(f"❌ Chat failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Chat test failed: {e}")

def test_career_guidance():
    """Test career guidance functionality."""
    print("\n🚀 Testing Career Guidance...")
    
    guidance_data = {
        "current_skills": {
            "PROG": 4,
            "TEST": 3,
            "DBAD": 3
        },
        "career_goals": "I want to become a Senior Software Architect within 2-3 years",
        "experience_years": 4,
        "industry": "Financial Technology",
        "llm_provider": {
            "provider": "ollama",
            "fallback": True
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/ai/career-guidance",
            json=guidance_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Career guidance completed:")
            career_paths = result.get('career_paths', [])
            if career_paths:
                print(f"   Career Paths: {len(career_paths)} paths suggested")
            skills_gap = result.get('skills_gap_analysis', {})
            if skills_gap:
                print(f"   Skills Gap Analysis: Available")
            next_steps = result.get('next_steps', [])
            if next_steps:
                print(f"   Next Steps: {len(next_steps)} recommendations")
        else:
            print(f"❌ Career guidance failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Career guidance test failed: {e}")

def test_sfia_data_endpoints():
    """Test SFIA data endpoints."""
    print("\n📊 Testing SFIA Data Endpoints...")
    
    endpoints = [
        ("skills", "/api/sfia9/skills"),
        ("levels", "/api/sfia9/levels"), 
        ("attributes", "/api/sfia9/attributes"),
        ("statistics", "/api/sfia9/statistics")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ {name}: {len(data)} items")
                elif isinstance(data, dict):
                    print(f"✅ {name}: {len(data)} keys")
                else:
                    print(f"✅ {name}: Data available")
            else:
                print(f"❌ {name} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {name} test failed: {e}")

def main():
    """Run all CLI command tests."""
    print("🧪 IntelliSFIA CLI Command Testing")
    print("=" * 50)
    
    # Check API health first
    print("🏥 Checking API Health...")
    healthy, status = check_api_health()
    
    if healthy:
        print(f"✅ API server is healthy")
        print(f"   Status: {status}")
        
        # Run all tests
        test_llm_providers()
        test_sfia_data_endpoints()
        test_skill_assessment()
        test_evidence_validation()
        test_conversation_chat()
        test_career_guidance()
        
        print("\n🎉 CLI Command Testing Complete!")
        print("\nReal-world CLI commands you can now try:")
        print("python scripts/intellisfia-cli.py health")
        print("python scripts/intellisfia-cli.py providers list")
        print("python scripts/intellisfia-cli.py assess --skill PROG --evidence 'Your evidence here'")
        print("python scripts/intellisfia-cli.py chat --message 'Hello, I need career advice'")
        print("python scripts/intellisfia-cli.py validate --evidence 'Evidence text here'")
        
    else:
        print(f"❌ API server is not healthy: {status}")
        print("Please start the API server first:")
        print("python start.py --service api --dev")

if __name__ == "__main__":
    main()