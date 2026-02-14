# Microservices Architecture Migration - Complete ✅

**Date:** February 14, 2025
**Status:** ✅ **COMPLETED**

---

## What Changed

The Streamlit UI (`app.py`) has been **successfully migrated** from a monolithic architecture (direct imports) to a **microservices architecture** (HTTP API calls).

### Before (Monolithic):
```python
from src.agent_engine import run_simulation
from src.vector_search import find_similar_drugs

# Direct function calls
result = run_simulation(drug_name, similar_drugs, patient_profile)
```

### After (Microservices):
```python
import requests

# HTTP API calls
response = requests.post(
    f"{API_URL}/analyze",
    json={
        "drug_name": drug_name,
        "patient_profile": patient_profile,
        "drug_smiles": smiles_input
    }
)
result = response.json()["result"]
```

---

## Key Changes Made

### 1. **Removed Direct Imports**
- ❌ Removed: `from src.agent_engine import run_simulation`
- ❌ Removed: `from src.vector_search import find_similar_drugs`
- ❌ Removed: `from src.input_processor import get_drug_fingerprint`
- ✅ Kept: `import requests` (already present)

### 2. **Added API Configuration**
```python
# API URL from environment variable or default
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

# Support for Streamlit Secrets
if hasattr(st, "secrets") and "API_URL" in st.secrets:
    API_BASE_URL = st.secrets["API_URL"]
```

### 3. **Added API Health Check**
- Real-time API connection status
- Cached health checks (60-second TTL)
- Visual status indicators in UI
- Error messages with troubleshooting tips

### 4. **Replaced Analysis Logic**
- **Before:** Direct function calls with progress steps
- **After:** Single HTTP POST to `/analyze` endpoint
- API handles all backend processing (fingerprinting, vector search, LLM)
- UI just displays results

### 5. **Enhanced Error Handling**
- Connection errors (API not reachable)
- Timeout errors (API too slow)
- HTTP status code handling (500, 503, etc.)
- Detailed error messages with troubleshooting

### 6. **Added API Status Display**
- Real-time API health in status bar
- API URL shown in sidebar
- Refresh button for API status
- Health check endpoint in About tab

---

## Architecture Diagram

### New Microservices Architecture:

```
┌─────────────────────┐
│   Streamlit UI      │
│     (app.py)        │
│  Port: 8501         │
└──────────┬──────────┘
           │ HTTP POST /analyze
           │ JSON Request
           ▼
┌─────────────────────┐
│   FastAPI API       │
│     (api.py)        │
│  Port: 8000/10000   │
└──────────┬──────────┘
           │ Direct imports
           ▼
┌─────────────────────┐
│  Backend Engine      │
│     (src/)          │
│  - agent_engine      │
│  - vector_search     │
│  - input_processor   │
└─────────────────────┘
```

**Benefits:**
- ✅ UI and API can be deployed separately
- ✅ Better for cloud-native architecture
- ✅ Easier scaling (scale API independently)
- ✅ Better for competition demo (shows proper architecture)

---

## Configuration

### Environment Variables

**For UI (Streamlit):**
```bash
API_URL=http://localhost:8000              # Local development
API_URL=https://anukriti-api.onrender.com  # Production (Render)
```

**For API (FastAPI):**
```bash
GOOGLE_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash
PORT=10000  # Render uses 10000
```

### Streamlit Secrets (for Streamlit Cloud)

Create `.streamlit/secrets.toml`:
```toml
API_URL = "https://anukriti-api.onrender.com"
```

---

## Testing

### Local Testing

**1. Start API:**
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

**2. Start UI:**
```bash
export API_URL=http://localhost:8000
streamlit run app.py
```

**3. Test Flow:**
- Open http://localhost:8501
- Check API status (should show "🟢 API Connected")
- Run an analysis (e.g., Warfarin + CYP2C9 Poor Metabolizer)
- Verify results display correctly

### Production Testing

**1. Deploy API to Render:**
- Get API URL: `https://anukriti-api.onrender.com`

**2. Configure UI:**
```bash
export API_URL=https://anukriti-api.onrender.com
streamlit run app.py
```

**3. Or use Streamlit Secrets:**
- Add `API_URL` to Streamlit Cloud secrets

---

## API Endpoints Used

### `GET /` - Health Check
```python
response = requests.get(f"{API_URL}/")
# Returns: {"status": "Anukriti AI Engine Online", "version": "0.2.0", ...}
```

### `GET /health` - Detailed Health
```python
response = requests.get(f"{API_URL}/health")
# Returns: Detailed service status
```

### `POST /analyze` - Drug Analysis
```python
response = requests.post(
    f"{API_URL}/analyze",
    json={
        "drug_name": "Warfarin",
        "patient_profile": "ID: TEST\nGenetics: CYP2C9 Poor Metabolizer",
        "drug_smiles": "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
        "similar_drugs": None  # API handles this
    }
)
# Returns: {"result": "...", "risk_level": "High", "drug_name": "Warfarin", "status": "success"}
```

---

## Error Handling

### Connection Errors
```python
except requests.exceptions.ConnectionError:
    st.error("Could not connect to API. Check if API is running.")
```

### Timeout Errors
```python
except requests.exceptions.Timeout:
    st.error("API request timed out (>120 seconds). Try again.")
```

### HTTP Errors
```python
if response.status_code == 503:
    raise Exception("AI service temporarily unavailable")
elif response.status_code == 500:
    error_detail = response.json().get("detail", "Unknown error")
    raise Exception(f"Server error: {error_detail}")
```

---

## Deployment Scenarios

### Scenario 1: Both on Same Server (Docker)
- UI and API in same container
- Use `http://localhost:8000` for API_URL
- Works but not ideal for microservices

### Scenario 2: Separate Deployments (Recommended)
- **API:** Deploy to Render (or AWS)
- **UI:** Deploy to Streamlit Cloud (or separate Render service)
- Use production API URL
- **Best for competition demo**

### Scenario 3: Local Development
- API: `uvicorn api:app --port 8000`
- UI: `streamlit run app.py` (with `API_URL=http://localhost:8000`)
- Fast iteration and debugging

---

## Competition Benefits

### ✅ **Shows Proper Architecture**
- Microservices design
- API-first approach
- Separation of concerns

### ✅ **Cloud-Native**
- Can deploy UI and API separately
- Scales independently
- Better for AWS/Render deployment

### ✅ **Professional Demo**
- Shows you understand modern architecture
- Demonstrates API design skills
- Better than monolithic approach

---

## Migration Checklist

- [x] Remove direct imports from `app.py`
- [x] Add API URL configuration
- [x] Replace function calls with HTTP requests
- [x] Add API health check
- [x] Update error handling
- [x] Add API status display
- [x] Test locally
- [ ] Deploy API to Render
- [ ] Deploy UI with API URL configured
- [ ] Test end-to-end
- [ ] Record demo video

---

## Next Steps

1. **Deploy API to Render:**
   ```bash
   git push origin main
   # Then deploy on render.com
   ```

2. **Configure UI with API URL:**
   - Set `API_URL` environment variable
   - Or use Streamlit Secrets

3. **Test End-to-End:**
   - Run analysis from UI
   - Verify API calls work
   - Check error handling

4. **Build Kiro UI (Alternative):**
   - Use the same API URL
   - Call `/analyze` endpoint
   - Display results

---

## Files Modified

- ✅ `app.py` - Migrated to microservices architecture
- ✅ `DEPLOYMENT_ANALYSIS.md` - Updated with new architecture

---

**Status: ✅ MIGRATION COMPLETE - READY FOR DEPLOYMENT**
