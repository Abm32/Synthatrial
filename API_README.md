# Anukriti AI Pharmacogenomics API

FastAPI-based REST API for the SynthaTrial pharmacogenomics platform.

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key"
   export GEMINI_MODEL="gemini-2.5-flash"  # Optional
   ```

3. **Run the API**
   ```bash
   python api.py
   ```

   The API will be available at `http://localhost:8000`

4. **Test the API**
   ```bash
   # Health check
   curl http://localhost:8000/

   # Run test suite
   python test_api.py
   ```

### Interactive Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 API Endpoints

### `GET /`
Health check endpoint that returns API status and configuration.

**Response:**
```json
{
  "status": "Anukriti AI Engine Online",
  "version": "0.2.0",
  "model": "gemini-2.5-flash"
}
```

### `POST /analyze`
Analyze drug-patient interaction and predict pharmacogenomics risk.

**Request Body:**
```json
{
  "drug_name": "Warfarin",
  "patient_profile": "ID: HG00096\nAge: 45\nGenetics: CYP2C9 Poor Metabolizer",
  "drug_smiles": "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
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

## 🧪 Testing

### Run Test Suite
```bash
# Test local API
python test_api.py

# Test deployed API
python test_api.py https://anukriti-api.onrender.com
```

### Manual Testing with cURL

**Health Check:**
```bash
curl -s http://localhost:8000/ | jq
```

**Warfarin Analysis:**
```bash
curl -s -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "drug_name": "Warfarin",
    "patient_profile": "ID: HG00096\nAge: 45\nGenetics: CYP2C9 Poor Metabolizer\nConditions: Atrial Fibrillation",
    "similar_drugs": ["Warfarin (CYP2C9 substrate, bleeding risk)"]
  }' | jq
```

**Codeine Analysis:**
```bash
curl -s -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "drug_name": "Codeine",
    "patient_profile": "ID: SP-02\nAge: 52\nGenetics: CYP2D6 Poor Metabolizer\nConditions: Chronic Pain",
    "similar_drugs": ["Codeine (CYP2D6 substrate, prodrug activation)"]
  }' | jq
```

## 🎨 Frontend Integration

### Example HTML/JavaScript

See `examples/anukriti_frontend_example.html` for a complete working example.

**Basic JavaScript Integration:**
```javascript
async function analyzeRisk(drugName, patientProfile) {
  const response = await fetch('http://localhost:8000/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      drug_name: drugName,
      patient_profile: patientProfile,
      similar_drugs: []
    })
  });

  const data = await response.json();
  console.log('Risk Level:', data.risk_level);
  console.log('Full Result:', data.result);
  return data;
}
```

### Example Python Client

```python
import requests

def analyze_drug(drug_name, patient_profile, api_url="http://localhost:8000"):
    response = requests.post(
        f"{api_url}/analyze",
        json={
            "drug_name": drug_name,
            "patient_profile": patient_profile,
            "similar_drugs": []
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"Risk Level: {data['risk_level']}")
        print(f"Result:\n{data['result']}")
        return data
    else:
        print(f"Error: {response.text}")
        return None

# Example usage
analyze_drug(
    "Warfarin",
    "ID: HG00096\nAge: 45\nGenetics: CYP2C9 Poor Metabolizer"
)
```

## 🚀 Deployment

### Deploy to Render

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for complete deployment instructions.

**Quick Deploy:**
1. Push code to GitHub
2. Create new Web Service on Render
3. Set environment variables:
   - `GOOGLE_API_KEY`: Your Gemini API key
4. Deploy with:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn api:app --host 0.0.0.0 --port 10000`

### Deploy with Docker

```bash
# Build image
docker build -t anukriti-api -f docker/Dockerfile.prod .

# Run container
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_API_KEY="your_key" \
  anukriti-api \
  uvicorn api:app --host 0.0.0.0 --port 8000
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | Yes | - | Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-2.5-flash` | Gemini model to use |
| `GEMINI_TEMPERATURE` | No | `0.3` | LLM temperature (0.0-1.0) |
| `PORT` | No | `8000` | Port to run the API on |

### Model Options

- `gemini-2.5-flash` (default) - Fast, cost-effective
- `gemini-2.5-pro` - More accurate, slower
- `gemini-2.0-flash` - Alternative fast model
- `gemini-1.5-flash` - Legacy fast model

## 📊 API Response Format

### Success Response

```json
{
  "result": "RISK LEVEL: High\n\nPREDICTED REACTION: Increased bleeding risk...",
  "risk_level": "High",
  "drug_name": "Warfarin",
  "status": "success"
}
```

### Error Response

```json
{
  "detail": "Server configuration error: Missing GOOGLE_API_KEY"
}
```

## 🔒 Security Considerations

### Production Deployment

1. **API Keys**: Never commit API keys to version control
2. **CORS**: Restrict allowed origins in production
3. **Rate Limiting**: Implement rate limiting for production use
4. **HTTPS**: Always use HTTPS in production (automatic with Render)
5. **Input Validation**: API validates all inputs using Pydantic models

### Example CORS Configuration

```python
# In api.py, update CORS middleware for production:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

## 📈 Performance

### Response Times

- **Health Check**: < 100ms
- **Analysis (with vector search)**: 5-15 seconds
- **Analysis (without vector search)**: 3-10 seconds

### Optimization Tips

1. **Pre-compute similar drugs**: Pass `similar_drugs` in request
2. **Cache results**: Implement caching for repeated queries
3. **Use faster model**: Switch to `gemini-2.5-flash` for speed
4. **Upgrade hosting**: Use paid tier for better performance

## 🐛 Troubleshooting

### Common Issues

**1. API Key Error**
```
Error: Server configuration error: Missing GOOGLE_API_KEY
```
**Solution**: Set `GOOGLE_API_KEY` environment variable

**2. Slow Response Times**
```
Request takes > 30 seconds
```
**Solution**:
- Check network connection
- Verify Gemini API is accessible
- Consider using faster model

**3. CORS Errors**
```
Access to fetch blocked by CORS policy
```
**Solution**: CORS is enabled for all origins by default. Check browser console for specific error.

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python api.py
```

## 📚 Additional Resources

- [SynthaTrial Documentation](docs/README.md)
- [Deployment Guide](RENDER_DEPLOYMENT.md)
- [Frontend Example](examples/anukriti_frontend_example.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🆘 Support

For issues or questions:
- Check the [troubleshooting section](#troubleshooting)
- Review API logs
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

**Version**: 0.2.0
**Last Updated**: 2026-02-13
