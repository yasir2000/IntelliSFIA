# IntelliSFIA Multi-LLM Integration Guide 🚀

## CLI, SDK, and Web Support for Multi-LLM Capabilities

This document provides comprehensive guidance for using IntelliSFIA's new multi-LLM provider capabilities across all interfaces: **Command Line Interface (CLI)**, **Python Software Development Kit (SDK)**, and **Web Application**.

---

## 🖥️ **Command Line Interface (CLI)**

### **Installation and Setup**

```bash
# Install CLI dependencies
pip install rich click pyyaml requests

# Make CLI executable
chmod +x intellisfia_cli.py

# Optional: Add to PATH for global access
ln -s $(pwd)/intellisfia_cli.py /usr/local/bin/intellisfia
```

### **Quick Start**

```bash
# Check API health and provider status
python intellisfia_cli.py health

# List available LLM providers
python intellisfia_cli.py providers list

# Test a specific provider
python intellisfia_cli.py providers test --provider anthropic

# Perform skill assessment
python intellisfia_cli.py assess --skill PROG --evidence "5 years Python development..." --provider openai

# Start interactive AI chat
python intellisfia_cli.py chat --provider claude

# Validate evidence quality
python intellisfia_cli.py validate --file evidence.txt

# Get career guidance
python intellisfia_cli.py career --role "Senior Developer" --experience "3 years full-stack development"
```

### **Advanced CLI Features**

#### **Provider Management**
```bash
# Test all available providers
for provider in ollama openai anthropic google cohere; do
    python intellisfia_cli.py providers test --provider $provider
done

# Compare provider performance
python intellisfia_cli.py providers benchmark --iterations 5
```

#### **Batch Processing**
```bash
# Create batch assessment file
cat > batch_assessments.json << EOF
{
  "assessments": [
    {
      "skill_code": "PROG",
      "evidence": "Led development of microservices...",
      "llm_provider": {"provider": "anthropic", "fallback": true}
    },
    {
      "skill_code": "ARCH",
      "evidence": "Designed cloud architecture...",
      "llm_provider": {"provider": "openai", "fallback": true}
    }
  ]
}
EOF

# Run batch assessment
python intellisfia_cli.py batch --input batch_assessments.json
```

#### **Configuration Management**
```bash
# Show current configuration
python intellisfia_cli.py config show

# Set default provider
python intellisfia_cli.py config set default_provider anthropic

# Enable cost tracking
python intellisfia_cli.py config set cost_tracking true

# Set temperature for responses
python intellisfia_cli.py config set temperature 0.7
```

#### **Session and Export Management**
```bash
# Export conversation session
python intellisfia_cli.py export --format json --output session_$(date +%Y%m%d).json

# Export as YAML
python intellisfia_cli.py export --format yaml --output session_report.yml
```

---

## 🐍 **Python SDK**

### **Installation**

```bash
pip install aiohttp requests pydantic
```

### **Quick Start**

```python
import asyncio
from intellisfia_sdk import IntelliSFIAClient, LLMProviderConfig, quick_assess

# Quick assessment (synchronous)
result = quick_assess(
    skill_code="PROG",
    evidence="5 years of Python development with FastAPI and React",
    provider="anthropic"
)
print(f"Recommended Level: {result.recommended_level}")
print(f"Confidence: {result.confidence}%")

# Async client usage
async def main():
    async with IntelliSFIAClient() as client:
        # Health check
        health = await client.health_check()
        print(f"API Status: {health['status']}")
        
        # Get available providers
        providers = await client.get_providers()
        for provider in providers:
            print(f"{provider.provider}: {provider.available}")
        
        # Perform assessment
        assessment = await client.assess_skill(
            skill_code="ARCH",
            evidence="Designed microservices architecture for e-commerce platform",
            provider="claude"
        )
        print(f"Assessment: {assessment.assessment}")

asyncio.run(main())
```

### **Advanced SDK Usage**

