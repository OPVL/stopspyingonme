#!/bin/bash
set -e

echo "🔧 Setting up pre-commit hooks..."

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    .venv/bin/pip install pre-commit
fi

# Install the git hook scripts
.venv/bin/pre-commit install

echo "✅ Pre-commit hooks installed successfully!"
echo "💡 Run 'pre-commit run --all-files' to check all files"
