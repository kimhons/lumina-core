# Lumina Core

Central orchestration and core services for Lumina AI.

## Overview

This repository contains the central orchestration service and core components of Lumina AI, a next-generation autonomous agent system that brings light and clarity to complex tasks. Lumina AI seamlessly connects thoughts and actions, delivering tangible results through natural language processing.

## Architecture

The Lumina Core package consists of several key components:

### Orchestration Service

The central orchestration service coordinates between all specialized agents and manages the execution flow. It handles:

- Message routing
- Provider selection
- Task delegation
- Context management

### API Gateway

The API gateway exposes Lumina AI capabilities to clients through:

- HTTP REST API
- WebSocket interface for real-time communication

## Installation

```bash
# Clone the repository
git clone https://github.com/kimhons/lumina-core.git
cd lumina-core

# Install the package
pip install -e .
```

## Usage

Here's a simple example of how to use the Lumina Core package:

```python
from lumina.orchestration.service import OrchestrationService
from lumina.api.gateway import APIGateway

# Initialize the orchestration service
service = OrchestrationService()

# Register providers (example with OpenAI)
from providers.openai import OpenAIProvider
openai_provider = OpenAIProvider(api_key="your-api-key")
service.register_provider("openai", openai_provider)

# Initialize the API gateway
api = APIGateway(service)

# Run the API gateway
api.run(host="0.0.0.0", port=8000)
```

## Development

### Setup Development Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=lumina
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
