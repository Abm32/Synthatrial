# Pinecone Index Setup Guide

## Quick Setup (Recommended)

Run the automated setup script:

```bash
# Make sure your API key is set
export PINECONE_API_KEY="your_api_key_here"

# Run the setup script
python scripts/setup_pinecone_index.py
```

The script will:
- ✅ Check if the index already exists
- ✅ Create the index with correct settings (2048 dimensions, cosine metric)
- ✅ Verify the index is ready

## Manual Setup (Alternative)

If you prefer to create the index manually:

### Step 1: Go to Pinecone Dashboard
Visit: https://app.pinecone.io/

### Step 2: Create New Index
1. Click **"Create Index"** button
2. Fill in the form:
   - **Index Name**: `drug-index`
   - **Dimensions**: `2048`
   - **Metric**: `cosine`
   - **Cloud Provider**: Choose AWS or GCP
   - **Region**: Choose your preferred region (e.g., `us-east-1`)

### Step 3: Click "Create Index"
Wait 1-2 minutes for the index to be ready.

## Verify Setup

After creating the index, verify it works:

```bash
python -c "
from pinecone import Pinecone
import os
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index('drug-index')
print('✓ Index is ready!')
print(f'  Total vectors: {index.describe_index_stats().get(\"total_vector_count\", 0)}')
"
```

## Index Configuration

**Required Settings:**
- **Name**: `drug-index` (must match exactly)
- **Dimensions**: `2048` (matches molecular fingerprint size)
- **Metric**: `cosine` (for similarity search)

**Why these settings?**
- **2048 dimensions**: Our molecular fingerprints (Morgan Fingerprints) are 2048 bits
- **Cosine metric**: Best for comparing molecular similarity vectors
- **Index name**: Must match what the code expects

## Troubleshooting

### "Index not found" Error

**Solution**: Run the setup script:
```bash
python scripts/setup_pinecone_index.py
```

### "Invalid dimension" Error

**Solution**: The index must have exactly 2048 dimensions. Delete and recreate:
```bash
python scripts/setup_pinecone_index.py
# Choose option 2 to delete and recreate
```

### "Quota exceeded" Error

**Solution**: 
- Check your Pinecone plan limits
- Free tier allows 1 index
- Upgrade plan if needed

### Index Creation Takes Too Long

**Solution**: 
- Normal: 1-5 minutes
- If >10 minutes, check Pinecone dashboard for errors
- Try a different region

## Next Steps

After creating the index:

1. **Verify it works**:
   ```bash
   python quick_test.py
   ```

2. **Ingest ChEMBL data**:
   ```bash
   python scripts/ingest_chembl_to_pinecone.py
   ```

3. **Test vector search**:
   ```bash
   python main.py
   ```

## Free Tier Limits

Pinecone free tier includes:
- ✅ 1 index
- ✅ 100,000 vectors
- ✅ Sufficient for MVP/testing

For production with full ChEMBL (millions of drugs), consider upgrading.

## API Key Setup

If you haven't set your API key yet:

```bash
# Option 1: Export in terminal
export PINECONE_API_KEY="your_key_here"

# Option 2: Add to .env file
echo "PINECONE_API_KEY=your_key_here" >> .env

# Option 3: Set in Python
import os
os.environ["PINECONE_API_KEY"] = "your_key_here"
```

Get your API key from: https://app.pinecone.io/
