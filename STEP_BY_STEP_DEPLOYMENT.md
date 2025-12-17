# Step-by-Step Deployment Instructions

Follow these steps in order to deploy your Photo Contest app to Streamlit Cloud.

---

## STEP 1: Install Git (Required)

### Option A: Install Git for Windows
1. Go to: https://git-scm.com/download/win
2. Click "Download for Windows"
3. Run the installer
4. Use all default settings (just click "Next" through all steps)
5. **Restart VS Code/Cursor** after installation

### Option B: Use GitHub Desktop (Easier - No Command Line)
1. Go to: https://desktop.github.com/
2. Download GitHub Desktop
3. Install it
4. Sign in with your GitHub account (or create one)

**Choose ONE option above, then continue to Step 2.**

---

## STEP 2: Create GitHub Account

1. Go to: https://github.com
2. Click "Sign up" (top right)
3. Enter:
   - Username (remember this!)
   - Email address
   - Password
4. Verify your email
5. Complete setup

**✅ You now have a GitHub account**

---

## STEP 3: Create GitHub Repository

1. Go to: https://github.com
2. Click the **"+"** icon (top right) → **"New repository"**
3. Fill in:
   - **Repository name**: `photo-contest` (or any name you like)
   - **Description**: "Photo Contest Application" (optional)
   - **Visibility**: Select **"Public"** ⚠️ (Required for free Streamlit Cloud)
   - **DO NOT** check "Add a README file" (you already have one)
   - **DO NOT** add .gitignore (you already have one)
4. Click **"Create repository"**

**✅ Repository created! You'll see a page with setup instructions**

---

## STEP 4: Upload Your Code to GitHub

### If you installed Git (Option A):

1. **Open PowerShell or Command Prompt** in your project folder:
   - Press `Win + R`
   - Type: `powershell`
   - Navigate to your project:
     ```powershell
     cd "C:\Users\Guest 1\photo_contest"
     ```

2. **Initialize Git**:
   ```powershell
   git init
   ```

3. **Add all files**:
   ```powershell
   git add .
   ```

4. **Create first commit**:
   ```powershell
   git commit -m "Initial commit - Photo Contest App"
   ```

5. **Connect to GitHub** (replace YOUR_USERNAME with your GitHub username):
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/photo-contest.git
   ```

6. **Rename branch to main**:
   ```powershell
   git branch -M main
   ```

7. **Push to GitHub**:
   ```powershell
   git push -u origin main
   ```
   - You'll be asked for username and password
   - Username: Your GitHub username
   - Password: Use a **Personal Access Token** (see below)

### If you used GitHub Desktop (Option B):

1. Open **GitHub Desktop**
2. Click **"File"** → **"Add Local Repository"**
3. Click **"Choose..."** and select: `C:\Users\Guest 1\photo_contest`
4. Click **"Add Repository"**
5. At the bottom, enter commit message: "Initial commit - Photo Contest App"
6. Click **"Commit to main"**
7. Click **"Publish repository"**
8. Make sure **"Keep this code private"** is **UNCHECKED** (must be public)
9. Click **"Publish repository"**

**✅ Your code is now on GitHub!**

---

## STEP 5: Create Personal Access Token (If using Git command line)

If you used Git command line and need a password:

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Name it: "Streamlit Deployment"
4. Select expiration: **90 days** (or your preference)
5. Check these permissions:
   - ✅ `repo` (all repo permissions)
6. Click **"Generate token"**
7. **COPY THE TOKEN** (you won't see it again!)
8. Use this token as your password when pushing

---

## STEP 6: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**:
   - Visit: https://share.streamlit.io
   - Click **"Sign in"**
   - Click **"Continue with GitHub"**
   - Authorize Streamlit Cloud

2. **Create New App**:
   - Click **"New app"** button
   - You'll see a form:
     - **Repository**: Select `YOUR_USERNAME/photo-contest`
     - **Branch**: Select `main`
     - **Main file path**: Type `app.py`
     - **App URL** (optional): `photo-contest` (will become `photo-contest.streamlit.app`)

3. **Click "Deploy"**
   - Wait 1-2 minutes for deployment
   - You'll see build logs

4. **✅ Success!**
   - Your app is live at: `https://photo-contest.streamlit.app`
   - Click the URL to open your app

---

## STEP 7: First-Time Setup

1. **Open your deployed app** (the Streamlit Cloud URL)

2. **Register Admin Account**:
   - Click "Register" tab
   - Username: `alphabetagamma`
   - Password: (choose a secure password)
   - Name: Admin User
   - Employee ID: EMP001
   - Designation: Administrator
   - Click "Register"

3. **Login as Admin**:
   - Switch to "Login" tab
   - Enter username: `alphabetagamma`
   - Enter password
   - Click "Login"

4. **Test the App**:
   - Upload a test photo
   - Enable voting phase
   - Test voting
   - End voting to see results

---

## STEP 8: Share Your App

1. **Copy your app URL**: `https://photo-contest.streamlit.app`
2. **Share with users** via:
   - Email
   - WhatsApp
   - Teams/Slack
   - Any messaging platform

3. **Users can**:
   - Open the URL in any browser
   - Register their accounts
   - Upload photos (max 2 per user)
   - Vote for photos

---

## Troubleshooting

### Problem: "Git is not recognized"
**Solution**: Install Git (Step 1) and restart your terminal

### Problem: "Repository not found"
**Solution**: Make sure repository name matches exactly

### Problem: "Authentication failed"
**Solution**: Use Personal Access Token instead of password (Step 5)

### Problem: "App failed to deploy"
**Solution**: 
- Check `requirements.txt` exists
- Check `app.py` is in root folder
- Check build logs for errors

### Problem: "Data is lost after restart"
**Solution**: This is normal for Streamlit Cloud free tier. Consider database for production.

---

## Quick Checklist

- [ ] Git installed OR GitHub Desktop installed
- [ ] GitHub account created
- [ ] Repository created (Public)
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud account created
- [ ] App deployed on Streamlit Cloud
- [ ] Admin account registered
- [ ] App tested and working
- [ ] URL shared with users

---

## Need Help?

- **Streamlit Cloud Docs**: https://docs.streamlit.io/streamlit-cloud
- **GitHub Help**: https://docs.github.com
- **Streamlit Community**: https://discuss.streamlit.io

---

**🎉 Congratulations! Your app is now live on the internet!**

