# 🚀 Anukriti AI - Quick Start Guide

**Get your Pharmacogenomics API deployed in 15 minutes!**

## What You Have Now

✅ **FastAPI Wrapper** (`api.py`) - Production-ready REST API
✅ **Test Suite** (`test_api.py`) - Automated testing
✅ **Frontend Example** (`examples/anukriti_frontend_example.html`) - Beautiful dark-themed UI
✅ **Deployment Guide** (`RENDER_DEPLOYMENT.md`) - Step-by-step instructions
✅ **API Documentation** (`API_README.md`) - Complete API reference

## 3-Step Deployment

### 1️⃣ Test Locally (2 minutes)

```bash
# Set your API key
export GOOGLE_API_KEY="your_gemini_api_key"

# Start the API
python api.py

# In another terminal, test it
curl http://localhost:8000/
python test_api.py
```

### 2️⃣ Push to GitHub (1 minute)

```bash
git add api.py test_api.py *.md examples/anukriti_frontend_example.html
git commit -m "Add FastAPI wrapper for Render deployment"
git push origin main
```

### 3️⃣ Deploy to Render (10 minutes)

1. Go to [render.com](https://render.com) and sign up (free)
2. Click "New +" → "Web Service" → Connect GitHub
3. Select your repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port 10000`
   - **Environment Variable**: `GOOGLE_API_KEY` = your key
5. Click "Create Web Service"
6. Wait 2-5 minutes ⏳

## Test Your Deployed API

```bash
# Health check
curl https://anukriti-api.onrender.com/

# Warfarin analysis
curl -X POST https://anukriti-api.onrender.com/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "drug_name": "Warfarin",
    "patient_profile": "ID: HG00096\nAge: 45\nGenetics: CYP2C9 Poor Metabolizer",
    "similar_drugs": ["Warfarin (CYP2C9 substrate, bleeding risk)"]
  }'
```

## Use the Frontend

1. Open `examples/anukriti_frontend_example.html`
2. Update line 267 with your Render URL:
   ```javascript
   const API_BASE_URL = 'https://anukriti-api.onrender.com';
   ```
3. Open in browser
4. Click "Warfarin" → "Run Simulation"
5. See results in 10-30 seconds! 🎉

## API Endpoints

### `GET /`
Health check - returns API status

### `POST /analyze`
Analyze drug-patient interaction

**Request:**
```json
{
  "drug_name": "Warfarin",
  "patient_profile": "ID: HG00096\nAge: 45\nGenetics: CYP2C9 Poor Metabolizer",
  "similar_drugs": ["Warfarin (CYP2C9 substrate, bleeding risk)"]
}
```

**Response:**
```json
{
  "result": "RISK LEVEL: High\n\nPREDICTED REACTION: ...",
  "risk_level": "High",
  "drug_name": "Warfarin",
  "status": "success"
}
```

## Example Use Cases

### Warfarin (High Risk)
```bash
curl -X POST https://anukriti-api.onrender.com/analyze \
  -H 'Content-Type: application/json' \
  -d '{"drug_name":"Warfarin","patient_profile":"ID: HG00096\nGenetics: CYP2C9 Poor Metabolizer","similar_drugs":["Warfarin (CYP2C9 substrate, bleeding risk)"]}'
```

### Codeine (High Risk)
```bash
curl -X POST https://anukriti-api.onrender.com/analyze \
  -H 'Content-Type: application/json' \
  -d '{"drug_name":"Codeine","patient_profile":"ID: SP-02\nGenetics: CYP2D6 Poor Metabolizer","similar_drugs":["Codeine (CYP2D6 substrate, prodrug)"]}'
```

### Clopidogrel (Medium Risk)
```bash
curl -X POST https://anukriti-api.onrender.com/analyze \
  -H 'Content-Type: application/json' \
  -d '{"drug_name":"Clopidogrel","patient_profile":"ID: SP-03\nGenetics: CYP2C19 Poor Metabolizer","similar_drugs":["Clopidogrel (CYP2C19 substrate)"]}'
```

## Troubleshooting

**API returns 500 error?**
→ Check `GOOGLE_API_KEY` is set in Render environment variables

**Slow response (30+ seconds)?**
→ Normal for free tier - first request wakes up the instance

**Frontend can't connect?**
→ Update API URL in HTML file (line 267)

**Need detailed logs?**
→ Check Render dashboard → Logs tab

## Interactive Documentation

Once deployed, visit:
- **Swagger UI**: `https://anukriti-api.onrender.com/docs`
- **ReDoc**: `https://anukriti-api.onrender.com/redoc`

## Files Created

| File | Purpose |
|------|---------|
| `api.py` | FastAPI application |
| `test_api.py` | Test suite |
| `RENDER_DEPLOYMENT.md` | Detailed deployment guide |
| `API_README.md` | Complete API documentation |
| `DEPLOYMENT_CHECKLIST.md` | Step-by-step checklist |
| `examples/anukriti_frontend_example.html` | Frontend UI |

## Next Steps

1. ✅ Deploy to Render
2. ✅ Test with provided examples
3. ✅ Customize frontend colors/layout
4. ✅ Add your own drug examples
5. ✅ Share your API URL!

## Need More Help?

- **Detailed Guide**: See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
- **API Docs**: See [API_README.md](API_README.md)
- **Checklist**: See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Render Docs**: [render.com/docs](https://render.com/docs)

---

**Your API will be live at**: `https://anukriti-api.onrender.com`

**Ready to deploy?** Follow the 3 steps above! 🚀
