# Cloudinary Setup Guide

## Why Cloudinary?

Cloudinary provides **free cloud storage** for your photos, allowing:
- ✅ **Unlimited photos** (25GB free storage)
- ✅ **Fast loading** (CDN delivery)
- ✅ **Automatic optimization** (images are optimized automatically)
- ✅ **No data loss** (photos persist even when Streamlit Cloud redeploys)
- ✅ **Free tier** (no credit card required for basic use)

## Step-by-Step Setup

### 1. Create a Free Cloudinary Account

1. Go to **https://cloudinary.com/users/register/free**
2. Sign up with your email (or use Google/GitHub)
3. Verify your email if required

### 2. Get Your Cloudinary Credentials

After signing up, you'll see your **Dashboard** with:
- **Cloud Name** (e.g., `dxyz123abc`)
- **API Key** (e.g., `123456789012345`)
- **API Secret** (e.g., `abcdefghijklmnopqrstuvwxyz123456`)

**Important:** Keep these credentials secure!

### 3. Add Credentials to Streamlit Cloud

1. Go to your **Streamlit Cloud** dashboard: https://share.streamlit.io/
2. Click on your app (or create a new one)
3. Click **"Settings"** (⚙️ icon) or **"Secrets"**
4. Click **"Edit secrets"** or **"Add new secret"**
5. Add the following in the secrets editor:

```toml
[cloudinary]
cloud_name = "your-cloud-name-here"
api_key = "your-api-key-here"
api_secret = "your-api-secret-here"
```

**Example:**
```toml
[cloudinary]
cloud_name = "dxyz123abc"
api_key = "123456789012345"
api_secret = "abcdefghijklmnopqrstuvwxyz123456"
```

6. Click **"Save"**

### 4. Redeploy Your App

After saving secrets:
- Streamlit Cloud will automatically redeploy your app
- Or click **"Reboot app"** in the Streamlit Cloud dashboard

### 5. Test It Out!

1. Upload a photo through your app
2. The photo will be automatically uploaded to Cloudinary
3. Check your Cloudinary dashboard to see the uploaded photos

## How It Works

- **If Cloudinary is configured:** Photos are uploaded to Cloudinary (best option)
- **If Cloudinary is NOT configured:** Photos are stored as base64 in CSV (fallback, limited to ~10-20 photos)

## Storage Limits

### Cloudinary Free Tier:
- **25 GB storage** (thousands of photos!)
- **25 GB bandwidth/month** (plenty for a photo contest)
- **No credit card required**

### Base64 Fallback (if Cloudinary not configured):
- **~10-20 photos max** (due to GitHub file size limits)
- CSV files become very large

## Troubleshooting

### Photos not uploading to Cloudinary?
1. Check that secrets are saved correctly in Streamlit Cloud
2. Verify credentials are correct (no extra spaces)
3. Check Streamlit Cloud logs for errors

### App works but photos disappear?
- Make sure Cloudinary credentials are configured
- Check that photos are being uploaded (check Cloudinary dashboard)

### Need Help?
- Cloudinary Docs: https://cloudinary.com/documentation
- Streamlit Secrets: https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management

## Security Note

⚠️ **Never commit your Cloudinary credentials to Git!**
- They should ONLY be in Streamlit Cloud Secrets
- The `.gitignore` file already excludes secrets files
- Keep your API Secret private

