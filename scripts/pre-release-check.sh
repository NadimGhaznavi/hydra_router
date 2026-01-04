#!/bin/bash
#

poetry run pytest
./scripts/check-code-quality.sh

echo "Next: Run the ./scripts/update-version.sh script"
