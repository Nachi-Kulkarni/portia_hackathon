# Project Overview: Insurance Claim Negotiator

This project is a **voice-driven insurance claim settlement negotiator** built using the Portia SDK. It leverages AI to process insurance claims with emotional intelligence, using voice analysis to understand customer sentiment and adjust responses accordingly.

## Key Technologies

- **Python 3.11+**
- **Portia SDK** - Core framework for AI agent orchestration
- **Hume AI** - For voice emotion analysis
- **FastAPI** - Web framework for API endpoints
- **Uvicorn** - ASGI server for FastAPI
- **Pydantic** - Data validation and settings management
- **PyAudio, NumPy, SciPy** - Audio processing
- **Pandas** - Data processing
- **AsyncIO-MQTT** - MQTT protocol support for real-time communication

## Project Structure

The project follows a modular structure:

- `src/` - Main source code directory
  - `agents/` - Core AI agent implementations
  - `config/` - Configuration files
  - `data/` - Mock data and data models
  - `demo/` - Demonstration scripts
  - `hooks/` - Portia hooks
  - `models/` - Data models
  - `tools/` - Specialized tools for claim processing
  - `utils/` - Utility functions
  - `voice/` - Voice processing and integration with Hume AI
- `tests/` - Unit and integration tests
- `scripts/` - Utility scripts
- `docs/` - Documentation files

## Core Components

### 1. Claim Negotiation Agent (`src/agents/claim_negotiator.py`)

The main agent that orchestrates the entire claim negotiation process:

- Integrates voice emotion analysis with claim processing
- Uses a comprehensive pipeline for end-to-end claim handling
- Combines multiple specialized tools for policy lookup, claim validation, precedent analysis, compliance checking, and settlement offer generation

### 2. Voice Integration (`src/voice/hume_integration.py`)

- `HumeEmotionAnalysisTool`: Analyzes customer emotion from voice input
- `VoiceResponseGeneratorTool`: Generates emotionally appropriate responses

### 3. Specialized Tools (`src/tools/`)

- `PolicyLookupTool`: Retrieves policy information
- `ClaimValidationTool`: Validates claims for authenticity and coverage
- `PrecedentAnalysisTool`: Analyzes historical cases to recommend settlement amounts
- `ComplianceCheckTool`: Ensures regulatory compliance for settlements
- `SettlementOfferTool`: Generates final settlement offers

## Development Environment

### Dependencies

Dependencies are managed via `pyproject.toml` and include:

- Core Portia SDK
- FastAPI and Uvicorn for web services
- Pydantic for data validation
- Hume AI SDK for emotion analysis
- Audio processing libraries (PyAudio, NumPy, SciPy)
- Data processing (Pandas)
- Testing frameworks (Pytest)

### Development Dependencies

- Ruff (linting)
- Black (code formatting)
- MyPy (type checking)
- Pre-commit hooks

## Building and Running

### Setup

1. Install dependencies (using uv, pip, or your preferred Python package manager):
   ```bash
   # If using uv
   uv sync

   # If using pip
   pip install -e .
   ```

2. Set up environment variables for API keys and configuration:
   - `HUME_API_KEY` and `HUME_SECRET_KEY` for voice emotion analysis
   - `PORTIA_CONFIG__OPENAI_API_KEY` for Portia
   - `PORTIA_CONFIG__PORTIA_API_KEY` for Portia

### Running Tests

```bash
# Run basic functionality test
python test_portia_minimal.py

# Run full test suite (if configured)
pytest
```

### Running the Application

A specific entry point script would be needed to start the application, likely using Uvicorn to serve a FastAPI application.

## Development Conventions

- Follow Python best practices for code style and structure
- Use type hints extensively
- Write unit tests for new functionality
- Use Ruff for linting, Black for formatting, and MyPy for type checking
- Follow Portia SDK conventions for tool and agent development