# SFIA AI Framework - Complete SDK and Web Application

A comprehensive AI-powered framework for intelligent Skills Framework for the Information Age (SFIA) analysis, featuring multi-agent collaboration, knowledge graphs, and advanced reasoning capabilities.

## 🎯 Overview

The SFIA AI Framework transforms how organizations understand, analyze, and leverage skills data through:

- **🤖 Multi-Agent Intelligence**: CrewAI-powered specialized agents for comprehensive analysis
- **🕸️ Knowledge Graph**: Neo4j-based semantic understanding and relationship mapping
- **🧠 Advanced Reasoning**: ML-powered inference engine for intelligent decision making
- **📊 Interactive Dashboards**: Real-time insights and visualizations
- **🔗 Complete SDK**: Easy integration for developers and applications
- **🌐 Web Applications**: Both Streamlit and FastAPI interfaces

## 🏗️ Architecture

```
sfia_ai_framework/
├── core/                    # Core framework components
│   ├── agents.py           # Multi-agent system with CrewAI
│   ├── knowledge_graph.py  # Neo4j knowledge graph implementation
│   └── reasoning.py        # ML-powered reasoning engine
├── models/                 # Data models and schemas
│   └── sfia_models.py      # Pydantic models for all entities
├── sdk/                    # Software Development Kit
│   └── __init__.py         # Complete SDK interface
├── examples/               # Real-world scenarios and examples
│   └── scenarios.py        # Comprehensive scenarios implementation
├── web/                    # Web applications
│   ├── app.py             # Streamlit interactive dashboard
│   └── api.py             # FastAPI REST API server
└── tests/                  # Comprehensive test suite
    └── test_framework.py   # Integration and unit tests
```

## 🚀 Quick Start

### Prerequisites

1. **Neo4j Database**: Download and install from [Neo4j](https://neo4j.com/download/)
2. **Python 3.11+**: Ensure you have Python 3.11 or higher
3. **OpenAI API Key**: Optional, for AI agent capabilities

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd sfia_ai_framework

# Install dependencies
pip install -r requirements.txt

# Or using Poetry
poetry install
```

### Basic Usage

```python
import asyncio
from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig, SFIASDKContext

async def main():
    # Configure SDK
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="your_password",
        openai_api_key="your_openai_key"  # Optional
    )
    
    # Use SDK with context manager
    async with SFIASDKContext(config) as sdk:
        # Load SFIA ontology
        await sdk.load_sfia_ontology("path/to/sfia.ttl")
        
        # Analyze skill gaps
        result = await sdk.analyze_skill_gaps(
            current_role="Junior Developer",
            target_role="Senior Developer"
        )
        
        print(f"Skill gaps identified: {len(result.get('skill_gaps', []))}")

# Run the example
asyncio.run(main())
```

## 🎯 Key Features

### 1. Multi-Agent Intelligence

The framework includes five specialized AI agents:

- **Skills Analyst**: Deep analysis of skills, competencies, and relationships
- **Career Advisor**: Personalized career progression recommendations
- **Team Specialist**: Optimal team composition and collaboration analysis
- **Learning Specialist**: Personalized learning paths and resource recommendations
- **Workforce Planner**: Strategic workforce planning and organizational insights

```python
# Multi-agent career analysis
result = await sdk.analyze_career_progression(
    current_role="Developer",
    target_role="Solution Architect",
    timeline="2 years"
)
```

### 2. Knowledge Graph Operations

Semantic understanding through Neo4j-powered knowledge graphs:

```python
# Query skills by category and level
skills = await sdk.query_skills(
    category="Development",
    level=4,
    keyword="programming"
)

# Get comprehensive statistics
stats = await sdk.get_knowledge_graph_statistics()

