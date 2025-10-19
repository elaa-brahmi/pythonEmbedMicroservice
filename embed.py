from fastapi import FastAPI
from pipeline.model_loader import load_model
from pipeline.pinecone_client import init_pinecone
from pipeline.data_handler import load_data
from pipeline.indexer import upsert_batches
import os

app = FastAPI(title="AI Career Embed Service")

# Path to the cleaned jobs JSON
DATA_FILE = os.path.join(os.path.dirname(__file__), "data/cleaned_jobs.json")

# Cached globals to avoid re-loading heavy objects on every request
MODEL = None
INDEX = None


@app.on_event("startup")
def startup_event():
    """Load the embedding model and initialize Pinecone once at startup.

    This keeps the /embed endpoint fast and avoids re-downloading models
    for every request.
    """
    global MODEL, INDEX
    MODEL = load_model()
    INDEX = init_pinecone()


@app.post("/embed")
async def embed_data():
    if MODEL is None or INDEX is None:
        # Fallback in case startup didn't run (e.g. direct call)
        MODEL = load_model()
        INDEX = init_pinecone()

    data = load_data(DATA_FILE)
    print(f"Loaded {len(data)} job entries from {DATA_FILE}")
    upsert_batches(INDEX, MODEL, data)
    return {"message": f"Embedded {len(data)} jobs successfully."}
