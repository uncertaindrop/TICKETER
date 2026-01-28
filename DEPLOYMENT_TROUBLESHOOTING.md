# 🔧 DEPLOYMENT TROUBLESHOOTING

## Issue: Dockerfile Build Failed (apt-key error)

### ✅ FIXED!

The Dockerfile has been updated to use the modern Chrome installation method.

### What Was Wrong:
- Old method used deprecated `apt-key` command
- Debian/Ubuntu removed this in newer versions

### What's Fixed:
- Now downloads Chrome .deb file directly
- Installs without deprecated commands
- More reliable and future-proof

---

## 🚀 How to Redeploy

### If You're Using Railway/Render:

**Option 1: Push the Fixed Dockerfile**
```bash
# Get the updated Dockerfile (already downloaded)
# Then push to GitHub:
git add Dockerfile
git commit -m "Fix: Update Dockerfile for modern Chrome installation"
git push origin main
```

Railway/Render will automatically rebuild with the fixed Dockerfile.

**Option 2: Force Rebuild**
- Railway: Go to deployment → Click "Redeploy"
- Render: Go to service → Click "Manual Deploy"

---

## 📝 What Changed in the Dockerfile

**Old (Broken):**
```dockerfile
# Using deprecated apt-key
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
```

**New (Fixed):**
```dockerfile
# Direct .deb installation - no apt-key needed
RUN wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y --no-install-recommends /tmp/google-chrome.deb
```

---

## 🧪 Testing Locally with Docker

Want to test the fixed Dockerfile before deploying?

```bash
# Build locally
docker build -t ticketer .

# Run locally
docker run -p 5000:5000 ticketer

# Visit http://localhost:5000
```

If it builds successfully locally, it will work on Railway/Render!

---

## 🔍 Other Common Deployment Issues

### Issue: Build succeeds but app crashes

**Check:**
1. Is `TICKETER_IMPROVED.py` or `TICKETER_CLOUD.py` in the directory?
2. Does Dockerfile CMD match your filename?

**Fix in Dockerfile:**
```dockerfile
# If your file is named TICKETER.py:
CMD ["python", "TICKETER.py"]

# If it's TICKETER_IMPROVED.py:
CMD ["python", "TICKETER_IMPROVED.py"]

# If it's TICKETER_CLOUD.py:
CMD ["python", "TICKETER_CLOUD.py"]
```

### Issue: "Port already in use"

**Fix:** Change the port in your Python file:
```python
# At the bottom of TICKETER_IMPROVED.py
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
```

### Issue: "Module not found: pdfdata2"

**Fix:** Make sure `pdfdata2.py` is in the same directory and committed to Git:
```bash
git add pdfdata2.py
git commit -m "Add pdfdata2.py"
git push origin main
```

### Issue: Chrome crashes in container

**Fix:** Already handled in the Dockerfile with:
```dockerfile
ENV DISPLAY=:99
# And proper Chrome dependencies
```

---

## 🎯 Quick Deployment Checklist

Before deploying, verify:

- [ ] All files are in your directory:
  - [ ] Dockerfile (the fixed version!)
  - [ ] requirements.txt
  - [ ] TICKETER_IMPROVED.py (or your main file)
  - [ ] pdfdata2.py
  - [ ] TICKETHELPER_CLOUD.html
  - [ ] railway.json (for Railway) or render.yaml (for Render)

- [ ] Files are committed to Git:
  ```bash
  git status  # Should show nothing or only untracked files
  ```

- [ ] Pushed to GitHub:
  ```bash
  git push origin main
  ```

- [ ] Platform is connected to your repo:
  - Railway: Check project settings
  - Render: Check service settings

---

## 🚨 Emergency: Start Fresh

If all else fails, start completely fresh:

```bash
# 1. Delete the old deployment
# Railway: Delete project in dashboard
# Render: Delete service in dashboard

# 2. Verify you have all files locally
ls -la

# Should see:
# Dockerfile
# requirements.txt
# TICKETER_IMPROVED.py
# pdfdata2.py
# TICKETHELPER_CLOUD.html
# etc.

# 3. Make sure Dockerfile is the fixed version
head -40 Dockerfile
# Should see the direct .deb installation method

# 4. Commit everything
git add .
git commit -m "Fresh start with fixed Dockerfile"
git push origin main -f  # Force push if needed

# 5. Create new deployment
# Railway: New Project → Deploy from GitHub
# Render: New Web Service → Connect repo
```

---

## 📞 Platform-Specific Help

### Railway
- **Logs:** Click deployment → View Logs
- **Rebuild:** Deployments tab → Click "Redeploy"
- **Settings:** Check environment variables
- **Support:** https://discord.gg/railway

### Render
- **Logs:** Service dashboard → Logs tab
- **Rebuild:** Manual Deploy button
- **Settings:** Environment tab
- **Support:** https://render.com/support

### Fly.io
```bash
# Check status
flyctl status

# View logs
flyctl logs

# Redeploy
flyctl deploy

# SSH into container (for debugging)
flyctl ssh console
```

---

## ✅ Success Indicators

Your deployment is working when:

1. **Build succeeds** - No red errors
2. **Container starts** - Shows "Running" status
3. **Health check passes** - Green checkmark
4. **You can access the URL** - Opens the interface
5. **Test Connection works** - Button shows ✅

---

## 🎉 After Successful Deploy

Once it's working:

1. **Bookmark your URL**: https://your-app.railway.app
2. **Test with a PDF**: Upload and verify parsing
3. **Check logs**: Make sure everything logs properly
4. **Update this repo**: So you have the working version

---

## 💡 Pro Tip

Keep a local Docker test before every cloud deploy:

```bash
# Quick test script
docker build -t ticketer-test . && \
docker run -p 5000:5000 ticketer-test &
sleep 10
curl http://localhost:5000/health
# Should return: {"status":"ok"}
```

If it works locally, it'll work in the cloud! 🚀

---

**Your Dockerfile is now fixed and ready to deploy!** Just push it to GitHub and Railway/Render will rebuild automatically.
