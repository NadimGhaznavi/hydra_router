#!/bin/bash
# Code quality check script for hydra_router

set -e

echo "🔍 Running code quality checks..."

echo "📝 Running flake8..."
flake8 hydra_router

echo "🔍 Running mypy..."
mypy hydra_router

echo "🎨 Running black (check only)..."
black --check hydra_router

echo "📦 Running isort (check only)..."
isort --check-only hydra_router

echo "🔒 Running bandit security check..."
bandit -r hydra_router --skip B101

echo "✅ All code quality checks passed!"
