# 🔄 UPDATE WORKFLOW GUIDE

## Quick Summary
When you make changes to any files (TICKETER.py, pdfdata2.py, HTML, etc.), just:
1. Save your changes
2. Run the deployment script
3. Wait 2-5 minutes
4. Your cloud app is updated!

---

## 📝 The Update Process

### Method 1: Using Deployment Scripts (Easiest) ⭐

#### On Mac/Linux:
```bash
chmod +x deploy.sh
./deploy.sh
```

#### On Windows:
```bash
deploy.bat
```

The script will:
1. Ask what you changed
2. Show you the files being updated
3. Commit & push to GitHub
4. Auto-deploy to your cloud platform

**That's it!** Railway/Render auto-deploys in 2-5 minutes.

---

### Method 2: Manual Git Commands

```bash
# 1. Add your changes
git add .

# 2. Commit with a message
git commit -m "Update: improved PDF parsing"

# 3. Push to GitHub
git push origin main

# Railway/Render auto-deploy automatically
# Fly.io: run 'flyctl deploy' manually
```

---

## 🎯 Common Update Scenarios

### Scenario 1: Fixed a Bug in TICKETER.py

```bash
# Edit TICKETER_IMPROVED.py
nano TICKETER_IMPROVED.py
# (make your changes)

# Deploy
./deploy.sh
# Select option 1: "TICKETER.py"

# Wait 2-5 minutes
# ✅ Updated!
```

### Scenario 2: Improved PDF Parsing in pdfdata2.py

```bash
# Edit pdfdata2.py
nano pdfdata2.py
# (improve CST extraction, add new field, etc.)

# Deploy
./deploy.sh
# Select option 2: "pdfdata2.py"

# ✅ New parsing logic is live!
```

### Scenario 3: Changed Both TICKETER.py and pdfdata2.py

```bash
# Edit both files
nano TICKETER_IMPROVED.py
nano pdfdata2.py

# Deploy
./deploy.sh
# Select option 4: "Both Python files"

# ✅ Both updated!
```

### Scenario 4: UI Changes (HTML/CSS)

```bash
# Edit TICKETHELPER_CLOUD.html
nano TICKETHELPER_CLOUD.html

# Deploy
./deploy.sh
# Select option 3: "TICKETHELPER.html"

# ✅ New UI is live!
```

---

## 🔍 Verifying Updates

### 1. Check GitHub
Go to your repository: `https://github.com/YOUR_USERNAME/ticketer`
- Should see your latest commit
- Timestamp should be recent

### 2. Check Cloud Platform

#### Railway:
1. Go to https://railway.app
2. Click your project
3. Go to "Deployments" tab
4. Should see "Building" → "Deploying" → "Active"
5. Takes ~2 minutes

#### Render:
1. Go to https://dashboard.render.com
2. Click your service
3. Check "Events" tab
4. Should see "Deploy started" → "Live"
5. Takes ~3-5 minutes

#### Fly.io:
```bash
flyctl status
flyctl logs
```

### 3. Test Your Changes

Visit your app URL and test the changes:
```
https://your-app.railway.app
```

---

## 🛠️ Development Workflow

### Recommended Process:

```
Local Testing → Git Commit → Push → Auto-Deploy → Test Cloud
     ↓              ↓            ↓         ↓            ↓
  Your PC      Git commit    GitHub   Railway     Production
```

### Step-by-Step:

1. **Make changes locally**
   ```bash
   nano TICKETER_IMPROVED.py
   ```

2. **Test locally** (optional but recommended)
   ```bash
   python TICKETER_IMPROVED.py
   # Visit http://localhost:5000
   ```

3. **Deploy to cloud**
   ```bash
   ./deploy.sh
   ```

4. **Test in cloud**
   ```
   Visit https://your-app.railway.app
   ```

5. **Check logs** (if issues)
   - Railway: Dashboard → Logs
   - Render: Dashboard → Logs
   - Fly.io: `flyctl logs`

---

## 📦 What Gets Deployed?

When you push to GitHub, these files are deployed:

✅ **Always included:**
- `TICKETER_IMPROVED.py` (or `TICKETER_CLOUD.py`)
- `pdfdata2.py`
- `TICKETHELPER_CLOUD.html`
- `requirements.txt`
- `Dockerfile`
- Railway/Render config files

❌ **Never deployed (in .gitignore):**
- `logs/` directory
- `screenshots/` directory
- `uploads/` directory
- `pmm_cookies.json`
- `__pycache__/`
- `.env` file

---

## 🔐 Handling Sensitive Files

