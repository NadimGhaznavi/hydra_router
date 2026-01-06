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

# Build documentation
cd docs && make html
```

## Release Process

1. **Run pre-release validation**: `./scripts/pre-release-check.sh`
2. Ensure all tests pass and code quality checks are clean
3. Update version in `pyproject.toml`:
   ```bash
   poetry version patch  # for bug fixes
   poetry version minor  # for new features
   poetry version major  # for breaking changes
   ```
4. Commit the version change
5. Create and push a git tag:
   ```bash
   git tag v$(poetry version -s)
   git push origin v$(poetry version -s)
   ```
6. GitHub Actions will automatically build and publish to PyPI

**Important**: The pre-release check script must pass completely before creating any release. This ensures code quality, security, and functionality standards are met.

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

### Pre-Release Validation

Before creating a release, run the comprehensive pre-release check:

```bash
# Run complete pre-release validation
./scripts/pre-release-check.sh
```

This script performs all code quality checks, runs the full test suite, and ensures the codebase is ready for release. It includes:

- **flake8**: Linting and style checking
- **mypy**: Static type checking  
- **black**: Code formatting
- **isort**: Import sorting
- **bandit**: Security vulnerability scanning
- **pytest**: Full test suite execution
- **shfmt**: Shell script formatting

All checks must pass before proceeding with a release.
