"""
IntelliSFIA Framework - Command Line Interface (CLI)

A comprehensive CLI tool for interacting with the IntelliSFIA Framework,
supporting multiple LLM models including Ollama local models.
"""

import click
import asyncio
import json
import yaml
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree
import questionary

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig, SFIASDKContext
from sfia_ai_framework.examples.scenarios import SFIAScenarios
from sfia_ai_framework.models.sfia_models import *

# Initialize Rich console for beautiful output
console = Console()

# Global configuration
CLI_CONFIG_FILE = Path.home() / ".sfia_cli" / "config.yaml"
CLI_HISTORY_FILE = Path.home() / ".sfia_cli" / "history.json"

class CLIConfig:
    """CLI Configuration management"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".sfia_cli"
        self.config_file = self.config_dir / "config.yaml"
        self.history_file = self.config_dir / "history.json"
        self.config = self.load_config()
    
    def ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """Load CLI configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                console.print(f"[red]Error loading config: {e}[/red]")
                return {}
        return self.get_default_config()
    
    def save_config(self):
        """Save CLI configuration"""
        self.ensure_config_dir()
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "neo4j": {
                "uri": "bolt://localhost:7687",
                "user": "neo4j",
                "password": ""
            },
            "llm": {
                "default_provider": "openai",
                "providers": {
                    "openai": {
                        "api_key": "",
                        "model": "gpt-4",
                        "base_url": "https://api.openai.com/v1"
                    },
                    "ollama": {
                        "base_url": "http://localhost:11434",
                        "model": "llama2",
                        "enabled": True
                    },
                    "anthropic": {
                        "api_key": "",
                        "model": "claude-3-sonnet-20240229"
                    },
                    "azure": {
                        "api_key": "",
                        "endpoint": "",
                        "model": "gpt-4",
                        "api_version": "2024-02-15-preview"
                    }
                }
            },
            "agents": {
                "enabled": True,
                "max_iterations": 5,
                "temperature": 0.7,
                "verbose": False
            },
            "reasoning": {
                "enabled": True,
                "ml_models_path": "~/.sfia_cli/ml_models"
            },
            "output": {
                "format": "table",  # table, json, yaml
                "color": True,
                "pager": True
            },
            "logging": {
                "level": "INFO",
                "file": "~/.sfia_cli/sfia_cli.log"
            }
        }
    
    def add_to_history(self, command: str, result: Dict[str, Any]):
        """Add command to history"""
        self.ensure_config_dir()
        history = []
        
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            except:
                history = []
        
        history.append({
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "success": result.get("success", False),
            "duration": result.get("duration", 0)
        })
        
        # Keep only last 100 commands
        history = history[-100:]
        
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving history: {e}[/red]")

# Global CLI config instance
cli_config = CLIConfig()

class SFIACLIContext:
    """CLI Context for managing SDK instance"""
    
    def __init__(self):
        self.sdk: Optional[SFIASDK] = None
        self.scenarios: Optional[SFIAScenarios] = None
        self.config = cli_config.config
    
    async def initialize_sdk(self) -> bool:
        """Initialize SDK with current configuration"""
        try:
            sdk_config = SFIASDKConfig(
                neo4j_uri=self.config["neo4j"]["uri"],
                neo4j_user=self.config["neo4j"]["user"],
                neo4j_password=self.config["neo4j"]["password"],
                openai_api_key=self.get_llm_api_key(),
                enable_agents=self.config["agents"]["enabled"],
                enable_reasoning=self.config["reasoning"]["enabled"]
            )
            
            self.sdk = SFIASDK(sdk_config)
            await self.sdk.initialize()
            self.scenarios = SFIAScenarios(self.sdk)
            
            return True
        except Exception as e:
            console.print(f"[red]SDK initialization failed: {e}[/red]")
            return False
    
    def get_llm_api_key(self) -> Optional[str]:
        """Get API key for the current LLM provider"""
        provider = self.config["llm"]["default_provider"]
        provider_config = self.config["llm"]["providers"].get(provider, {})
        return provider_config.get("api_key")
    
    async def close(self):
        """Close SDK connection"""
        if self.sdk:
            await self.sdk.close()
            self.sdk = None
            self.scenarios = None

# Global CLI context
cli_context = SFIACLIContext()

# Utility functions
def format_output(data: Any, format_type: str = None) -> str:
    """Format output according to configuration"""
    format_type = format_type or cli_config.config["output"]["format"]
    
    if format_type == "json":
        return json.dumps(data, indent=2, default=str)
    elif format_type == "yaml":
        return yaml.dump(data, default_flow_style=False)
    else:
        return str(data)

def create_table(data: List[Dict[str, Any]], title: str = None) -> Table:
    """Create a Rich table from data"""
    if not data:
        return Table(title=title or "No Data")
    
    table = Table(title=title, show_header=True, header_style="bold magenta")
    
    # Add columns
    if data:
        for key in data[0].keys():
            table.add_column(str(key).replace('_', ' ').title())
        
        # Add rows
        for row in data:
            table.add_row(*[str(v) for v in row.values()])
    
    return table

async def ensure_sdk_initialized():
    """Ensure SDK is initialized"""
    if not cli_context.sdk:
        console.print("[yellow]Initializing SDK...[/yellow]")
        success = await cli_context.initialize_sdk()
        if not success:
            raise click.ClickException("Failed to initialize SDK")

