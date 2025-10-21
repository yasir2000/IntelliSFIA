# IntelliSFIA Framework

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.15+-red.svg)](https://neo4j.com/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Enabled-orange.svg)](https://github.com/joaomdmoura/crewAI)
[![Multi-LLM](https://img.shields.io/badge/Multi--LLM-Support-purple.svg)](#multi-llm-providers)

> **Intelligent Skills Framework for the Information Age**  
> *A comprehensive, production-ready AI framework combining SFIA with cutting-edge multi-agent intelligence, knowledge graphs, and local/cloud LLM support.*

## 🚀 Overview

**IntelliSFIA** revolutionizes skills analysis and career development by combining the Skills Framework for the Information Age (SFIA) with advanced AI technologies. It features autonomous multi-agent collaboration, semantic knowledge graphs, and seamless integration with multiple LLM providers including local models via Ollama.

### ✨ Core Capabilities

- 🤖 **Multi-Agent Intelligence**: 5 specialized AI agents for skills analysis, career guidance, team optimization, and workforce planning
- 🧠 **Knowledge Graph**: Neo4j-powered semantic understanding of skills, relationships, and career pathways  
- 🌐 **Multi-LLM Support**: OpenAI, Anthropic Claude, Azure OpenAI, HuggingFace, **Ollama (local models)**
- ⚡ **Rich CLI Interface**: Beautiful command-line tools with interactive features and configuration management
- 🌊 **Web Applications**: Modern React frontend, Streamlit dashboard, and FastAPI REST API with 30+ endpoints
- 🧪 **Production Ready**: Docker, Kubernetes, monitoring, and comprehensive testing
- 🔒 **Privacy First**: Local model support via Ollama for sensitive organizational data
- 📊 **RDF Conversion**: Original SFIA to RDF/Turtle conversion capabilities maintained

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    IntelliSFIA Framework                        │
├─────────────────────────────────────────────────────────────────┤
│  CLI Interface          │  Web Dashboard    │  REST API         │
│  (Rich + Click)         │  (Streamlit)      │  (FastAPI)        │
├─────────────────────────────────────────────────────────────────┤
│                     Unified SDK Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Multi-Agent System     │  Knowledge Graph  │  ML Reasoning     │
│  (CrewAI + LangChain)   │  (Neo4j + RDF)    │  (scikit-learn)   │
├─────────────────────────────────────────────────────────────────┤
│                    Multi-LLM Provider Layer                     │
│  OpenAI │ Anthropic │ Azure OpenAI │ HuggingFace │ Ollama      │
└─────────────────────────────────────────────────────────────────┘
```

## 🏢 Enterprise Integration

IntelliSFIA provides comprehensive enterprise integration capabilities to automatically analyze SFIA levels from business systems in real-time:

### Supported Enterprise Systems

- **SAP ERP & SuccessFactors**: HR data, activities, performance metrics
- **Microsoft Power BI**: Analytics datasets and dashboards  
- **SQL Databases**: PostgreSQL, MySQL, Oracle, SQL Server
- **MongoDB**: Document-based activity and performance data
- **Apache Kafka**: Real-time streaming data processing
- **Custom REST APIs**: Generic HTTP-based integrations

### Real-time Analysis Features

- **Automatic SFIA Level Suggestions**: Based on task complexity, performance metrics, and skill demonstrations
- **Workforce Intelligence**: Organization-wide insights and skill gap analysis  
- **Compliance Reporting**: Automated audit trails and governance reports
- **Performance Monitoring**: Real-time tracking of skill development and career progression
- **Anomaly Detection**: Identify skill mismatches and development opportunities

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                Enterprise System Connectors                     │
├─────────────────────────────────────────────────────────────────┤
│  SAP    │ Power BI │ Database │ MongoDB │ Kafka │ Custom APIs   │
├─────────────────────────────────────────────────────────────────┤
│                Real-time Analysis Engine                        │
│  Task Analysis │ Performance Metrics │ SFIA Level Reasoning     │
├─────────────────────────────────────────────────────────────────┤
│                    Caching & Streaming                          │
│                   Redis + Event Streaming                       │
├─────────────────────────────────────────────────────────────────┤
│              IntelliSFIA Core Framework                         │
│           Knowledge Graph + ML + Multi-Agent AI                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Quick Start

### Prerequisites

- Python 3.11+
- Neo4j 5.15+ (or Docker)
- Poetry (recommended) or pip

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Semantic-partners/sfia-rdf.git
cd sfia-rdf

# Install Python dependencies with Poetry (recommended)
poetry install

# Or install with pip
pip install -r requirements.txt

# Install Frontend dependencies (for modern web UI)
cd sfia_ai_framework/frontend
npm install
cd ../..
```

### 2. Setup Neo4j Database

```bash
# Quick start with Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:5.15
```

### 3. Configure Environment

```bash
# Create configuration file
cp .env.example .env

# Edit .env with your settings:
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=password
# OPENAI_API_KEY=your_key_here
# OLLAMA_BASE_URL=http://localhost:11434

# Configure Frontend environment
cd sfia_ai_framework/frontend
echo "REACT_APP_API_URL=http://localhost:8000" > .env
echo "REACT_APP_WS_URL=ws://localhost:8000/ws" >> .env
cd ../..
```

### 4. Initialize Framework

```bash
# Convert SFIA data to RDF (original functionality)
poetry run python sfia_rdf/convert_sfia.py

# Initialize AI framework
python -m sfia_ai_framework.cli init

# Or use the CLI directly
intellisfia init --config configs/development.yaml
```

### 5. Run the Complete System

```bash
# Start backend services (Terminal 1)
docker-compose up -d neo4j redis
poetry run uvicorn sfia_ai_framework.web.api:app --reload

# Start React frontend (Terminal 2)
cd sfia_ai_framework/frontend
npm start

# Optional: Start Streamlit dashboard (Terminal 3)
poetry run streamlit run sfia_ai_framework/web/intellisfia_app.py
```

### 6. Access the Applications

- **🌟 Modern Web App**: http://localhost:3000 (React Frontend - **Recommended**)
- **📊 API Documentation**: http://localhost:8000/docs
- **📈 Streamlit Dashboard**: http://localhost:8501 (Alternative UI)
- **🔍 Neo4j Browser**: http://localhost:7474

## 💻 CLI Usage

IntelliSFIA provides a comprehensive command-line interface:

```bash
# Interactive shell with rich console
intellisfia shell

# Skills analysis
intellisfia analyze skill PROG
intellisfia skills list --category Technical --limit 10

# Career development
intellisfia analyze career \
  --from "Junior Developer" \
  --to "Senior Developer" \
  --timeline "2 years"

# Team optimization
intellisfia optimize team \
  --project "AI Platform" \
  --size 5 \
  --skills "Python,ML,DevOps"

# Multi-LLM operations
intellisfia llm test --provider ollama
intellisfia llm compare "What skills for Data Scientist?"
intellisfia llm switch --provider anthropic

# Real-world scenarios
intellisfia scenarios run hiring --interactive
intellisfia scenarios run team_formation
intellisfia scenarios run skills_gap

# System operations
intellisfia health
intellisfia config show
intellisfia kg query "MATCH (s:Skill) RETURN s LIMIT 5"
```

## 🐍 Python SDK

Use the comprehensive SDK for programmatic access:

```python
import asyncio
from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig

async def main():
    # Configure SDK
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        llm_config={
            "default_provider": "openai",
            "providers": {
                "openai": {
                    "api_key": "your-api-key",
                    "model": "gpt-4"
                },
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "model": "llama2"
                }
            }
        }
    )
    
    # Use the framework
    async with SFIASDK(config) as sdk:
        # Query skills
        skills = await sdk.query_skills(category="Technical", limit=5)
        print(f"Found {len(skills)} technical skills")
        
        # Analyze career progression
        analysis = await sdk.analyze_career_progression(
            "Software Developer", 
            "Technical Lead", 
            "18 months"
        )
        
        # Optimize team composition
        team_result = await sdk.optimize_team_for_project({
            "project_name": "AI Platform",
            "required_skills": ["Python", "Machine Learning", "DevOps"],
            "team_size": 6
        }, available_team_data)
        
        # Compare LLM responses
        comparisons = await sdk.compare_llm_responses(
            "What are the key skills for a Data Scientist?"
        )

asyncio.run(main())
```

## 🌐 Web Applications

IntelliSFIA provides multiple web interfaces for different use cases:

### 🌟 Modern React Frontend (Recommended)

Professional enterprise-grade web application with modern UI/UX:

```bash
# Start the React frontend
cd sfia_ai_framework/frontend
npm start

# Visit: http://localhost:3000
```

**Features:**
- **📊 Interactive Dashboard**: Real-time metrics, charts, and system health monitoring
- **👥 Employee Analysis**: Complete SFIA assessment workflows with detailed reports
- **🏢 Enterprise Integration**: Real-time business system connections and analysis
- **📈 Analytics & Reporting**: Comprehensive insights and visualizations
- **🤖 Multi-Agent AI**: Direct access to specialized AI agents
- **🧠 Knowledge Graph**: Interactive visualization and exploration
- **⚙️ Settings & Configuration**: Complete system administration
- **📱 Progressive Web App**: Installable with offline capabilities
- **🎨 Material-UI Design**: Professional, responsive, accessible interface

### 📈 Streamlit Dashboard (Alternative)

Interactive analytics dashboard for quick prototyping:

```bash
# Start the Streamlit dashboard
streamlit run sfia_ai_framework/web/intellisfia_app.py

# Visit: http://localhost:8501
```

**Features:**
- Skills explorer and search
- Career pathway visualization  
- Team composition optimizer
- Real-time agent interactions
- Multi-LLM provider switching

### FastAPI REST API

Production-ready REST API with 30+ endpoints:

```bash
# Start the API server
uvicorn sfia_ai_framework.web.api:app --reload

# Visit: http://localhost:8000/docs
```

**Key Endpoints:**
- `GET /api/skills` - Skills management
- `POST /api/agents/{agent}/execute` - Agent operations
- `POST /api/kg/query` - Knowledge graph queries
- `POST /api/reasoning/analyze` - ML-powered analysis
- `GET /api/health` - System health check

## 🤖 Multi-Agent System

IntelliSFIA features five specialized AI agents:

### 🎯 Skills Analyst
- **Role**: SFIA Skills Analysis Expert
- **Capabilities**: Skill categorization, competency mapping, gap analysis
- **Preferred LLM**: GPT-4, Claude-3 (most capable models)

### 💼 Career Advisor
- **Role**: Career Development Specialist  
- **Capabilities**: Career planning, progression paths, personalized guidance
- **Preferred LLM**: Conversational models (GPT-3.5, Claude)

### 👥 Team Specialist
- **Role**: Team Composition Expert
- **Capabilities**: Team optimization, dynamics analysis, skill complementarity
- **Preferred LLM**: Local models (Ollama) for privacy

### 📚 Learning Specialist
- **Role**: Learning & Development Expert
- **Capabilities**: Learning path design, resource recommendations
- **Preferred LLM**: Educational-focused models

### 📊 Workforce Planner
- **Role**: Strategic Workforce Analyst
- **Capabilities**: Organizational planning, capability forecasting
- **Preferred LLM**: Analytical models (GPT-4, Claude-3)

## 🌍 Multi-LLM Provider Support

### Supported Providers

| Provider | Models | Use Cases | Privacy |
|----------|--------|-----------|---------|
| **OpenAI** | GPT-3.5, GPT-4, GPT-4-turbo | High-quality analysis, general use | Cloud |
| **Anthropic** | Claude-3 (Haiku, Sonnet, Opus) | Safety-focused, analytical tasks | Cloud |
| **Azure OpenAI** | GPT-3.5, GPT-4 | Enterprise compliance | Cloud |
| **HuggingFace** | Various open models | Research, experimentation | Cloud |
| **Ollama** | Llama2, Mistral, CodeLlama | **Local deployment, privacy** | **Local** |

### Local Models with Ollama

Perfect for sensitive organizational data:

```yaml
# Use local models for privacy-sensitive operations
llm:
  default_provider: "ollama"
  providers:
    ollama:
      base_url: "http://localhost:11434"
      model: "llama2"  # or llama2:13b, mistral, etc.
      temperature: 0.7
```

```bash
# Install and run Ollama models
ollama pull llama2:13b
ollama pull mistral:7b
ollama pull codellama:13b

# Use with IntelliSFIA
intellisfia llm test --provider ollama
intellisfia agents execute team_specialist --provider ollama
```

## 🧠 Knowledge Graph

Neo4j-powered semantic understanding:

### Graph Schema
```cypher
// Core SFIA entities and relationships
(Skill)-[:BELONGS_TO]->(Category)
(Skill)-[:HAS_LEVEL]->(Level)
(Skill)-[:REQUIRES]->(Skill)
(Role)-[:REQUIRES]->(Skill)
(Person)-[:HAS_SKILL]->(Skill)
(Team)-[:INCLUDES]->(Person)
(Organization)-[:HAS_TEAM]->(Team)
```

### Query Examples
```bash
# Find related skills
intellisfia kg query "
  MATCH (s:Skill {code: 'PROG'})-[:RELATES_TO]-(related:Skill)
  RETURN s.title, related.title, related.code
"

# Career progression paths
intellisfia kg query "
  MATCH path = (current:Role)-[:PROGRESSES_TO*1..3]->(target:Role)
  WHERE current.title = 'Software Developer'
  RETURN path
"

# Skills gap analysis
intellisfia kg query "
  MATCH (current:Role)-[:REQUIRES]->(skill:Skill)
  MATCH (target:Role)-[:REQUIRES]->(required:Skill)
  WHERE current.title = 'Junior Developer' 
    AND target.title = 'Senior Developer'
    AND NOT EXISTS((current)-[:REQUIRES]->(required))
  RETURN required.title as missing_skill
"
```

## 🏢 Enterprise Integration

### Real-time SFIA Analysis from Business Systems

IntelliSFIA automatically connects to enterprise systems to analyze employee tasks, activities, and performance data, providing intelligent SFIA level suggestions in real-time.

#### Quick Start

```bash
# Initialize enterprise integration
intellisfia enterprise init --config config/enterprise.yaml

# Analyze employee from enterprise data
intellisfia enterprise analyze_employee --employee-id EMP001

# Get organization insights
intellisfia enterprise insights --format dashboard

# Generate compliance report
intellisfia enterprise compliance_report --output report.json
```

#### Supported Systems

- **SAP ERP & SuccessFactors** - HR data and performance metrics
- **Microsoft Power BI** - Analytics datasets and dashboards  
- **SQL Databases** - PostgreSQL, MySQL, Oracle integration
- **MongoDB** - Document-based activity tracking
- **Apache Kafka** - Real-time data streaming
- **Custom APIs** - REST/HTTP integrations

#### Key Features

- 🔄 **Real-time Analysis** - Continuous SFIA level monitoring
- 📊 **Performance Integration** - KPI and metrics-based suggestions
- 🎯 **Automated Reasoning** - ML-powered skill level inference
- 📈 **Workforce Intelligence** - Organization-wide insights
- ⚡ **Event-driven** - Real-time callbacks and notifications
- 📋 **Compliance Reports** - Audit trails and governance

#### API Integration Example

```python
from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig

# Initialize SDK with enterprise capabilities
config = SFIASDKConfig()
sdk = SFIASDK(config)
await sdk.initialize()
await sdk.initialize_enterprise_integration()

# Connect to enterprise system
await sdk.add_enterprise_system(
    system_name="hr_database",
    system_type="postgresql",
    credentials={"connection_string": "postgresql://user:pass@host/db"}
)

# Analyze employee SFIA levels from enterprise data  
result = await sdk.analyze_employee_sfia_levels("EMP001")
print(f"SFIA Level Suggestions: {len(result['suggestions'])}")

# Get organization insights
insights = await sdk.get_organization_sfia_insights()
print(f"Total Employees: {insights['total_employees']}")
print(f"Departments: {len(insights['departments'])}")
```

## 📊 Real-World Scenarios

Five comprehensive use cases included:

### 1. 🎯 Technical Hiring
```bash
intellisfia scenarios run hiring --role "Data Scientist" --interactive
```
- Skill-based candidate matching
- Interview question generation
- Competency assessment frameworks

### 2. 📈 Career Development
```bash
intellisfia scenarios run career --current "Business Analyst" --target "Product Manager"
```
- Individual career planning
- Skill gap identification
- Learning path recommendations

### 3. 👥 Team Formation
```bash
intellisfia scenarios run team_formation --project "Mobile App" --size 5
```
- Project-based team assembly
- Skill complementarity analysis
- Team dynamics optimization

### 4. 🏢 Organizational Assessment
```bash
intellisfia scenarios run org_assessment --company "TechCorp" --size "500+"
```
- Enterprise skill inventory
- Capability gap analysis
- Strategic workforce planning

### 5. 🎓 Skills Gap Analysis
```bash
intellisfia scenarios run skills_gap --department "Engineering"
```
- Current vs. target state analysis
- Development priority ranking
- Resource allocation guidance

## 📊 Original SFIA RDF Conversion

The framework maintains the original SFIA to RDF conversion capabilities:

```bash
# Convert SFIA spreadsheet to RDF/Turtle format
poetry run python sfia_rdf/convert_sfia.py

# Configure paths in convert_sfia.py:
# SFIA_SKILLS_SHEET, SFIA_ATTRIBUTES_SHEET, SFIA_LEVELS_SHEET
```

**Features:**
- Convert SFIA skills data from CSV to RDF/Turtle format
- Support for skills, categories, levels, and attributes
- Modular parser architecture
- Standard vocabularies (SKOS, Dublin Core)

For detailed modeling information, see [conversion_readme.md](conversion_readme.md)

## 🚀 Production Deployment

### Docker Deployment

```bash
# Quick deployment with Docker Compose
docker-compose up -d

# Scale services
docker-compose up -d --scale intellisfia-api=3

# With custom configuration
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f deployment/kubernetes/

# Monitor deployment
kubectl get pods -n intellisfia
kubectl logs -f deployment/intellisfia-api -n intellisfia
```

### Environment Configurations

- **Development**: Local with Ollama models
- **Staging**: Cloud deployment with multiple providers
- **Production**: High availability with monitoring and alerting

## 📈 Monitoring & Observability

### Health Checks
```bash
# System health
intellisfia health

# Component-specific checks
intellisfia health --component neo4j
intellisfia health --component llm
intellisfia health --component agents
```

### Metrics & Dashboards
- Prometheus metrics collection
- Grafana dashboards for visualization
- Performance monitoring and alerting
- Error tracking and logging

## 🧪 Testing

Comprehensive test suite with multiple levels:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/performance/   # Performance tests

# Run with coverage
pytest --cov=sfia_ai_framework --cov-report=html

# Test specific components
pytest tests/test_agents.py -v
pytest tests/test_llm_providers.py -v
```

## 📚 Project Structure

```
sfia-rdf/
├── sfia_rdf/                           # Original RDF converter
│   ├── convert_sfia.py                 # SFIA to RDF conversion
│   ├── namespaces.py                   # RDF namespaces
│   └── parsers/                        # Data parsers
├── sfia_ai_framework/                  # IntelliSFIA Framework
│   ├── cli/__init__.py                 # CLI interface
│   ├── llm/providers.py                # Multi-LLM providers
│   ├── core/
│   │   ├── agents.py                   # Multi-agent system
│   │   ├── enhanced_agents.py          # Enhanced agents
│   │   ├── knowledge_graph.py          # Neo4j integration
│   │   └── reasoning.py                # ML reasoning
│   ├── sdk/__init__.py                 # Unified SDK
│   ├── models/sfia_models.py           # Data models
│   ├── web/
│   │   ├── app.py                      # Streamlit dashboard
│   │   └── api.py                      # FastAPI REST API
│   ├── examples/scenarios.py           # Real-world scenarios
│   └── tests/test_framework.py         # Test suite
├── deployment/
│   ├── production_guide.py             # Production deployment
│   ├── docker-compose.yml              # Docker configuration
│   └── kubernetes/                     # K8s manifests
├── examples/usage_examples.py          # Usage examples
├── configs/                            # Configuration files
├── data/                               # SFIA data files
├── README.md                           # This file
├── pyproject.toml                      # Package configuration
├── conversion_readme.md                # RDF conversion details
└── INTELLISFIA_REBRAND.md             # Rebranding notes
```

## 🔒 Security & Privacy

### Data Protection
- **Local Model Support**: Ollama for sensitive data processing
- **Encryption**: At rest and in transit
- **Access Control**: API key authentication and role-based access
- **Audit Logging**: Comprehensive activity tracking

### Compliance Features
- **Data Sovereignty**: Complete local processing option
- **PII Handling**: Secure credential management
- **Rate Limiting**: API protection and throttling
- **Request Validation**: Input sanitization

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Install development dependencies**: `poetry install --dev`
4. **Make your changes** with tests
5. **Run the test suite**: `pytest`
6. **Submit a pull request**

### Development Setup
```bash
# Clone and setup
git clone https://github.com/Semantic-partners/sfia-rdf.git
cd sfia-rdf

# Install with development dependencies
poetry install --dev

# Setup pre-commit hooks
pre-commit install

# Run development server
python -m sfia_ai_framework.cli dev
```

## 📄 License & Attribution

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### SFIA Attribution

**Important Note**: SFIA (the _Skills Framework for the Information Age_, https://sfia-online.org) is a competency framework. This work contains references to SFIA with the permission of the SFIA Foundation. The rights to any SFIA content remain with SFIA - see [SFIA_LICENSE_NOTE](SFIA_LICENSE_NOTE) for information.

## 🙏 Acknowledgments

- **SFIA Foundation** for the Skills Framework for the Information Age
- **Neo4j** for graph database technology
- **CrewAI** for multi-agent orchestration framework
- **OpenAI, Anthropic** and other LLM providers for AI capabilities
- **Ollama** for enabling local model deployment
- **Open Source Community** for the amazing tools and libraries

## 📞 Support & Community

- 🐛 **Issues**: [GitHub Issues](https://github.com/Semantic-partners/sfia-rdf/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Semantic-partners/sfia-rdf/discussions)
- 📧 **Email**: [support@intellisfia.com](mailto:support@intellisfia.com)
- 📖 **Documentation**: [docs.intellisfia.com](https://docs.intellisfia.com)

---

<div align="center">

**IntelliSFIA Framework - Built with ❤️ for the future of skills and careers**

[⭐ Star us on GitHub](https://github.com/Semantic-partners/sfia-rdf) | [📖 Documentation](https://docs.intellisfia.com) | [💬 Community](https://github.com/Semantic-partners/sfia-rdf/discussions)

</div>

