#!/bin/bash

# Finance Assistant Home Assistant Integration - GitHub Setup Script

set -e

echo "🚀 Setting up Finance Assistant Home Assistant Integration for GitHub/HACS"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI (gh) is not installed. You'll need to create the repository manually."
    echo "   Please install GitHub CLI: https://cli.github.com/"
    echo "   Or create the repository manually at: https://github.com/new"
    echo ""
    echo "   Repository name should be: finance-assistant-ha"
    echo "   Description: Finance Assistant Home Assistant Integration"
    echo "   Make it public"
    echo "   Don't initialize with README (we already have one)"
    echo ""
    read -p "Press Enter when you've created the repository..."
else
    echo "✅ GitHub CLI found. Creating repository..."
    
    # Create the repository
    gh repo create chbarnhouse/finance-assistant-ha \
        --public \
        --description "Finance Assistant Home Assistant Integration" \
        --homepage "https://github.com/chbarnhouse/finance-assistant" \
        --source . \
        --remote origin \
        --push
fi

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git remote add origin https://github.com/chbarnhouse/finance-assistant-ha.git
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial release: Finance Assistant Home Assistant Integration v0.14.63

- Complete Home Assistant integration for Finance Assistant
- Sensor and calendar platforms
- Config flow with API key authentication
- Real-time data coordinator
- HACS ready with validation workflows"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push -u origin main

# Create release tag
echo "🏷️  Creating release tag..."
git tag -a v0.14.63 -m "Release v0.14.63: Initial Home Assistant Integration"
git push origin v0.14.63

echo ""
echo "🎉 Repository setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Verify the repository at: https://github.com/chbarnhouse/finance-assistant-ha"
echo "2. Check that GitHub Actions are running: https://github.com/chbarnhouse/finance-assistant-ha/actions"
echo "3. Submit for HACS inclusion: https://hacs.xyz/docs/publish/include"
echo "4. Update documentation with the new repository URL"
echo ""
echo "🔗 Repository URL: https://github.com/chbarnhouse/finance-assistant-ha"
echo "📦 HACS Installation URL: https://github.com/chbarnhouse/finance-assistant-ha" 