### pmm_cookies.json

This file is NOT deployed automatically (it's in .gitignore).

**To update cookies in cloud:**

#### Railway:
```bash
railway link
railway run bash
# Then upload pmm_cookies.json manually
```

Or use Railway's persistent volumes feature.

#### Render:
Use environment variables or persistent disk (paid feature).

#### Fly.io:
```bash
flyctl ssh console
# Upload file manually
```

---

## 🐛 Troubleshooting Updates

### Issue: Changes not showing up

**Solution:**
1. Check GitHub - is latest commit there?
2. Check deployment status - did it deploy?
3. Clear browser cache (Ctrl+F5)
4. Check cloud logs for errors

### Issue: Deployment failed

**Solution:**
1. Check logs in cloud platform
2. Common causes:
   - Syntax error in Python
   - Missing import
   - Dockerfile issue
3. Fix locally and redeploy

### Issue: Git push rejected

**Solution:**
```bash
# Someone else pushed, pull first
git pull origin main --rebase
git push origin main
```

### Issue: Lost local changes

**Solution:**
```bash
# Check git status
git status

# Recover uncommitted changes
git stash
git stash pop
```

---

## 📊 Version Control Best Practices

### Good Commit Messages:
```bash
✅ "Fix: CST code extraction for 10-digit format"
✅ "Add: Support for new store locations"
✅ "Improve: Status progression retry logic"
✅ "Update: UI styling for mobile devices"

❌ "update"
❌ "changes"
❌ "fix"
```

### Branching (Advanced):

For major changes, use branches:
```bash
# Create feature branch
git checkout -b feature/improved-parsing

# Make changes
nano pdfdata2.py

# Test locally
python TICKETER_IMPROVED.py

# Commit
git add .
git commit -m "Improve: PDF parsing accuracy"

# Push branch
git push origin feature/improved-parsing

# Merge to main when ready
git checkout main
git merge feature/improved-parsing
git push origin main
```

---

## 🚀 Advanced: Continuous Integration

### Automated Testing (Optional)

Create `.github/workflows/test.yml`:
```yaml
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests/
```

### Staging Environment

Deploy to two apps:
- **Staging**: `https://ticketer-staging.railway.app`
- **Production**: `https://ticketer.railway.app`

Test in staging before promoting to production.

---

## 📱 Quick Reference Card

| Task | Command |
|------|---------|
| Deploy changes | `./deploy.sh` |
| Check status | Visit cloud dashboard |
| View logs | Check platform logs |
| Test locally | `python TICKETER_IMPROVED.py` |
| Roll back | `git revert HEAD` then push |

---

## 🎯 Real-World Example

Let's say you want to add support for a new CST code format:

```bash
# 1. Edit pdfdata2.py
nano pdfdata2.py
# Add new regex pattern: CST_NEW_RE = re.compile(r"^XX\d{6}$")

# 2. Test locally
python TICKETER_IMPROVED.py
# Upload a test PDF with new format

# 3. Works? Deploy!
./deploy.sh
# Select: "2) pdfdata2.py"
# Message: "Add support for XX-format CST codes"

# 4. Wait 2-5 minutes

# 5. Test in production
# Visit https://your-app.railway.app
# Upload the same test PDF

# 6. ✅ Success!
```

---

## ⏰ Deployment Timeline

| Platform | Push to GitHub | Building | Deploying | Total |
|----------|---------------|----------|-----------|-------|
| Railway  | Instant       | ~1 min   | ~1 min    | ~2 min |
| Render   | Instant       | ~2 min   | ~1 min    | ~3 min |
| Fly.io   | Manual deploy | ~2 min   | ~1 min    | ~3 min |

---

## 💡 Pro Tips

1. **Test locally first** - Saves time and cloud resources
2. **Commit often** - Small commits are easier to debug
3. **Use meaningful messages** - Future you will thank you
4. **Keep staging sync** - Test before production deploy
5. **Monitor logs** - Check after each deploy
6. **Tag releases** - `git tag v1.0.0` for important versions

---

## 📞 Need Help?

### Common Questions:

**Q: Do I need to restart the cloud app after deploy?**  
A: No, Railway/Render auto-restart automatically.

**Q: How do I roll back a bad deploy?**  
A: 
```bash
git revert HEAD
git push origin main
```

**Q: Can I deploy without Git?**  
A: Use Fly.io's direct deploy: `flyctl deploy`

**Q: How do I deploy to multiple environments?**  
A: Use branches - `main` for production, `staging` for testing.

---

**The workflow is simple: Edit → Deploy → Test → Done! 🎉**
