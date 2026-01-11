# Scripts

This directory contains utility scripts for the VibeSync project.

## bump-version.sh

Automated version bumping script for frontend and backend.

### Usage

```bash
./scripts/bump-version.sh [COMPONENT] [TYPE]
```

**COMPONENT:**
- `frontend` - Bump frontend version only
- `backend` - Bump backend version only
- `all` - Bump both frontend and backend versions

**TYPE:**
- `patch` - Bug fixes (0.1.0 → 0.1.1)
- `minor` - New features (0.1.0 → 0.2.0)
- `major` - Breaking changes (0.1.0 → 1.0.0)

### Examples

```bash
# Bump frontend patch version
./scripts/bump-version.sh frontend patch

# Bump backend minor version
./scripts/bump-version.sh backend minor

# Bump both to major version
./scripts/bump-version.sh all major
```

### What it does

1. Updates version in `package.json` or `pyproject.toml`
2. Updates version constants in code (`version.js`, `version.py`)
3. Creates a git commit with conventional commit message
4. Creates a git tag (e.g., `frontend-v0.1.1`, `backend-v0.2.0`)
5. Shows instructions to push changes

### After Running

Push your changes and tags:
```bash
git push && git push --tags
```
