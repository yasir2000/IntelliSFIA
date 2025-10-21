#!/usr/bin/env python3
"""
IntelliSFIA CLI - Command Line Interface for Multi-LLM SFIA Assessment
=====================================================================

A comprehensive CLI tool for SFIA skills assessment with multi-LLM provider support,
conversation memory, evidence validation, and career guidance.

Features:
- Multi-LLM provider selection (Ollama, OpenAI, Anthropic, Google, Cohere)
- Interactive skill assessments with AI guidance
- Evidence validation and quality scoring
- Career pathway recommendations
- Conversation memory and context awareness
- Batch processing capabilities
- Export/import functionality

Usage:
    python intellisfia_cli.py assess --skill PROG --evidence "5 years Python..."
    python intellisfia_cli.py providers list
    python intellisfia_cli.py chat --provider anthropic
    python intellisfia_cli.py validate-evidence evidence.txt
"""

import argparse
import asyncio
import json
import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.markdown import Markdown
import yaml

# Try to import optional dependencies
try:
    import click
except ImportError:
    click = None

# Configure Rich console
console = Console()

class IntelliSFIACLI:
    """Main CLI class for IntelliSFIA multi-LLM assessment system."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load CLI configuration from file."""
        config_file = Path.home() / ".intellisfia" / "config.yml"
        default_config = {
            "default_provider": "auto",
            "fallback_enabled": True,
            "temperature": 0.3,
            "max_tokens": 2000,
            "conversation_memory": True,
            "export_format": "json",
            "api_timeout": 30
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
        
        return default_config
    
    def save_config(self):
        """Save current configuration to file."""
        config_file = Path.home() / ".intellisfia" / "config.yml"
        config_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            console.print(f"[green]Configuration saved to {config_file}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make HTTP request to IntelliSFIA API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=self.config["api_timeout"])
            else:
                response = requests.post(url, json=data, timeout=self.config["api_timeout"])
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.ConnectionError:
            console.print(f"[red]Error: Cannot connect to IntelliSFIA API at {self.base_url}[/red]")
            console.print("[yellow]Please ensure the API server is running with: python intellisfia_ai_api.py[/yellow]")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            console.print(f"[red]API Error: {e}[/red]")
            sys.exit(1)
    
    def check_api_health(self) -> bool:
        """Check if the API is healthy and return status."""
        try:
            health = self.make_request("GET", "/health")
            
            # Display health status
            table = Table(title="API Health Status")
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Details")
            
            table.add_row("API Server", "✅ Healthy", f"Available at {self.base_url}")
            table.add_row("Multi-LLM", "✅ Enabled" if health.get("multi_llm_enabled") else "❌ Disabled", 
                         f"{health.get('provider_count', 0)} providers available")
            table.add_row("Providers", "✅ Active", ", ".join(health.get("available_providers", [])))
            table.add_row("Sessions", "✅ Ready", f"{health.get('active_sessions', 0)} active")
            
            console.print(table)
            return True
            
        except Exception:
            console.print("[red]❌ API server is not available[/red]")
            return False
    
    def list_providers(self):
        """List all available LLM providers with status."""
        providers = self.make_request("GET", "/api/llm/providers")
        
        table = Table(title="Available LLM Providers")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Model")
        table.add_column("Requests", justify="right")
        table.add_column("Cost/Token", justify="right")
        table.add_column("Cache Size", justify="right")
        
        for provider in providers:
            status = "✅ Available" if provider["available"] else "❌ Unavailable"
            cost = f"${provider['cost_per_token']:.6f}" if provider['cost_per_token'] > 0 else "Free"
            
            table.add_row(
                provider["provider"].title(),
                status,
                provider["model"],
                str(provider["request_count"]),
                cost,
                str(provider.get("cache_size", 0))
            )
        
        console.print(table)
    
    def test_provider(self, provider: str = "auto"):
        """Test a specific LLM provider."""
        console.print(f"[blue]Testing provider: {provider}[/blue]")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Testing provider...", total=None)
            
            test_data = {
                "provider": provider,
                "fallback": self.config["fallback_enabled"]
            }
            
            try:
                response = self.make_request("POST", "/api/llm/test", test_data)
                
                # Display test results
                panel = Panel(
                    f"""[green]✅ Provider Test Successful[/green]

[cyan]Provider:[/cyan] {response.get('provider', 'Unknown')}
[cyan]Model:[/cyan] {response.get('model', 'Unknown')}
[cyan]Response Time:[/cyan] {response.get('response_time', 0):.2f}s
[cyan]Tokens Used:[/cyan] {response.get('tokens', 0)}
[cyan]Cost:[/cyan] ${response.get('cost', 0):.6f}

[white]Response:[/white]
{response.get('response', 'No response')}""",
                    title="Provider Test Results"
                )
                console.print(panel)
                
            except Exception as e:
                console.print(f"[red]❌ Provider test failed: {e}[/red]")
    
    def assess_skill(self, skill_code: str, evidence: str, provider: str = None):
        """Perform AI-powered SFIA skill assessment."""
        provider = provider or self.config["default_provider"]
        
        console.print(f"[blue]Assessing skill {skill_code} using {provider} provider[/blue]")
        
        assessment_data = {
            "skill_code": skill_code.upper(),
            "evidence": evidence,
            "context": f"CLI assessment for {skill_code}",
            "llm_provider": {
                "provider": provider,
                "fallback": self.config["fallback_enabled"]
            }
        }
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Analyzing evidence...", total=None)
            
            try:
                response = self.make_request("POST", "/api/assess/skill", assessment_data)
                
                # Display assessment results
                self.display_assessment_results(response)
                
            except Exception as e:
                console.print(f"[red]❌ Assessment failed: {e}[/red]")
    
    def display_assessment_results(self, assessment: Dict):
        """Display formatted assessment results."""
        # Main assessment panel
        main_panel = Panel(
            f"""[green]✅ SFIA Assessment Complete[/green]

[cyan]Skill:[/cyan] {assessment.get('skill_code', 'Unknown')} - {assessment.get('skill_name', 'Unknown Skill')}
[cyan]Recommended Level:[/cyan] [bold]{assessment.get('recommended_level', 'N/A')}[/bold]
[cyan]Confidence:[/cyan] {assessment.get('confidence', 0)}%
[cyan]Provider:[/cyan] {assessment.get('provider_used', 'Unknown')}

[white]Assessment:[/white]
{assessment.get('assessment', 'No assessment available')}""",
            title="SFIA Skill Assessment"
        )
        console.print(main_panel)
        
        # Evidence quality if available
        if 'evidence_quality_score' in assessment:
            quality_score = assessment['evidence_quality_score']
            quality_color = "green" if quality_score >= 80 else "yellow" if quality_score >= 60 else "red"
            
            quality_panel = Panel(
                f"""[{quality_color}]Evidence Quality Score: {quality_score}%[/{quality_color}]

{assessment.get('evidence_feedback', 'No feedback available')}""",
                title="Evidence Quality Analysis"
            )
            console.print(quality_panel)
        
        # Recommendations if available
        if assessment.get('development_recommendations'):
            rec_panel = Panel(
                assessment['development_recommendations'],
                title="Development Recommendations"
            )
            console.print(rec_panel)
    
    def validate_evidence(self, evidence_file: str = None, evidence_text: str = None):
        """Validate professional evidence."""
        if evidence_file:
            try:
                with open(evidence_file, 'r', encoding='utf-8') as f:
                    evidence_text = f.read()
            except Exception as e:
                console.print(f"[red]Error reading file: {e}[/red]")
                return
        
        if not evidence_text:
            console.print("[red]No evidence provided[/red]")
            return
        
        validation_data = {
            "evidence": evidence_text,
            "context": "CLI evidence validation"
        }
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Validating evidence...", total=None)
            
            try:
                response = self.make_request("POST", "/api/validate/evidence", validation_data)
                
                # Display validation results
                score = response.get('evidence_quality_score', 0)
                score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
                
                panel = Panel(
                    f"""[{score_color}]Quality Score: {score}%[/{score_color}]

[cyan]Completeness:[/cyan] {response.get('completeness', 'N/A')}%
[cyan]Relevance:[/cyan] {response.get('relevance', 'N/A')}%
[cyan]Authenticity:[/cyan] {response.get('authenticity', 'N/A')}%

[white]Feedback:[/white]
{response.get('feedback', 'No feedback available')}

[white]Suggestions for Improvement:[/white]
{response.get('suggestions', 'No suggestions available')}""",
                    title="Evidence Validation Results"
                )
                console.print(panel)
                
            except Exception as e:
                console.print(f"[red]❌ Validation failed: {e}[/red]")
    
    def start_chat(self, provider: str = None):
        """Start an interactive AI chat session."""
        provider = provider or self.config["default_provider"]
        
        console.print(f"[blue]Starting AI chat with {provider} provider[/blue]")
        console.print("[yellow]Type 'exit' to quit, 'help' for commands[/yellow]")
        
        while True:
            try:
                user_input = Prompt.ask("\n[green]You[/green]")
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    console.print("[blue]Goodbye![/blue]")
                    break
                
                if user_input.lower() == 'help':
                    self.show_chat_help()
                    continue
                
                if user_input.lower().startswith('/provider '):
                    new_provider = user_input.split(' ', 1)[1]
                    provider = new_provider
                    console.print(f"[blue]Switched to {provider} provider[/blue]")
                    continue
                
                # Send message to AI
                chat_data = {
                    "message": user_input,
                    "provider": provider,
                    "session_id": self.session_id
                }
                
                with Progress(SpinnerColumn(), TextColumn("AI is thinking...")) as progress:
                    progress.add_task("Processing...", total=None)
                    response = self.make_request("POST", "/api/chat", chat_data)
                
                # Display AI response
                ai_response = response.get('response', 'No response')
                console.print(f"\n[cyan]AI Assistant[/cyan]: {ai_response}")
                
                # Store session ID for conversation memory
                if 'session_id' in response:
                    self.session_id = response['session_id']
                
            except KeyboardInterrupt:
                console.print("\n[blue]Chat session ended[/blue]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    def show_chat_help(self):
        """Show chat commands help."""
        help_text = """[cyan]Chat Commands:[/cyan]
- [green]exit/quit/bye[/green]: Exit chat
- [green]/provider <name>[/green]: Switch LLM provider
- [green]help[/green]: Show this help

[cyan]Provider Options:[/cyan]
- auto, ollama, openai, anthropic, google, cohere

[cyan]Example Questions:[/cyan]
- "What skills do I need for a senior developer role?"
- "Assess my evidence for SFIA skill PROG"
- "How can I improve my evidence quality?"
"""
        console.print(Panel(help_text, title="Chat Help"))
    
    def career_guidance(self, role: str, experience: str):
        """Get AI-powered career guidance."""
        guidance_data = {
            "target_role": role,
            "current_experience": experience,
            "context": "CLI career guidance request"
        }
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Generating career guidance...", total=None)
            
            try:
                response = self.make_request("POST", "/api/guidance/career", guidance_data)
                
                panel = Panel(
                    f"""[green]✅ Career Guidance Generated[/green]

[cyan]Target Role:[/cyan] {role}

[white]Recommendations:[/white]
{response.get('guidance', 'No guidance available')}

[white]Suggested Skills:[/white]
{response.get('suggested_skills', 'No skills suggested')}

[white]Learning Path:[/white]
{response.get('learning_path', 'No learning path available')}""",
                    title="AI Career Guidance"
                )
                console.print(panel)
                
            except Exception as e:
                console.print(f"[red]❌ Career guidance failed: {e}[/red]")
    
    def export_session(self, format: str = "json", filename: str = None):
        """Export conversation session or assessment results."""
        if not self.session_id:
            console.print("[yellow]No active session to export[/yellow]")
            return
        
        try:
            # Get session history
            session_data = self.make_request("GET", f"/api/sessions/{self.session_id}/history")
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"intellisfia_session_{timestamp}.{format}"
            
            if format.lower() == "json":
                with open(filename, 'w') as f:
                    json.dump(session_data, f, indent=2, default=str)
            elif format.lower() == "yaml":
                with open(filename, 'w') as f:
                    yaml.dump(session_data, f, default_flow_style=False)
            else:
                console.print(f"[red]Unsupported format: {format}[/red]")
                return
            
            console.print(f"[green]Session exported to {filename}[/green]")
            
        except Exception as e:
            console.print(f"[red]Export failed: {e}[/red]")
    
    def batch_assess(self, input_file: str):
        """Perform batch assessment from JSON/YAML file."""
        try:
            with open(input_file, 'r') as f:
                if input_file.endswith('.yaml') or input_file.endswith('.yml'):
                    batch_data = yaml.safe_load(f)
                else:
                    batch_data = json.load(f)
            
            assessments = batch_data.get('assessments', [])
            results = []
            
            with Progress() as progress:
                task = progress.add_task("Processing assessments...", total=len(assessments))
                
                for assessment in assessments:
                    try:
                        result = self.make_request("POST", "/api/assess/skill", assessment)
                        results.append(result)
                        progress.advance(task)
                    except Exception as e:
                        console.print(f"[red]Failed assessment: {e}[/red]")
            
            # Export results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"batch_results_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            console.print(f"[green]Batch assessment complete. Results saved to {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Batch assessment failed: {e}[/red]")

def create_parser():
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="IntelliSFIA CLI - Multi-LLM SFIA Assessment Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--api-url", 
        default="http://localhost:8000",
        help="IntelliSFIA API base URL"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Health check command
    health_parser = subparsers.add_parser("health", help="Check API health status")
    
    # Provider commands
    providers_parser = subparsers.add_parser("providers", help="LLM provider management")
    providers_subparsers = providers_parser.add_subparsers(dest="provider_action")
    
    providers_subparsers.add_parser("list", help="List available providers")
    
    test_parser = providers_subparsers.add_parser("test", help="Test a provider")
    test_parser.add_argument("--provider", default="auto", help="Provider to test")
    
    # Assessment command
    assess_parser = subparsers.add_parser("assess", help="Perform skill assessment")
    assess_parser.add_argument("--skill", required=True, help="SFIA skill code")
    assess_parser.add_argument("--evidence", required=True, help="Evidence text or file")
    assess_parser.add_argument("--provider", help="LLM provider to use")
    
    # Evidence validation command
    validate_parser = subparsers.add_parser("validate", help="Validate evidence")
    validate_parser.add_argument("--file", help="Evidence file path")
    validate_parser.add_argument("--text", help="Evidence text")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start interactive AI chat")
    chat_parser.add_argument("--provider", help="LLM provider for chat")
    
    # Career guidance command
    career_parser = subparsers.add_parser("career", help="Get career guidance")
    career_parser.add_argument("--role", required=True, help="Target role")
    career_parser.add_argument("--experience", required=True, help="Current experience")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export session data")
    export_parser.add_argument("--format", choices=["json", "yaml"], default="json")
    export_parser.add_argument("--output", help="Output filename")
    
    # Batch processing command
    batch_parser = subparsers.add_parser("batch", help="Batch assessment processing")
    batch_parser.add_argument("--input", required=True, help="Input JSON/YAML file")
    
    # Configuration command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_action")
    
    config_subparsers.add_parser("show", help="Show current configuration")
    
    set_parser = config_subparsers.add_parser("set", help="Set configuration value")
    set_parser.add_argument("key", help="Configuration key")
    set_parser.add_argument("value", help="Configuration value")
    
    return parser

def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = IntelliSFIACLI(args.api_url)
    
    try:
        if args.command == "health":
            cli.check_api_health()
        
        elif args.command == "providers":
            if args.provider_action == "list":
                cli.list_providers()
            elif args.provider_action == "test":
                cli.test_provider(args.provider)
        
        elif args.command == "assess":
            # Check if evidence is a file
            if os.path.isfile(args.evidence):
                with open(args.evidence, 'r') as f:
                    evidence = f.read()
            else:
                evidence = args.evidence
            
            cli.assess_skill(args.skill, evidence, args.provider)
        
        elif args.command == "validate":
            cli.validate_evidence(args.file, args.text)
        
        elif args.command == "chat":
            cli.start_chat(args.provider)
        
        elif args.command == "career":
            cli.career_guidance(args.role, args.experience)
        
        elif args.command == "export":
            cli.export_session(args.format, args.output)
        
        elif args.command == "batch":
            cli.batch_assess(args.input)
        
        elif args.command == "config":
            if args.config_action == "show":
                console.print(Panel(yaml.dump(cli.config, default_flow_style=False), title="Configuration"))
            elif args.config_action == "set":
                cli.config[args.key] = args.value
                cli.save_config()
                console.print(f"[green]Set {args.key} = {args.value}[/green]")
    
    except KeyboardInterrupt:
        console.print("\n[blue]Operation cancelled[/blue]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()