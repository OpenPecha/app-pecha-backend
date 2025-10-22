#!/bin/bash
# Quick hotfix release script

echo "🔥 Creating Hotfix Release with Timestamp Version"
echo "================================================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Run the Python release script with Poetry
poetry run python scripts/release_sprint.py --type hotfix

echo ""
echo "✅ Hotfix release completed!"
echo "📋 To view all tags: git tag -l"
echo "📋 To view recent tags: git tag -l --sort=-version:refname | head -10"
