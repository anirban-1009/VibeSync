#!/usr/bin/env bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Show usage
usage() {
    echo "Usage: ./scripts/bump-version.sh [COMPONENT] [TYPE]"
    echo ""
    echo "COMPONENT:"
    echo "  frontend    Bump frontend version"
    echo "  backend     Bump backend version"
    echo "  all         Bump both frontend and backend"
    echo ""
    echo "TYPE:"
    echo "  patch       Bump patch version (0.1.0 -> 0.1.1)"
    echo "  minor       Bump minor version (0.1.0 -> 0.2.0)"
    echo "  major       Bump major version (0.1.0 -> 1.0.0)"
    echo ""
    echo "Examples:"
    echo "  ./scripts/bump-version.sh frontend patch"
    echo "  ./scripts/bump-version.sh backend minor"
    echo "  ./scripts/bump-version.sh all patch"
    exit 1
}

# Bump backend version
bump_backend() {
    local bump_type=$1
    local pyproject="backend/pyproject.toml"

    echo -e "${BLUE}Bumping backend version (${bump_type})...${NC}" >&2

    # Get current version
    current_version=$(grep -E '^version = ' "$pyproject" | sed 's/version = "\(.*\)"/\1/')

    # Parse version
    IFS='.' read -r major minor patch <<< "$current_version"

    # Bump version
    case $bump_type in
        patch)
            patch=$((patch + 1))
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        *)
            echo -e "${RED}Invalid bump type: $bump_type${NC}" >&2
            exit 1
            ;;
    esac

    new_version="${major}.${minor}.${patch}"

    # Update pyproject.toml
    sed -i.bak "s/version = \".*\"/version = \"${new_version}\"/" "$pyproject"
    rm -f "${pyproject}.bak"

    # Update version.py
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"${new_version}\"/" "backend/app/version.py"
    rm -f "backend/app/version.py.bak"

    echo -e "${GREEN}✓ Backend: ${current_version} -> ${new_version}${NC}" >&2
    echo "$new_version"
}

# Bump frontend version
bump_frontend() {
    local bump_type=$1

    echo -e "${BLUE}Bumping frontend version (${bump_type})...${NC}" >&2

    # Get current version before bump
    current_version=$(grep -E '"version":' frontend/package.json | sed 's/.*"version": "\(.*\)".*/\1/')

    # Use npm version to bump (this also creates a git commit by default, so we use --no-git-tag-version)
    cd frontend
    npm version "$bump_type" --no-git-tag-version > /dev/null 2>&1
    cd ..

    # Get new version
    new_version=$(grep -E '"version":' frontend/package.json | sed 's/.*"version": "\(.*\)".*/\1/')

    # Update version.js
    sed -i.bak "s/export const VERSION = '.*'/export const VERSION = '${new_version}'/" "frontend/src/version.js"
    rm -f "frontend/src/version.js.bak"

    echo -e "${GREEN}✓ Frontend: ${current_version} -> ${new_version}${NC}" >&2
    echo "$new_version"
}

# Main script
main() {
    if [ $# -ne 2 ]; then
        usage
    fi

    component=$1
    bump_type=$2

    # Validate bump type
    if [[ ! "$bump_type" =~ ^(patch|minor|major)$ ]]; then
        echo -e "${RED}Error: Invalid bump type '$bump_type'${NC}"
        usage
    fi

    # Bump version(s)
    case $component in
        frontend)
            new_version=$(bump_frontend "$bump_type")
            git add frontend/package.json frontend/src/version.js
            git commit -m "chore(release): frontend v${new_version}"
            git tag "frontend-v${new_version}"
            echo -e "${GREEN}Created tag: frontend-v${new_version}${NC}"
            ;;
        backend)
            new_version=$(bump_backend "$bump_type")
            git add backend/pyproject.toml backend/app/version.py
            git commit -m "chore(release): backend v${new_version}"
            git tag "backend-v${new_version}"
            echo -e "${GREEN}Created tag: backend-v${new_version}${NC}"
            ;;
        all)
            frontend_version=$(bump_frontend "$bump_type")
            backend_version=$(bump_backend "$bump_type")
            git add frontend/package.json frontend/src/version.js backend/pyproject.toml backend/app/version.py
            git commit -m "chore(release): v${frontend_version}"
            git tag "v${frontend_version}"
            echo -e "${GREEN}Created tag: v${frontend_version}${NC}"
            ;;
        *)
            echo -e "${RED}Error: Invalid component '$component'${NC}"
            usage
            ;;
esac

    echo ""
    echo -e "${BLUE}To push changes and tags, run:${NC}"
    echo "  git push && git push --tags"
}

main "$@"
