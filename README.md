# restack-gen

A command-line interface tool for scaffolding opinionated Restack agent frameworks in Python and TypeScript. Provides comprehensive project generation, code templates, and development workflow management.

## Features

- **Multi-language Support**: Generate projects in Python and TypeScript
- **Template-driven Generation**: Extensible template system with Jinja2
- **Project Scaffolding**: Complete project structure with agents, workflows, and functions
- **Development Workflow**: Integrated testing, linting, and build tools
- **Environment Diagnostics**: Comprehensive system and dependency checking
- **Package Manager Integration**: Support for uv, pip, pnpm, and npm

## Installation

### Prerequisites

- Python 3.8+
- uv package manager (recommended) or pip

### Install from Source

```bash
# Clone the repository
git clone https://github.com/DSamuelHodge/agentic-builder-cli.git
cd agentic-builder-cli

# Create virtual environment
uv venv

# Activate environment
# On Windows
.venv\Scripts\activate
# On Unix/macOS
source .venv/bin/activate

# Install in development mode
uv pip install -e .
```

### Install from PyPI (Future)

```bash
uv pip install restack-gen
# or
pip install restack-gen
```

## Quick Start

```bash
# Create a new Restack project
restack-gen new my-agent-app

# Navigate to project
cd my-agent-app

# Generate components
restack-gen generate agent EmailAgent
restack-gen generate workflow EmailCampaign
restack-gen generate function send_email

# Run development server
restack-gen dev

# Execute tests
restack-gen test

# Check environment
restack-gen doctor
```

## Commands

| Command | Description | Arguments |
|---------|-------------|-----------|
| `new <app_name>` | Create a new Restack application with full project structure | `<app_name>`: Application name |
| `generate <type> <name>` | Generate code components using templates | `<type>`: agent/function/workflow<br>`<name>`: Component name |
| `routes` | List all registered agents, workflows, and functions in the project | None |
| `dev` | Start the local development server and hot-reload environment | None |
| `build` | Run type checking, linting, and code formatting validation | None |
| `test` | Execute the complete test suite with pytest | `[args]`: Additional pytest arguments |
| `doctor` | Perform comprehensive environment and dependency diagnostics | None |
| `list-templates` | Display all available code generation templates | None |
| `version` | Show the current version of restack-gen | None |
| `help` | Display help information and usage instructions | None |

## Command Flags

| Flag | Description | Applies To |
|------|-------------|------------|
| `--lang <py\|ts>` | Specify target language (Python/TypeScript) | `new`, `generate` |
| `--pm <uv\|pip\|pnpm\|npm>` | Set preferred package manager | `new` |
| `--cwd <path>` | Execute command in specified directory | All commands |
| `--force` | Overwrite existing files without confirmation | `generate`, `new` |
| `--dry-run` | Preview actions without making changes | `new`, `generate`, `dev` |
| `--quiet` | Suppress informational output | All commands |
| `--verbose` | Enable detailed logging and output | All commands |
| `--yes` | Automatically answer yes to all prompts | `generate` |
| `--no-color` | Disable ANSI color output | All commands |
| `--help` | Display command-specific help | All commands |

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RESTACK_HOST` | Restack service endpoint URL | `http://localhost:5233` |
| `PYTHONPATH` | Python module search path | System default |

### Project Structure

Generated projects follow this structure:

```
my-agent-app/
├── src/
│   ├── agents/          # AI agent implementations
│   ├── functions/       # Reusable function definitions
│   └── workflows/       # Workflow orchestration logic
├── tests/               # Test suite
├── scripts/             # Development and deployment scripts
├── restack.toml         # Project configuration
├── pyproject.toml       # Python project metadata
└── README.md            # Project documentation
```

### Template System

Templates use Jinja2 syntax with predefined context variables:

- `name`: Component name (snake_case)
- `pascal_name`: Component name (PascalCase)
- `app_name`: Application name
- `timeouts_start_to_close_seconds`: Default timeout value
- `retry_policies_default_json`: Default retry configuration

## Development

