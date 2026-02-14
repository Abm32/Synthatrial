# 🏆 Competition Deployment Guide - Anukriti AI

**Quick deployment for competition demo without AWS costs!**

## 🚀 Immediate Action Plan (Tonight)

### Option 1: Render.com (Recommended - Python Backend)

**Why Render?**
- ✅ Free tier, no credit card required
- ✅ Perfect for Python/FastAPI
- ✅ Automatic HTTPS
- ✅ Easy environment variables
- ✅ Built-in monitoring

**Deploy in 5 Minutes:**

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Ready for competition deployment"
   git push origin main
   ```

2. **Deploy to Render**:
   - Go to [render.com](https://render.com) → Sign up (free)
   - Click "New +" → "Web Service"
   - Connect GitHub → Select your repo
   - **Name**: `anukriti-ai-competition`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port 10000`
   - **Environment Variables**:
     - `GOOGLE_API_KEY`: Your Gemini API key
     - `GEMINI_MODEL`: `gemini-2.5-flash`
   - Click "Create Web Service"

3. **Get Your Live URL**:
   ```
   https://anukriti-ai-competition.onrender.com
   ```

4. **Test Immediately**:
   ```bash
   curl https://anukriti-ai-competition.onrender.com/
   ```

### Option 2: Vercel (Alternative - Serverless)

**For Vercel deployment:**

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy**:
   ```bash
   vercel --prod
   ```

3. **Set Environment Variables**:
   ```bash
   vercel env add GOOGLE_API_KEY
   ```

## 🎬 Demo Video Setup

### Frontend Options

**Option A: Use Existing HTML Frontend**
- File: `examples/anukriti_frontend_example.html`
- Update API URL to your Render deployment
- Host on Vercel/Netlify for free

**Option B: Simple Test Interface**
Create `demo.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Anukriti AI - Competition Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        input, textarea {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: none;
            border-radius: 8px;
            background: rgba(255,255,255,0.9);
            color: #333;
        }
        button {
            background: #ff6b6b;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        button:hover { background: #ff5252; }
        .result {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            white-space: pre-wrap;
        }
        .risk-high { color: #ff4444; font-weight: bold; }
        .risk-medium { color: #ffaa00; font-weight: bold; }
        .risk-low { color: #44ff44; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧬 Anukriti AI: Pharmacogenomics Risk Simulator</h1>
        <p><em>AI-powered drug safety prediction using genetic profiles</em></p>

        <h3>Drug Information</h3>
        <input type="text" id="drugName" placeholder="Drug Name (e.g., Warfarin)" value="Warfarin">

        <h3>Patient Profile</h3>
        <textarea id="patientProfile" rows="4" placeholder="Enter patient genetics and conditions">ID: DEMO-001
Age: 45
Genetics: CYP2C9 Poor Metabolizer
Conditions: Atrial Fibrillation</textarea>

        <button onclick="runAnalysis()">🚀 Analyze Risk</button>

        <div id="result" style="display:none;"></div>
    </div>

    <script>
        async function runAnalysis() {
            const drugName = document.getElementById('drugName').value;
            const patientProfile = document.getElementById('patientProfile').value;
            const resultDiv = document.getElementById('result');

            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '⏳ Analyzing...';

            try {
                const response = await fetch('https://anukriti-ai-competition.onrender.com/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        drug_name: drugName,
                        patient_profile: patientProfile
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    const riskClass = `risk-${data.risk_level?.toLowerCase() || 'unknown'}`;
                    resultDiv.innerHTML = `
                        <div class="result">
                            <div class="${riskClass}" style="font-size: 20px; margin-bottom: 15px;">
                                ⚠️ RISK LEVEL: ${data.risk_level || 'Unknown'}
                            </div>
                            <div>${data.result}</div>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<div class="result" style="color: #ff4444;">Error: ${data.detail}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="result" style="color: #ff4444;">Error: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>
```

## 📝 Competition Article Content

### "How I Built This" Section

**Architecture Overview:**
```
"The Anukriti AI platform uses a cloud-agnostic microservices architecture:

