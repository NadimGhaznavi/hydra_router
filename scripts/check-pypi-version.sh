#!/bin/bash
# Check if current version exists on PyPI

set -e

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep "^version = " pyproject.toml | sed 's/version = "\(.*\)"/\1/')

echo "🔍 Checking PyPI for ai-hydra version $CURRENT_VERSION..."

# Check if version exists on PyPI
if pip index versions ai-hydra 2>/dev/null | grep -q "$CURRENT_VERSION"; then
	echo "❌ Version $CURRENT_VERSION already exists on PyPI"
	echo "💡 You need to bump the version before publishing"
	echo "   Use: ./scripts/update-version.sh \"X.Y.Z\" \"Description\""
	exit 1
else
	echo "✅ Version $CURRENT_VERSION is available for publishing"
	echo "🚀 Ready to publish to PyPI!"
fi
