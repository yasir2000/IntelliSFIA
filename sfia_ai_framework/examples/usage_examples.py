"""
Example Usage and Integration Guide for IntelliSFIA Multi-Agent Framework

This module provides comprehensive examples showing how to use the framework
with different LLM providers and scenarios.
"""

import asyncio
import json
import yaml
from typing import Dict, Any, List
from pathlib import Path
import os

# Import SDK
from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig

# Import LLM providers
from sfia_ai_framework.llm.providers import LLMManager, LLMConfig, LLMProvider

# Import models
from sfia_ai_framework.models.sfia_models import SFIASkill, CareerProfile, TeamMember


async def example_basic_setup():
    """Basic setup example with OpenAI"""
    print("🚀 Basic Setup Example")
    print("=" * 50)
    
    # Configure SDK with OpenAI
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        llm_config={
            "default_provider": "openai",
            "providers": {
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY", "your-api-key"),
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7
                }
            }
        }
    )
    
    # Initialize SDK
    async with SFIASDK(config) as sdk:
        # Test basic functionality
        health = await sdk.health_check()
        print(f"✅ Framework health: {health}")
        
        # Query skills
        skills = await sdk.query_skills(category="Technical", limit=5)
        print(f"🎯 Found {len(skills)} technical skills")
        
        # Analyze a skill
        if skills:
            analysis = await sdk.analyze_skill_detailed(skills[0].code)
            print(f"📊 Skill analysis sample: {analysis['detailed_analysis'][:100]}...")


async def example_ollama_local_setup():
    """Setup example with Ollama local models"""
    print("\n🏠 Ollama Local Models Example")
    print("=" * 50)
    
    # Configure SDK with Ollama
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j", 
        neo4j_password="password",
        llm_config={
            "default_provider": "ollama",
            "providers": {
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "model": "llama2",  # or any model you have installed
                    "temperature": 0.7
                }
            }
        }
    )
    
    # Initialize SDK
    async with SFIASDK(config) as sdk:
        # Test with local model
        health = await sdk.health_check()
        print(f"✅ Local model health: {health}")
        
        # Career progression analysis with local model
        progression = await sdk.analyze_career_progression(
            current_role="Junior Developer",
            target_role="Senior Developer",
            timeline="18 months"
        )
        
        print(f"🎯 Career progression insights generated locally")
        print(f"📈 Skill gaps: {len(progression['multi_agent_analysis'])} analyses")


async def example_multi_provider_setup():
    """Multi-provider setup with fallback"""
    print("\n🌐 Multi-Provider Setup Example")
    print("=" * 50)
    
    # Configure multiple providers
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password", 
        llm_config={
            "default_provider": "openai",
            "providers": {
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY", "your-openai-key"),
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7
                },
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "model": "llama2",
                    "temperature": 0.7
                },
                "anthropic": {
                    "api_key": os.getenv("ANTHROPIC_API_KEY", "your-anthropic-key"),
                    "model": "claude-3-sonnet-20240229",
                    "temperature": 0.7
                }
            }
        }
    )
    
    # Initialize SDK
    async with SFIASDK(config) as sdk:
        # Compare responses from different providers
        query = "What are the key skills for a Data Scientist role?"
        
        comparisons = await sdk.compare_llm_responses(query)
        
        print(f"🔍 Compared responses from {len(comparisons)} providers:")
        for provider, response in comparisons.items():
            print(f"  {provider}: {response[:100]}...")


async def example_team_optimization():
    """Team optimization scenario"""
    print("\n👥 Team Optimization Example")
    print("=" * 50)
    
    # Sample project requirements
    project_requirements = {
        "project_name": "AI-Powered Customer Service Platform",
        "duration": "6 months",
        "technology_stack": ["Python", "Machine Learning", "REST APIs", "Cloud Deployment"],
        "team_size": 5,
        "required_skills": [
            "Software Development",
            "Machine Learning",
            "System Architecture", 
            "User Experience Design",
            "Project Management"
        ]
    }
    
    # Sample available team
    available_team = [
        {
            "name": "Alice Johnson",
            "current_role": "Senior Developer",
            "skills": {"Software Development": 5, "System Architecture": 4, "Machine Learning": 3},
            "experience_years": 8
        },
        {
            "name": "Bob Smith", 
            "current_role": "ML Engineer",
            "skills": {"Machine Learning": 5, "Software Development": 4, "Data Analysis": 5},
            "experience_years": 6
        },
        {
            "name": "Carol Davis",
            "current_role": "UX Designer",
            "skills": {"User Experience Design": 5, "User Research": 4, "Prototyping": 4},
            "experience_years": 5
        },
        {
            "name": "David Wilson",
            "current_role": "Project Manager", 
            "skills": {"Project Management": 5, "Agile Methodologies": 4, "Stakeholder Management": 5},
            "experience_years": 10
        }
    ]
    
    # Basic configuration
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        llm_config={
            "default_provider": "openai",
            "providers": {
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY", "demo"),
                    "model": "gpt-3.5-turbo"
                }
            }
        }
    )
    
    async with SFIASDK(config) as sdk:
        # Optimize team composition
        optimization = await sdk.optimize_team_for_project(
            project_requirements, 
            available_team
        )
        
        print(f"🎯 Team optimization completed")
        print(f"📊 Analysis components: {list(optimization['multi_agent_analysis'].keys())}")
        print(f"💡 Strategic insights available")


