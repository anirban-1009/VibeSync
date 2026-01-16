# VibeSync Versioning Guide

## Overview

VibeSync uses **independent semantic versioning** for frontend and backend components.

## Semantic Versioning Format

`MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backwards-compatible)
- **PATCH**: Bug fixes (backwards-compatible)

## Current Versions

- **Frontend**: `0.1.0` (defined in `frontend/package.json`)
- **Backend**: `0.1.0` (defined in `backend/pyproject.toml`)

## When to Bump Versions

### Frontend
- **MAJOR** (1.0.0): Complete UI redesign, breaking state management changes
- **MINOR** (0.2.0): New components, new features (e.g., playlist support)
- **PATCH** (0.1.1): Bug fixes, styling tweaks, performance improvements

### Backend
- **MAJOR** (1.0.0): Breaking API changes, database schema changes
- **MINOR** (0.2.0): New endpoints, new features (e.g., new socket events)
- **PATCH** (0.1.1): Bug fixes, security patches

## How to Update Versions

### Frontend
```bash
cd frontend

# Patch release (0.1.0 -> 0.1.1)
npm version patch

# Minor release (0.1.0 -> 0.2.0)
npm version minor

# Major release (0.1.0 -> 1.0.0)
npm version major
```

### Backend
Manually update `backend/pyproject.toml`:
```toml
[project]
version = "0.2.0"
```

## Release Process

1. **Update version** in respective `package.json` or `pyproject.toml`
2. **Update CHANGELOG** (if you have one)
3. **Commit**: `git commit -m "chore(release): frontend v0.2.0"`
4. **Tag**: `git tag frontend-v0.2.0` or `git tag backend-v0.2.0`
5. **Push**: `git push --tags`

## Version Independence

Frontend and backend versions can (and should) evolve independently:

**Example scenario:**
- Frontend: `1.2.3` (many UI iterations)
- Backend: `0.5.0` (API is still stabilizing)

This is perfectly fine! Each component follows its own release cycle.

## Pre-1.0.0 Versions

- Current `0.x.x` versions indicate **pre-production** software
- Breaking changes can happen in minor versions
- Once stable, bump to `1.0.0`

## Good Practices

- Keep a CHANGELOG.md for each component
- Use git tags with prefixes: `frontend-v0.1.0`, `backend-v0.1.0`
- Document breaking changes clearly
- Sync major versions only when there's a compelling reason

## Version Display

### Frontend
Add to your app to display version:
```javascript
// src/version.js
export const VERSION = '0.1.0';
```

### Backend
Add to your API response:
```python
@app.get("/version")
async def get_version():
    return {"version": "0.1.0"}
```
