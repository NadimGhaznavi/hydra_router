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

    [[ -n "$ANSWER" ]] || {
        echo "Enter 'y', 'Y', 'n' or 'N'"
        continue
    }

    [[ "$ANSWER" =~ ^[yYnN]$ ]] || {
        echo "Enter 'y', 'Y', 'n' or 'N'"
        continue
    }

    [[ "$ANSWER" =~ ^[yY]$ ]] && {
        echo "YES!!!!"
        ANSWER="yes"
        break
    }

    [[ "$ANSWER" =~ ^[nN]$ ]] && {
        echo "NO! Not yet..."
        ANSWER="no"
        break
    }

    break
    done
}

main_branch_proc() {
    local BASE_DIR="$1"
    echo
    echo "Base directory            : $BASE_DIR"

    # Get the version out of the TOML file
    TOML_FILE=$BASE_DIR/pyproject.toml
    TOML_VERSION="$(sed -nE 's/^[[:space:]]*version[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/p' "$TOML_FILE" | head -n1)"
    [[ -n "${TOML_VERSION:-}" ]] || { echo "ERROR: Could not find version in $TOML_FILE" >&2; exit 1; }
    echo "Current TOML file version : $TOML_VERSION"

    # Get the version out of the Constants file
    CONST_FILE=$BASE_DIR/hydra_router/constants/DHydra.py
    CONST_VERSION="$(sed -nE 's/^[[:space:]]*VERSION[[:space:]]*:[[:space:]]*str[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/p' "$CONST_FILE" | head -n1)"
    [[ -n "${CONST_VERSION:-}" ]] || { echo "ERROR: Could not find VERSION in $CONST_FILE" >&2; exit 1; }
    echo "Current Constants version : $CONST_VERSION"

    echo
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

    while true; do
    read -rp "Enter new release name: " NEW_REL_NAME

    [[ -n "$NEW_REL_NAME" ]] || {
        echo "Releases must be named."
        continue
    }

    break
    done
    NEW_REL_STR="Release v$NEW_VERSION - $NEW_REL_NAME"

    echo "New version set to : $NEW_VERSION"
    echo "Release string     : $NEW_REL_STR"
}
