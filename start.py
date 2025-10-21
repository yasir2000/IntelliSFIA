#!/usr/bin/env python3
"""
IntelliSFIA Unified Startup Script
=================================

Cross-platform startup script for IntelliSFIA services.
Automatically detects OS and starts appropriate services.

Usage:
    python start.py --service api --port 8000
    python start.py --service cli --help
    python start.py --service all --dev
    python start.py --install-deps --llm-providers all
"""

import argparse
import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import List, Optional

def get_python_executable() -> str:
    """Get the appropriate Python executable for the current platform."""
    if platform.system() == "Windows":
        # Try python first, then py
        for cmd in ["python", "py"]:
            try:
                result = subprocess.run([cmd, "--version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return cmd
            except FileNotFoundError:
                continue
    return "python3" if platform.system() != "Windows" else "python"

def install_dependencies(llm_providers: Optional[str] = None, dev: bool = False):
    """Install project dependencies."""
    python_cmd = get_python_executable()
    
    # Base installation
    cmd = [python_cmd, "-m", "pip", "install", "-e", "."]
    
    # Add optional dependencies
    extras = []
    if llm_providers:
        if llm_providers == "all":
            extras.extend(["llm", "crewai"])
        else:
            extras.append("llm")
    
    if dev:
        extras.append("dev")
    
    if extras:
        cmd[-1] += f"[{','.join(extras)}]"
    
    print(f"Installing dependencies: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0

def start_api_server(port: int = 8000, dev: bool = False, host: str = "0.0.0.0"):
    """Start the API server."""
    python_cmd = get_python_executable()
    
    if dev:
        # Development mode with auto-reload
        cmd = [python_cmd, "-m", "uvicorn", "intellisfia.api:app", 
               "--reload", "--host", host, "--port", str(port)]
    else:
        # Production mode
        cmd = [python_cmd, "scripts/intellisfia-api.py"]
    
    print(f"Starting API server on {host}:{port}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n✅ API server stopped")

def start_cli(*args):
    """Start the CLI with provided arguments."""
    python_cmd = get_python_executable()
    cmd = [python_cmd, "scripts/intellisfia-cli.py"] + list(args)
    
    print(f"Starting CLI: {' '.join(cmd)}")
    subprocess.run(cmd)

def setup_development_environment():
    """Set up development environment with pre-commit hooks."""
    python_cmd = get_python_executable()
    
    print("🔧 Setting up development environment...")
    
    # Install dev dependencies
    if not install_dependencies(dev=True):
        print("❌ Failed to install dev dependencies")
        return False
    
    # Install pre-commit hooks
    try:
        subprocess.run([python_cmd, "-m", "pre_commit", "install"], check=True)
        print("✅ Pre-commit hooks installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Failed to install pre-commit hooks")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="IntelliSFIA Unified Startup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py --service api --port 8000
  python start.py --service cli assess --skill PROG --provider anthropic
  python start.py --install-deps --llm-providers all --dev
  python start.py --setup-dev
        """
    )
    
    parser.add_argument("--service", choices=["api", "cli", "all"], 
                       help="Service to start")
    parser.add_argument("--port", type=int, default=8000,
                       help="Port for API server (default: 8000)")
    parser.add_argument("--host", default="0.0.0.0",
                       help="Host for API server (default: 0.0.0.0)")
    parser.add_argument("--dev", action="store_true",
                       help="Run in development mode")
    parser.add_argument("--install-deps", action="store_true",
                       help="Install dependencies")
    parser.add_argument("--llm-providers", 
                       choices=["basic", "all"], default="basic",
                       help="LLM providers to install")
    parser.add_argument("--setup-dev", action="store_true",
                       help="Set up development environment")
    
    # Parse known args to allow CLI arguments to pass through
    args, unknown = parser.parse_known_args()
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Please run this script from the IntelliSFIA root directory")
        sys.exit(1)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies(args.llm_providers, args.dev):
            print("❌ Failed to install dependencies")
            sys.exit(1)
        print("✅ Dependencies installed successfully")
    
    # Set up development environment
    if args.setup_dev:
        if not setup_development_environment():
            sys.exit(1)
        print("✅ Development environment set up successfully")
        return
    
    # Start services
    if args.service == "api":
        start_api_server(args.port, args.dev, args.host)
    elif args.service == "cli":
        start_cli(*unknown)
    elif args.service == "all":
        print("🚀 Starting all services...")
        # TODO: Implement concurrent service startup
        start_api_server(args.port, args.dev, args.host)
    elif not args.install_deps and not args.setup_dev:
        parser.print_help()
        print("\n💡 Quick start:")
        print("  python start.py --install-deps --llm-providers all")
        print("  python start.py --service api --dev")

if __name__ == "__main__":
    main()