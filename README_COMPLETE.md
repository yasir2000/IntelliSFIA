"""
Complete README for IntelliSFIA Multi-Agent Framework

A comprehensive, production-ready AI framework for Skills Framework for the Information Age (SFIA)
with multi-agent intelligence, knowledge graphs, and multi-LLM provider support.
"""

# IntelliSFIA Multi-Agent Framework

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.15+-red.svg)](https://neo4j.com/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Enabled-orange.svg)](https://github.com/joaomdmoura/crewAI)

## 🚀 Overview

IntelliSFIA is a comprehensive, production-ready AI framework that combines the Skills Framework for the Information Age (SFIA) with cutting-edge AI technologies. It features multi-agent collaboration, knowledge graphs, and support for multiple LLM providers including local models via Ollama.

### ✨ Key Features

- **🤖 Multi-Agent Intelligence**: Specialized AI agents for skills analysis, career guidance, team optimization, and workforce planning
- **🧠 Knowledge Graph**: Neo4j-powered semantic understanding of skills, relationships, and career pathways
- **🌐 Multi-LLM Support**: Integration with OpenAI, Anthropic Claude, Azure OpenAI, HuggingFace, and Ollama local models
- **⚡ Comprehensive CLI**: Rich command-line interface with interactive features and configuration management
- **🌊 Web Applications**: Streamlit dashboard and FastAPI REST API with 30+ endpoints
- **🧪 Full Test Suite**: Unit, integration, and performance tests with 90%+ coverage
- **📊 Production Ready**: Docker, Kubernetes, monitoring, and deployment configurations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        IntelliSFIA Framework                    │
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

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- Neo4j 5.15+
- Poetry (recommended) or pip
- Docker (for containerized deployment)
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/intellisfia.git
   cd intellisfia
   ```

2. **Install dependencies**
   ```bash
   # Using Poetry (recommended)
   poetry install
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Set up Neo4j**
   ```bash
   # Using Docker
   docker run -d \
     --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password \
     -e NEO4J_PLUGINS='["apoc"]' \
     neo4j:5.15
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Initialize the framework**
   ```bash
   # Load SFIA data into Neo4j
   python -m sfia_ai_framework.cli init
   
   # Or using the CLI directly
   intellisfia init --config configs/development.yaml
   ```

## 🎯 Quick Examples

### Using the CLI

```bash
# Interactive shell
intellisfia shell

# Analyze a skill
intellisfia analyze skill PROG

# Career progression analysis  
intellisfia analyze career --from "Junior Developer" --to "Senior Developer"

# Team optimization
intellisfia optimize team --project "AI Platform" --size 5

# Health check
intellisfia health
```

### Using the SDK

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
                    "model": "gpt-3.5-turbo"
                }
            }
        }
    )
    
    # Use SDK
    async with SFIASDK(config) as sdk:
        # Query skills
        skills = await sdk.query_skills(category="Technical", limit=5)
        print(f"Found {len(skills)} technical skills")
        
        # Analyze career progression
        analysis = await sdk.analyze_career_progression(
            "Junior Developer", 
            "Senior Developer", 
            "2 years"
        )
        print("Career progression analysis completed")

asyncio.run(main())
```

### Using Local Models with Ollama

```python
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
```

## 🌐 Web Applications

### Streamlit Dashboard

```bash
# Start the web dashboard
streamlit run sfia_ai_framework/web/app.py
```

Visit `http://localhost:8501` for the interactive dashboard featuring:
- Skills explorer and search
- Career pathway visualization
- Team composition optimizer
- Real-time analytics

### FastAPI REST API

```bash
# Start the API server
uvicorn sfia_ai_framework.web.api:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API documentation with 30+ endpoints:
- `/skills` - Skills management
- `/agents` - Multi-agent operations
- `/knowledge-graph` - Graph queries
- `/reasoning` - ML-powered analysis

## 🤖 Multi-Agent System

The framework includes five specialized AI agents:

### 🎯 Skills Analyst
- **Role**: SFIA Skills Analysis Expert
- **Capabilities**: Skill categorization, competency mapping, gap analysis
- **Preferred Provider**: Most capable model (GPT-4, Claude-3)

### 💼 Career Advisor  
- **Role**: Career Development Specialist
- **Capabilities**: Career planning, progression paths, personalized guidance
- **Preferred Provider**: Conversational models

### 👥 Team Specialist
- **Role**: Team Composition Expert
- **Capabilities**: Team optimization, dynamics analysis, skill complementarity
- **Preferred Provider**: Local models for privacy (Ollama)

### 📚 Learning Specialist
- **Role**: Learning & Development Expert
- **Capabilities**: Learning path design, resource recommendations, skill development
- **Preferred Provider**: Educational-focused models

### 📊 Workforce Planner
- **Role**: Strategic Workforce Analyst
- **Capabilities**: Organizational planning, capability forecasting, strategic insights
- **Preferred Provider**: Analytical models

## 🧠 Knowledge Graph

The Neo4j-powered knowledge graph provides:

- **Skills Ontology**: Hierarchical skill structure with categories and levels
- **Career Pathways**: Progression routes and prerequisites  
- **Competency Mapping**: Skills to roles relationships
- **Network Analysis**: Skills clustering and similarity
- **Semantic Search**: Natural language skill queries

### Graph Schema

```cypher
// Core entities
(Skill)-[:BELONGS_TO]->(Category)
(Skill)-[:HAS_LEVEL]->(Level)
(Skill)-[:REQUIRES]->(Skill)
(Role)-[:REQUIRES]->(Skill)
(Person)-[:HAS_SKILL]->(Skill)
(Team)-[:INCLUDES]->(Person)
```

## 🌍 Multi-LLM Provider Support

### Supported Providers

| Provider | Models | Features |
|----------|--------|----------|
| **OpenAI** | GPT-3.5, GPT-4, GPT-4-turbo | High quality, fast responses |
| **Anthropic** | Claude-3 (Haiku, Sonnet, Opus) | Safety-focused, analytical |
| **Azure OpenAI** | GPT-3.5, GPT-4 | Enterprise-grade, compliance |
| **HuggingFace** | Various open models | Research, experimentation |
| **Ollama** | Llama2, Mistral, CodeLlama | Local deployment, privacy |

### Configuration

```yaml
llm:
  default_provider: "openai"
  fallback_providers: ["anthropic", "ollama"]
  providers:
    openai:
      api_key: "${OPENAI_API_KEY}"
      model: "gpt-4"
      temperature: 0.7
      max_retries: 3
    ollama:
      base_url: "http://localhost:11434"
      model: "llama2"
      temperature: 0.7
    anthropic:
      api_key: "${ANTHROPIC_API_KEY}"
      model: "claude-3-sonnet-20240229" 
      temperature: 0.7
```

## 📊 Real-World Scenarios

The framework includes five comprehensive scenarios:

### 1. 🎯 Technical Hiring Scenario
- Skill-based candidate matching
- Interview question generation
- Competency assessment

### 2. 📈 Career Development Scenario  
- Individual career planning
- Skill gap identification
- Learning path recommendations

### 3. 👥 Team Formation Scenario
- Project-based team assembly
- Skill complementarity analysis
- Team dynamics optimization

### 4. 🏢 Organizational Assessment
- Enterprise skill inventory
- Capability gap analysis
- Strategic workforce planning

### 5. 🎓 Skills Gap Analysis
- Current vs. target state analysis
- Development priority ranking
- Resource allocation guidance

## 🧪 Testing

Comprehensive test suite with multiple testing levels:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/performance/   # Performance tests

# Run with coverage
pytest --cov=sfia_ai_framework --cov-report=html
```

### Test Coverage

- **Unit Tests**: Core functionality, data models, utilities
- **Integration Tests**: Database operations, API endpoints, agent workflows
- **Performance Tests**: Load testing, response times, scalability
- **Mock Tests**: External API interactions, error scenarios

## 🚀 Production Deployment

### Docker Deployment

```bash
# Build and deploy with Docker Compose
docker-compose up -d

# Scale services
docker-compose up -d --scale sfia-api=3
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f deployment/kubernetes/

# Monitor deployment
kubectl get pods -n sfia-ai
```

### Environment Configurations

- **Development**: Local development with Ollama
- **Staging**: Cloud deployment with multiple providers
- **Production**: High availability with monitoring

## 📖 API Documentation

### Skills API

```bash
# List skills
GET /api/skills?category=Technical&level=5

# Get skill details
GET /api/skills/{skill_code}

# Analyze skill
POST /api/skills/{skill_code}/analyze
```

### Agents API

```bash
# Execute agent task
POST /api/agents/{agent_name}/execute
{
  "task": "Analyze team composition for AI project",
  "context": {...}
}

# Multi-agent collaboration
POST /api/agents/collaborate
{
  "scenario": "career_progression",
  "parameters": {...}
}
```

### Knowledge Graph API

```bash
# Graph queries
POST /api/kg/query
{
  "cypher": "MATCH (s:Skill)-[:BELONGS_TO]->(c:Category) RETURN s, c"
}

# Skill relationships
GET /api/kg/skills/{skill_code}/relationships
```

## ⚙️ Configuration

### Environment Variables

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# LLM Provider API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
HUGGINGFACE_API_KEY=your_hf_key

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
```

### Configuration Files

Configuration can be managed via YAML files:

```yaml
# configs/production.yaml
framework:
  neo4j_uri: "bolt+s://prod-neo4j:7687"
  neo4j_user: "neo4j"
  neo4j_password: "${NEO4J_PROD_PASSWORD}"
  debug: false
  log_level: "WARNING"

llm:
  default_provider: "openai"
  fallback_providers: ["anthropic", "azure_openai"]
  providers:
    # ... provider configurations
```

## 🔒 Security

### Authentication & Authorization

- API key-based authentication
- Role-based access control
- Rate limiting and throttling
- Request validation and sanitization

### Data Protection

- Encryption at rest and in transit
- Secure credential management
- PII data handling compliance
- Audit logging

### Local Model Privacy

- Ollama integration for sensitive data
- On-premises deployment options
- No data sharing with external providers
- Complete data sovereignty

## 📈 Monitoring & Observability

### Health Checks

```bash
# Framework health
curl http://localhost:8000/health

# Individual component health
sfia-ai health --component neo4j
sfia-ai health --component llm
sfia-ai health --component agents
```

### Metrics & Logging

- Prometheus metrics collection
- Grafana dashboards
- Structured logging
- Performance monitoring
- Error tracking

### Alerting

- Service availability alerts
- Performance threshold alerts
- Error rate monitoring
- Resource utilization alerts

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/your-org/intellisfia.git
cd intellisfia

# Install development dependencies
poetry install --dev

# Setup pre-commit hooks
pre-commit install

# Run development server
python -m sfia_ai_framework.cli dev
```

### Code Standards

- Python 3.11+ with type hints
- Black code formatting
- Flake8 linting
- Pytest for testing
- Comprehensive documentation

## 📚 Documentation

- **API Documentation**: `/docs` endpoint (FastAPI auto-generated)
- **CLI Help**: `sfia-ai --help` (comprehensive command help)
- **Developer Guide**: [docs/developer-guide.md](docs/developer-guide.md)
- **Deployment Guide**: [docs/deployment.md](docs/deployment.md)
- **Architecture Guide**: [docs/architecture.md](docs/architecture.md)

## 🆘 Support & Troubleshooting

### Common Issues

**Neo4j Connection Issues**
```bash
# Check Neo4j status
docker ps | grep neo4j

# View Neo4j logs
docker logs neo4j
```

**LLM Provider Issues**
```bash
# Test LLM connectivity
intellisfia llm test --provider openai

# Check provider health
intellisfia health --component llm
```

**Performance Issues**
```bash
# Monitor resource usage
intellisfia system monitor

# Performance profiling
intellisfia system profile
```

### Getting Help

- 📧 Email: support@intellisfia.com
- 💬 Discord: [IntelliSFIA Community](https://discord.gg/intellisfia)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/intellisfia/issues)
- 📖 Documentation: [docs.intellisfia.com](https://docs.intellisfia.com)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SFIA Foundation** for the Skills Framework for the Information Age
- **Neo4j** for graph database technology
- **CrewAI** for multi-agent orchestration
- **OpenAI, Anthropic, and other LLM providers** for AI capabilities
- **Ollama** for local model deployment
- **Open Source Community** for the amazing tools and libraries

## 🗺️ Roadmap

### Version 2.0 (Q2 2024)
- [ ] Advanced skill prediction algorithms
- [ ] Real-time collaboration features
- [ ] Mobile application support
- [ ] Enhanced visualization tools

### Version 2.1 (Q3 2024)
- [ ] Voice interface integration
- [ ] Advanced analytics dashboard
- [ ] Multi-tenant architecture
- [ ] Enterprise SSO integration

### Version 3.0 (Q4 2024)
- [ ] AI-powered skill simulation
- [ ] VR/AR training integration
- [ ] Blockchain credentialing
- [ ] Global skills marketplace

---

<div align="center">

**Built with ❤️ for the future of skills and careers**

[🌟 Star us on GitHub](https://github.com/your-org/intellisfia) | [📖 Documentation](https://docs.intellisfia.com) | [💬 Community](https://discord.gg/intellisfia)

</div>