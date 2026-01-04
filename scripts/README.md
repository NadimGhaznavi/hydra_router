# Scripts Directory

This directory contains utility scripts for the hydra_router project.

## Available Scripts

### `update-version.sh`
Updates the project version in both `pyproject.toml` and `hydra_router/constants/DHydra.py`.

**Usage:**
```bash
./scripts/update-version.sh <version> <description>
```

**Examples:**
```bash
# Patch release
./scripts/update-version.sh "0.3.15" "Release v0.3.15 - Bug fixes"

# Minor release
./scripts/update-version.sh "0.4.0" "Release v0.4.0 - New features"

# Major release
./scripts/update-version.sh "1.0.0" "Release v1.0.0 - Production ready"
```

**Features:**
- ✅ Validates version format (semantic versioning: X.Y.Z)
- ✅ Updates `pyproject.toml` version field
- ✅ Updates `DHydra.VERSION` constant
- ✅ Stores description in `MSG` variable
- ✅ Cross-platform compatible (Linux/macOS)
- ✅ Provides helpful next steps

### `check-code-quality.sh`
Runs all code quality checks including flake8, mypy, black, isort, and bandit.

**Usage:**
```bash
./scripts/check-code-quality.sh
```

## Typical Release Workflow

1. **Update version:**
   ```bash
   ./scripts/update-version.sh "0.3.15" "Release v0.3.15 - Sunshine"
   ```

2. **Run quality checks:**
   ```bash
   ./scripts/check-code-quality.sh
   ```

3. **Run tests:**
   ```bash
   poetry run pytest
   ```

4. **Review changes:**
   ```bash
   git diff
   ```

5. **Commit and tag:**
   ```bash
   git add .
   git commit -m "Release v0.3.15 - Sunshine"
   git tag v0.3.15
   ```

6. **Push to trigger CI/CD:**
   ```bash
   git push origin main
   git push origin v0.3.15
   ```

The GitHub Actions workflow will automatically build and publish to PyPI when a version tag is pushed.
