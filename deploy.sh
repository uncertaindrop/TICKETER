#!/bin/bash
# deploy.sh - Quick deployment script for Ticketer updates

set -e  # Exit on error

echo "=================================="
echo "🚀 TICKETER DEPLOYMENT SCRIPT"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git is initialized
if [ ! -d .git ]; then
    echo -e "${YELLOW}📦 Git not initialized. Initializing...${NC}"
    git init
    echo -e "${GREEN}✓ Git initialized${NC}"
fi

# Check if remote exists
if ! git remote | grep -q 'origin'; then
    echo -e "${YELLOW}⚠️  No git remote found.${NC}"
    echo ""
    echo "Please add your GitHub repository:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo ""
    read -p "Enter your GitHub repo URL: " repo_url
    git remote add origin "$repo_url"
    echo -e "${GREEN}✓ Remote added${NC}"
fi

echo ""
echo "=================================="
echo "📝 What did you change?"
echo "=================================="
echo ""
echo "Select what you modified:"
echo "1) TICKETER.py / TICKETER_IMPROVED.py"
echo "2) pdfdata2.py"
echo "3) TICKETHELPER.html"
echo "4) Both Python files (TICKETER + pdfdata2)"
echo "5) Everything (full update)"
echo "6) Custom commit message"
echo ""
read -p "Choice (1-6): " choice

case $choice in
    1)
        commit_msg="Update: TICKETER.py - improved automation logic"
        ;;
    2)
        commit_msg="Update: pdfdata2.py - improved PDF parsing"
        ;;
    3)
        commit_msg="Update: TICKETHELPER.html - UI improvements"
        ;;
    4)
        commit_msg="Update: TICKETER.py + pdfdata2.py - code improvements"
        ;;
    5)
        commit_msg="Update: Full codebase refresh"
        ;;
    6)
        read -p "Enter commit message: " commit_msg
        ;;
    *)
        commit_msg="Update: Code improvements"
        ;;
esac

echo ""
echo -e "${YELLOW}📋 Files to be committed:${NC}"
git status --short
echo ""

read -p "Continue with deployment? (y/n): " confirm
if [[ $confirm != [yY] ]]; then
    echo -e "${RED}❌ Deployment cancelled${NC}"
    exit 1
fi

echo ""
echo "=================================="
echo "🔄 Deploying changes..."
echo "=================================="

# Add all changes
echo "• Adding files..."
git add .

# Commit changes
echo "• Committing: $commit_msg"
git commit -m "$commit_msg" || {
    echo -e "${YELLOW}⚠️  No changes to commit (or commit failed)${NC}"
    echo "Checking if we need to push existing commits..."
}

# Get current branch
branch=$(git branch --show-current)
if [ -z "$branch" ]; then
    branch="main"
    git branch -M main
fi

# Push to GitHub
echo "• Pushing to GitHub ($branch)..."
git push -u origin "$branch" || {
    echo -e "${RED}❌ Push failed. You may need to pull first:${NC}"
    echo "   git pull origin $branch --rebase"
    exit 1
}

echo ""
echo "=================================="
echo -e "${GREEN}✅ DEPLOYMENT SUCCESSFUL!${NC}"
echo "=================================="
echo ""
echo "🎉 Your changes are now on GitHub!"
echo ""
echo "📍 Next steps:"
echo "   • Railway: Auto-deploys in ~2 minutes"
echo "   • Render: Auto-deploys in ~3-5 minutes"
echo "   • Fly.io: Run 'flyctl deploy' manually"
echo ""
echo "🔍 Check deployment status:"
echo "   • Railway: https://railway.app (check Deployments tab)"
echo "   • Render: https://dashboard.render.com (check your service)"
echo "   • Fly.io: flyctl status"
echo ""
echo -e "${GREEN}✓ Done!${NC}"
