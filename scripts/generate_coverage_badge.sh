#!/bin/bash

# Generates an SVG coverage badge
# Usage: ./scripts/generate_coverage_badge.sh

cd "$(dirname "$0")/../backend" || exit

echo "Running tests to generate coverage data..."
uv run pytest tests --cov=app

echo "Generating coverage.svg..."
uv run coverage-badge -o coverage.svg -f

echo "Done! Badge saved to backend/coverage.svg"
