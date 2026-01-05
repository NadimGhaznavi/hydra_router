#!/bin/bash
#

# Exsit on error
set -e

# Clear the terminal
clear

# Project name
HYDRA_ROUTER="hydra_router"

# Source the functions file
FUNCTIONS="hydra-release-functions.sh"
SCRIPTS_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd -- "$SCRIPTS_DIR/.." && pwd)"

if [ -e "$SCRIPTS_DIR/$FUNCTIONS" ]; then
	source "$SCRIPTS_DIR/$FUNCTIONS"
else
	echo "FATAL ERROR: Unable to find functions file: $SCRIPTS_DIR/$FUNCTIONS"
	exit 1
fi

cd $BASE_DIR

echo "🔍 Executing pre-release tests..."
echo $DIV

echo "📝 Running flake8..."
flake8 $HYDRA_ROUTER
echo $DIV

echo "🔍 Running mypy..."
mypy $HYDRA_ROUTER
echo $DIV

echo "🎨 Running black ..."
black $HYDRA_ROUTER
echo $DIV

echo "📦 Running isort ..."
isort $HYDRA_ROUTER

echo "🔒 Running bandit security check..."
bandit -r $HYDRA_ROUTER #--skip B101

echo "🧹 Executing: poetry run pytest..."
poetry run pytest
echo $DIV

echo "🚦 Executing: shrmt -w scripts/..."
shfmt -w scripts/
echo $DIV

echo "✅ All code quality checks passed!"