# Generate interactive visualization
viz = await sdk.visualize_knowledge_graph("output.html")
```

### 3. Advanced Reasoning Engine

ML-powered reasoning for intelligent insights:

```python
# Career path recommendations
recommendations = await sdk.recommend_career_paths(
    current_skills=["PROG", "SENG", "TEST"],
    career_goals={"target_role": "Tech Lead", "timeline": "18 months"}
)

# Team optimization
optimization = await sdk.optimize_team_composition(
    project_requirements={"skills": ["PROG", "ARCH", "UNAN"], "duration": "6 months"},
    available_team=[...]
)
```

### 4. Real-World Scenarios

The framework includes comprehensive scenarios for common use cases:

#### Hiring Optimization
```python
from sfia_ai_framework.examples.scenarios import SFIAScenarios

scenarios = SFIAScenarios(sdk)
hiring_result = await scenarios.hiring_optimization_scenario()
```

#### Career Development Planning
```python
career_result = await scenarios.career_development_scenario()
```

#### Team Formation
```python
team_result = await scenarios.team_formation_scenario()
```

#### Organizational Assessment
```python
org_result = await scenarios.organizational_assessment_scenario()
```

## 🌐 Web Applications

### Streamlit Dashboard

Interactive web interface for exploring SFIA data and AI capabilities:

```bash
# Run Streamlit app
streamlit run sfia_ai_framework/web/app.py
```

Features:
- 📊 Real-time knowledge graph statistics
- 👥 Hiring optimization interface
- 📈 Career development planning
- 🔧 Team formation tools
- 🏢 Organizational analysis
- 📊 Skills insights and analytics

### FastAPI REST API

Professional REST API for programmatic access:

```bash
# Run FastAPI server
uvicorn sfia_ai_framework.web.api:app --reload
```

Key endpoints:
- `POST /sdk/initialize` - Initialize the framework
- `GET /knowledge-graph/statistics` - Get graph statistics
- `POST /reasoning/skill-gaps` - Analyze skill gaps
- `POST /agents/career-progression` - Multi-agent career analysis
- `POST /scenarios/hiring-optimization` - Run hiring scenario

API Documentation: `http://localhost:8000/docs`

## 🎭 Multi-Agent Scenarios

### 1. Hiring Optimization

**Scenario**: Tech company needs to optimize hiring decisions for multiple roles.

**Process**:
1. Analyze job requirements and candidate profiles
2. Calculate skill fit scores and development potential
3. Generate hiring recommendations with reasoning
4. Provide onboarding timelines and development plans

**Output**: Detailed candidate rankings, fit analysis, and strategic hiring recommendations.

### 2. Career Development Planning

**Scenario**: Individual employee seeks personalized career progression path.

**Process**:
1. Assess current skills and experience level
2. Analyze career aspirations and learning preferences
3. Identify skill gaps and development priorities
4. Generate comprehensive learning plan with resources

**Output**: Personalized development roadmap with timelines and success metrics.

### 3. Team Formation & Optimization

**Scenario**: Organization needs to form optimal teams for multiple projects.

**Process**:
1. Analyze project requirements and available talent
2. Optimize team composition for skill coverage
3. Identify development opportunities within projects
4. Balance workload and growth potential

**Output**: Optimized team assignments with skill coverage analysis and development opportunities.

### 4. Organizational Skills Assessment

**Scenario**: Enterprise-wide skills assessment for strategic planning.

**Process**:
1. Analyze current organizational capabilities
2. Identify skills gaps relative to strategic initiatives
3. Generate workforce development recommendations
4. Create strategic skills roadmap

**Output**: Comprehensive organizational skills report with strategic recommendations.

## 🔧 SDK Reference

### Core Classes

#### SFIASDK
Main SDK class providing unified access to all framework capabilities.

