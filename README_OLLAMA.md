# IntelliSFIA + Ollama LLM Integration 🤖

> **Intelligent SFIA Assessment with Local Large Language Models**

This integration brings the power of local Large Language Models (LLMs) to IntelliSFIA, enabling intelligent, privacy-focused SFIA skills assessment and career guidance without relying on external APIs.

## 🌟 Features

### **🧠 Intelligent Assessment**
- **Skill Level Evaluation**: AI-powered analysis of evidence against SFIA competency levels
- **Evidence Validation**: Intelligent parsing and assessment of professional evidence
- **Contextual Analysis**: Takes into account role context and career stage

### **📊 Advanced Analytics**
- **Skills Gap Analysis**: Identifies gaps between current and target role requirements
- **Career Path Recommendations**: Personalized career progression guidance
- **Learning Path Planning**: Structured development recommendations

### **🔒 Privacy-First**
- **Local Processing**: All AI inference happens on your local machine
- **No Data Transmission**: Your assessment data never leaves your environment
- **Enterprise Ready**: Perfect for organizations with strict data privacy requirements

### **⚡ Performance**
- **Fast Local Inference**: Quick responses without network latency
- **Scalable**: Handle multiple assessments simultaneously
- **Cost Effective**: No API usage costs

## 🚀 Quick Start

### **Prerequisites**

1. **Install Ollama**
   ```bash
   # Visit https://ollama.ai or run:
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Download a Model**
   ```bash
   # Recommended models:
   ollama pull llama3.1:8b      # Balanced performance (4GB RAM)
   ollama pull llama3.1:13b     # Better quality (8GB RAM)
   ollama pull codellama:7b     # Code-focused (4GB RAM)
   ```

3. **Start Ollama Service**
   ```bash
   ollama serve
   ```

### **Setup IntelliSFIA Integration**

1. **Install Dependencies**
   ```bash
   pip install -r requirements-ollama.txt
   ```

2. **Process SFIA Data** (if not already done)
   ```bash
   python sfia_ai_framework/sfia_ai_framework/data/sfia9_data_processor.py
   ```

3. **Test Integration**
   ```bash
   python test_ollama_integration.py
   ```

4. **Run Demo**
   ```bash
   python demo_ollama_integration.py
   ```

## 📋 Usage Examples

### **Basic Skill Assessment**

```python
from sfia_ai_framework.sfia_ai_framework.services.ollama_service import OllamaService, OllamaConfig, IntelliSFIAAgent

# Configure Ollama
config = OllamaConfig(model="llama3.1:8b", temperature=0.3)
ollama = OllamaService(config)

# Create intelligent agent
agent = IntelliSFIAAgent(ollama)

# Assess a skill
evidence = """
I have 3 years of Python development experience.
Led a team of 4 developers on a microservices project.
Implemented CI/CD pipelines and code review processes.
"""

assessment = agent.assess_skill_level("PROG", evidence, "Senior Developer Role")
print(f"Recommended Level: {assessment['recommended_level']}")
print(f"Confidence: {assessment['confidence']}%")
```

### **Skills Gap Analysis**

```python
# Current skills profile
current_skills = {
    "PROG": 4,  # Programming - Level 4
    "ARCH": 2,  # Architecture - Level 2  
    "RLMT": 3   # Relationship Management - Level 3
}

# Analyze gap for target role
gap_analysis = agent.analyze_skills_gap(current_skills, "Technical Lead")

# Get recommendations
recommendations = gap_analysis["recommendations"]
print("Priority Skills:", recommendations["priority_skills"])
print("Learning Path:", recommendations["learning_path"])
```

### **Career Path Recommendations**

```python
# Professional profile
profile = {
    "current_role": "Software Developer",
    "years_experience": 5,
    "interests": ["AI/ML", "Leadership", "Architecture"],
    "industry": "Financial Technology"
}

# Get career recommendations
career_paths = agent.recommend_career_path(profile)

for path in career_paths["career_paths"]:
    print(f"Role: {path['role_title']}")
    print(f"Timeline: {path['timeline']}")
    print(f"Key Skills: {path['key_skills_needed']}")