# Click CLI setup
@click.group()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """IntelliSFIA Framework Command Line Interface
    
    A comprehensive CLI for intelligent skills analysis using multi-agent AI,
    knowledge graphs, and advanced reasoning capabilities.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if config:
        # Load custom config file
        try:
            with open(config, 'r') as f:
                custom_config = yaml.safe_load(f)
                cli_config.config.update(custom_config)
        except Exception as e:
            console.print(f"[red]Error loading config file: {e}[/red]")

# Configuration commands
@cli.group()
def config():
    """Configuration management commands"""
    pass

@config.command()
def show():
    """Show current configuration"""
    console.print(Panel(Syntax(yaml.dump(cli_config.config, default_flow_style=False), "yaml"), 
                       title="Current Configuration"))

@config.command()
@click.option('--neo4j-uri', help='Neo4j database URI')
@click.option('--neo4j-user', help='Neo4j username')
@click.option('--neo4j-password', help='Neo4j password')
@click.option('--openai-key', help='OpenAI API key')
@click.option('--ollama-url', help='Ollama server URL')
@click.option('--default-provider', type=click.Choice(['openai', 'ollama', 'anthropic', 'azure']), 
              help='Default LLM provider')
def set(neo4j_uri, neo4j_user, neo4j_password, openai_key, ollama_url, default_provider):
    """Set configuration values"""
    config_updated = False
    
    if neo4j_uri:
        cli_config.config["neo4j"]["uri"] = neo4j_uri
        config_updated = True
    
    if neo4j_user:
        cli_config.config["neo4j"]["user"] = neo4j_user
        config_updated = True
    
    if neo4j_password:
        cli_config.config["neo4j"]["password"] = neo4j_password
        config_updated = True
    
    if openai_key:
        cli_config.config["llm"]["providers"]["openai"]["api_key"] = openai_key
        config_updated = True
    
    if ollama_url:
        cli_config.config["llm"]["providers"]["ollama"]["base_url"] = ollama_url
        config_updated = True
    
    if default_provider:
        cli_config.config["llm"]["default_provider"] = default_provider
        config_updated = True
    
    if config_updated:
        cli_config.save_config()
        console.print("[green]Configuration updated successfully![/green]")
    else:
        console.print("[yellow]No configuration changes made[/yellow]")

@config.command()
def init():
    """Initialize configuration interactively"""
    console.print(Panel("SFIA AI Framework CLI Configuration", style="bold blue"))
    
    # Neo4j configuration
    console.print("\n[bold]Neo4j Database Configuration[/bold]")
    neo4j_uri = questionary.text("Neo4j URI:", default=cli_config.config["neo4j"]["uri"]).ask()
    neo4j_user = questionary.text("Neo4j Username:", default=cli_config.config["neo4j"]["user"]).ask()
    neo4j_password = questionary.password("Neo4j Password:").ask()
    
    # LLM configuration
    console.print("\n[bold]LLM Provider Configuration[/bold]")
    default_provider = questionary.select(
        "Default LLM Provider:",
        choices=["openai", "ollama", "anthropic", "azure"],
        default=cli_config.config["llm"]["default_provider"]
    ).ask()
    
    if default_provider == "openai":
        openai_key = questionary.password("OpenAI API Key:").ask()
        if openai_key:
            cli_config.config["llm"]["providers"]["openai"]["api_key"] = openai_key
    
    elif default_provider == "ollama":
        ollama_url = questionary.text(
            "Ollama Server URL:", 
            default=cli_config.config["llm"]["providers"]["ollama"]["base_url"]
        ).ask()
        ollama_model = questionary.text(
            "Ollama Model:", 
            default=cli_config.config["llm"]["providers"]["ollama"]["model"]
        ).ask()
        
        cli_config.config["llm"]["providers"]["ollama"]["base_url"] = ollama_url
        cli_config.config["llm"]["providers"]["ollama"]["model"] = ollama_model
    
    # Agent configuration
    console.print("\n[bold]Agent Configuration[/bold]")
    enable_agents = questionary.confirm("Enable AI Agents?", default=True).ask()
    enable_reasoning = questionary.confirm("Enable Reasoning Engine?", default=True).ask()
    
    # Update configuration
    cli_config.config["neo4j"]["uri"] = neo4j_uri
    cli_config.config["neo4j"]["user"] = neo4j_user
    cli_config.config["neo4j"]["password"] = neo4j_password
    cli_config.config["llm"]["default_provider"] = default_provider
    cli_config.config["agents"]["enabled"] = enable_agents
    cli_config.config["reasoning"]["enabled"] = enable_reasoning
    
    cli_config.save_config()
    console.print("\n[green]Configuration saved successfully![/green]")

# LLM provider commands
@cli.group()
def llm():
    """LLM provider management commands"""
    pass

@llm.command()
def providers():
    """List available LLM providers"""
    providers_data = []
    current_provider = cli_config.config["llm"]["default_provider"]
    
    for name, config in cli_config.config["llm"]["providers"].items():
        providers_data.append({
            "Provider": name,
            "Status": "Active" if name == current_provider else "Available",
            "Model": config.get("model", "N/A"),
            "Base URL": config.get("base_url", "N/A"),
            "Has API Key": "Yes" if config.get("api_key") else "No"
        })
    
    table = create_table(providers_data, "LLM Providers")
    console.print(table)

@llm.command()
@click.argument('provider', type=click.Choice(['openai', 'ollama', 'anthropic', 'azure']))
def switch(provider):
    """Switch to a different LLM provider"""
    old_provider = cli_config.config["llm"]["default_provider"]
    cli_config.config["llm"]["default_provider"] = provider
    cli_config.save_config()
    
    console.print(f"[green]Switched from {old_provider} to {provider}[/green]")

@llm.command()
@click.argument('provider')
@click.argument('model')
def set_model(provider, model):
    """Set model for a specific provider"""
    if provider in cli_config.config["llm"]["providers"]:
        cli_config.config["llm"]["providers"][provider]["model"] = model
        cli_config.save_config()
        console.print(f"[green]Set {provider} model to {model}[/green]")
    else:
        console.print(f"[red]Provider {provider} not found[/red]")

@llm.command()
@click.option('--provider', help='Test specific provider')
async def test(provider):
    """Test LLM provider connectivity"""
    await ensure_sdk_initialized()
    
    test_provider = provider or cli_config.config["llm"]["default_provider"]
    
    console.print(f"[yellow]Testing {test_provider} connectivity...[/yellow]")
    
    try:
        # Simple test using the agent crew
        if cli_context.sdk.agent_crew:
            # Test with a simple query
            test_result = await cli_context.sdk.agent_crew.analyze_skill("PROG")
            console.print(f"[green]{test_provider} is working correctly![/green]")
        else:
            console.print(f"[yellow]Agents not enabled, cannot test {test_provider}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error testing {test_provider}: {e}[/red]")

# SDK commands
@cli.group()
def sdk():
    """SDK management commands"""
    pass

@sdk.command()
async def init():
    """Initialize SDK"""
    with console.status("[bold green]Initializing SDK..."):
        success = await cli_context.initialize_sdk()
    
    if success:
        console.print("[green]SDK initialized successfully![/green]")
    else:
        console.print("[red]SDK initialization failed![/red]")

@sdk.command()
async def status():
    """Show SDK status"""
    if not cli_context.sdk:
        console.print("[red]SDK not initialized[/red]")
        return
    
    status_data = {
        "SDK Status": "Initialized" if cli_context.sdk._initialized else "Not Initialized",
        "Knowledge Graph": "Available" if cli_context.sdk.knowledge_graph else "Not Available",
        "Reasoning Engine": "Available" if cli_context.sdk.reasoning_engine else "Not Available",
        "Agent Crew": "Available" if cli_context.sdk.agent_crew else "Not Available",
        "LLM Provider": cli_config.config["llm"]["default_provider"],
        "Agents Enabled": str(cli_config.config["agents"]["enabled"]),
        "Reasoning Enabled": str(cli_config.config["reasoning"]["enabled"])
    }
    
    table = Table(title="SDK Status", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    for component, status in status_data.items():
        table.add_row(component, status)
    
    console.print(table)

@sdk.command()
async def close():
    """Close SDK connection"""
    await cli_context.close()
    console.print("[green]SDK connection closed[/green]")

# Knowledge Graph commands
@cli.group()
def kg():
    """Knowledge graph commands"""
    pass

@kg.command()
@click.argument('rdf_file', type=click.Path(exists=True))
async def load(rdf_file):
    """Load SFIA ontology from RDF file"""
    await ensure_sdk_initialized()
    
    with console.status(f"[bold green]Loading ontology from {rdf_file}..."):
        result = await cli_context.sdk.load_sfia_ontology(rdf_file)
    
    if result.success:
        console.print(f"[green]Ontology loaded successfully: {result.message}[/green]")
    else:
        console.print(f"[red]Failed to load ontology: {result.message}[/red]")

@kg.command()
async def stats():
    """Show knowledge graph statistics"""
    await ensure_sdk_initialized()
    
    with console.status("[bold green]Fetching statistics..."):
        result = await cli_context.sdk.get_knowledge_graph_statistics()
    
    if result.get("success"):
        stats = result.get("basic_stats", {})
        network = result.get("network_analysis", {})
        
        # Basic statistics table
        basic_table = Table(title="Knowledge Graph Statistics", show_header=True)
        basic_table.add_column("Metric", style="cyan")
        basic_table.add_column("Count", style="green")
        
        for metric, count in stats.items():
            basic_table.add_row(metric.replace('_', ' ').title(), str(count))
        
        console.print(basic_table)
        
        # Network analysis table
        if network:
            network_table = Table(title="Network Analysis", show_header=True)
            network_table.add_column("Metric", style="cyan")
            network_table.add_column("Value", style="green")
            
            for metric, value in network.items():
                network_table.add_row(metric.replace('_', ' ').title(), str(value))
            
            console.print(network_table)
    else:
        console.print(f"[red]Failed to get statistics: {result.get('error')}[/red]")

@kg.command()
@click.option('--category', help='Filter by category')
@click.option('--level', type=int, help='Filter by level')
@click.option('--keyword', help='Filter by keyword')
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
async def query(category, level, keyword, format):
    """Query skills from knowledge graph"""
    await ensure_sdk_initialized()
    
    with console.status("[bold green]Querying skills..."):
        result = await cli_context.sdk.query_skills(category, level, keyword)
    
    if result.get("success"):
        skills = result.get("skills", [])
        
        if format:
            console.print(format_output(skills, format))
        else:
            if skills:
                table = create_table(skills, f"Skills Query Results ({len(skills)} found)")
                console.print(table)
            else:
                console.print("[yellow]No skills found matching criteria[/yellow]")
    else:
        console.print(f"[red]Query failed: {result.get('error')}[/red]")

@kg.command()
@click.option('--output', '-o', default='knowledge_graph.html', help='Output file path')
async def visualize(output):
    """Generate knowledge graph visualization"""
    await ensure_sdk_initialized()
    
    with console.status(f"[bold green]Generating visualization..."):
        result = await cli_context.sdk.visualize_knowledge_graph(output)
    
    if result.get("success"):
        console.print(f"[green]Visualization saved to: {result.get('visualization_file')}[/green]")
    else:
        console.print(f"[red]Visualization failed: {result.get('error')}[/red]")

# Reasoning commands
@cli.group()
def reason():
    """Reasoning engine commands"""
    pass

@reason.command()
@click.argument('current_role')
@click.argument('target_role')
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
async def gaps(current_role, target_role, format):
    """Analyze skill gaps between roles"""
    await ensure_sdk_initialized()
    
    with console.status(f"[bold green]Analyzing skill gaps..."):
        result = await cli_context.sdk.analyze_skill_gaps(current_role, target_role)
    
    if result.get("success"):
        gaps = result.get("skill_gaps", [])
        
        if format:
            console.print(format_output(result, format))
        else:
            if gaps:
                table = create_table(gaps, f"Skill Gaps: {current_role} → {target_role}")
                console.print(table)
            else:
                console.print("[green]No skill gaps found![/green]")
    else:
        console.print(f"[red]Analysis failed: {result.get('error')}[/red]")

@reason.command()
@click.option('--skills', '-s', multiple=True, help='Current skills (can be specified multiple times)')
@click.option('--goal', help='Career goal')
@click.option('--timeline', default='2 years', help='Timeline for career progression')
async def career(skills, goal, timeline):
    """Get career recommendations"""
    await ensure_sdk_initialized()
    
    skills_list = list(skills) if skills else []
    career_goals = {"target_role": goal, "timeline": timeline} if goal else {}
    
    with console.status("[bold green]Generating career recommendations..."):
        result = await cli_context.sdk.recommend_career_paths(skills_list, career_goals)
    
    if result.get("success"):
        recommendations = result.get("recommendations", [])
        
        if recommendations:
            table = create_table(recommendations, "Career Recommendations")
            console.print(table)
        else:
            console.print("[yellow]No career recommendations available[/yellow]")
    else:
        console.print(f"[red]Failed to get recommendations: {result.get('error')}[/red]")

# Agent commands
@cli.group()
def agents():
    """AI agent commands"""
    pass

@agents.command()
@click.argument('current_role')
@click.argument('target_role')
@click.option('--timeline', default='2 years', help='Timeline for progression')
async def career_analysis(current_role, target_role, timeline):
    """Multi-agent career progression analysis"""
    await ensure_sdk_initialized()
    
    if not cli_context.sdk.agent_crew:
        console.print("[red]AI agents not available. Check your LLM configuration.[/red]")
        return
    
    with console.status("[bold green]Running multi-agent career analysis..."):
        result = await cli_context.sdk.analyze_career_progression(current_role, target_role, timeline)
    
    if result.get("success"):
        analysis = result.get("result", {})
        console.print(Panel(format_output(analysis, "yaml"), title="Career Progression Analysis"))
    else:
        console.print(f"[red]Analysis failed: {result.get('error')}[/red]")

@agents.command()
@click.argument('project_file', type=click.Path(exists=True))
async def team_optimization(project_file):
    """Multi-agent team optimization"""
    await ensure_sdk_initialized()
    
    if not cli_context.sdk.agent_crew:
        console.print("[red]AI agents not available. Check your LLM configuration.[/red]")
        return
    
    # Load project requirements from file
    try:
        with open(project_file, 'r') as f:
            project_data = yaml.safe_load(f)
        
        project_requirements = project_data.get("requirements", {})
        available_team = project_data.get("team", [])
        
        with console.status("[bold green]Running multi-agent team optimization..."):
            result = await cli_context.sdk.optimize_project_team(project_requirements, available_team)
        
        if result.get("success"):
            optimization = result.get("result", {})
            console.print(Panel(format_output(optimization, "yaml"), title="Team Optimization Result"))
        else:
            console.print(f"[red]Optimization failed: {result.get('error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]Error loading project file: {e}[/red]")

# Scenario commands
@cli.group()
def scenarios():
    """Real-world scenario commands"""
    pass

@scenarios.command()
async def hiring():
    """Run hiring optimization scenario"""
    await ensure_sdk_initialized()
    
    with console.status("[bold green]Running hiring optimization scenario..."):
        result = await cli_context.scenarios.hiring_optimization_scenario()
    
    # Display results
    console.print(Panel(f"Scenario: {result['scenario']}", style="bold blue"))
    console.print(f"Company: {result['company']}")
    console.print(f"Analysis Date: {result['analysis_date']}")
    
    # Show recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        rec_table = create_table(recommendations, "Hiring Recommendations")
        console.print(rec_table)

@scenarios.command()
async def career_dev():
    """Run career development scenario"""
    await ensure_sdk_initialized()
    
    with console.status("[bold green]Running career development scenario..."):
        result = await cli_context.scenarios.career_development_scenario()
    
    console.print(Panel(format_output(result, "yaml"), title="Career Development Plan"))

@scenarios.command()
async def team_formation():
    """Run team formation scenario"""
    await ensure_sdk_initialized()
    
    with console.status("[bold green]Running team formation scenario..."):
        result = await cli_context.scenarios.team_formation_scenario()
    
    console.print(Panel(format_output(result, "yaml"), title="Team Formation Results"))

@scenarios.command()
async def org_assessment():
    """Run organizational assessment scenario"""
    await ensure_sdk_initialized()
    
    with console.status("[bold green]Running organizational assessment scenario..."):
        result = await cli_context.scenarios.organizational_assessment_scenario()
    
    console.print(Panel(format_output(result, "yaml"), title="Organizational Assessment"))

@scenarios.command()
async def all():
    """Run all scenarios"""
    await ensure_sdk_initialized()
    
    scenarios_list = ["hiring", "career_dev", "team_formation", "org_assessment"]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        for scenario in scenarios_list:
            task = progress.add_task(f"Running {scenario} scenario...", total=1)
            
            try:
                if scenario == "hiring":
                    result = await cli_context.scenarios.hiring_optimization_scenario()
                elif scenario == "career_dev":
                    result = await cli_context.scenarios.career_development_scenario()
                elif scenario == "team_formation":
                    result = await cli_context.scenarios.team_formation_scenario()
                elif scenario == "org_assessment":
                    result = await cli_context.scenarios.organizational_assessment_scenario()
                
                progress.update(task, completed=1)
                console.print(f"[green]✓ {scenario} completed[/green]")
                
            except Exception as e:
                console.print(f"[red]✗ {scenario} failed: {e}[/red]")

# History and utility commands
@cli.command()
def history():
    """Show command history"""
    if cli_config.history_file.exists():
        try:
            with open(cli_config.history_file, 'r') as f:
                history = json.load(f)
            
            history_data = []
            for entry in history[-20:]:  # Show last 20
                history_data.append({
                    "Timestamp": entry["timestamp"][:19],  # Remove microseconds
                    "Command": entry["command"][:50] + "..." if len(entry["command"]) > 50 else entry["command"],
                    "Success": "✓" if entry["success"] else "✗",
                    "Duration": f"{entry['duration']:.2f}s"
                })
            
            if history_data:
                table = create_table(history_data, "Command History (Last 20)")
                console.print(table)
            else:
                console.print("[yellow]No command history found[/yellow]")
        
        except Exception as e:
            console.print(f"[red]Error reading history: {e}[/red]")
    else:
        console.print("[yellow]No command history found[/yellow]")

@cli.command()
def version():
    """Show version information"""
    version_info = {
        "SFIA AI Framework": "1.0.0",
        "CLI Version": "1.0.0",
        "Python": sys.version.split()[0],
        "Platform": sys.platform
    }
    
    table = Table(title="Version Information", show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="green")
    
    for component, version in version_info.items():
        table.add_row(component, version)
    
    console.print(table)

# Enterprise Integration Commands
@cli.group()
def enterprise():
    """Enterprise integration commands for real-time SFIA analysis"""
    pass

@enterprise.command()
@click.option('--config', '-c', help='Path to integration configuration file')
@click.option('--redis-url', default='redis://localhost:6379', help='Redis URL for caching')
async def init(config, redis_url):
    """Initialize enterprise integration"""
    await ensure_sdk_initialized()
    
    with console.status("[bold green]Initializing enterprise integration..."):
        result = await cli_context.sdk.initialize_enterprise_integration(config, redis_url)
    
    if result.success:
        console.print("✅ Enterprise integration initialized successfully", style="green")
    else:
        console.print(f"❌ Failed to initialize: {result.message}", style="red")

@enterprise.command()
@click.option('--employee-id', '-e', required=True, help='Employee ID to analyze')
@click.option('--format', '-f', type=click.Choice(['json', 'table']), default='table', help='Output format')
async def analyze_employee(employee_id, format):
    """Analyze SFIA levels for a specific employee using enterprise data"""
    await ensure_sdk_initialized()
    
    with console.status(f"[bold green]Analyzing employee {employee_id}..."):
        result = await cli_context.sdk.analyze_employee_sfia_levels(employee_id)
    
    if result.get("success"):
        if format == 'json':
            console.print_json(data=result)
        else:
            console.print(f"\n📊 SFIA Analysis for Employee {employee_id}", style="bold blue")
            console.print(f"🕐 Analysis Time: {result['analysis_timestamp']}")
            
            if result['suggestions']:
                table = Table(title=f"SFIA Level Suggestions for {employee_id}")
                table.add_column("Skill", style="cyan")
                table.add_column("Current Level", style="yellow")
                table.add_column("Suggested Level", style="green")
                table.add_column("Confidence", style="magenta")
                table.add_column("Timeline", style="blue")
                
                for suggestion in result['suggestions']:
                    table.add_row(
                        suggestion['skill_name'],
                        str(suggestion.get('current_level', 'N/A')),
                        str(suggestion['suggested_level']),
                        f"{suggestion['confidence_score']:.1%}",
                        suggestion['timeline_estimate']
                    )
                
                console.print(table)
                
                # Show improvement areas for first suggestion
                if result['suggestions'][0].get('improvement_areas'):
                    console.print("\n💡 Key Improvement Areas:", style="bold yellow")
                    for area in result['suggestions'][0]['improvement_areas']:
                        console.print(f"  • {area}")
            else:
                console.print("No SFIA suggestions found for this employee.", style="yellow")
    else:
        console.print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}", style="red")

@enterprise.command()
@click.option('--department', '-d', required=True, help='Department name to analyze')
@click.option('--format', '-f', type=click.Choice(['json', 'summary']), default='summary', help='Output format')
async def analyze_department(department, format):
    """Analyze SFIA levels for all employees in a department"""
    await ensure_sdk_initialized()
    
    with console.status(f"[bold green]Analyzing department {department}..."):
        result = await cli_context.sdk.analyze_department_sfia_levels(department)
    
    if result.get("success"):
        if format == 'json':
            console.print_json(data=result)
        else:
            console.print(f"\n📊 SFIA Analysis for {department} Department", style="bold blue")
            console.print(f"🕐 Analysis Time: {result['analysis_timestamp']}")
            console.print(f"👥 Employees Analyzed: {len(result['employees'])}")
            
            # Summary table
            table = Table(title=f"{department} Department SFIA Summary")
            table.add_column("Employee ID", style="cyan")
            table.add_column("Skills Analyzed", style="yellow")
            table.add_column("Avg Suggested Level", style="green")
            table.add_column("Avg Confidence", style="magenta")
            
            for employee_id, suggestions in result['employees'].items():
                if suggestions:
                    avg_level = sum(s['suggested_level'] for s in suggestions) / len(suggestions)
                    avg_confidence = sum(s['confidence_score'] for s in suggestions) / len(suggestions)
                    
                    table.add_row(
                        employee_id,
                        str(len(suggestions)),
                        f"{avg_level:.1f}",
                        f"{avg_confidence:.1%}"
                    )
            
            console.print(table)
    else:
        console.print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}", style="red")

@enterprise.command()
@click.option('--format', '-f', type=click.Choice(['json', 'dashboard']), default='dashboard', help='Output format')
async def insights(format):
    """Get organization-wide SFIA insights and analytics"""
    await ensure_sdk_initialized()
    
    with console.status("[bold green]Generating organization insights..."):
        result = await cli_context.sdk.get_organization_sfia_insights()
    
    if result.get("success"):
        if format == 'json':
            console.print_json(data=result)
        else:
            console.print("\n🏢 Organization SFIA Insights Dashboard", style="bold blue")
            console.print(f"🕐 Generated: {result.get('analysis_timestamp', 'N/A')}")
            
            # Overview
            console.print(f"\n📊 Overview:")
            console.print(f"  👥 Total Employees: {result.get('total_employees', 0)}")
            console.print(f"  🏢 Departments: {len(result.get('departments', {}))}")
            console.print(f"  🎯 Skills Tracked: {len(result.get('skill_distribution', {}))}")
            
            # Department breakdown
            if result.get('departments'):
                dept_table = Table(title="Department Analysis")
                dept_table.add_column("Department", style="cyan")
                dept_table.add_column("Employees", style="yellow") 
                dept_table.add_column("Avg Level", style="green")
                dept_table.add_column("Skills", style="magenta")
                
                for dept_name, dept_data in result['departments'].items():
                    dept_table.add_row(
                        dept_name,
                        str(dept_data.get('employee_count', 0)),
                        f"{dept_data.get('avg_level', 0):.1f}",
                        str(len(dept_data.get('skills', [])))
                    )
                
                console.print(dept_table)
            
            # Level distribution
            if result.get('level_distribution'):
                console.print(f"\n📈 SFIA Level Distribution:")
                total_assignments = sum(result['level_distribution'].values())
                for level, count in sorted(result['level_distribution'].items()):
                    percentage = (count / total_assignments) * 100 if total_assignments > 0 else 0
                    bar = "█" * int(percentage / 5)  # Simple bar chart
                    console.print(f"  Level {level}: {count:3d} assignments {bar} ({percentage:.1f}%)")
            
            # High performers
            if result.get('high_performers'):
                console.print(f"\n⭐ Top Performers ({len(result['high_performers'])} found):")
                for performer in result['high_performers'][:5]:  # Top 5
                    console.print(f"  • {performer['employee_id']}: {performer['skill']} Level {performer['level']}")
    else:
        console.print(f"❌ Failed to get insights: {result.get('error', 'Unknown error')}", style="red")

@enterprise.command()
@click.option('--department', '-d', help='Department to generate report for (optional)')
@click.option('--output', '-o', help='Output file path for the report')
async def compliance_report(department, output):
    """Generate SFIA compliance report for audit and governance"""
    await ensure_sdk_initialized()
    
    with console.status("[bold green]Generating compliance report..."):
        result = await cli_context.sdk.generate_sfia_compliance_report(department)
    
    if result.get("success"):
        if output:
            import json
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            console.print(f"✅ Report saved to {output}", style="green")
        
        console.print(f"\n📋 SFIA Compliance Report", style="bold blue")
        console.print(f"🎯 Scope: {result['scope']}")
        console.print(f"🕐 Generated: {result['generated_at']}")
        
        summary = result['summary']
        console.print(f"\n📊 Summary:")
        console.print(f"  👥 Employees Analyzed: {summary['total_employees_analyzed']}")
        console.print(f"  🎯 Skills Assessed: {summary['skills_assessed']}")
        console.print(f"  📈 Average Confidence: {summary['average_confidence_score']:.1%}")
        console.print(f"  ✅ Compliance Rate: {summary['compliance_percentage']:.1%}")
        
        if result.get('recommendations'):
            console.print(f"\n💡 Key Recommendations:")
            for rec in result['recommendations'][:5]:
                console.print(f"  • {rec}")
    else:
        console.print(f"❌ Failed to generate report: {result.get('error', 'Unknown error')}", style="red")

@enterprise.command()
async def health():
    """Check health status of connected enterprise systems"""
    await ensure_sdk_initialized()
    
    with console.status("[bold green]Checking system health..."):
        result = await cli_context.sdk.get_system_health_status()
    
    if result.get("success"):
        console.print(f"\n🏥 System Health Status", style="bold blue")
        console.print(f"🕐 Checked: {result['timestamp']}")
        
        health_table = Table(title="Connected Systems Health")
        health_table.add_column("System", style="cyan")
        health_table.add_column("Status", style="green")
        health_table.add_column("Endpoint", style="yellow")
        health_table.add_column("Last Check", style="magenta")
        
        for system_name, health_data in result['systems'].items():
            status_icon = "✅" if health_data['status'] == 'healthy' else "❌"
            
            health_table.add_row(
                system_name,
                f"{status_icon} {health_data['status']}",
                health_data.get('endpoint', 'N/A'),
                health_data.get('timestamp', 'N/A')
            )
        
        console.print(health_table)
    else:
        console.print(f"❌ Failed to check health: {result.get('error', 'Unknown error')}", style="red")


# Interactive shell command
@cli.command()
async def shell():
    """Start interactive shell"""
    console.print(Panel("SFIA AI Framework Interactive Shell", style="bold blue"))
    console.print("Type 'help' for available commands or 'exit' to quit.")
    
    await ensure_sdk_initialized()
    
    while True:
        try:
            command = questionary.text("sfia> ").ask()
            
            if command.lower() in ['exit', 'quit']:
                break
            elif command.lower() == 'help':
                console.print("""
