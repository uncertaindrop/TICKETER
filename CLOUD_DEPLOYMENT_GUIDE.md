# 🌐 CLOUD DEPLOYMENT GUIDE - TICKETER

## 📋 Quick Overview

This guide covers **3 easy cloud hosting options** (all have free tiers):

1. **Railway.app** - Easiest, auto-deploys from GitHub ⭐ RECOMMENDED
2. **Render.com** - Free tier, Docker support
3. **Fly.io** - More control, good free tier

---

## 🚀 OPTION 1: Railway.app (EASIEST) ⭐

### Why Railway?
- ✅ Free $5/month credit (enough for light usage)
- ✅ Auto-deploys from GitHub
- ✅ Built-in logs & monitoring
- ✅ Easy environment variables
- ✅ Public URL automatically

### Step-by-Step Deployment:

#### 1. Prepare Your Files
```bash
# Your project folder should have:
- TICKETER_IMPROVED.py (or TICKETER_CLOUD.py)
- pdfdata2.py
- TICKETHELPER.html
- requirements.txt
- Dockerfile
- railway.json
```

#### 2. Create GitHub Repository
```bash
# In your project folder:
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/ticketer.git
git push -u origin main
```

#### 3. Deploy to Railway

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `ticketer` repository
5. Railway will auto-detect Dockerfile and deploy!

#### 4. Get Your URL

Once deployed:
- Click on your project
- Go to "Settings" → "Networking"
- Click "Generate Domain"
- Your app will be at: `https://ticketer-production-xxxx.up.railway.app`

#### 5. Update HTML File

Edit `TICKETHELPER.html` and change:
```javascript
// OLD:
fetch('http://127.0.0.1:5000/parse_pdfs', ...)

// NEW:
fetch('https://YOUR-RAILWAY-URL.up.railway.app/parse_pdfs', ...)
```

Do this for all fetch calls.

### Railway Environment Variables (Optional)
In Railway dashboard → Variables:
```
PORT=5000
PYTHON_VERSION=3.11
```

---

## 🚀 OPTION 2: Render.com

### Why Render?
- ✅ Completely free tier (no credit card)
- ✅ Auto-sleep after 15 min inactivity (wakes on request)
- ✅ Docker support
- ✅ Easy SSL/HTTPS

### Step-by-Step:

#### 1. Push to GitHub (same as Railway)

#### 2. Deploy to Render

1. Go to https://render.com
2. Sign up
3. Click "New +" → "Web Service"
4. Connect GitHub repository
5. Configure:
   - **Name:** ticketer
   - **Environment:** Docker
   - **Plan:** Free
   - **Build Command:** (auto-detected from Dockerfile)
   - **Start Command:** `python TICKETER_IMPROVED.py`

6. Click "Create Web Service"

#### 3. Get Your URL

Your app will be at: `https://ticketer-xxxx.onrender.com`

### ⚠️ Render Free Tier Limitations:
- Sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- 750 hours/month free (plenty for most usage)

---

## 🚀 OPTION 3: Fly.io

### Why Fly.io?
- ✅ Generous free tier (3 VMs)
- ✅ Doesn't auto-sleep
- ✅ Global deployment
- ✅ Good for production

### Step-by-Step:

#### 1. Install Fly CLI
```bash
# macOS:
brew install flyctl

# Windows:
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Linux:
curl -L https://fly.io/install.sh | sh
```

#### 2. Login and Initialize
```bash
# Login
flyctl auth login

# In your project folder:
flyctl launch
```

Answer prompts:
- App name: `ticketer-yourname`
- Region: Choose closest to Cyprus
- Postgres database: No
- Deploy now: Yes

#### 3. Deploy
```bash
flyctl deploy
```

#### 4. Get Your URL
```bash
flyctl open
```

Your app will be at: `https://ticketer-yourname.fly.dev`

---

## 🔧 TESTING YOUR DEPLOYMENT

### 1. Health Check
Visit: `https://your-url.com/health`

Should return:
```json
{"status": "ok", "timestamp": "2025-01-24T..."}
```

### 2. Access Interface
Visit: `https://your-url.com/`

You should see the TICKETHELPER interface.

### 3. Test Upload
Try uploading a PDF and check if parsing works.

---

## ⚠️ IMPORTANT: CAPTCHA & OTP HANDLING

**Problem:** Cloud servers run headless Chrome, so you can't manually solve CAPTCHA/OTP.

**Solutions:**

### Option A: Cookie-Based (Recommended)
1. Run locally ONCE to login and solve CAPTCHA/OTP
2. This creates `pmm_cookies.json`
3. Upload this file to your cloud server
4. Set cookies to expire in 30 days or longer

**How to upload cookies to cloud:**

**Railway:**
```bash
# Use Railway CLI
railway run bash
# Then manually copy pmm_cookies.json or use environment variable
```

**Render:**
- Use persistent disk (paid feature) OR
- Store cookies in environment variable as JSON string

**Fly.io:**
```bash
flyctl ssh console
# Copy pmm_cookies.json to /app/
```