async def example_skills_gap_analysis():
    """Skills gap analysis scenario"""
    print("\n📈 Skills Gap Analysis Example") 
    print("=" * 50)
    
    # Configure with local Ollama for privacy
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        llm_config={
            "default_provider": "ollama",
            "providers": {
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "model": "llama2",
                    "temperature": 0.6
                }
            }
        }
    )
    
    async with SFIASDK(config) as sdk:
        # Analyze skills gaps for multiple scenarios
        scenarios = [
            ("Junior Developer", "Technical Lead", "2 years"),
            ("Business Analyst", "Product Manager", "18 months"),
            ("System Administrator", "DevOps Engineer", "1 year")
        ]
        
        for current, target, timeline in scenarios:
            print(f"\n🔍 Analyzing: {current} → {target} ({timeline})")
            
            try:
                analysis = await sdk.analyze_career_progression(current, target, timeline)
                print(f"  ✅ Analysis completed with {len(analysis['multi_agent_analysis'])} components")
            except Exception as e:
                print(f"  ❌ Error: {e}")


async def example_organizational_assessment():
    """Organizational skills assessment"""
    print("\n🏢 Organizational Assessment Example")
    print("=" * 50)
    
    # Sample organization data
    organization_data = {
        "company": "TechCorp Solutions",
        "size": "500-1000 employees",
        "industry": "Software Development",
        "departments": [
            {"name": "Engineering", "size": 150, "focus": "Product Development"},
            {"name": "Data Science", "size": 25, "focus": "Analytics & AI"},
            {"name": "DevOps", "size": 30, "focus": "Infrastructure"},
            {"name": "QA", "size": 40, "focus": "Quality Assurance"}
        ],
        "current_challenges": [
            "Scaling development teams",
            "Cloud migration",
            "AI integration",
            "Skills retention"
        ]
    }
    
    # Multi-provider configuration for comprehensive analysis
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687", 
        neo4j_user="neo4j",
        neo4j_password="password",
        llm_config={
            "default_provider": "openai",
            "providers": {
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY", "demo"),
                    "model": "gpt-4",
                    "temperature": 0.7
                },
                "ollama": {
                    "base_url": "http://localhost:11434", 
                    "model": "llama2",
                    "temperature": 0.6
                }
            }
        }
    )
    
    async with SFIASDK(config) as sdk:
        # Comprehensive organizational assessment
        assessment = await sdk.assess_organizational_skills(organization_data)
        
        print(f"🎯 Organizational assessment completed")
        print(f"🏢 Company: {assessment['organization']}")
        print(f"📊 Analysis areas: {list(assessment['multi_agent_analysis'].keys())}")


async def example_cli_integration():
    """Example of CLI-style operations"""
    print("\n💻 CLI Integration Example")
    print("=" * 50)
    
    # Simulate CLI configuration
    cli_config = {
        "framework": {
            "neo4j_uri": "bolt://localhost:7687",
            "neo4j_user": "neo4j", 
            "neo4j_password": "password"
        },
        "llm": {
            "default_provider": "openai",
            "providers": {
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY", "demo"),
                    "model": "gpt-3.5-turbo"
                }
            }
        }
    }
    
    # Convert to SDK config
    sdk_config = SFIASDKConfig(
        neo4j_uri=cli_config["framework"]["neo4j_uri"],
        neo4j_user=cli_config["framework"]["neo4j_user"],
        neo4j_password=cli_config["framework"]["neo4j_password"],
        llm_config=cli_config["llm"]
    )
    
    async with SFIASDK(sdk_config) as sdk:
        # Simulate CLI commands
        print("$ intellisfia skills list --category=Technical --limit=3")
        skills = await sdk.query_skills(category="Technical", limit=3)
        for skill in skills:
            print(f"  - {skill.code}: {skill.title}")
        
        print("\n$ intellisfia analyze skill PROG")
        try:
            analysis = await sdk.analyze_skill_detailed("PROG")
            print(f"  ✅ Analysis completed: {len(analysis)} components")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print("\n$ intellisfia health")
        health = await sdk.health_check()
        print(f"  🟢 Status: {health.get('status', 'unknown')}")


