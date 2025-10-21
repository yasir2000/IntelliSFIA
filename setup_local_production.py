#!/usr/bin/env python3
"""
Local Production Setup for IntelliSFIA with Ollama
=================================================

This script sets up IntelliSFIA to run locally with Ollama for testing.
Use this if Docker is not available.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
import requests
from pathlib import Path


class LocalSetup:
    """Setup IntelliSFIA locally with Ollama"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.ollama_url = "http://localhost:11434"
        
    def check_ollama(self) -> bool:
        """Check if Ollama is installed and running"""
        print("🔍 Checking Ollama installation...")
        
        # Check if ollama command exists
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Ollama found: {result.stdout.strip()}")
            else:
                print("❌ Ollama command failed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Ollama not found. Please install from https://ollama.ai")
            return False
        
        # Check if service is running
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama service is running")
                return True
            else:
                print("❌ Ollama service not responding")
                return False
        except requests.RequestException:
            print("🔄 Ollama service not running. Starting...")
            return self.start_ollama()
    
    def start_ollama(self) -> bool:
        """Start Ollama service"""
        try:
            # Start ollama serve in background
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # Wait for service to start
            for i in range(10):
                time.sleep(2)
                try:
                    response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
                    if response.status_code == 200:
                        print("✅ Ollama service started successfully")
                        return True
                except requests.RequestException:
                    continue
            
            print("❌ Failed to start Ollama service")
            return False
            
        except Exception as e:
            print(f"❌ Error starting Ollama: {e}")
            return False
    
    def setup_models(self) -> bool:
        """Download required models"""
        print("📥 Setting up LLM models...")
        
        # Get available models
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code != 200:
                print("❌ Cannot access Ollama API")
                return False
            
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            print(f"📚 Available models: {', '.join(model_names) if model_names else 'None'}")
            
            # Check for recommended models
            recommended = ['llama3.1:8b', 'codellama:7b']
            missing_models = [m for m in recommended if not any(m in name for name in model_names)]
            
            if missing_models:
                print(f"📥 Missing recommended models: {', '.join(missing_models)}")
                
                for model in missing_models[:1]:  # Download only the first one to save time
                    print(f"⬇️  Downloading {model} (this may take several minutes)...")
                    try:
                        result = subprocess.run(['ollama', 'pull', model], 
                                              capture_output=True, text=True, timeout=600)
                        if result.returncode == 0:
                            print(f"✅ {model} downloaded successfully")
                        else:
                            print(f"❌ Failed to download {model}: {result.stderr}")
                            return False
                    except subprocess.TimeoutExpired:
                        print(f"⏰ Download timeout for {model}")
                        return False
            else:
                print("✅ Required models are available")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up models: {e}")
            return False
    
    def setup_python_env(self) -> bool:
        """Setup Python environment"""
        print("🐍 Setting up Python environment...")
        
        # Check Python version
        if sys.version_info < (3, 9):
            print(f"❌ Python 3.9+ required, found {sys.version}")
            return False
        
        print(f"✅ Python {sys.version.split()[0]} found")
        
        # Install requirements
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
        
        try:
            print("📦 Installing Python dependencies...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Python dependencies installed")
                return True
            else:
                print(f"❌ Failed to install dependencies: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Dependency installation timeout")
            return False
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    
    def create_env_file(self):
        """Create environment configuration file"""
        env_content = f"""# IntelliSFIA Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Ollama Configuration
OLLAMA_BASE_URL={self.ollama_url}
OLLAMA_MODEL=llama3.1:8b
LLM_PROVIDER=ollama

# Database (SQLite for development)
DATABASE_URL=sqlite:///./intellisfia.db

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=INFO
"""
        
        env_file = self.project_root / ".env"
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Environment file created: {env_file}")
    
    def start_api_server(self) -> bool:
        """Start the API server"""
        print("🚀 Starting IntelliSFIA API server...")
        
        api_script = self.project_root / "src" / "intellisfia" / "api.py"
        if not api_script.exists():
            print(f"❌ API script not found: {api_script}")
            return False
        
        try:
            # Start the server in background
            cmd = [sys.executable, '-m', 'uvicorn', 'src.intellisfia.api:app', 
                   '--host', '0.0.0.0', '--port', '8000', '--reload']
            
            print("🔄 Starting server with command:", ' '.join(cmd))
            process = subprocess.Popen(cmd, cwd=str(self.project_root))
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            for i in range(15):
                time.sleep(2)
                try:
                    response = requests.get("http://localhost:8000/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ API server started successfully!")
                        print(f"📄 Process ID: {process.pid}")
                        return True
                except requests.RequestException:
                    continue
            
            print("❌ API server failed to start")
            process.terminate()
            return False
            
        except Exception as e:
            print(f"❌ Error starting API server: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run basic functionality tests"""
        print("🧪 Running functionality tests...")
        
        tests = [
            ("Ollama API", f"{self.ollama_url}/api/tags"),
            ("IntelliSFIA Health", "http://localhost:8000/health"),
            ("IntelliSFIA Docs", "http://localhost:8000/docs"),
        ]
        
        all_passed = True
        for test_name, url in tests:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {test_name}: PASS")
                else:
                    print(f"❌ {test_name}: FAIL (HTTP {response.status_code})")
                    all_passed = False
            except Exception as e:
                print(f"❌ {test_name}: FAIL ({str(e)})")
                all_passed = False
        
        # Test LLM integration
        try:
            print("🧠 Testing LLM integration...")
            test_payload = {
                "prompt": "What is SFIA in one sentence?",
                "provider": "ollama",
                "max_tokens": 50
            }
            
            response = requests.post("http://localhost:8000/api/ai/chat", 
                                   json=test_payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ LLM Integration: PASS")
                print(f"   Response preview: {result.get('response', '')[:100]}...")
            else:
                print(f"❌ LLM Integration: FAIL (HTTP {response.status_code})")
                all_passed = False
                
        except Exception as e:
            print(f"❌ LLM Integration: FAIL ({str(e)})")
            all_passed = False
        
        return all_passed
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 IntelliSFIA Local Production Setup")
        print("=" * 50)
        
        steps = [
            ("Checking Ollama", self.check_ollama),
            ("Setting up models", self.setup_models),
            ("Setting up Python environment", self.setup_python_env),
            ("Creating environment file", lambda: (self.create_env_file(), True)[1]),
            ("Starting API server", self.start_api_server),
            ("Running tests", self.run_tests)
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            try:
                if not step_func():
                    print(f"❌ {step_name} failed!")
                    return False
            except Exception as e:
                print(f"❌ {step_name} failed with error: {e}")
                return False
        
        print("\n" + "=" * 50)
        print("🎉 Setup Complete!")
        print("=" * 50)
        print("")
        print("🌐 Access Points:")
        print("• API Server:      http://localhost:8000")
        print("• API Docs:        http://localhost:8000/docs")
        print("• Ollama API:      http://localhost:11434")
        print("")
        print("🧪 Test Commands:")
        print("• Health check:    curl http://localhost:8000/health")
        print("• Ollama models:   curl http://localhost:11434/api/tags")
        print("• Test chat:       python test_production.py")
        print("")
        print("✅ IntelliSFIA is now running locally with Ollama!")
        
        return True


def main():
    """Main setup execution"""
    setup = LocalSetup()
    success = setup.run_setup()
    
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    
    print("\n💡 Keep this terminal open to keep the server running.")
    print("   Press Ctrl+C to stop the server.")
    
    try:
        # Keep the script running
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()