Available commands:
- kg stats          : Show knowledge graph statistics
- kg query          : Query skills
- reason gaps <current> <target> : Analyze skill gaps
- agents career_analysis <current> <target> : AI career analysis
- scenarios hiring  : Run hiring scenario
- config show       : Show configuration
- exit/quit         : Exit shell
                """)
            else:
                # Parse and execute command
                try:
                    # This is a simplified command parser
                    # In a full implementation, you'd use click's command parsing
                    console.print(f"[yellow]Executing: {command}[/yellow]")
                except Exception as e:
                    console.print(f"[red]Command error: {e}[/red]")
        
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    console.print("Goodbye!")


# Portfolio Assessment Commands (IoC Methodology)
@cli.group()
def portfolio():
    """Portfolio assessment using IoC (Institute of Coding) methodology"""
    pass

@portfolio.command()
@click.option('--portfolio-file', '-p', required=True, type=click.Path(exists=True), 
              help='Path to portfolio entries JSON file')
@click.option('--supervisor-file', '-s', required=True, type=click.Path(exists=True),
              help='Path to supervisor comments JSON file')
@click.option('--student-name', required=True, help='Student name')
@click.option('--assessor-name', required=True, help='Assessor name')
@click.option('--skill-code', '-k', help='Suggested SFIA skill code (e.g., DTAN)')
@click.option('--skill-level', '-l', type=int, help='Suggested SFIA level (1-7)')
@click.option('--output', '-o', type=click.Path(), help='Output file for assessment results')
def assess(portfolio_file, supervisor_file, student_name, assessor_name, skill_code, skill_level, output):
    """Assess student portfolio using IoC methodology"""
    async def _assess():
        try:
            # Load portfolio data
            with open(portfolio_file, 'r', encoding='utf-8') as f:
                portfolio_entries = json.load(f)
            
            with open(supervisor_file, 'r', encoding='utf-8') as f:
                supervisor_comments = json.load(f)
            
            student_info = {
                'id': f"student_{datetime.now().strftime('%Y%m%d')}",
                'name': student_name
            }
            
            assessor_info = {
                'id': f"assessor_{datetime.now().strftime('%Y%m%d')}",
                'name': assessor_name
            }
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Assessing portfolio using IoC methodology...", total=None)
                
                async with SFIASDKContext(cli_context.get_sdk_config()) as sdk:
                    result = await sdk.assess_portfolio(
                        portfolio_entries=portfolio_entries,
                        supervisor_comments=supervisor_comments,
                        student_info=student_info,
                        assessor_info=assessor_info,
                        suggested_skill=skill_code,
                        suggested_level=skill_level
                    )
            
            if result.success:
                # Display results
                console.print(f"\n[bold green]✓ Portfolio Assessment Complete[/bold green]")
                console.print(f"Status: {result.message}")
                
                if result.summary:
                    summary = result.summary
                    
                    # Create results table
                    table = Table(title="Portfolio Assessment Summary")
                    table.add_column("Metric", style="cyan")
                    table.add_column("Value", style="magenta")
                    
                    table.add_row("Student", summary.student_name)
                    table.add_row("Skill Assessed", summary.skill_assessed)
                    table.add_row("Level", str(summary.level_assessed))
                    table.add_row("Total Score", f"{summary.total_score:.1f}/100")
                    table.add_row("Technical Score", f"{summary.technical_score:.1f}/64")
                    table.add_row("Reflection Score", f"{summary.reflection_score:.1f}/36")
                    table.add_row("Proficiency Level", summary.proficiency_level.value.title())
                    table.add_row("Overall Pass", "✓" if summary.pass_status else "✗")
                    table.add_row("Generic Responsibility", "✓" if summary.generic_responsibility_pass else "✗")
                    
                    console.print(table)
                    
                    # Show recommendations
                    if result.recommendations:
                        console.print(f"\n[bold blue]📝 Recommendations:[/bold blue]")
                        for i, rec in enumerate(result.recommendations, 1):
                            console.print(f"{i}. {rec}")
                
                # Save results if output specified
                if output:
                    with open(output, 'w', encoding='utf-8') as f:
                        json.dump(result.dict(), f, indent=2, default=str)
                    console.print(f"\n[dim]Results saved to: {output}[/dim]")
                
            else:
                console.print(f"[bold red]✗ Assessment failed: {result.message}[/bold red]")
                
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
    
    asyncio.run(_assess())

@portfolio.command()
@click.option('--activities', '-a', required=True, help='Description of student activities')
@click.option('--level', '-l', default='placement', help='Student level (placement, graduate, etc.)')
def guidance(activities, level):
    """Get portfolio mapping guidance"""
    async def _guidance():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating portfolio guidance...", total=None)
                
                async with SFIASDKContext(cli_context.get_sdk_config()) as sdk:
                    guidance = await sdk.get_portfolio_mapping_guidance(
                        activities_description=activities,
                        student_level=level
                    )
            
            # Display recommended skills
            if guidance.recommended_skills:
                console.print(f"\n[bold blue]🎯 Recommended SFIA Skills:[/bold blue]")
                
                skills_table = Table()
                skills_table.add_column("Skill Code", style="cyan")
                skills_table.add_column("Skill Name", style="white")
                skills_table.add_column("Level", style="magenta")
                skills_table.add_column("Confidence", style="green")
                
                for skill in guidance.recommended_skills:
                    skills_table.add_row(
                        skill['skill_code'],
                        skill['skill_name'],
                        str(skill['suggested_level']),
                        f"{skill['confidence']:.2f}"
                    )
                
                console.print(skills_table)
            
            # Display mapping suggestions
            if guidance.mapping_suggestions:
                console.print(f"\n[bold blue]💡 Mapping Suggestions:[/bold blue]")
                for suggestion in guidance.mapping_suggestions:
                    panel = Panel(
                        f"[bold]{suggestion['description']}[/bold]\n\n"
                        f"Example: {suggestion['example']}",
                        title=suggestion['title'],
                        border_style="blue"
                    )
                    console.print(panel)
            
            # Display best practices
            if guidance.best_practices:
                console.print(f"\n[bold green]✨ Best Practices:[/bold green]")
                for i, practice in enumerate(guidance.best_practices, 1):
                    console.print(f"{i}. {practice}")
                    
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
    
    asyncio.run(_guidance())

@portfolio.command()
@click.option('--portfolio-file', '-p', required=True, type=click.Path(exists=True),
              help='Path to portfolio entries JSON file')
@click.option('--skill-code', '-k', required=True, help='SFIA skill code to validate against')
@click.option('--skill-level', '-l', required=True, type=int, help='SFIA level to validate against')
def validate(portfolio_file, skill_code, skill_level):
    """Validate portfolio evidence against SFIA requirements"""
    async def _validate():
        try:
            # Load portfolio data
            with open(portfolio_file, 'r', encoding='utf-8') as f:
                portfolio_entries = json.load(f)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Validating portfolio evidence...", total=None)
                
                async with SFIASDKContext(cli_context.get_sdk_config()) as sdk:
                    validation = await sdk.validate_portfolio_evidence(
                        portfolio_entries=portfolio_entries,
                        skill_code=skill_code,
                        skill_level=skill_level
                    )
            
            if validation.get('success'):
                console.print(f"\n[bold green]✓ Portfolio Validation Complete[/bold green]")
                
                metrics = validation['coverage_metrics']
                
                # Coverage metrics table
                table = Table(title=f"Coverage Analysis: {skill_code} Level {skill_level}")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="magenta")
                table.add_column("IoC Requirement", style="yellow")
                
                table.add_row("Total Components", str(metrics['total_components']), "All")
                table.add_row("Covered Components", str(metrics['covered_components']), "85%+")
                table.add_row("Coverage Percentage", f"{metrics['coverage_percentage']:.1f}%", "85%")
                table.add_row("Multiple Entry Components", str(metrics['multiple_entry_components']), "85%+")
                table.add_row("Multiple Entry Percentage", f"{metrics['multiple_entry_percentage']:.1f}%", "85%")
                
                console.print(table)
                
                # IoC criteria status
                meets_criteria = validation['meets_ioc_criteria']
                status_color = "green" if meets_criteria else "red"
                status_icon = "✓" if meets_criteria else "✗"
                console.print(f"\n[bold {status_color}]{status_icon} Meets IoC Criteria: {meets_criteria}[/bold {status_color}]")
                
                # Recommendations
                if validation['recommendations']:
                    console.print(f"\n[bold blue]📝 Recommendations:[/bold blue]")
                    for i, rec in enumerate(validation['recommendations'], 1):
                        console.print(f"{i}. {rec}")
                
            else:
                console.print(f"[bold red]✗ Validation failed: {validation.get('error', 'Unknown error')}[/bold red]")
                
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
    
    asyncio.run(_validate())

@portfolio.command()
@click.option('--skill-code', '-k', required=True, help='SFIA skill code')
@click.option('--skill-level', '-l', required=True, type=int, help='SFIA level')
@click.option('--placement', '-p', help='Placement/internship context')
@click.option('--output', '-o', type=click.Path(), help='Output file for template')
def template(skill_code, skill_level, placement, output):
    """Generate portfolio template for specific SFIA skill"""
    async def _template():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating portfolio template...", total=None)
                
                async with SFIASDKContext(cli_context.get_sdk_config()) as sdk:
                    template = await sdk.generate_portfolio_template(
                        skill_code=skill_code,
                        skill_level=skill_level,
                        placement_context=placement
                    )
            
            if template.get('success'):
                console.print(f"\n[bold green]✓ Portfolio Template Generated[/bold green]")
                console.print(f"Skill: {template['skill_name']} ({skill_code}) Level {skill_level}")
                
                if output:
                    # Save complete template to file
                    with open(output, 'w', encoding='utf-8') as f:
                        json.dump(template, f, indent=2, default=str)
                    console.print(f"\n[dim]Template saved to: {output}[/dim]")
                else:
                    # Display summary in console
                    console.print(f"\n[bold blue]📋 Template Structure:[/bold blue]")
                    
                    structure = template['portfolio_structure']
                    
                    # Technical achievement
                    tech_panel = Panel(
                        f"Weight: {template['assessment_criteria']['technical_achievement']['weight']}\n\n"
                        + "\n".join(f"• {req}" for req in structure['technical_achievement_entries']['requirements']),
                        title="Technical Achievement Entries",
                        border_style="blue"
                    )
                    console.print(tech_panel)
                    
                    # Reflection
                    reflection_panel = Panel(
                        f"Weight: {template['assessment_criteria']['reflection']['weight']}\n\n"
                        + "\n".join(f"• {topic}" for topic in structure['reflection_entries']['suggested_topics'][:3]),
                        title="Reflection Entries",
                        border_style="green"
                    )
                    console.print(reflection_panel)
                    
                    # Scoring thresholds
                    console.print(f"\n[bold yellow]🎯 Scoring Thresholds:[/bold yellow]")
                    thresholds = template['scoring_thresholds']
                    console.print(f"• Competency: {thresholds['competency']}+")
                    console.print(f"• Proficiency: {thresholds['proficiency']}+")
                    console.print(f"• Developing: {thresholds['developing']}")
                
            else:
                console.print(f"[bold red]✗ Template generation failed: {template.get('error', 'Unknown error')}[/bold red]")
                
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
    
    asyncio.run(_template())

@portfolio.command()
def methodology():
    """Display IoC portfolio mapping methodology information"""
    console.print(f"\n[bold blue]📚 IoC Portfolio Mapping Methodology[/bold blue]")
    console.print("Institute of Coding (IoC) criterion-based assessment approach")
    
    # Assessment components
    console.print(f"\n[bold green]🔍 Assessment Components:[/bold green]")
    
    tech_panel = Panel(
        "Weight: 16 points\n\n"
        "• Multiple entries for 85%+ of skill components\n"
        "• Supervisor verification of accuracy\n"
        "• Evidence-based content with specific details\n"
        "• Contextual evaluation by supervisor",
        title="Technical Achievement",
        border_style="blue"
    )
    console.print(tech_panel)
    
    reflection_panel = Panel(
        "Weight: 9 points\n\n"
        "• Professional writing style\n"
        "• Personal development identification\n"
        "• Professional accountability demonstration\n"
        "• Evidence-based reflection with comparisons",
        title="Reflection",
        border_style="green"
    )
    console.print(reflection_panel)
    
    generic_panel = Panel(
        "SFIA generic responsibility characteristics:\n\n"
        "• 13+ of 17 core characteristics demonstrated\n"
        "• 26+ instances of core characteristics\n"
        "• 44+ total instances of all characteristics",
        title="Generic Responsibility Characteristics",
        border_style="yellow"
    )
    console.print(generic_panel)
    
    # Scoring thresholds
    console.print(f"\n[bold yellow]🎯 Scoring Thresholds:[/bold yellow]")
    console.print("• [bold green]Competency:[/bold green] 85+ points")
    console.print("• [bold blue]Proficiency:[/bold blue] 65+ points")
    console.print("• [bold red]Developing:[/bold red] Below 65 points")
    
    # Best practices
    console.print(f"\n[bold cyan]✨ Best Practices:[/bold cyan]")
    practices = [
        "Document separate achievements rather than incremental progress",
        "Include specific details like numbers, quantities, examples",
        "Demonstrate challenges encountered and solutions applied",
        "Show progression and development over time",
        "Include supervisor verification and contextual comments",
        "Reflect on business impact and professional accountability"
    ]
    
    for i, practice in enumerate(practices, 1):
        console.print(f"{i}. {practice}")


# ============================================================================
# SFIA 9 Enhanced Framework Commands
# ============================================================================

@cli.group()
def sfia9():
    """SFIA 9 enhanced framework commands"""
    pass

@sfia9.command()
@click.argument('code')
def attribute(code):
    """Get SFIA 9 attribute by code"""
    async def _get_attribute():
        async with create_cli_context() as ctx:
            attribute = ctx.sdk.get_sfia9_attribute(code.upper())
            
            if not attribute:
                console.print(f"[red]Attribute {code} not found[/red]")
                return
            
            # Display attribute details
            table = Table(title=f"SFIA 9 Attribute: {attribute.name}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Code", attribute.code)
            table.add_row("Name", attribute.name)
            table.add_row("Type", attribute.type)
            table.add_row("URL", attribute.url or "N/A")
            table.add_row("Available Levels", ", ".join(attribute.levels))
            
            console.print(table)
            
            # Display description
            console.print(Panel(attribute.description, title="Description"))
            
            # Display guidance notes
            if attribute.guidance_notes:
                console.print(Panel(attribute.guidance_notes, title="Guidance Notes"))
            
            # Display level descriptions
            if attribute.level_descriptions:
                console.print("\n[bold]Level Descriptions:[/bold]")
                for level, desc in attribute.level_descriptions.items():
                    console.print(f"[cyan]Level {level}:[/cyan] {desc[:200]}...")
    
    asyncio.run(_get_attribute())

@sfia9.command()
@click.argument('code')
def skill(code):
    """Get SFIA 9 skill by code"""
    async def _get_skill():
        async with create_cli_context() as ctx:
            skill = ctx.sdk.get_sfia9_skill(code.upper())
            
            if not skill:
                console.print(f"[red]Skill {code} not found[/red]")
                return
            
            # Display skill details
            table = Table(title=f"SFIA 9 Skill: {skill.name}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Code", skill.code)
            table.add_row("Name", skill.name)
            table.add_row("Category", skill.category)
            table.add_row("Subcategory", skill.subcategory)
            table.add_row("URL", skill.url or "N/A")
            table.add_row("Available Levels", ", ".join(map(str, skill.available_levels)))
            
            console.print(table)
            
            # Display description
            console.print(Panel(skill.description, title="Description"))
            
            # Display guidance notes
            if skill.guidance_notes:
                console.print(Panel(skill.guidance_notes[:500] + "...", title="Guidance Notes"))
    
    asyncio.run(_get_skill())

@sfia9.command()
@click.argument('query')
@click.option('--limit', '-l', default=10, help='Maximum number of results')
def search(query, limit):
    """Search SFIA 9 skills"""
    async def _search_skills():
        async with create_cli_context() as ctx:
            skills = ctx.sdk.search_sfia9_skills(query, limit)
            
            if not skills:
                console.print(f"[red]No skills found for query: {query}[/red]")
                return
            
            # Display search results
            table = Table(title=f"SFIA 9 Skills Search: '{query}'")
            table.add_column("Code", style="cyan")
            table.add_column("Name", style="white")
            table.add_column("Category", style="green")
            table.add_column("Levels", style="yellow")
            
            for skill in skills:
                levels_str = ", ".join(map(str, skill.available_levels))
                table.add_row(skill.code, skill.name[:40], skill.category[:20], levels_str)
            
            console.print(table)
            console.print(f"\n[green]Found {len(skills)} skills[/green]")
    
    asyncio.run(_search_skills())

@sfia9.command()
@click.argument('category')
def category(category):
    """Get SFIA 9 skills by category"""
    async def _get_category():
        async with create_cli_context() as ctx:
            overview = ctx.sdk.get_sfia9_category_overview(category)
            
            if "error" in overview:
                console.print(f"[red]{overview['error']}[/red]")
                return
            
            # Display category overview
            console.print(f"[bold]Category: {category}[/bold]")
            console.print(f"Total Skills: {overview['total_skills']}")
            console.print(f"Subcategories: {', '.join(overview['subcategories'])}")
            
            # Display level distribution
            console.print("\n[bold]Level Distribution:[/bold]")
            for level, count in sorted(overview['level_distribution'].items()):
                console.print(f"Level {level}: {count} skills")
            
            # Display skills
            if overview['skills']:
                table = Table(title="Skills in Category")
                table.add_column("Code", style="cyan")
                table.add_column("Name", style="white")
                table.add_column("Levels", style="yellow")
                
                for skill in overview['skills']:
                    levels_str = ", ".join(map(str, skill['levels']))
                    table.add_row(skill['code'], skill['name'], levels_str)
                
                console.print(table)
    
    asyncio.run(_get_category())

@sfia9.command()
def statistics():
    """Get SFIA 9 framework statistics"""
    async def _get_statistics():
        async with create_cli_context() as ctx:
            stats = ctx.sdk.get_sfia9_statistics()
            
            # Display statistics
            table = Table(title="SFIA 9 Framework Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")
            
            for key, value in stats.items():
                if key != 'data_loaded':
                    table.add_row(key.replace('_', ' ').title(), str(value))
            
            console.print(table)
            
            if stats.get('data_loaded'):
                console.print("[green]✓ SFIA 9 data successfully loaded[/green]")
            else:
                console.print("[red]✗ SFIA 9 data not loaded[/red]")
    
    asyncio.run(_get_statistics())

@sfia9.command()
@click.argument('skill_code')
@click.argument('level', type=int)
@click.argument('evidence')
def assess(skill_code, level, evidence):
    """Assess evidence against SFIA 9 skill and level"""
    async def _assess_evidence():
        async with create_cli_context() as ctx:
            assessment = ctx.sdk.assess_sfia9_skill_evidence(skill_code.upper(), level, evidence)
            
            if "error" in assessment:
                console.print(f"[red]{assessment['error']}[/red]")
                return
            
            # Display assessment results
            console.print(f"[bold]Assessment Results: {skill_code} Level {level}[/bold]")
            console.print(f"Match Score: {assessment['match_score']:.2f}")
            console.print(f"Assessment: {assessment['assessment']}")
            
            if assessment.get('recommendations'):
                console.print("\n[bold]Recommendations:[/bold]")
                for rec in assessment['recommendations']:
                    console.print(f"• {rec}")
    
    asyncio.run(_assess_evidence())


# Main CLI entry point
if __name__ == '__main__':
    try:
        cli()
    finally:
        # Cleanup
        if cli_context.sdk:
            asyncio.run(cli_context.close())