#### **Multi-Provider Configuration**
```python
from intellisfia_sdk import LLMProviderConfig, LLMProvider

# Configure provider with specific settings
provider_config = LLMProviderConfig(
    provider=LLMProvider.ANTHROPIC,
    model="claude-3-sonnet-20240229",
    temperature=0.3,
    max_tokens=2000,
    fallback=True,
    ensemble=False,
    cost_limit=0.10
)

async with IntelliSFIAClient() as client:
    assessment = await client.assess_skill(
        skill_code="PROG",
        evidence="Your evidence here",
        provider=provider_config
    )
```

#### **Batch Processing**
```python
from intellisfia_sdk import AssessmentRequest

# Create batch requests
requests = [
    AssessmentRequest(
        skill_code="PROG",
        evidence="Python development experience...",
        llm_provider=LLMProviderConfig(provider=LLMProvider.ANTHROPIC)
    ),
    AssessmentRequest(
        skill_code="ARCH",
        evidence="System architecture design...",
        llm_provider=LLMProviderConfig(provider=LLMProvider.OPENAI)
    )
]

async with IntelliSFIAClient() as client:
    results = await client.batch_assess(requests, max_concurrent=3)
    for result in results:
        if isinstance(result, Exception):
            print(f"Error: {result}")
        else:
            print(f"Skill: {result.skill_code}, Level: {result.recommended_level}")
```

#### **Conversation Management**
```python
from intellisfia_sdk import IntelliSFIASession

async with IntelliSFIAClient() as client:
    async with IntelliSFIASession(client) as session:
        # Send messages with context
        response1 = await client.send_message(
            "What skills do I need for a senior developer role?",
            provider="openai"
        )
        
        response2 = await client.send_message(
            "How can I demonstrate these skills?",
            provider="anthropic"  # Different provider, same session
        )
        
        # Get conversation history
        history = await client.get_conversation_history()
        print(f"Session has {len(history.messages)} messages")
```

#### **Evidence Validation Workflow**
```python
async with IntelliSFIAClient() as client:
    # Validate evidence
    validation = await client.validate_evidence(
        evidence="Led a team of 5 developers to build a React/Node.js application..."
    )
    
    print(f"Quality Score: {validation.evidence_quality_score}%")
    print(f"Completeness: {validation.completeness}%")
    print(f"Suggestions: {', '.join(validation.suggestions)}")
    
    # Use validation results for improved assessment
    if validation.evidence_quality_score > 80:
        assessment = await client.assess_skill("TEAM", validation.evidence)
```

#### **Error Handling and Resilience**
```python
from intellisfia_sdk import IntelliSFIAError, ProviderError, APIConnectionError

async def robust_assessment(client, skill_code, evidence):
    try:
        # Try primary provider
        return await client.assess_skill(
            skill_code=skill_code,
            evidence=evidence,
            provider="anthropic"
        )
    except ProviderError:
        # Fallback to different provider
        return await client.assess_skill(
            skill_code=skill_code,
            evidence=evidence,
            provider="openai"
        )
    except APIConnectionError:
        # Handle connection issues
        print("API temporarily unavailable")
        return None
    except IntelliSFIAError as e:
        print(f"Assessment error: {e}")
        return None
```

---

## 🌐 **Web Application**

### **Setup and Configuration**

```bash
# Navigate to frontend directory
cd sfia_ai_framework/frontend

# Install dependencies
npm install

# Configure environment variables
cat > .env.local << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENABLE_MULTI_LLM=true
REACT_APP_ENABLE_COST_TRACKING=true
REACT_APP_DEFAULT_PROVIDER=auto
EOF

# Start development server
npm start
```

### **Web Interface Features**

#### **1. Multi-LLM Provider Selection**
- **Provider Selector Component**: Choose from Ollama, OpenAI, Anthropic, Google, Cohere
- **Real-time Status**: Live monitoring of provider availability
- **Cost Estimation**: See estimated costs before making requests
- **Fallback Configuration**: Set backup providers automatically
- **Performance Metrics**: View response times and success rates

