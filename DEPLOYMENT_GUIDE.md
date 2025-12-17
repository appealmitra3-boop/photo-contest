# Streamlit Cloud Deployment Guide

## Step-by-Step Instructions

### Step 1: Prepare Your Code ✅
- ✅ `requirements.txt` - Created
- ✅ `.gitignore` - Created  
- ✅ `README.md` - Created
- ✅ `.streamlit/config.toml` - Created

### Step 2: Create GitHub Repository

1. **Initialize Git** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit - Photo Contest App"
```

2. **Create GitHub Repository**:
   - Go to [github.com](https://github.com)
   - Click "New repository"
   - Name it: `photo-contest` (or any name you prefer)
   - Make it **Public** (required for free Streamlit Cloud)
   - Don't initialize with README (you already have one)
   - Click "Create repository"

3. **Push to GitHub**:
```bash
git remote add origin https://github.com/YOUR_USERNAME/photo-contest.git
git branch -M main
git push -u origin main
```

**Note**: Replace `YOUR_USERNAME` with your GitHub username.

### Step 3: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create New App**:
   - Click "New app" button
   - Select your repository: `YOUR_USERNAME/photo-contest`
   - Set main file path: `app.py`
   - Set app URL (optional): `photo-contest` (will be `photo-contest.streamlit.app`)

3. **Configure Secrets (Optional but Recommended)**:
   - Click "Advanced settings"
   - Click "Secrets"
   - Add admin username:
   ```toml
   ADMIN_USERNAME = "alphabetagamma"
   ```
   - Then update `app.py` to read from secrets (optional):
   ```python
   ADMIN_USERNAME = st.secrets.get("ADMIN_USERNAME", "alphabetagamma")
   ```

4. **Deploy**:
   - Click "Deploy"
   - Wait for deployment (usually 1-2 minutes)
   - Your app will be live at: `https://photo-contest.streamlit.app`

### Step 4: Post-Deployment

1. **First Run**:
   - The app will automatically create `data/` and `photos/` folders
   - Register the admin account first: `alphabetagamma`
   - Then register other users

2. **Data Persistence**:
   - ⚠️ **Important**: Streamlit Cloud is ephemeral
   - Data persists during the session but may be lost on app restart
   - For production, consider:
     - Using a database (PostgreSQL)
     - Using cloud storage (AWS S3) for photos
     - Regular backups

3. **Sharing**:
   - Share the URL with your users
   - They can register and start using the app

## Troubleshooting

### Common Issues:

1. **Import Errors**:
   - Check `requirements.txt` has all dependencies
   - Ensure versions are compatible

2. **File Not Found Errors**:
   - The app creates folders automatically
   - Make sure `ensure_structure()` runs on startup

3. **Data Loss**:
   - This is expected on Streamlit Cloud
   - Consider database for production use

4. **Admin Access**:
   - Make sure admin username matches exactly (case-sensitive)
   - Register admin account first

## Updating Your App

1. Make changes to `app.py`
2. Commit and push to GitHub:
```bash
git add .
git commit -m "Update description"
git push
```
3. Streamlit Cloud will automatically redeploy

## Security Notes

- ✅ Passwords are hashed (SHA-256)
- ✅ HTTPS enabled automatically
- ⚠️ Admin username is in code (consider using Secrets)
- ⚠️ Data stored in CSV files (not encrypted)

## Next Steps for Production

1. **Database Migration**:
   - Replace CSV files with PostgreSQL
   - Use SQLAlchemy or similar

2. **Cloud Storage**:
   - Store photos in AWS S3 or Google Cloud Storage
   - Update `save_photo()` function

3. **Backup System**:
   - Regular database backups
   - Photo storage backups

4. **Monitoring**:
   - Add logging
   - Monitor errors

## Support

For Streamlit Cloud issues:
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-cloud)
- [Streamlit Community](https://discuss.streamlit.io/)