```

## 🎯 Real-World Demo

The integration includes a comprehensive demo showcasing:

### **Demo 1: Intelligent Skill Assessment**
- **Scenario**: Mid-level developer seeking senior role promotion
- **Skills**: Programming (PROG) assessment
- **Evidence**: Real development experience and achievements
- **Output**: Detailed SFIA level recommendation with reasoning

### **Demo 2: Skills Gap Analysis**
- **Scenario**: Current developer → Senior Software Architect
- **Analysis**: Identifies strengths, gaps, and priority development areas
- **Output**: Actionable learning path with timeline

### **Demo 3: Career Path Recommendations**
- **Scenario**: 5-year experienced developer seeking career direction
- **Analysis**: Multiple career trajectories based on interests and skills
- **Output**: Personalized progression paths with timelines

## 🔧 Configuration Options

### **Model Selection**
```python
# Performance focused (faster, less RAM)
config = OllamaConfig(model="llama3.1:8b")

# Quality focused (slower, more RAM)  
config = OllamaConfig(model="llama3.1:13b")

# Code specialized
config = OllamaConfig(model="codellama:7b")
```

### **Response Tuning**
```python
config = OllamaConfig(
    model="llama3.1:8b",
    temperature=0.3,     # Lower = more consistent
    max_tokens=2048,     # Response length
    host="localhost",    # Ollama host
    port=11434          # Ollama port
)
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   IntelliSFIA   │    │  Ollama Service  │    │   Local LLM     │
│   Frontend      │◄──►│   Integration    │◄──►│   (llama3.1)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SFIA 9 Data   │    │ AI Assessment    │    │ Privacy-First   │
│   (147 Skills)  │    │    Agents        │    │   Processing    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📊 Performance Benchmarks

| Model | RAM Usage | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| llama3.1:8b | 4GB | Fast | Good | General use |
| llama3.1:13b | 8GB | Medium | Excellent | High-quality assessment |
| codellama:7b | 4GB | Fast | Code-focused | Technical skills |

## 🛠️ Troubleshooting

### **Common Issues**

1. **Ollama Not Found**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Service Not Running**
   ```bash
   # Start Ollama
   ollama serve
   
   # Test connection
   curl http://localhost:11434/api/tags
   ```

3. **Model Not Available**
   ```bash
   # Download required model
   ollama pull llama3.1:8b
   
   # List available models
   ollama list
   ```

4. **SFIA Data Missing**
   ```bash
   # Process SFIA data
   python sfia_ai_framework/sfia_ai_framework/data/sfia9_data_processor.py
   ```

### **Performance Optimization**

- **RAM**: Ensure sufficient RAM for your chosen model
- **CPU**: Multi-core processors significantly improve inference speed
- **Model Size**: Balance quality vs. performance based on your needs

## 🔮 Advanced Features

### **Custom Prompting**
Modify system prompts for specialized assessments:

```python
custom_prompt = """
You are a specialized SFIA assessor for cybersecurity roles.
Focus on security-specific competencies and threat awareness.
"""

assessment = agent.assess_skill_level(
    "SCAD",  # Security Administration
    evidence,
    context,
    system_prompt=custom_prompt
)
```

### **Batch Processing**
Process multiple assessments efficiently:

```python
assessments = []
for skill_code, evidence in skill_evidence_pairs:
    assessment = agent.assess_skill_level(skill_code, evidence)
    assessments.append(assessment)
```

### **Integration with Web Interface**
Add to your FastAPI backend:

```python
@app.post("/api/assess-skill")
async def assess_skill(request: SkillAssessmentRequest):
    agent = IntelliSFIAAgent(ollama_service)
    assessment = agent.assess_skill_level(
        request.skill_code,
        request.evidence,
        request.context
    )
    return assessment
```

## 🤝 Contributing

We welcome contributions to improve the Ollama integration:

1. **Enhanced Prompting**: Better system prompts for more accurate assessments
2. **New Models**: Support for additional Ollama models
3. **Performance**: Optimization for faster inference
4. **Features**: New AI-powered assessment capabilities

## 📄 License

This integration follows the same license as IntelliSFIA (Apache 2.0) with proper SFIA Foundation attribution.

## 🙏 Acknowledgments

- **Ollama Team** for the excellent local LLM platform
- **Meta AI** for the Llama models
- **SFIA Foundation** for the Skills Framework for the Information Age
- **IntelliSFIA Community** for feedback and contributions

---

**Ready to experience intelligent SFIA assessment with local AI? Start with the demo!** 🚀

```bash
python demo_ollama_integration.py
```