### Option B: API-Based CAPTCHA Solving (Advanced)
Use services like:
- 2Captcha.com
- Anti-Captcha.com
- CapMonster.cloud

Example with 2Captcha:
```python
from twocaptcha import TwoCaptcha

solver = TwoCaptcha('YOUR_API_KEY')
result = solver.recaptcha(
    sitekey='6Le-YOUR-SITEKEY',
    url='https://pmm.irepair.gr'
)
```

### Option C: Hybrid Approach (Best)
1. Keep cookies valid for 30 days
2. When cookies expire, send email/SMS notification
3. Operator logs in locally to refresh cookies
4. Upload new cookies to cloud

---

## 📁 FILE STRUCTURE FOR DEPLOYMENT

```
ticketer/
├── TICKETER_IMPROVED.py      # Main application
├── TICKETHELPER.html          # Frontend (update URLs!)
├── pdfdata2.py                # PDF parser
├── requirements.txt           # Python deps
├── Dockerfile                 # Container config
├── docker-compose.yml         # Local testing
├── railway.json              # Railway config
├── render.yaml               # Render config
├── .dockerignore             # Docker ignore rules
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

### .gitignore
```
__pycache__/
*.pyc
logs/
screenshots/
uploads/
pmm_cookies.json
.env
venv/
```

---

## 💰 COST COMPARISON

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| **Railway** | $5 credit/month | $0.000463/min | Easy deployment |
| **Render** | 750 hrs/month | $7/month | Always-free option |
| **Fly.io** | 3 VMs free | $1.94/month/VM | Production use |

**Recommendation:** Start with Railway for ease, move to Fly.io for production.

---

## 🔒 SECURITY CONSIDERATIONS

### 1. Environment Variables
Never hardcode credentials! Use environment variables:

```python
# In your code:
import os
username = os.environ.get('CRM_USERNAME')
password = os.environ.get('CRM_PASSWORD')
```

Set in platform:
- **Railway:** Settings → Variables
- **Render:** Environment → Environment Variables
- **Fly.io:** `flyctl secrets set CRM_USERNAME=xxx`

### 2. HTTPS
All platforms provide free SSL/HTTPS automatically.

### 3. Authentication
Add basic auth to your Flask app:

```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

users = {
    "admin": "your-secure-password"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username

@app.route("/")
@auth.login_required
def index():
    return send_from_directory('.', "TICKETHELPER.html")
```

---

## 🐛 TROUBLESHOOTING

### Issue: "Application failed to start"
**Solution:** Check logs:
- Railway: Click on deployment → Logs
- Render: Dashboard → Logs
- Fly.io: `flyctl logs`

### Issue: Chrome crashes in cloud
**Solution:** Ensure Dockerfile has proper Chrome setup:
```dockerfile
# Add to Dockerfile:
ENV DISPLAY=:99
RUN apt-get install -y xvfb
CMD xvfb-run python TICKETER_IMPROVED.py
```

### Issue: Uploads not working
**Solution:** Check file size limits:
- Railway: 100MB
- Render: 100MB (free), unlimited (paid)
- Fly.io: No hard limit

### Issue: Timeouts
**Solution:** Increase timeout in code:
```python
driver.set_page_load_timeout(300)  # 5 minutes
```

### Issue: Port binding error
**Solution:** Use environment PORT:
```python
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
```

---

## 📊 MONITORING

### Railway
- Built-in metrics dashboard
- View CPU, memory, network usage
- Check logs in real-time

### Render
- Logs tab shows all output
- Metrics tab shows resource usage
- Email alerts for crashes

### Fly.io
```bash
flyctl status
flyctl logs
flyctl dashboard metrics
```

---

## 🔄 UPDATING YOUR APP

### Railway
```bash
git add .
git commit -m "Update"
git push
# Auto-deploys!
```

### Render
Same as Railway - just push to GitHub.

### Fly.io
```bash
git add .
git commit -m "Update"
flyctl deploy
```

---

## 📱 MOBILE ACCESS

All platforms give you a URL that works on:
- Desktop browsers
- Mobile browsers (iPhone, Android)
- Tablets

Access from anywhere!

---

## 🎯 QUICK START CHECKLIST

- [ ] Create GitHub repository
- [ ] Push all files to GitHub
- [ ] Choose cloud platform (Railway recommended)
- [ ] Deploy from GitHub
- [ ] Get public URL
- [ ] Update TICKETHELPER.html with new URL
- [ ] Test health endpoint
- [ ] Run locally once to get cookies
- [ ] Upload cookies to cloud
- [ ] Test with real PDF
- [ ] Set up monitoring/alerts

---

## 📞 SUPPORT

### Railway
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app

### Render
- Support: https://render.com/support
- Docs: https://render.com/docs

### Fly.io
- Community: https://community.fly.io
- Docs: https://fly.io/docs

---

## 🎉 SUCCESS!

Once deployed, you can:
- Access from anywhere
- Share URL with team
- No need for local server
- Auto-scaling if traffic increases
- Built-in backups (on paid tiers)

**Your app is now professional and cloud-hosted! 🚀**
