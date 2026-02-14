# 🚀 QUICK DEPLOY - Competition Ready in 10 Minutes

## Step 1: Push to GitHub (2 minutes)

```bash
git add .
git commit -m "Competition deployment ready"
git push origin main
```

## Step 2: Deploy to Render (5 minutes)

1. **Go to [render.com](https://render.com)** → Sign up (free, no card needed)

2. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect GitHub → Select your repo
   - **Name**: `anukriti-ai-competition`

3. **Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port 10000`

4. **Environment Variables**:
   - `GOOGLE_API_KEY`: Your Gemini API key
   - `GEMINI_MODEL`: `gemini-2.5-flash`

5. **Click "Create Web Service"**

## Step 3: Test Your Live API (2 minutes)

Your URL: `https://anukriti-ai-competition.onrender.com`

**Quick Test**:
```bash
curl https://anukriti-ai-competition.onrender.com/
```

**Demo Examples**:
```bash
curl https://anukriti-ai-competition.onrender.com/demo
```

## Step 4: Frontend Demo (1 minute)

1. **Update `demo.html`** - Change API_BASE to your Render URL
2. **Host on Vercel/Netlify** or open locally
3. **Test the interface**

## 🎬 Demo Script

**"Hi! I built Anukriti AI - an AI pharmacogenomics platform that predicts drug safety based on patient genetics."**

1. Show live interface
2. Enter "Warfarin" + "CYP2C9 Poor Metabolizer"
3. Click analyze → Show real-time AI response
4. Highlight risk level and clinical recommendations
5. Show API docs at `/docs`

**"This demonstrates AI's potential in personalized medicine, deployed on cloud infrastructure with enterprise-ready APIs."**

## 🏆 Competition Advantages

✅ **Working Live Demo** - Functional application
✅ **Real AI Integration** - Google Gemini LLM
✅ **Scientific Accuracy** - CPIC guidelines
✅ **Professional API** - OpenAPI documentation
✅ **Cloud Deployment** - Production-ready
✅ **Open Source** - Complete GitHub repo

## 🆘 Emergency Backup

If Render fails, use local demo:
```bash
python api.py
# Open demo.html and change API_BASE to http://localhost:8000
```

---
**🎯 Result**: Live AI application ready for competition in under 10 minutes!
