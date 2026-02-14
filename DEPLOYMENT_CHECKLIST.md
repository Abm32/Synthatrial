# 🚀 Anukriti AI Deployment Checklist

Complete step-by-step guide to deploy your Pharmacogenomics API to Render.

## ✅ What's Already Done

I've created the following files for you:

1. **`api.py`** - FastAPI wrapper with two endpoints:
   - `GET /` - Health check
   - `POST /analyze` - Drug analysis endpoint

2. **`RENDER_DEPLOYMENT.md`** - Complete deployment guide

3. **`API_README.md`** - API documentation and usage guide

4. **`test_api.py`** - Test script for local and deployed API

5. **`examples/anukriti_frontend_example.html`** - Beautiful dark-themed frontend example

6. **`requirements.txt`** - Already includes FastAPI and uvicorn

## 📋 Deployment Steps

### Step 1: Test Locally (5 minutes)

```bash
# 1. Make sure you're in the SynthaTrial directory
cd /home/abhimanyu/Desktop/SynthaTrial-repo

# 2. Activate your conda environment
conda activate synthatrial

# 3. Verify dependencies are installed
pip install fastapi uvicorn[standard]

# 4. Set your API key
export GOOGLE_API_KEY="your_gemini_api_key_here"

# 5. Start the API
python api.py
```

In another terminal, test it:
```bash
# Health check
curl -s http://localhost:8000/

# Full test suite
python test_api.py
```

Expected output:
```json
{
  "status": "Anukriti AI Engine Online",
  "version": "0.2.0",
  "model": "gemini-2.5-flash"
}
```

### Step 2: Push to GitHub (2 minutes)

```bash
# Check what's new
git status

# Add new files
git add api.py RENDER_DEPLOYMENT.md API_README.md test_api.py DEPLOYMENT_CHECKLIST.md
git add examples/anukriti_frontend_example.html

# Commit
git commit -m "Add FastAPI wrapper and Render deployment files"

# Push to GitHub
git push origin main
```

### Step 3: Deploy to Render (10 minutes)

