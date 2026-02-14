# Quick Start: Using the New Improvements

## 1. Install New Dependencies

```bash
pip install -r requirements.txt
```

This will install `tenacity` for retry logic.

---

## 2. Update Your Code (If Needed)

### Using Configuration

**Before:**
```python
import os
api_key = os.getenv("GOOGLE_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
```

**After:**
```python
from src.config import config
api_key = config.GOOGLE_API_KEY
model = config.GEMINI_MODEL
```

### Using Exceptions

**Before:**
```python
if not mol:
    raise ValueError("Invalid SMILES string")
```

**After:**
```python
from src.exceptions import InvalidSMILESError
if not mol:
    raise InvalidSMILESError(smiles, reason="RDKit could not parse")
```

### Using Logging

**Before:**
```python
print("Processing drug...")
```

**After:**
```python
from src.logging_config import get_logger
logger = get_logger(__name__)
logger.info("Processing drug...")
```

---

## 3. Set Up Logging (One-Time Setup)

Add to your main entry points:

**app.py:**
```python
from src.logging_config import setup_logging
setup_logging()  # At the top, after imports
```

**main.py:**
```python
from src.logging_config import setup_logging
setup_logging()  # At the top, after imports
```

---

## 4. Environment Variables (Optional)

Add these to your `.env` file for fine-tuning:

```bash
# Retry Configuration
GEMINI_MAX_RETRIES=3
PINECONE_MAX_RETRIES=3

# Caching
ENABLE_CACHING=true
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/synthatrial.log
```

---

## 5. What's Automatic?

✅ **Retry Logic** - Automatically retries failed API calls (no code changes needed)
✅ **Caching** - Automatically caches fingerprints (enabled by default)
✅ **Error Handling** - Better error messages automatically
✅ **Configuration Validation** - Automatically validates on startup

---

## 6. Testing

Everything should work as before, but with:
- Better error messages
- Automatic retries on failures
- Faster repeated operations (caching)
- Better debugging (logging)

---

## Need Help?

See `IMPROVEMENTS_IMPLEMENTED.md` for detailed documentation.
