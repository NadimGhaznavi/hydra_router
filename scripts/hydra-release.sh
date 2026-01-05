#!/bin/bash

# Clear the terminal
clear

# Source the functions file
FUNCTIONS="hydra-release-functions.sh"
SCRIPTS_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
echo "SCRIPT_DIR: $SCRIPT_DIR"
if [ -e "$SCRIPTS_DIR/$FUNCTIONS" ]; then
	source "$SCRIPTS_DIR/$FUNCTIONS"
else
	echo "FATAL ERROR: Unable to find functions file: $SCRIPTS_DIR/$FUNCTIONS"
	exit 1
fi

# Exit on non-zero exit codes
set -e

# Get the base directory
BASE_DIR="$(cd -- "$SCRIPTS_DIR/.." && pwd)"

echo $DIV
echo $DIV
echo
echo "Hydra Router Release Tool"
echo "========================="
echo

# Get the git branch that we're on so we know where we're at in the release process
CUR_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
#echo "Current Git branch : $CUR_BRANCH"

if [ $CUR_BRANCH == "main" ]; then
	echo "We're on the MAIN line, almost ready to release!!"
	exit 1

elif [ $CUR_BRANCH == "dev" ]; then
	echo "We're cruising along the DEV line."
	dev_branch_process

else
	echo "Up in the clouds of the $CUR_BRANCH branch..."
	feat_branch_process
fi

echo $DIV
echo $DIV
