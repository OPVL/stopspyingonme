#!/bin/bash
set -e

echo "🔍 Running code quality checks..."

echo "📝 Formatting with black..."
.venv/bin/black app/ tests/

echo "📦 Sorting imports with isort..."
.venv/bin/isort app/ tests/

echo "🔍 Linting with flake8..."
.venv/bin/flake8 app/ tests/

echo "🔍 Type checking with mypy..."
.venv/bin/mypy app/

echo "✅ All linting checks passed!"
