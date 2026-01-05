#!/usr/bin/env bash
# hydra-release-functions.sh

# (optional) guard against double-sourcing
[[ ${_HELPER_SH_LOADED:-} ]] && return
_HELPER_SH_LOADED=1

DIV="----------------------------------------------------------------------------"

dev_branch_proc() {
	echo
	echo "MERGE into DEV not yet implemented"
}

feat_branch_proc() {
	# Print out git status
	echo "Confirm that git state is correct:"
	echo $DIV
	git status
	echo $DIV

	while true; do
		read -rp "Ready to release from $CUR_BRANCH [y|n]: " ANSWER
		ANSWER=${ANSWER,,} # lowercase

		[[ "$ANSWER" == y || "$ANSWER" == n ]] || {
			echo "Enter y or n"
			continue
		}

		[[ "$ANSWER" == y ]] && {
			ACTION="release"
			break
		}
		[[ "$ANSWER" == n ]] && {
			ACTION="exit"
			break
		}
	done

	if [ $ACTION == "exit" ]; then
		echo "Abort count down, exiting now..."
		return
	fi

	# Get the version out of the TOML file
	TOML_VERSION=$(get_cur_toml_version $BASE_DIR)
	echo "Current TOML file version : $TOML_VERSION"

	# Get the version out of the Constants file
	CONST_VERSION=$(get_cur_const_version $BASE_DIR)
	echo "Current Constants version : $CONST_VERSION"

	NEW_VERSION=$(get_new_version)
	NEW_REL_STR=$(get_new_release_name)

	echo "New version set to        : $NEW_VERSION"
	echo "Release string            : $NEW_REL_STR"

	# Get this feature branch name
	FEAT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

	# Switch the the dev branch
	git checkout dev

	# Merge the feature branch into dev
	git merge $FEAT_BRANCH -m "Merging $FEAT_BRANCH into dev"

	# Create a new branch for the release
	git checkout -b release/$NEW_VERSION

	# Update the version number in the TOML file
	update_toml_version $NEW_VERSION
}

get_cur_const_version() {
	local BASE_DIR="$1"
	CONST_FILE=$BASE_DIR/hydra_router/constants/DHydra.py
	CONST_VERSION="$(sed -nE 's/^[[:space:]]*VERSION[[:space:]]*:[[:space:]]*str[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/p' "$CONST_FILE" | head -n1)"
	[[ -n "${CONST_VERSION:-}" ]] || {
		echo "ERROR: Could not find VERSION in $CONST_FILE" >&2
		exit 1
	}
	echo $CONST_VERSION
}

get_scripts_dir() {
	echo "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
}

get_cur_toml_version() {
	local BASE_DIR="$1"
	# Get the version out of the TOML file
	TOML_FILE=$BASE_DIR/pyproject.toml
	TOML_VERSION="$(sed -nE 's/^[[:space:]]*version[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/p' "$TOML_FILE" | head -n1)"
	[[ -n "${TOML_VERSION:-}" ]] || {
		echo "ERROR: Could not find version in $TOML_FILE" >&2
		exit 1
	}
	echo $TOML_VERSION
}

get_new_release_name() {
	while true; do
		read -rp "Enter new release name: " NEW_REL_NAME

		[[ -n "$NEW_REL_NAME" ]] || {
			echo "Releases must be named."
			continue
		}

		break
	done
	NEW_REL_STR="Release v$NEW_VERSION - $NEW_REL_NAME"
	echo $NEW_REL_STR
}

get_new_version() {
	while true; do
		read -rp "Enter new version number (e.g. 0.4.6): " NEW_VERSION

		[[ -n "$NEW_VERSION" ]] || {
			echo "Version cannot be empty."
			continue
		}

		[[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
			echo "Invalid version format (expected X.Y.Z)."
			continue
		}

		break
	done
	echo $NEW_VERSION
}

main_branch_proc() {
	local BASE_DIR="$1"
	echo
	echo "Base directory            : $BASE_DIR"

	# Get the version out of the TOML file
	TOML_VERSION=$(get_cur_toml_version $BASE_DIR)
	echo "Current TOML file version : $TOML_VERSION"

	# Get the version out of the Constants file
	CONST_VERSION=$(get_cur_const_version $BASE_DIR)
	echo "Current Constants version : $CONST_VERSION"

	echo

	NEW_VERSION=$(get_new_version)
	NEW_REL_STR=$(get_new_release_name)

	echo "New version set to : $NEW_VERSION"
	echo "Release string     : $NEW_REL_STR"
}

update_toml_version() {
	local NEW_VERSION="$1"

	SCRIPTS_DIR=$(get_scripts_dir)
	TOML_FILE="$SCRIPTS_DIR/pyproject.toml"

	echo "📦 Updating $TOML_FILE..."
	if [ -f "$TOML_FILE" ]; then
		# Use sed to replace the version line
		if [[ "$OSTYPE" == "darwin"* ]]; then
			# macOS sed requires -i ''
			sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" $TOML_FILE
		else
			# Linux sed
			sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" $TOML_FILE
		fi
		echo "✅ Updated $TOML_FILE version to $NEW_VERSION"
	else
		echo "❌ Error: $TOML_FILE not found"
		exit 1
	fi
}
