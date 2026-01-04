# Packaging and Deployment Guidelines

## Package Management

This project uses **Poetry** for dependency management and packaging:

- Use `poetry install` to install dependencies
- Use `poetry add <package>` to add new dependencies
- Use `poetry build` to build distribution packages
- The `pyproject.toml` file should be configured for Poetry compatibility

## PyPI Publishing

This project uses **GitHub Actions** for automated PyPI publishing:

- Publishing is triggered on tagged releases
- The GitHub Action workflow handles building and uploading to PyPI
- Ensure proper version bumping in `pyproject.toml` before creating releases
- Use semantic versioning (e.g., 1.0.0, 1.0.1, 1.1.0)

## Development Workflow

1. Make changes and test locally
2. Update version in `pyproject.toml` if needed
3. Commit changes and push to main branch
4. Create a git tag for releases: `git tag v1.0.0`
5. Push the tag: `git push origin v1.0.0`
6. GitHub Actions will automatically build and publish to PyPI

## Configuration Notes

- Ensure `pyproject.toml` is properly configured for Poetry
- GitHub repository secrets should contain PyPI API tokens
- The GitHub Actions workflow file should be in `.github/workflows/`