### Testing

```bash
# Run complete test suite
python -m pytest

# Run with coverage
python -m pytest --cov=restack_gen --cov-report=html

# Run specific test file
python -m pytest tests/test_cli.py
```

### Code Quality

```bash
# Lint code
python -m ruff check .

# Format code
python -m ruff format .

# Type checking (future)
# mypy restack_gen/
```

### Building

```bash
# Build distribution
python -m build

# Install in development mode
uv pip install -e .
```

## Architecture

### Core Components

- **CLI Interface** (`cli.py`): Argument parsing and command dispatch
- **Command Registry** (`commands/__init__.py`): Command registration and execution
- **Project Structure** (`core/project.py`): Directory structure management
- **Template Engine** (`core/templates.py`): Jinja2-based code generation
- **Validation** (`core/validation.py`): Input sanitization and path checking
- **Utilities** (`utils/`): Console output, text processing, TOML handling

### Design Principles

- **Modular Architecture**: Clear separation between CLI, core logic, and utilities
- **Template-driven Generation**: Extensible template system for code generation
- **Configuration as Code**: TOML-based project configuration
- **Error Resilience**: Comprehensive error handling with user-friendly messages
- **Testability**: High test coverage with isolated unit tests

## Roadmap

### Version 0.3.0 (Q1 2026)
- [ ] Multi-language template expansion (Go, Rust)
- [ ] Plugin system for custom generators
- [ ] Interactive mode with guided project creation
- [ ] Template marketplace integration

### Version 0.4.0 (Q2 2026)
- [ ] Cloud deployment templates (AWS Lambda, Google Cloud Functions)
- [ ] Advanced workflow patterns and templates
- [ ] Performance optimization and caching
- [ ] Shell completion scripts (bash, zsh, fish, PowerShell)

### Version 0.5.0 (Q3 2026)
- [ ] AI-powered code suggestions and refactoring
- [ ] Multi-framework support (FastAPI, Express.js integration)
- [ ] Enterprise security features and audit logging
- [ ] Team collaboration and project sharing

### Version 1.0.0 (Q4 2026)
- [ ] Production-ready enterprise features
- [ ] Comprehensive documentation and tutorials
- [ ] Community template ecosystem
- [ ] Commercial support and SLA options

### Future Considerations
- **AI Integration**: GitHub Copilot-style intelligent code completion
- **Microservices**: Distributed system templates and orchestration
- **DevOps Integration**: Kubernetes, Docker Swarm deployment templates
- **Multi-cloud**: Azure Functions, Vercel integration

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Install development dependencies: `uv pip install -e ".[dev]"`
4. Run tests: `python -m pytest`
5. Ensure code quality: `python -m ruff check . && python -m ruff format .`
6. Submit a pull request

### Code Standards

- **Python Version**: 3.8+ compatibility
- **Code Style**: Black formatting with 88-character line length
- **Linting**: Ruff for fast, comprehensive code quality
- **Testing**: pytest with minimum 90% coverage requirement
- **Documentation**: Inline docstrings and comprehensive README

### Testing Guidelines

- Unit tests for all public functions and methods
- Integration tests for CLI command workflows
- End-to-end tests for complete user scenarios
- Mock external dependencies for reliable testing
- Test edge cases and error conditions

## License

Copyright 2025 Derrick Hodge. Licensed under the APACHE 2.0 License.

## Support

- **Issues**: [GitHub Issues](https://github.com/DSamuelHodge/agentic-builder-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/DSamuelHodge/agentic-builder-cli/discussions)
- **Documentation**: [Restack Documentation](https://docs.restack.io)

## Changelog

### Version 0.2.0 (November 2025)
- Complete CLI command implementation
- Comprehensive test suite (79 tests, 96% coverage)
- Template-driven code generation
- Environment diagnostics and validation
- Virtual environment and package management integration
- Production-ready error handling and logging

### Version 0.1.0 (October 2025)
- Initial modular CLI architecture
- Basic project scaffolding
- Core utility functions
- Foundation for template system
