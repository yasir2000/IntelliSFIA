#!/usr/bin/env python3
"""
Docker Production Test Results
=============================
"""

import requests
import json

def test_docker_production():
    print("🐳 Docker Production Test Results")
    print("=" * 50)
    
    tests = [
        ("API Health", "http://localhost:8000/health"),
        ("Frontend", "http://localhost:3000"),
        ("Nginx Proxy", "http://localhost:80"),
        ("Ollama API", "http://localhost:11434/api/tags"),
        ("API Docs", "http://localhost:8000/docs"),
        ("SFIA Stats", "http://localhost:8000/api/sfia9/statistics")
    ]
    
    results = []
    
    for test_name, url in tests:
        try:
            response = requests.get(url, timeout=5)
            status = "✅ PASS" if response.status_code == 200 else f"⚠️  HTTP {response.status_code}"
            results.append((test_name, status, response.status_code))
            print(f"{status} {test_name}")
        except Exception as e:
            status = f"❌ FAIL: {str(e)[:50]}"
            results.append((test_name, status, 0))
            print(f"{status} {test_name}")
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    passed = sum(1 for _, _, code in results if code == 200)
    total = len(results)
    print(f"• Tests Passed: {passed}/{total}")
    print(f"• Success Rate: {(passed/total*100):.1f}%")
    
    print("\n🌐 Access Points:")
    print("• Frontend:    http://localhost:3000")
    print("• API:         http://localhost:8000")
    print("• API Docs:    http://localhost:8000/docs")
    print("• Nginx Proxy: http://localhost:80")
    print("• Ollama:      http://localhost:11434")
    
    print("\n🐳 Docker Services:")
    print("• intellisfia-frontend (React)")
    print("• intellisfia-api (FastAPI)")
    print("• intellisfia-ollama (LLM)")
    print("• intellisfia-nginx (Proxy)")  
    print("• intellisfia-postgres (Database)")
    print("• intellisfia-redis (Cache)")
    
    return passed == total

if __name__ == "__main__":
    success = test_docker_production()
    print(f"\n{'🎉 All tests passed!' if success else '⚠️  Some tests failed'}")