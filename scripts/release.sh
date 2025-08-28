#!/bin/bash

# Release script for beaglegaze-python-sdk
# Usage: ./scripts/release.sh <version>
# Example: ./scripts/release.sh 0.1.0

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.1.0"
    exit 1
fi

VERSION=$1
TAG="v${VERSION}"

echo "🚀 Preparing release ${TAG}"

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Error: You must be on the main branch to create a release"
    echo "Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Check if working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: Working directory is not clean"
    echo "Please commit or stash your changes first"
    git status --short
    exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^${TAG}$"; then
    echo "❌ Error: Tag ${TAG} already exists"
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Run tests
echo "🧪 Running tests..."
source venv/bin/activate
pytest

echo "✅ All tests passed!"

# Create and push tag
echo "🏷️  Creating tag ${TAG}..."
git tag -a "${TAG}" -m "Release ${TAG}"

echo "📤 Pushing tag to GitHub..."
git push origin "${TAG}"

echo "🎉 Release ${TAG} created successfully!"
echo "📦 GitHub Actions will now build and publish the package to TestPyPI"
echo "🔗 Check the progress at: https://github.com/beaglegaze/beaglegaze-python-sdk/actions"