🧬 Core Engine: Python-based pharmacogenomics simulation using Google Gemini LLM
🔬 Data Layer: RDKit molecular fingerprinting + Pinecone vector database
🌐 API Layer: FastAPI with automatic OpenAPI documentation
🚀 Deployment: Containerized for any cloud platform (currently on Render)

The system is designed for enterprise scalability - while demonstrated on Render's
free tier, it's fully compatible with AWS Lambda, Fargate, and Kubernetes for
production deployment."
```

**Key Features to Highlight:**
- ✅ Real-time pharmacogenomics risk assessment
- ✅ CPIC guideline compliance
- ✅ Multi-enzyme genetic analysis (CYP2D6, CYP2C19, CYP2C9)
- ✅ RESTful API with interactive documentation
- ✅ Cloud-agnostic containerized deployment
- ✅ Enterprise-ready security and monitoring

## 🎯 Demo Script (2-3 minutes)

1. **Introduction** (30s):
   "Hi! I'm demonstrating Anukriti AI - an AI-powered pharmacogenomics platform that predicts drug safety based on patient genetics."

2. **Show the Interface** (30s):
   - Open your deployed frontend
   - Explain the input fields
   - "Here we enter a drug name and patient genetic profile"

3. **Live Demo** (60s):
   - Enter "Warfarin" as drug
   - Patient profile: "CYP2C9 Poor Metabolizer, Atrial Fibrillation"
   - Click analyze
   - Show real-time AI analysis
   - Highlight risk level and recommendations

4. **Technical Highlights** (30s):
   - "The system uses Google Gemini AI with CPIC clinical guidelines"
   - "Molecular fingerprinting for drug similarity"
   - "Deployed on cloud infrastructure with REST API"
   - Show API documentation at `/docs`

5. **Conclusion** (30s):
   - "This demonstrates AI's potential in personalized medicine"
   - "Enterprise-ready for healthcare integration"

## 🔧 Quick Fixes & Optimizations

### Make API More Demo-Friendly

Add to `api.py`:

```python
@app.get("/demo")
async def demo_examples():
    """Get demo examples for testing"""
    return {
        "examples": [
            {
                "drug_name": "Warfarin",
                "patient_profile": "ID: DEMO-001\nAge: 45\nGenetics: CYP2C9 Poor Metabolizer\nConditions: Atrial Fibrillation",
                "expected_risk": "High"
            },
            {
                "drug_name": "Codeine",
                "patient_profile": "ID: DEMO-002\nAge: 32\nGenetics: CYP2D6 Poor Metabolizer\nConditions: Chronic Pain",
                "expected_risk": "High"
            },
            {
                "drug_name": "Ibuprofen",
                "patient_profile": "ID: DEMO-003\nAge: 28\nGenetics: CYP2C9 Normal Metabolizer\nConditions: Headache",
                "expected_risk": "Low"
            }
        ]
    }
```

### Environment Variables for Competition

Create `.env.competition`:
```bash
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=0.3
ENVIRONMENT=competition
DEBUG=false
```

## 🏆 Competition Advantages

**Why This Approach Wins:**

1. **Working Demo**: Live, functional application
2. **Professional Quality**: Enterprise-grade architecture
3. **Real AI Integration**: Actual LLM-powered analysis
4. **Scientific Accuracy**: CPIC guideline compliance
5. **Scalable Design**: Cloud-agnostic deployment
6. **Complete Documentation**: API docs, deployment guides
7. **Open Source**: Full GitHub repository

## 📞 Emergency Support

**If deployment fails:**

1. **Check logs** in Render dashboard
2. **Verify environment variables** are set
3. **Test locally first**:
   ```bash
   python api.py
   curl http://localhost:8000/
   ```
4. **Fallback**: Use existing `examples/anukriti_frontend_example.html` with mock data

**Contact for urgent help:**
- GitHub Issues: [Your repo]/issues
- Email: [Your email]

---

**🎯 Goal**: Have live demo URL within 2 hours!
**🏆 Result**: Professional AI application ready for competition judging!
