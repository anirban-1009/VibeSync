# Pre-commit Setup Guide

This project uses [pre-commit](https://pre-commit.com/) to ensure code quality before commits.

## What's Included

### Python (Backend)
- **Ruff**: Fast Python linter and formatter
- **mypy**: Static type checker
- **General checks**: Trailing whitespace, EOF fixes, large files

### JavaScript (Frontend)
- **Prettier**: Code formatter
- **ESLint**: Linting for React/JavaScript

### Security
- **detect-secrets**: Prevents committing secrets/credentials
- **Private key detection**: Catches SSH keys, API tokens

### Git Hygiene
- **Conventional commits**: Enforces commit message format
- **Merge conflict detection**
- **Case conflict detection**

## Installation

### Step 1: Install pre-commit

```bash
# Using uv (recommended)
uv tool install pre-commit

# Or using homebrew (macOS)
brew install pre-commit
```

### Step 2: Install the git hooks

From the project root:

```bash
pre-commit install

# Also install commit-msg hook for commit message validation
pre-commit install --hook-type commit-msg
```

### Step 3: (Optional) Run on all files

```bash
pre-commit run --all-files
```

## Usage

Once installed, pre-commit will automatically run on every `git commit`. If any check fails, the commit will be blocked.

### Bypassing Pre-commit (Not Recommended)

If you absolutely need to bypass pre-commit:

```bash
git commit --no-verify -m "your message"
```

### Manual Execution

Run pre-commit manually on staged files:

```bash
pre-commit run
```

Run on all files:

```bash
pre-commit run --all-files
```

Run a specific hook:

```bash
pre-commit run ruff --all-files
pre-commit run prettier --all-files
```

## Commit Message Format

Commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Examples

```bash
feat(backend): add Spotify playlist import
fix(frontend): resolve player sync issue
docs(readme): update installation instructions
chore(deps): update dependencies
```

### Valid Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Other changes

### Valid Scopes
- `backend`
- `frontend`
- `spotify`
- `socket`
- `auth`
- `ui`
- `deps`

## Troubleshooting

### Pre-commit is slow on first run
The first run downloads and installs all hooks. Subsequent runs are much faster due to caching.

### Hook failed but I can't see why
Run with verbose mode:
```bash
pre-commit run --verbose --all-files
```

### Updating hooks
```bash
pre-commit autoupdate
```

### Clear cache
```bash
pre-commit clean
```

## CI/CD Integration

The same checks run in GitHub Actions on every push and PR, ensuring code quality even if pre-commit is bypassed locally.