1. **Go to Render**
   - Visit [render.com](https://render.com)
   - Sign up or log in (free tier, no credit card needed)

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Click "Build and deploy from a Git repository"
   - Connect your GitHub account
   - Select your `SynthaTrial` repository

3. **Configure Service**

   Fill in these exact settings:

   | Setting | Value |
   |---------|-------|
   | **Name** | `anukriti-api` |
   | **Environment** | `Python 3` |
   | **Region** | Choose closest to you |
   | **Branch** | `main` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn api:app --host 0.0.0.0 --port 10000` |
   | **Instance Type** | `Free` |

4. **Set Environment Variables**

   Click "Environment" tab and add:

   | Key | Value |
   |-----|-------|
   | `GOOGLE_API_KEY` | Your actual Gemini API key |
   | `GEMINI_MODEL` | `gemini-2.5-flash` (optional) |

5. **Deploy**
   - Click "Create Web Service"
   - Wait 2-5 minutes for deployment
   - Render will show you the URL (e.g., `https://anukriti-api.onrender.com`)

### Step 4: Test Deployed API (2 minutes)

```bash
# Replace with your actual Render URL
export API_URL="https://anukriti-api.onrender.com"

# Health check
curl -s $API_URL/

# Full test
python test_api.py $API_URL
```

### Step 5: Test Frontend (2 minutes)

1. Open `examples/anukriti_frontend_example.html` in a text editor

2. Update the API URL (line 267):
   ```javascript
   const API_BASE_URL = 'https://anukriti-api.onrender.com';
   ```

3. Open the HTML file in your browser

4. Click "Warfarin" example button

5. Click "Run Simulation"

6. Wait 10-30 seconds for results

## 🎯 Expected Results

### Health Check Response
```json
{
  "status": "Anukriti AI Engine Online",
  "version": "0.2.0",
  "model": "gemini-2.5-flash"
}
```

### Analysis Response (Warfarin Example)
```json
{
  "result": "RISK LEVEL: High\n\nPREDICTED REACTION: Increased bleeding risk due to reduced warfarin metabolism...",
  "risk_level": "High",
  "drug_name": "Warfarin",
  "status": "success"
}
```

## 🐛 Troubleshooting

### Issue: "Module not found" error
**Solution**: Make sure `requirements.txt` includes all dependencies
```bash
pip install -r requirements.txt
```

### Issue: "GOOGLE_API_KEY not set"
**Solution**: Set environment variable in Render dashboard
- Go to your service → Environment tab
- Add `GOOGLE_API_KEY` with your actual key

### Issue: API returns 500 error
**Solution**: Check Render logs
- Go to your service → Logs tab
- Look for error messages
- Verify API key is correct

### Issue: Slow response (30+ seconds)
**Solution**: This is normal for free tier
- Free tier instances sleep after 15 minutes
- First request wakes up the instance (~30 seconds)
- Subsequent requests are faster (5-15 seconds)

### Issue: Frontend can't connect to API
**Solution**: Check CORS and URL
- Verify API URL in HTML file is correct
- Check browser console for errors
- API has CORS enabled for all origins

## 📱 Using Your API

### cURL Examples

**Warfarin (High Risk):**
```bash
curl -X POST https://anukriti-api.onrender.com/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "drug_name": "Warfarin",
    "patient_profile": "ID: HG00096\nAge: 45\nGenetics: CYP2C9 Poor Metabolizer\nConditions: Atrial Fibrillation",
    "similar_drugs": ["Warfarin (CYP2C9 substrate, bleeding risk)"]
  }'
```

**Codeine (High Risk):**
```bash
curl -X POST https://anukriti-api.onrender.com/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "drug_name": "Codeine",
    "patient_profile": "ID: SP-02\nAge: 52\nGenetics: CYP2D6 Poor Metabolizer\nConditions: Chronic Pain",
    "similar_drugs": ["Codeine (CYP2D6 substrate, prodrug activation)"]
  }'
```

**Clopidogrel (Medium Risk):**
```bash
curl -X POST https://anukriti-api.onrender.com/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "drug_name": "Clopidogrel",
    "patient_profile": "ID: SP-03\nAge: 58\nGenetics: CYP2C19 Poor Metabolizer\nConditions: Recent MI",
    "similar_drugs": ["Clopidogrel (CYP2C19 substrate, antiplatelet)"]
  }'
```

### Python Example

```python
import requests

response = requests.post(
    'https://anukriti-api.onrender.com/analyze',
    json={
        'drug_name': 'Warfarin',
        'patient_profile': 'ID: HG00096\nAge: 45\nGenetics: CYP2C9 Poor Metabolizer',
        'similar_drugs': ['Warfarin (CYP2C9 substrate, bleeding risk)']
    }
)

data = response.json()
print(f"Risk Level: {data['risk_level']}")
print(f"Result:\n{data['result']}")
```

### JavaScript Example

```javascript
const response = await fetch('https://anukriti-api.onrender.com/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    drug_name: 'Warfarin',
    patient_profile: 'ID: HG00096\nAge: 45\nGenetics: CYP2C9 Poor Metabolizer',
    similar_drugs: ['Warfarin (CYP2C9 substrate, bleeding risk)']
  })
});

const data = await response.json();
console.log('Risk Level:', data.risk_level);
```

## 🎨 Frontend Customization

The example frontend (`examples/anukriti_frontend_example.html`) includes:

- ✅ Dark "bio-digital" theme with neon cyan accents
- ✅ Responsive 2-column layout
- ✅ Pre-loaded drug examples (Warfarin, Codeine, Clopidogrel)
- ✅ Color-coded risk levels (Red=High, Orange=Medium, Green=Low)
- ✅ Loading spinner and error handling
- ✅ API status indicator

To customize:
1. Update colors in CSS (search for `#00ffff` for cyan)
2. Add more drug examples in the `examples` object
3. Modify layout in the HTML structure
4. Update API URL in JavaScript

## 📊 API Documentation

Once deployed, visit these URLs:

- **Swagger UI**: `https://anukriti-api.onrender.com/docs`
- **ReDoc**: `https://anukriti-api.onrender.com/redoc`

These provide interactive API documentation where you can test endpoints directly.

## 🚀 Next Steps

1. **Custom Domain**: Add your own domain in Render settings
2. **Rate Limiting**: Implement rate limiting for production
3. **Caching**: Add caching for repeated queries
4. **Monitoring**: Set up uptime monitoring
5. **Analytics**: Track API usage and performance

## 📚 Additional Resources

- [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) - Detailed deployment guide
- [API_README.md](API_README.md) - Complete API documentation
- [examples/anukriti_frontend_example.html](examples/anukriti_frontend_example.html) - Frontend example

## ✅ Checklist Summary

- [ ] Test API locally (`python api.py`)
- [ ] Run test suite (`python test_api.py`)
- [ ] Push to GitHub (`git push origin main`)
- [ ] Create Render account
- [ ] Deploy to Render with correct settings
- [ ] Set `GOOGLE_API_KEY` environment variable
- [ ] Test deployed API health check
- [ ] Test deployed API analysis endpoint
- [ ] Update frontend HTML with deployed URL
- [ ] Test frontend in browser
- [ ] Share your API URL! 🎉

---

**Need Help?**
- Check [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed instructions
- Review [API_README.md](API_README.md) for API usage
- Check Render logs for deployment issues
- Test locally first to isolate problems

**Your API will be live at**: `https://anukriti-api.onrender.com` (or your chosen name)

Good luck with your deployment! 🚀