async def example_configuration_management():
    """Configuration management examples"""
    print("\n⚙️  Configuration Management Example")
    print("=" * 50)
    
    # Create sample configurations
    configs = {
        "development": {
            "framework": {
                "neo4j_uri": "bolt://localhost:7687",
                "neo4j_user": "neo4j",
                "neo4j_password": "dev_password"
            },
            "llm": {
                "default_provider": "ollama",
                "providers": {
                    "ollama": {
                        "base_url": "http://localhost:11434",
                        "model": "llama2",
                        "temperature": 0.8
                    }
                }
            }
        },
        "production": {
            "framework": {
                "neo4j_uri": "bolt://prod-neo4j:7687",
                "neo4j_user": "neo4j",
                "neo4j_password": "prod_password"
            },
            "llm": {
                "default_provider": "openai",
                "providers": {
                    "openai": {
                        "api_key": "${OPENAI_API_KEY}",
                        "model": "gpt-4",
                        "temperature": 0.7
                    },
                    "anthropic": {
                        "api_key": "${ANTHROPIC_API_KEY}",
                        "model": "claude-3-sonnet-20240229", 
                        "temperature": 0.7
                    }
                }
            }
        }
    }
    
    # Save configurations
    config_dir = Path("configs")
    config_dir.mkdir(exist_ok=True)
    
    for env, config in configs.items():
        config_file = config_dir / f"{env}.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        print(f"💾 Saved configuration: {config_file}")
    
    # Load and use development config
    dev_config_file = config_dir / "development.yaml"
    if dev_config_file.exists():
        with open(dev_config_file, "r") as f:
            dev_config = yaml.safe_load(f)
        
        sdk_config = SFIASDKConfig(
            neo4j_uri=dev_config["framework"]["neo4j_uri"],
            neo4j_user=dev_config["framework"]["neo4j_user"],
            neo4j_password=dev_config["framework"]["neo4j_password"],
            llm_config=dev_config["llm"]
        )
        
        print(f"📥 Loaded development configuration")
        print(f"🔧 Default provider: {sdk_config.llm_config['default_provider']}")


async def example_error_handling():
    """Error handling and resilience examples"""
    print("\n🛡️  Error Handling Example")
    print("=" * 50)
    
    # Configuration with invalid provider
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        llm_config={
            "default_provider": "invalid_provider",
            "providers": {
                "openai": {
                    "api_key": "invalid_key",
                    "model": "gpt-3.5-turbo"
                }
            }
        }
    )
    
    try:
        async with SFIASDK(config) as sdk:
            # This should handle errors gracefully
            health = await sdk.health_check()
            print(f"🔍 Health check result: {health}")
            
            # Try operations that might fail
            try:
                skills = await sdk.query_skills(limit=1)
                print(f"✅ Skills query successful: {len(skills)} results")
            except Exception as e:
                print(f"❌ Skills query failed: {e}")
            
            try:
                analysis = await sdk.analyze_skill_detailed("NONEXISTENT")
                print(f"✅ Skill analysis successful")
            except Exception as e:
                print(f"❌ Skill analysis failed: {e}")
                
    except Exception as e:
        print(f"❌ SDK initialization failed: {e}")


async def run_all_examples():
    """Run all examples"""
    print("🚀 IntelliSFIA Framework - Comprehensive Examples")
    print("=" * 60)
    
    examples = [
        ("Basic Setup", example_basic_setup),
        ("Ollama Local Models", example_ollama_local_setup),
        ("Multi-Provider Setup", example_multi_provider_setup),
        ("Team Optimization", example_team_optimization),
        ("Skills Gap Analysis", example_skills_gap_analysis),
        ("Organizational Assessment", example_organizational_assessment),
        ("CLI Integration", example_cli_integration),
        ("Configuration Management", example_configuration_management),
        ("Error Handling", example_error_handling)
    ]
    
    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\n❌ {name} failed: {e}")
        
        print("\n" + "─" * 60)
    
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    # Run examples
    asyncio.run(run_all_examples())