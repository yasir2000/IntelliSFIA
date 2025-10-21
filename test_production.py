#!/usr/bin/env python3
"""
Production Test Suite for IntelliSFIA with Ollama
=================================================

This script tests the production deployment to ensure all services are working correctly.
"""

import asyncio
import json
import time
import requests
import sys
from typing import Dict, Any


class ProductionTester:
    """Test suite for production deployment"""
    
    def __init__(self):
        self.base_urls = {
            'api': 'http://localhost:8000',
            'frontend': 'http://localhost:3000',
            'ollama': 'http://localhost:11434',
            'nginx': 'http://localhost:80'
        }
        self.test_results = {}
    
    def test_service_health(self, service: str, url: str) -> bool:
        """Test if a service is responding"""
        try:
            response = requests.get(url, timeout=5)
            success = response.status_code == 200
            self.test_results[f"{service}_health"] = {
                'status': 'PASS' if success else 'FAIL',
                'response_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
            return success
        except requests.RequestException as e:
            self.test_results[f"{service}_health"] = {
                'status': 'FAIL',
                'error': str(e)
            }
            return False
    
    def test_ollama_models(self) -> bool:
        """Test Ollama model availability"""
        try:
            response = requests.get(f"{self.base_urls['ollama']}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                self.test_results['ollama_models'] = {
                    'status': 'PASS',
                    'available_models': model_names,
                    'model_count': len(model_names)
                }
                return len(model_names) > 0
            else:
                self.test_results['ollama_models'] = {
                    'status': 'FAIL',
                    'error': f"HTTP {response.status_code}"
                }
                return False
        except Exception as e:
            self.test_results['ollama_models'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test key API endpoints"""
        endpoints = [
            ('/health', 'Health check'),
            ('/docs', 'API documentation'),
            ('/api/sfia9/skills', 'SFIA skills endpoint'),
            ('/api/sfia9/statistics', 'SFIA statistics')
        ]
        
        all_passed = True
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.base_urls['api']}{endpoint}", timeout=10)
                success = response.status_code in [200, 201]
                
                self.test_results[f"api_{endpoint.replace('/', '_')}"] = {
                    'status': 'PASS' if success else 'FAIL',
                    'description': description,
                    'response_code': response.status_code
                }
                
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.test_results[f"api_{endpoint.replace('/', '_')}"] = {
                    'status': 'FAIL',
                    'description': description,
                    'error': str(e)
                }
                all_passed = False
        
        return all_passed
    
    def test_llm_integration(self) -> bool:
        """Test LLM integration through API"""
        try:
            test_payload = {
                "prompt": "What is SFIA?",
                "provider": "ollama",
                "max_tokens": 100
            }
            
            response = requests.post(
                f"{self.base_urls['api']}/api/ai/chat",
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.test_results['llm_integration'] = {
                    'status': 'PASS',
                    'response_preview': result.get('response', '')[:100] + '...'
                }
                return True
            else:
                self.test_results['llm_integration'] = {
                    'status': 'FAIL',
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                return False
                
        except Exception as e:
            self.test_results['llm_integration'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🧪 Running Production Test Suite")
        print("=" * 50)
        
        tests = [
            ("API Health", lambda: self.test_service_health('api', f"{self.base_urls['api']}/health")),
            ("Frontend Health", lambda: self.test_service_health('frontend', self.base_urls['frontend'])),
            ("Ollama Health", lambda: self.test_service_health('ollama', f"{self.base_urls['ollama']}/api/tags")),
            ("Nginx Proxy", lambda: self.test_service_health('nginx', self.base_urls['nginx'])),
            ("Ollama Models", self.test_ollama_models),
            ("API Endpoints", self.test_api_endpoints),
            ("LLM Integration", self.test_llm_integration)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing {test_name}...")
            try:
                result = test_func()
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"   {status}")
            except Exception as e:
                print(f"   ❌ FAIL - {str(e)}")
        
        return self.test_results
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if result.get('status') == 'PASS')
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"{status_icon} {test_name}: {result['status']}")
            
            if 'error' in result:
                print(f"   Error: {result['error']}")
            elif 'response_time' in result:
                print(f"   Response time: {result['response_time']:.3f}s")
            elif 'available_models' in result:
                print(f"   Models: {', '.join(result['available_models'])}")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! Production deployment is working correctly.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please check the deployment.")
            
        return passed_tests == total_tests


def main():
    """Main test execution"""
    print("IntelliSFIA Production Test Suite")
    print("=" * 50)
    
    # Wait for services to start
    print("⏳ Waiting for services to fully start...")
    time.sleep(10)
    
    tester = ProductionTester()
    tester.run_all_tests()
    success = tester.print_summary()
    
    # Export results to JSON
    with open('test_results.json', 'w') as f:
        json.dump(tester.test_results, f, indent=2)
    print(f"\n📄 Detailed results saved to test_results.json")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()