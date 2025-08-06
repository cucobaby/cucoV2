# 🚄 Railway Deployment Guide

## 🎯 **Quick Deploy to Railway**

### **Method 1: GitHub Integration (Recommended)**

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add FastAPI server for Railway deployment"
   git push origin main
   ```

2. **Create Railway Project**:
   - Go to [railway.app](https://railway.app)
   - Click "Login" → Sign in with GitHub
   - Click "New Project" 
   - Select "Deploy from GitHub repo"
   - Choose your `cucoV2` repository
   - Railway auto-detects Python and uses `railway.toml`

3. **Set Environment Variables**:
   - In Railway dashboard → Your project → Variables tab
   - Add: `OPENAI_API_KEY` = `your_actual_openai_key_here`
   - Railway automatically provides `PORT` and other variables

4. **Deploy**:
   - Railway automatically builds and deploys!
   - You'll get a URL like: `https://your-app-name.railway.app`

### **Method 2: Railway CLI**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize and deploy
railway init
railway up
```

## 🔧 **Post-Deployment Setup**

### **1. Test Your API**
Visit your Railway URL:
- `https://your-app.railway.app/` - Health check
- `https://your-app.railway.app/health` - Detailed status

### **2. Update Browser Extension**
In your browser extension, update the API base URL:
```javascript
const API_BASE = 'https://your-app.railway.app';
```

### **3. Monitor & Scale**
- Railway dashboard shows:
  - Real-time logs
  - Memory/CPU usage
  - Deployment history
  - Custom domains (Pro plan)

## 🚨 **Important Notes**

### **Free Tier Limits**:
- 512MB RAM
- $5/month usage credit
- Apps sleep after 15 minutes of inactivity

### **Production Considerations**:
- Upgrade to Pro for:
  - More memory
  - No sleep mode
  - Custom domains
  - Better support

### **Security**:
- Never commit `.env` files
- Use Railway environment variables
- Consider rate limiting for production

## 🐛 **Troubleshooting**

### **Build Failed**:
- Check Railway logs in dashboard
- Verify `requirments.txt` is correct
- Ensure Python 3.9+ compatibility

### **API Not Responding**:
- Check environment variables are set
- Verify OpenAI API key is valid
- Monitor memory usage (may hit limits)

### **Cold Start Issues**:
- First request may take 10-15 seconds
- Consider Railway Pro to avoid sleeping

## 🎉 **Success Checklist**

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] API endpoints responding
- [ ] Ready for browser extension!

**Your API will be live at**: `https://[your-app-name].railway.app`
