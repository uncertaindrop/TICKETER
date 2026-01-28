@echo off
REM deploy.bat - Windows deployment script for Ticketer updates

setlocal enabledelayedexpansion

echo ==================================
echo 🚀 TICKETER DEPLOYMENT SCRIPT
echo ==================================
echo.

REM Check if git is initialized
if not exist .git (
    echo 📦 Git not initialized. Initializing...
    git init
    echo ✓ Git initialized
)

REM Check if remote exists
git remote >nul 2>&1
if errorlevel 1 (
    echo ⚠️  No git remote found.
    echo.
    set /p repo_url="Enter your GitHub repo URL: "
    git remote add origin !repo_url!
    echo ✓ Remote added
)

echo.
echo ==================================
echo 📝 What did you change?
echo ==================================
echo.
echo Select what you modified:
echo 1) TICKETER.py / TICKETER_IMPROVED.py
echo 2) pdfdata2.py
echo 3) TICKETHELPER.html
echo 4) Both Python files (TICKETER + pdfdata2)
echo 5) Everything (full update)
echo 6) Custom commit message
echo.
set /p choice="Choice (1-6): "

if "%choice%"=="1" set commit_msg=Update: TICKETER.py - improved automation logic
if "%choice%"=="2" set commit_msg=Update: pdfdata2.py - improved PDF parsing
if "%choice%"=="3" set commit_msg=Update: TICKETHELPER.html - UI improvements
if "%choice%"=="4" set commit_msg=Update: TICKETER.py + pdfdata2.py - code improvements
if "%choice%"=="5" set commit_msg=Update: Full codebase refresh
if "%choice%"=="6" (
    set /p commit_msg="Enter commit message: "
)

echo.
echo 📋 Files to be committed:
git status --short
echo.

set /p confirm="Continue with deployment? (y/n): "
if /i not "%confirm%"=="y" (
    echo ❌ Deployment cancelled
    exit /b 1
)

echo.
echo ==================================
echo 🔄 Deploying changes...
echo ==================================

echo • Adding files...
git add .

echo • Committing: %commit_msg%
git commit -m "%commit_msg%"

echo • Pushing to GitHub...
git push -u origin main

if errorlevel 1 (
    echo ❌ Push failed. You may need to pull first:
    echo    git pull origin main --rebase
    exit /b 1
)

echo.
echo ==================================
echo ✅ DEPLOYMENT SUCCESSFUL!
echo ==================================
echo.
echo 🎉 Your changes are now on GitHub!
echo.
echo 📍 Next steps:
echo    • Railway: Auto-deploys in ~2 minutes
echo    • Render: Auto-deploys in ~3-5 minutes
echo.
echo 🔍 Check deployment status:
echo    • Railway: https://railway.app
echo    • Render: https://dashboard.render.com
echo.
echo ✓ Done!
pause