#### **2. Enhanced Assessment Interface**
```typescript
// Example component usage
import { AIAssessmentPanel, LLMProviderConfig } from './components/AIComponents';

const MyAssessmentPage = () => {
  const [providerConfig, setProviderConfig] = useState<LLMProviderConfig>({
    provider: 'anthropic',
    fallback: true,
    ensemble: false,
    temperature: 0.3
  });

  return (
    <AIAssessmentPanel 
      providerConfig={providerConfig}
      onProviderChange={setProviderConfig}
      enableCostTracking={true}
      enableEnsembleMode={true}
    />
  );
};
```

#### **3. Conversation Chat with Provider Switching**
- **Dynamic Provider Selection**: Switch providers mid-conversation
- **Conversation Memory**: Maintains context across provider changes
- **Cost Tracking**: Per-message cost display
- **Export Functionality**: Save conversations in multiple formats

#### **4. Provider Performance Dashboard**
- **Real-time Metrics**: Monitor all providers simultaneously
- **Cost Breakdown**: Detailed cost analysis per provider
- **Success Rate Tracking**: Provider reliability metrics
- **Response Time Monitoring**: Performance comparison charts

#### **5. Ensemble Response Comparison**
- **Multi-Provider Testing**: Send same prompt to multiple providers
- **Side-by-Side Comparison**: Compare responses, costs, and performance
- **Quality Scoring**: AI-powered response quality assessment
- **Provider Recommendations**: Suggests best provider for specific tasks

### **Advanced Web Configuration**

#### **Custom Provider Configuration**
```typescript
// web_app_config.js
export const PROVIDER_CONFIGS = {
  development: {
    defaultProvider: 'ollama',
    enableCostTracking: true,
    maxDailyCost: 5.0,
    enableEnsemble: true
  },
  production: {
    defaultProvider: 'auto',
    enableCostTracking: true,
    maxDailyCost: 100.0,
    enableEnsemble: false
  }
};
```

#### **Theme Customization**
```typescript
// Custom theme with provider-specific colors
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
    providers: {
      ollama: '#10B981',
      openai: '#00A67D',
      anthropic: '#7C3AED',
      google: '#4285F4',
      cohere: '#FF6B35'
    }
  }
});
```

---

## 🔧 **Integration Examples**

### **1. Automated Assessment Pipeline**

```python
#!/usr/bin/env python3
"""
Automated SFIA Assessment Pipeline
Integrates CLI, SDK, and Web capabilities
"""
import asyncio
import json
from pathlib import Path
from intellisfia_sdk import IntelliSFIAClient, AssessmentRequest

async def automated_assessment_pipeline(evidence_dir: Path):
    """Process all evidence files in directory."""
    async with IntelliSFIAClient() as client:
        results = []
        
        for evidence_file in evidence_dir.glob("*.txt"):
            skill_code = evidence_file.stem.upper()
            evidence_text = evidence_file.read_text()
            
            # Validate evidence first
            validation = await client.validate_evidence(evidence_text)
            
            if validation.evidence_quality_score > 70:
                # High quality evidence - use premium provider
                provider = "anthropic"
            else:
                # Lower quality - use cost-effective provider
                provider = "google"
            
            assessment = await client.assess_skill(
                skill_code=skill_code,
                evidence=evidence_text,
                provider=provider
            )
            
            results.append({
                "skill": skill_code,
                "level": assessment.recommended_level,
                "confidence": assessment.confidence,
                "provider_used": assessment.provider_used,
                "cost": assessment.cost
            })
        
        return results

# Run pipeline
if __name__ == "__main__":
    evidence_dir = Path("./evidence_files")
    results = asyncio.run(automated_assessment_pipeline(evidence_dir))
    
    # Output results
    print(json.dumps(results, indent=2))
```

### **2. Web Widget Integration**

```html
<!-- Embed IntelliSFIA assessment widget -->
<!DOCTYPE html>
<html>
<head>
    <title>Skills Assessment Widget</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
</head>
<body>
    <div id="intellisfia-widget"></div>
    
    <script>
        // Configure widget
        const widgetConfig = {
            apiUrl: 'http://localhost:8000',
            defaultProvider: 'auto',
            enableProviderSelection: true,
            enableCostTracking: true,
            theme: 'light'
        };
        
        // Mount widget
        ReactDOM.render(
            React.createElement(IntelliSFIAWidget, widgetConfig),
            document.getElementById('intellisfia-widget')
        );
    </script>
</body>
</html>
```

