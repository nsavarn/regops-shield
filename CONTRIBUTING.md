# Contributing to RegOps Shield

First off, thank you for considering contributing to RegOps Shield! This project is a hackathon submission, but we welcome improvements and collaboration.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project adheres to a standard code of conduct. By participating, you are expected to uphold professional and respectful communication.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Relevant logs** (sanitize sensitive info)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- Use case and motivation
- Proposed implementation (if applicable)
- Potential drawbacks

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit changes with descriptive messages
4. Push to your fork
5. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Google Cloud SDK
- MongoDB Atlas account

### Local Setup

```bash
# Clone the repository
git clone https://github.com/nsavarn/regops-shield.git
cd regops-shield

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your values

# Run locally
uvicorn app:app --reload --port 8080
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_health.py -v
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Follow the commit message convention:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `chore:` - Maintenance tasks
   - `test:` - Test additions/modifications
4. Request review from maintainers

## Style Guidelines

### Python

- Follow PEP 8
- Use type hints for all functions
- Write docstrings for public methods
- Maximum line length: 88 characters (Black formatter)

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(agents): add compliance scoring algorithm
fix(api): handle MongoDB connection timeout
docs(readme): update deployment instructions
```

## Questions?

Feel free to open a GitHub Discussion or reach out via the repository's Issues tab.

Thank you for contributing! 🛡️