```python
sdk = SFIASDK(config)
await sdk.initialize()

# Knowledge graph operations
await sdk.load_sfia_ontology(rdf_file)
await sdk.query_skills(category, level, keyword)
await sdk.get_knowledge_graph_statistics()

# Reasoning operations
await sdk.analyze_skill_gaps(current_role, target_role)
await sdk.recommend_career_paths(skills, goals)
await sdk.optimize_team_composition(requirements, team)

# Agent operations
await sdk.analyze_career_progression(current, target, timeline)
await sdk.optimize_project_team(requirements, team)
await sdk.assess_organizational_skills(org_data)

# Utility operations
await sdk.visualize_knowledge_graph(output_file)
await sdk.export_knowledge_graph(format, output_file)
```

#### SFIASDKConfig
Configuration class for SDK initialization.

```python
config = SFIASDKConfig(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    openai_api_key="sk-...",  # Optional
    enable_agents=True,
    enable_reasoning=True,
    log_level="INFO"
)
```

### Data Models

The framework includes comprehensive Pydantic models for all SFIA entities:

- `Skill`: SFIA skills with levels and relationships
- `ProfessionalRole`: Job roles and requirements
- `CareerPathway`: Career progression paths
- `CompetencyProfile`: Individual competency assessments
- `LearningResource`: Training and development resources
- `TeamComposition`: Team structures and optimization
- `Assessment`: Skills assessments and results

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest sfia_ai_framework/tests/

# Run with coverage
python -m pytest --cov=sfia_ai_framework sfia_ai_framework/tests/

# Run specific test category
python -m pytest sfia_ai_framework/tests/test_framework.py::TestSDK
```

## 📊 Performance & Scalability

### Knowledge Graph Performance
- **Neo4j Optimization**: Indexed relationships and optimized queries
- **Batch Operations**: Efficient bulk data loading and updates
- **Connection Pooling**: Managed database connections

### AI Agent Efficiency
- **Parallel Processing**: Concurrent agent execution
- **Caching**: Intelligent caching of agent results
- **Rate Limiting**: Managed API calls to external services

### Reasoning Engine Scalability
- **ML Model Optimization**: Efficient scikit-learn implementations
- **Vectorized Operations**: NumPy and pandas optimizations
- **Memory Management**: Efficient data structures and cleanup

## 🔒 Security & Privacy

- **API Key Management**: Secure handling of external service keys
- **Data Validation**: Comprehensive input validation with Pydantic
- **Access Control**: Authentication and authorization for API endpoints
- **Data Privacy**: GDPR-compliant data handling practices

## 🛣️ Roadmap

### Phase 1: Core Foundation ✅
- Multi-agent system with CrewAI
- Neo4j knowledge graph implementation
- Advanced reasoning engine
- Complete SDK development

### Phase 2: Web Applications ✅
- Streamlit interactive dashboard
- FastAPI REST API
- Real-world scenarios implementation
- Comprehensive testing suite

### Phase 3: Enterprise Features 🔄
- Advanced security and authentication
- Multi-tenant architecture
- Enterprise integrations (LDAP, SSO)
- Advanced analytics and reporting

### Phase 4: AI Enhancement 📋
- Custom LLM fine-tuning for SFIA
- Advanced NLP for job description analysis
- Predictive analytics for skills trends
- Automated content generation

## 📚 Documentation

- **API Documentation**: Available at `/docs` when running FastAPI server
- **SDK Reference**: Comprehensive docstrings in all modules
- **Examples**: Real-world scenarios in `examples/scenarios.py`
- **Architecture Guide**: Detailed system design documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SFIA Foundation**: For the Skills Framework for the Information Age
- **CrewAI**: For the multi-agent AI framework
- **Neo4j**: For the graph database technology
- **OpenAI**: For the language model capabilities
- **FastAPI & Streamlit**: For the web application frameworks

## 📞 Support

- **Issues**: GitHub Issues for bug reports and feature requests
- **Documentation**: Comprehensive API docs and examples
- **Community**: Join our discussions for questions and collaboration

---

**SFIA AI Framework** - Transforming skills analysis through intelligent AI and semantic understanding. 🧠✨