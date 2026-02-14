# Anukriti AI - Render Deployment Guide

Complete guide for deploying the Anukriti AI Pharmacogenomics API to Render.

## 🚀 Quick Start

### Prerequisites
- GitHub account
- Render account (free tier available at [render.com](https://render.com))
- Google Gemini API key

### Step 1: Push to GitHub

From your local repository:

```bash
# Check current status
git status

# Add the new API files
git add api.py RENDER_DEPLOYMENT.md

# Commit changes
git commit -m "Add FastAPI wrapper for Render deployment"

# Push to GitHub
git push origin main
```

### Step 2: Deploy to Render

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up (no credit card required for free tier)

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Select "Build and deploy from a Git repository"
   - Connect your GitHub account
   - Choose your SynthaTrial repository

3. **Configure Service Settings**

   **Basic Settings:**
   - **Name**: `anukriti-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your deployment branch)

   **Build & Deploy:**
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```

   - **Start Command**:
     ```bash
     uvicorn api:app --host 0.0.0.0 --port 10000
     ```

   **Instance Type:**
   - Select **Free** tier (sufficient for testing and demos)

4. **Set Environment Variables**

   Click "Environment" tab and add:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `GOOGLE_API_KEY` | `your_gemini_api_key` | **Required** - Your Google Gemini API key |
   | `GEMINI_MODEL` | `gemini-2.5-flash` | Optional - Model to use (default: gemini-2.5-flash) |
   | `GEMINI_TEMPERATURE` | `0.3` | Optional - LLM temperature (default: 0.3) |
   | `PORT` | `10000` | Optional - Port (Render uses 10000 by default) |

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Wait for deployment to complete (usually 2-5 minutes)

### Step 3: Test Your Deployment

Once deployed, Render will provide a URL like:
```
https://anukriti-api.onrender.com
```

**Test Health Check:**
```bash
curl -s https://anukriti-api.onrender.com/
```

Expected response:
```json
{
  "status": "Anukriti AI Engine Online",
  "version": "0.2.0",
  "model": "gemini-2.5-flash"
}
```

**Test Analysis Endpoint:**
```bash
curl -s -X POST https://anukriti-api.onrender.com/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "drug_name": "Warfarin",
    "drug_smiles": "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
    "patient_profile": "ID: HG00096\nAge: 45\nGenetics: CYP2C9 Poor Metabolizer\nConditions: Atrial Fibrillation",
    "similar_drugs": ["Warfarin (CYP2C9 substrate, bleeding risk)"]
  }'
```

Expected response:
```json
{
  "result": "RISK LEVEL: High\n\nPREDICTED REACTION: ...",
  "risk_level": "High",
  "drug_name": "Warfarin",
  "status": "success"
}
```

## 📋 API Documentation

### Endpoints

#### `GET /`
Health check endpoint

**Response:**
```json
{
  "status": "Anukriti AI Engine Online",
  "version": "0.2.0",
  "model": "gemini-2.5-flash"
}
```

#### `POST /analyze`
Analyze drug-patient interaction

**Request Body:**
```json
{
  "drug_name": "string (required)",
  "patient_profile": "string (required)",
  "drug_smiles": "string (optional)",
  "similar_drugs": ["string"] (optional)
}
```

**Response:**
```json
{
  "result": "string - Full AI analysis",
  "risk_level": "Low|Medium|High",
  "drug_name": "string",
  "status": "success"
}
```

**Example Request:**
```bash
curl -X POST https://anukriti-api.onrender.com/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "drug_name": "Codeine",
    "patient_profile": "ID: SP-01\nAge: 45\nGenetics: CYP2D6 Poor Metabolizer\nConditions: Chronic Pain",
    "similar_drugs": ["Codeine (CYP2D6 substrate, prodrug activation)"]
  }'
```

## 🎨 Frontend Integration

### Example: Simple HTML/JavaScript

```html
<!DOCTYPE html>
<html>
<head>
    <title>Anukriti AI - Pharmacogenomics Risk Simulator</title>
    <style>
        body {
            background: #0a0e27;
            color: #00ffff;
            font-family: 'Courier New', monospace;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background: rgba(0, 255, 255, 0.1);
            border: 1px solid #00ffff;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        input, textarea {
            width: 100%;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid #00ffff;
            color: #00ffff;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        button {
            background: #00ffff;
            color: #0a0e27;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background: #00cccc;
        }
        .risk-high { color: #ff4444; }
        .risk-medium { color: #ffaa00; }
        .risk-low { color: #44ff44; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧬 Anukriti: AI Pharmacogenomics Risk Simulator</h1>

        <div class="card">
            <h2>Drug Information</h2>
            <label>Drug Name:</label>
            <input type="text" id="drugName" value="Warfarin">

            <label>SMILES (optional):</label>
            <input type="text" id="drugSmiles" placeholder="CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O">
        </div>

        <div class="card">
            <h2>Patient Profile</h2>
            <textarea id="patientProfile" rows="6">ID: HG00096
Age: 45
Genetics: CYP2C9 Poor Metabolizer
Conditions: Atrial Fibrillation
Lifestyle: Non-smoker, Moderate alcohol</textarea>
        </div>

        <button onclick="runSimulation()">🚀 Run Simulation</button>

        <div id="results" class="card" style="display:none;">
            <h2>Results</h2>
            <div id="riskLevel"></div>
            <div id="fullResult"></div>
        </div>
    </div>

    <script>
        async function runSimulation() {
            const drugName = document.getElementById('drugName').value;
            const drugSmiles = document.getElementById('drugSmiles').value;
            const patientProfile = document.getElementById('patientProfile').value;

            const resultsDiv = document.getElementById('results');
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = '<p>⏳ Running simulation...</p>';

            try {
                const response = await fetch('https://anukriti-api.onrender.com/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        drug_name: drugName,
                        drug_smiles: drugSmiles || null,
                        patient_profile: patientProfile,
                        similar_drugs: []
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    const riskClass = `risk-${data.risk_level.toLowerCase()}`;
                    resultsDiv.innerHTML = `
                        <h2>Results</h2>
                        <div class="${riskClass}" style="font-size: 24px; margin: 20px 0;">
                            ⚠️ RISK LEVEL: ${data.risk_level.toUpperCase()}
                        </div>
                        <pre style="white-space: pre-wrap;">${data.result}</pre>
                    `;
                } else {
                    resultsDiv.innerHTML = `<p style="color: #ff4444;">Error: ${data.detail}</p>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<p style="color: #ff4444;">Error: ${error.message}</p>`;
            }
        }
    </script>
</body>
</html>
```

## 🔧 Troubleshooting

### Common Issues

**1. Deployment Fails**
- Check build logs in Render dashboard
- Verify `requirements.txt` is in repository root
- Ensure Python version compatibility (3.10+)

**2. API Returns 500 Error**
- Verify `GOOGLE_API_KEY` is set in environment variables
- Check Render logs for detailed error messages
- Test API key locally first

**3. Slow Response Times (Free Tier)**
- Free tier instances sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Consider upgrading to paid tier for production use

**4. CORS Issues**
- API has CORS enabled for all origins
- If issues persist, check browser console for specific errors

### Viewing Logs

In Render dashboard:
1. Go to your service
2. Click "Logs" tab
3. View real-time logs and errors

### Manual Testing

Use the interactive API documentation:
```
https://anukriti-api.onrender.com/docs
```

This provides a Swagger UI for testing endpoints directly.

## 🚀 Production Considerations

### Scaling
- **Free Tier**: 512 MB RAM, sleeps after inactivity
- **Starter Tier** ($7/month): 512 MB RAM, no sleep
- **Standard Tier** ($25/month): 2 GB RAM, better performance

### Security
- Store API keys in Render environment variables (never in code)
- Enable HTTPS (automatic with Render)
- Consider rate limiting for production use
- Restrict CORS origins in production

### Monitoring
- Use Render's built-in metrics
- Set up health check monitoring
- Configure alerts for downtime

### Custom Domain
1. Go to service settings
2. Click "Custom Domains"
3. Add your domain and configure DNS

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SynthaTrial GitHub](https://github.com/your-username/SynthaTrial)

## 🆘 Support

For issues or questions:
- Check Render logs first
- Review this deployment guide
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

**Version**: 0.2.0
**Last Updated**: 2026-02-13
