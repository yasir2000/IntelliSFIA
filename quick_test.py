#!/usr/bin/env python3
"""
Quick Test for IntelliSFIA with Ollama
=====================================

This script performs a quick test of the current setup.
"""

import requests
import json
import sys


def test_ollama():
    """Test Ollama service"""
    print("🔍 Testing Ollama service...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            print(f"✅ Ollama is running with {len(models)} models:")
            for name in model_names:
                print(f"   • {name}")
            return True
        else:
            print(f"❌ Ollama API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False


def test_ollama_chat():
    """Test Ollama chat functionality"""
    print("\n🧠 Testing Ollama chat...")
    
    try:
        # Get available models first
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Cannot get model list")
            return False
        
        models = response.json().get('models', [])
        if not models:
            print("❌ No models available")
            return False
        
        # Use the first available model
        model_name = models[0]['name']
        print(f"🤖 Using model: {model_name}")
        
        # Test chat
        chat_payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": "What is SFIA? Answer in one sentence."}
            ],
            "stream": False
        }
        
        print("💭 Sending test prompt...")
        response = requests.post("http://localhost:11434/api/chat", 
                               json=chat_payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            message = result.get('message', {}).get('content', 'No response')
            print(f"✅ Chat test successful!")
            print(f"   Response: {message[:100]}...")
            return True
        else:
            print(f"❌ Chat API returned {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False


def test_intellisfia_api():
    """Test IntelliSFIA API if running"""
    print("\n🔍 Testing IntelliSFIA API...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ IntelliSFIA API is running")
            
            # Test docs endpoint
            response = requests.get("http://localhost:8000/docs", timeout=5)
            if response.status_code == 200:
                print("✅ API docs are available at http://localhost:8000/docs")
            
            return True
        else:
            print(f"❌ IntelliSFIA API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"ℹ️  IntelliSFIA API not running: {e}")
        return False


def main():
    """Run quick tests"""
    print("🧪 Quick Test Suite for IntelliSFIA + Ollama")
    print("=" * 50)
    
    tests = [
        ("Ollama Service", test_ollama),
        ("Ollama Chat", test_ollama_chat),
        ("IntelliSFIA API", test_intellisfia_api)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\nTests passed: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("🎉 All tests passed!")
    elif passed_count >= 2:
        print("⚠️  Most tests passed. Basic functionality is working.")
    else:
        print("❌ Multiple tests failed. Please check the setup.")
    
    print("\n💡 Next steps:")
    if results.get("Ollama Service") and results.get("Ollama Chat"):
        print("• Ollama is working! You can use it for LLM operations")
        print("• To start IntelliSFIA API: python setup_local_production.py")
    
    if not results.get("Ollama Service"):
        print("• Install Ollama from https://ollama.ai")
        print("• Start Ollama service: ollama serve")
    
    if results.get("Ollama Service") and not results.get("Ollama Chat"):
        print("• Download a model: ollama pull llama3.1:8b")


if __name__ == "__main__":
    main()