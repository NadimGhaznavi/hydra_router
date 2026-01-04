# Development Workflow

## Project Setup

This project uses Poetry for dependency management. To set up the development environment:

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install

# Activate the virtual environment
poetry shell
```

## Development Commands

```bash
# Add a new dependency
poetry add <package-name>

# Add a development dependency
poetry add --group dev <package-name>

# Run tests
poetry run pytest

# Build the package
poetry build

# Check package info
poetry show
```

## Release Process

1. Ensure all tests pass
2. Update version in `pyproject.toml`:
   ```bash
   poetry version patch  # for bug fixes
   poetry version minor  # for new features
   poetry version major  # for breaking changes
   ```
3. Commit the version change
4. Create and push a git tag:
   ```bash
   git tag v$(poetry version -s)
   git push origin v$(poetry version -s)
   ```
5. GitHub Actions will automatically publish to PyPI

## Code Quality

- Follow PEP 8 style guidelines
- Write tests for new functionality
- Use type hints where appropriate
- Keep dependencies minimal and up-to-date

### Code Quality Tools

This project uses several tools to maintain code quality:

- **flake8**: Linting and style checking
- **mypy**: Static type checking
- **black**: Code formatting
- **isort**: Import sorting
- **bandit**: Security vulnerability scanning
- **pre-commit**: Automated checks before commits

### Running Code Quality Checks

```bash
# Run all code quality checks
./scripts/check-code-quality.sh

# Run individual tools
poetry run flake8 hydra_router
poetry run mypy hydra_router
poetry run black hydra_router
poetry run isort hydra_router
poetry run bandit -r hydra_router

# Run pre-commit hooks on all files
poetry run pre-commit run --all-files
```
