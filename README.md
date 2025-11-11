
# cortex


Cortex module for Clearskies

This template scaffolds a dynamic Clearskies module for any kind of logic, integration, or API. You can use it to build modules for data processing, service integration, automation, or any custom business logic.

Your module can implement any logic you need: fetch data, process input, interact with external services, or perform custom actions. The endpoints and payloads are up to you.

## Installation

```bash
# Install uv if not already installed
pip install uv

# Create a virtual environment and install dependencies
uv sync
```

## Development

To set up your development environment with pre-commit hooks:

```bash
# Install uv if not already installed
pip install uv

# Create a virtual environment and install all dependencies (including dev)
uv sync

# Install dev dependencies (including ruff, black, mypy) in the project environment
uv pip install .[dev]

# Install pre-commit hooks
uv run pre-commit install

# Optionally, run pre-commit on all files
uv run pre-commit run --all-files
```

## Usage Example

```python
import clearskies
import clearskies_cortex

wsgi = clearskies.contexts.WsgiRef(
    clearskies_cortex.build__module()
)
wsgi()
```
