#!/bin/bash
# Version update script for hydra_router project

set -e

# Function to display usage
usage() {
    echo "Usage: $0 <version> <description>"
    echo ""
    echo "Examples:"
    echo "  $0 \"0.3.15\" \"Release v0.3.15 - Sunshine\""
    echo "  $0 \"1.0.0\" \"Major release v1.0.0 - Production ready\""
    echo ""
    echo "This script will:"
    echo "  - Update version in pyproject.toml"
    echo "  - Update VERSION constant in hydra_router/constants/DHydra.py"
    echo "  - Store description in MSG variable for later use"
    exit 1
}

# Check if correct number of arguments provided
if [ $# -ne 2 ]; then
    echo "Error: Exactly 2 arguments required"
    usage
fi

VERSION="$1"
DESCRIPTION="$2"

# Validate version format (basic semver check)
if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "Error: Version must be in format X.Y.Z (e.g., 0.3.15)"
    exit 1
fi

# Store description in MSG variable
MSG="$DESCRIPTION"

echo "🔄 Updating version to $VERSION"
echo "📝 Description: $MSG"

# Update pyproject.toml
echo "📦 Updating pyproject.toml..."
if [ -f "pyproject.toml" ]; then
    # Use sed to replace the version line
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed requires -i ''
        sed -i '' "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml
    else
        # Linux sed
        sed -i "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml
    fi
    echo "✅ Updated pyproject.toml version to $VERSION"
else
    echo "❌ Error: pyproject.toml not found"
    exit 1
fi

# Update DHydra.py constants file
CONSTANTS_FILE="hydra_router/constants/DHydra.py"
echo "🔧 Updating $CONSTANTS_FILE..."
if [ -f "$CONSTANTS_FILE" ]; then
    # Use sed to replace the VERSION constant
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed requires -i ''
        sed -i '' "s/VERSION: str = \".*\"/VERSION: str = \"$VERSION\"/" "$CONSTANTS_FILE"
    else
        # Linux sed
        sed -i "s/VERSION: str = \".*\"/VERSION: str = \"$VERSION\"/" "$CONSTANTS_FILE"
    fi
    echo "✅ Updated $CONSTANTS_FILE VERSION to $VERSION"
else
    echo "❌ Error: $CONSTANTS_FILE not found"
    exit 1
fi

# Verify the changes
echo ""
echo "🔍 Verifying changes..."
echo "pyproject.toml version:"
grep "^version = " pyproject.toml || echo "❌ Version not found in pyproject.toml"

echo "DHydra.py VERSION:"
grep "VERSION: str = " "$CONSTANTS_FILE" || echo "❌ VERSION not found in $CONSTANTS_FILE"

echo ""
echo "✅ Version update completed successfully!"
echo "📋 Summary:"
echo "   Version: $VERSION"
echo "   Description: $MSG"
echo ""
echo "💡 Next steps:"
echo "   1. Review the changes: git diff"
echo "   2. Run tests: poetry run pytest"
echo "   3. Run quality checks: ./scripts/check-code-quality.sh"
echo "   4. Commit changes: git add . && git commit -m \"$MSG\""
echo "   5. Create tag: git tag v$VERSION"
echo "   6. Push: git push origin main && git push origin v$VERSION"

echo <<FOOBAR
Next you'll need to run:

git add . -v
git commit -m "$MSG"
git tag -a v$VERSION -m "$MSG"
git push origin main --tags
FOOBAR
