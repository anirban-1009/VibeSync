# VibeSync - CI/CD & Code Quality Setup

## What's Been Configured

### 1. GitHub Actions Workflows
Located in `.github/workflows/`:

- **Backend CI** - Runs Ruff linting and formatting checks for Python code
- **Frontend CI** - Builds the React application to verify it compiles

### 2. Dependabot
- Automatically creates PRs for dependency updates
- Runs monthly to avoid noise
- Max 3 open PRs at a time
- Separate configurations for Python and npm

### 3. Pre-commit Hooks
Pre-commit is active and will run on every `git commit`:

#### Python (Backend)
- Ruff linter and formatter (fast Python checks)

#### General
- Trailing whitespace removal
- EOF fixes
- YAML/JSON syntax validation
- Large file detection
- Merge conflict detection

### 4. Automation Scripts
Located in `scripts/`:

- `generate_coverage_badge.sh`: Runs backend tests and generates the SVG coverage badge (`backend/coverage.svg`).

## How to Use

### Making a Commit

Pre-commit will automatically run when you commit:

```bash
git add .
git commit -m "feat(backend): add new feature"
```

If checks fail, the commit will be blocked. Fix the issues and try again.

### Bypass Pre-commit (if needed)

```bash
git commit --no-verify -m "your message"
```

### Run Pre-commit Manually

```bash
# On staged files
pre-commit run

# On all files
pre-commit run --all-files
```

## GitHub Actions

Workflows automatically run on:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

View results in the "Actions" tab of your GitHub repository.

## Troubleshooting

**Pre-commit is slow on first run?**
- First run downloads hooks, subsequent runs are cached

**Update hooks to latest versions:**
```bash
pre-commit autoupdate
```

**Clear cache:**
```bash
pre-commit clean
```

## Documentation

- Full pre-commit guide: `.github/PRE_COMMIT_GUIDE.md`
- GitHub Actions: `.github/workflows/`
- Dependabot config: `.github/dependabot.yml`

---

**Your code quality and CI/CD pipeline is now configured with minimal overhead!**
