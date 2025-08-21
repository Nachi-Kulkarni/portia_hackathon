# Voice-Driven Insurance Claim Negotiator

A sophisticated insurance claim settlement system built with Portia SDK that combines emotion-aware voice processing with enterprise-grade compliance and auditability.

## 🏆 Overview

This system represents the convergence of three breakthrough technologies:
- **Hume AI**: Provides genuine emotional intelligence for human-like conversations
- **Portia SDK**: Enables enterprise-grade control, auditability, and human oversight  
- **MCP Integration**: Allows flexible, real-time access to insurance systems and data

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- UV package manager (recommended by Portia)
- API keys for Portia and optionally Hume AI

### Installation

1. **Clone and setup:**
```bash
git clone <repository-url>
cd insurance-claim-negotiator
chmod +x scripts/setup.sh
./scripts/setup.sh
```

2. **Configure environment:**
Edit `.env` file with your API keys:
```bash
PORTIA_CONFIG__PORTIA_API_KEY="your-portia-api-key"
PORTIA_CONFIG__OPENAI_API_KEY="your-openai-api-key"
HUME_API_KEY="your-hume-api-key"  # Optional
HUME_SECRET_KEY="your-hume-secret-key"  # Optional
```

3. **Test the installation:**
```bash
python3 src/demo/basic_test.py
```

## 🧪 Testing

### Run All Tests
```bash
./scripts/run_tests.sh
```

### Individual Test Suites
```bash
# Unit tests
python -m pytest tests/unit/ -v

# Demo tests
python src/demo/basic_test.py
python src/demo/full_pipeline_test.py
```

## 🏗️ Architecture

### Core Components

#### 1. Base Agent (`src/agents/base_agent.py`)
- Portia SDK integration with execution hooks
- Audit trail generation and compliance logging
- Escalation triggers for high-value settlements and emotional distress

#### 2. Voice Integration (`src/voice/hume_integration.py`)
- Hume AI emotion analysis tool
- Emotionally appropriate response generation
- Mock emotion detection for testing without API keys

#### 3. Insurance Tools (`src/tools/`)
- **Policy Tools**: Database lookup and verification
- **Claim Tools**: Validation and fraud detection
- **Precedent Tools**: Historical settlement analysis
- **Compliance Tools**: Regulatory requirement checking

#### 4. Complete Pipeline (`src/agents/claim_negotiator.py`)
- End-to-end claim processing workflow
- Voice-emotion-aware claim handling
- Comprehensive audit trail generation

### Key Features

#### 🎭 Emotional Intelligence
- Real-time emotion detection from voice input
- Adaptive response generation based on emotional context
- Automatic escalation for extreme distress or threatening behavior

#### 🛡️ Enterprise Compliance
- Complete audit trails for all decisions
- Regulatory compliance checking (state and federal)
- Required approval workflows for high-value settlements
- Human-in-the-loop escalation triggers

#### 🔍 Advanced Risk Assessment
- Fraud risk scoring based on multiple factors
- Precedent analysis for settlement recommendations
- Policy coverage validation and verification

## 📊 Usage Examples

### Basic Claim Processing
```python
from src.agents.base_agent import BaseInsuranceAgent

agent = BaseInsuranceAgent("my_agent")

claim_data = {
    "claim_id": "CLM-001",
    "policy_number": "POL-2024-001",
    "claim_type": "auto_collision",
    "estimated_amount": 15000,
    "customer_emotion": "frustrated"
}

result = await agent.process_claim(claim_data)
print(f"Status: {result['processing_status']}")
```

### Voice-Aware Processing
```python
from src.agents.claim_negotiator import ClaimNegotiationAgent

agent = ClaimNegotiationAgent("voice_agent")

# Process with voice emotion analysis
result = await agent.process_voice_claim(
    audio_data="customer voice recording",
    claim_context=claim_data
)
```

### Complete Pipeline
```python
# Full end-to-end processing with all tools
result = await agent.negotiate_claim_full_pipeline(
    audio_data="audio_input",
    claim_data=claim_info
)
```

## 🔧 Configuration

### Environment Variables
```bash
# Core Portia Configuration
PORTIA_CONFIG__PORTIA_API_KEY="your-key"
PORTIA_CONFIG__OPENAI_API_KEY="your-key"
PORTIA_CONFIG__STORAGE_CLASS="cloud"

# Voice Processing (Optional)
HUME_API_KEY="your-key"
HUME_SECRET_KEY="your-key"

# Application Settings
DEBUG="true"
LOG_LEVEL="INFO"
DEMO_MODE="true"
ENABLE_AUDIT_LOGGING="true"
```

### Mock Data
The system includes comprehensive mock data in `src/data/mock_policies.json`:
- Sample insurance policies with different coverage types
- Historical precedent cases with settlement data
- Test scenarios for various claim types

## 🧭 Development

### Project Structure
```
insurance-claim-negotiator/
├── src/
│   ├── agents/          # Agent implementations
│   ├── voice/           # Voice processing tools
│   ├── tools/           # Insurance-specific tools
│   ├── data/            # Mock data and fixtures
│   └── demo/            # Demo and test scripts
├── tests/
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test fixtures
├── config/              # Configuration files
├── scripts/             # Utility scripts
└── docs/               # Documentation
```

### Adding New Tools
1. Create tool class inheriting from `Tool`
2. Implement `run()` method with `ToolRunContext`
3. Add to tool registry in agent setup
4. Add unit tests in `tests/unit/`

### Adding New Agents
1. Inherit from `BaseInsuranceAgent`
2. Override `_setup_tool_registry()` for custom tools
3. Override `_setup_execution_hooks()` for custom hooks
4. Add integration tests

## 🔍 Monitoring & Debugging

### Audit Trails
All agent decisions are logged with complete reasoning chains:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "tool_name": "policy_lookup",
  "arguments": {"policy_number": "POL-001"},
  "result_summary": "PolicyInfo object",
  "plan_run_id": "run_123"
}
```

### Compliance Reporting
Regulatory compliance is checked at every step:
- High-value settlement approval requirements
- State-specific regulation validation
- Required documentation verification
- Risk level assessment

### Error Handling
- Graceful fallback to mock data when APIs unavailable
- Comprehensive error logging and reporting
- Human escalation triggers for critical failures

## 🎯 Performance Metrics

Day 1 implementation targets:
- **Average Processing Time**: < 30 seconds per claim
- **Success Rate**: > 80% successful negotiations or proper escalations
- **Audit Completeness**: 100% of decisions logged with reasoning
- **Error Recovery**: Graceful fallback in 100% of error cases

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Add tests for new functionality
4. Ensure all tests pass: `./scripts/run_tests.sh`
5. Submit pull request

## 📜 License

This project demonstrates Portia SDK capabilities for insurance claim processing. See license terms for usage restrictions.

## 🆘 Support

- **Issues**: Report bugs and feature requests via GitHub issues
- **Documentation**: Additional docs in `docs/` directory
- **Tests**: Run `./scripts/run_tests.sh` for comprehensive testing

---

**Built with Portia SDK** - Enterprise-grade AI agent orchestration with complete auditability and human oversight.