### **3. CI/CD Integration**

```yaml
# .github/workflows/skills-assessment.yml
name: Automated Skills Assessment
on: [push, pull_request]

jobs:
  assess-skills:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install IntelliSFIA CLI
        run: |
          pip install -r requirements.txt
          chmod +x intellisfia_cli.py
      
      - name: Run Skills Assessment
        run: |
          # Start API server in background
          python intellisfia_ai_api.py &
          sleep 10
          
          # Run batch assessment
          python intellisfia_cli.py batch --input .github/skills_evidence.json
          
          # Export results
          python intellisfia_cli.py export --format json --output skills_report.json
      
      - name: Upload Assessment Report
        uses: actions/upload-artifact@v2
        with:
          name: skills-assessment-report
          path: skills_report.json
```

---

## 📊 **Monitoring and Analytics**

### **CLI Monitoring**
```bash
# Monitor provider performance
python intellisfia_cli.py providers monitor --interval 60

# Generate usage report
python intellisfia_cli.py report --period monthly --format pdf

# Cost analysis
python intellisfia_cli.py cost-analysis --provider all --period weekly
```

### **SDK Analytics**
```python
async def analytics_dashboard():
    async with IntelliSFIAClient() as client:
        providers = await client.get_providers()
        
        for provider in providers:
            print(f"Provider: {provider.provider}")
            print(f"  Requests: {provider.request_count}")
            print(f"  Cost: ${provider.total_cost:.4f}")
            print(f"  Success Rate: {provider.success_rate:.1f}%")
            print(f"  Avg Response Time: {provider.avg_response_time:.2f}s")
```

### **Web Dashboard**
- **Real-time Provider Status**: Live monitoring dashboard
- **Cost Tracking**: Daily/weekly/monthly cost breakdowns
- **Usage Analytics**: Request patterns and trends
- **Performance Metrics**: Response times and success rates
- **Export Capabilities**: CSV, JSON, PDF reports

---

## 🚀 **Best Practices**

### **Provider Selection Strategy**
1. **Development**: Use Ollama for privacy and cost savings
2. **Testing**: Use Google Gemini for cost-effective testing
3. **Production**: Use Anthropic Claude for high-quality assessments
4. **Specialized Tasks**: Use OpenAI for creative or complex analysis

### **Cost Optimization**
1. **Set Daily Limits**: Configure cost alerts and limits
2. **Use Fallback Chains**: Prioritize cost-effective providers
3. **Cache Responses**: Enable response caching for repeated requests
4. **Batch Processing**: Group similar requests together

### **Performance Optimization**
1. **Provider Health Monitoring**: Regularly check provider status
2. **Concurrent Request Limits**: Respect provider rate limits
3. **Timeout Configuration**: Set appropriate timeouts
4. **Error Handling**: Implement robust retry mechanisms

### **Security Considerations**
1. **API Key Management**: Store keys securely, rotate regularly
2. **Data Privacy**: Use local providers for sensitive data
3. **Access Control**: Implement authentication where needed
4. **Audit Logging**: Track usage and access patterns

---

## 🎯 **Conclusion**

The IntelliSFIA multi-LLM integration provides comprehensive support across CLI, SDK, and Web interfaces, enabling:

✅ **Flexible Provider Selection**: Choose the best LLM for each task
✅ **Cost Optimization**: Track and control AI usage costs
✅ **Performance Monitoring**: Real-time provider performance tracking
✅ **Seamless Integration**: Easy integration into existing workflows
✅ **Scalable Architecture**: Supports enterprise and individual use cases

Start with the CLI for quick testing, use the SDK for custom integrations, and leverage the Web interface for comprehensive assessment workflows.

**Ready to begin? Choose your interface and start assessing with multi-LLM power! 🚀**