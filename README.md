# Embedding Microservice

This small FastAPI service loads `data/cleaned_jobs.json`, generates embeddings with `sentence-transformers`, and upserts vectors into a Pinecone index.

Environment variables

- PINECONE_API_KEY: (required) your Pinecone API key
- PINECONE_INDEX_NAME: (optional) index name, default `rag-jobs`
- PINECONE_ENV: (optional) Pinecone environment

Quick start

1. Create a virtual environment and install requirements

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Set environment variables (PowerShell example)

```powershell
$env:PINECONE_API_KEY = "your-key-here"
$env:PINECONE_INDEX_NAME = "rag-jobs"
$env:PINECONE_ENV = "us-west1-gcp"  # optional
```

3. Run the service

```powershell
uvicorn embed:app --reload
```

4. Trigger embedding (POST)

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/embed
```

Notes

- The service expects `data/cleaned_jobs.json` to be an array of job records with at least a `job_title` and `id` field.
- Model loading can take time on first start; the model is loaded once at startup.
